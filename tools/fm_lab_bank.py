#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Offline classic DX7 content export; no renderer, MIDI I/O or firmware selection."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content/fm-lab"
SOURCE_PIN = "cf35dc26709ede9c974654dfc2135f8c25a00082"
OP_FIELDS = (
    "rate1 rate2 rate3 rate4 level1 level2 level3 level4 breakpoint left_depth right_depth "
    "left_curve right_curve rate_scaling am_sensitivity velocity_sensitivity output_level "
    "mode coarse fine detune"
).split()
GLOBAL_FIELDS = (
    "pitch_rate1 pitch_rate2 pitch_rate3 pitch_rate4 pitch_level1 pitch_level2 pitch_level3 "
    "pitch_level4 algorithm feedback oscillator_sync lfo_speed lfo_delay lfo_pmd lfo_amd "
    "lfo_sync lfo_wave lfo_pms transpose"
).split()
OP_MAX = [99] * 11 + [3, 3, 7, 3, 7, 99, 1, 31, 99, 14]
GLOBAL_MAX = [99] * 8 + [31, 7, 1, 99, 99, 99, 99, 1, 5, 7, 48]


def integers(values, maxima, label):
    if not isinstance(values, (list, tuple, bytes, bytearray)) or len(values) != len(maxima):
        raise ValueError(f"{label}: expected {len(maxima)} integers")
    for i, (value, maximum) in enumerate(zip(values, maxima)):
        if type(value) is not int or not 0 <= value <= maximum:
            raise ValueError(f"{label}[{i}]: expected integer 0..{maximum}")
    return bytes(values)


def validate_vced(voice):
    data = integers(voice, OP_MAX * 6 + GLOBAL_MAX + [126] * 10, "VCED")
    if any(c < 32 for c in data[145:]):
        raise ValueError("VCED: expected a printable ASCII name")
    return data


def classic(source):
    """Only the donor's explicitly unused final zero is discarded."""
    data = integers(source, [127] * 155 + [0], "source record")
    return validate_vced(data[:155])


def pack(voice):
    v = validate_vced(voice)
    packed = bytearray()
    for start in range(0, 126, 21):
        o = v[start:start + 21]
        packed.extend(o[:11])
        packed.extend((o[11] | o[12] << 2, o[13] | o[20] << 3,
                       o[14] | o[15] << 2, o[16], o[17] | o[18] << 1, o[19]))
    packed.extend(v[126:135])
    packed.append(v[135] | v[136] << 3)
    packed.extend(v[137:141])
    packed.extend((v[141] | v[142] << 1 | v[143] << 4, v[144]))
    packed.extend(v[145:155])
    return bytes(packed)


def unpack(packed):
    b = integers(packed, [127] * 128, "VMEM")
    voice = bytearray()
    for start in range(0, 102, 17):
        o = b[start:start + 17]
        # Reject rather than silently erase donor waveform/reserved bits.
        if o[11] & 0x70 or o[13] & 0x60 or o[15] & 0x40:
            raise ValueError("VMEM: non-classic reserved operator bits")
        voice.extend(o[:11])
        voice.extend((o[11] & 3, o[11] >> 2, o[12] & 7, o[13] & 3,
                      o[13] >> 2, o[14], o[15] & 1, o[15] >> 1, o[16], o[12] >> 3))
    if b[111] & 0x70:
        raise ValueError("VMEM: reserved global bits")
    voice.extend(b[102:111])
    voice.extend((b[111] & 7, b[111] >> 3))
    voice.extend(b[112:116])
    voice.extend((b[116] & 1, (b[116] >> 1) & 7, b[116] >> 4, b[117]))
    voice.extend(b[118:128])
    return validate_vced(voice)


def single_dump(voice):
    """Classic 155-byte single-voice dump, MIDI channel 1; never sent here."""
    v = validate_vced(voice)
    return bytes([0xF0, 0x43, 0, 0, 1, 0x1B]) + v + bytes([(-sum(v)) & 127, 0xF7])


def load_bank(path=CONTENT / "voices.json"):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    expected = {"schema_version", "bank_id", "operator_order", "operator_fields", "global_fields", "voices"}
    if (not isinstance(data, dict) or set(data) != expected
            or type(data["schema_version"]) is not int or data["schema_version"] != 1
            or data["bank_id"] != "fm-lab-original-20" or data["operator_order"] != "OP6..OP1"
            or data["operator_fields"] != OP_FIELDS or data["global_fields"] != GLOBAL_FIELDS
            or not isinstance(data["voices"], list) or len(data["voices"]) != 20):
        raise ValueError("bank: unsupported schema, field order or voice count")
    bank, identities, names = [], set(), set()
    for row in data["voices"]:
        if not isinstance(row, dict) or set(row) != {"id", "name", "operators", "global", "source_unused_byte"}:
            raise ValueError("voice: unsupported fields")
        name, identity = row["name"], row["id"]
        if (not isinstance(name, str) or not 1 <= len(name) <= 10
                or not name.strip() or any(not 32 <= ord(c) <= 126 for c in name)):
            raise ValueError("voice: name must be 1..10 printable ASCII characters")
        if (not isinstance(identity, str) or not re.fullmatch(r"fm-lab\.[a-z0-9]+(?:-[a-z0-9]+)*", identity)
                or identity in identities or name in names):
            raise ValueError("voice: invalid or duplicate content identity/name")
        if not isinstance(row["operators"], list) or len(row["operators"]) != 6:
            raise ValueError("voice: expected six operators in OP6..OP1 order")
        operators = b"".join(integers(o, OP_MAX, f"{identity} operator") for o in row["operators"])
        globals_ = integers(row["global"], GLOBAL_MAX, f"{identity} global")
        unused = integers([row["source_unused_byte"]], [0], "source unused byte")
        voice = classic(operators + globals_ + name.ljust(10).encode("ascii") + unused)
        bank.append((identity, name, voice))
        identities.add(identity)
        names.add(name)
    return bank


def note_fixture():
    """SMF format 0, channel 1, 120 BPM; three held notes then a chord, no program/CC/SysEx."""
    def vlq(value):
        result = [value & 127]
        while value >> 7:
            value >>= 7
            result.insert(0, (value & 127) | 128)
        return bytes(result)

    track = bytearray(b"\x00\xff\x51\x03\x07\xa1\x20")
    for note, velocity in [(36, 32), (60, 80), (84, 120)]:
        track.extend(b"\x00" + bytes([0x90, note, velocity]))
        track.extend(vlq(1920) + bytes([0x80, note, 0]))
        track.extend(vlq(2880) + b"\xff\x01\x00")
    for note in [48, 55, 60]:
        track.extend(b"\x00" + bytes([0x90, note, 80]))
    for i, note in enumerate([48, 55, 60]):
        track.extend(vlq(1920 if i == 0 else 0) + bytes([0x80, note, 0]))
    track.extend(vlq(5760) + b"\xff\x2f\x00")
    return b"MThd" + struct.pack(">IHHH", 6, 0, 1, 480) + b"MTrk" + struct.pack(">I", len(track)) + track


def artifacts(bank):
    files = {"voices.vced": b"".join(v for _, _, v in bank),
             "voices.vmem": b"".join(pack(v) for _, _, v in bank), "audition/notes.mid": note_fixture()}
    for identity, _, voice in bank:
        files[f"audition/{identity}.syx"] = single_dump(voice)
    return files


def manifest(bank, files):
    def digest(data):
        return hashlib.sha256(data).hexdigest()

    inputs = ["content/fm-lab/voices.json", "content/fm-lab/upstream/gen_voices.py",
              "content/fm-lab/upstream/dx7_voices.h", "content/fm-lab/upstream/LICENSING.md",
              "tools/fm_lab_bank.py", "LICENSE"]
    return {"schema_version": 1, "content_id": "fm-lab-original-20", "license": "GPL-3.0-only",
            "copyright": "Copyright (C) 2026 Sven Trogus (original voices and upstream generator)",
            "source_repository": "https://github.com/jsmith13/fm_lab", "source_commit": SOURCE_PIN,
            "source_paths": ["tools/gen_voices.py", "firmware/src/dx7_voices.h", "LICENSING.md"],
            "collection_repository": "https://github.com/kmplngj/Felucca-Engines-GPL",
            "collection_pin_policy": "Consumer must pin the reviewed collection commit; no floating branch.",
            "operator_order": "OP6..OP1", "source_record_bytes": 156, "discarded_byte": {"offset": 155, "required": 0},
            "voice_count": len(bank), "raw_bytes": {"source_records": 3120, "vced": 3100, "vmem": 2560},
            "inputs": {p: digest((ROOT / p).read_bytes()) for p in inputs},
            "voices": [{"id": i, "name": n, "vced_sha256": digest(v), "vmem_sha256": digest(pack(v))}
                       for i, n, v in bank],
            "artifacts": {p: {"bytes": len(b), "sha256": digest(b)} for p, b in sorted(files.items())},
            "scope": "Offline optional classic content only; no renderer, host IDs, slots, defaults or PCM parity."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "build/fm-lab")
    parser.add_argument("--check", action="store_true", help="require the reviewed content manifest to match")
    args = parser.parse_args()
    try:
        bank = load_bank()
        files = artifacts(bank)
        data = manifest(bank, files)
        if args.check and data != json.loads((CONTENT / "manifest.json").read_text()):
            raise ValueError("manifest differs; review input/serialization changes before updating it")
        for path, payload in files.items():
            output = args.out / path
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(payload)
        (args.out / "manifest.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, TypeError, KeyError) as error:
        parser.exit(1, f"fm-lab: {error}\n")
    print(f"fm-lab: 20 voices, 3100 B VCED / 2560 B VMEM; offline audition fixtures -> {args.out}")


if __name__ == "__main__":
    main()
