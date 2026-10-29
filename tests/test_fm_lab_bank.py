# SPDX-License-Identifier: GPL-3.0-only
"""Preserve the pinned source bytes and independently exercise classic wire fields."""
import copy
import hashlib
import json
from pathlib import Path
import random
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import fm_lab_bank as bank

NAMES = ["EPIANO 1", "EPIANO 2", "FM BASS", "SLAP BASS", "SUB BASS", "BRASS", "STRINGS",
         "GLASS PAD", "BELLS", "MARIMBA", "ORGAN", "CLAV", "PLUCK", "FLUTE", "SAW LEAD",
         "KOTO", "DEEP SUB", "808 SUB", "REESE", "INIT VOICE"]
SOURCE_HASHES = {
    "gen_voices.py": "275635a493fcc72cb58f797d049a2ea1839e190c44e12c30bfdb83745311b12d",
    "dx7_voices.h": "93e13fd62eb7cfbcc4ec5ebe63dde9b0b064e9ff1286983243e9317585fc626f",
    "LICENSING.md": "4d15c92fb7e1a08ea6ed48e9ed6504203587e54b1d248ba407f9a80a9a5a9b9f",
}


class BankTests(unittest.TestCase):
    def setUp(self):
        self.voices = bank.load_bank()

    def test_exact_pinned_source_and_all_twenty_records(self):
        upstream = bank.CONTENT / "upstream"
        for path, digest in SOURCE_HASHES.items():
            self.assertEqual(hashlib.sha256((upstream / path).read_bytes()).hexdigest(), digest)
        # Parse literal C data, never execute the donor generator.
        rows = re.findall(r"^    \{([\d, ]+)\},\s*/\* (.*?) \*/", (upstream / "dx7_voices.h").read_text(), re.M)
        self.assertEqual([name for _, name in rows], NAMES)
        self.assertEqual([name for _, name, _ in self.voices], NAMES)
        for (values, source_name), (_, name, vced) in zip(rows, self.voices):
            source = bytes(map(int, values.split(",")))
            self.assertEqual(len(source), 156)
            self.assertEqual(source[-1], 0)
            self.assertEqual(vced, source[:-1], name)
            self.assertEqual(vced[145:], source_name.ljust(10).encode("ascii"))
            self.assertEqual(bank.unpack(bank.pack(vced)), source[:-1], name)
        # Distinct source operator parameters detect accidental OP1-first order.
        self.assertEqual(self.voices[0][2][16], 70)  # EPIANO 1, OP6 output
        self.assertEqual(self.voices[0][2][121], 99)  # OP1 output
        self.assertEqual(self.voices[17][2][126:134], bytes([72, 99, 99, 0, 50, 50, 50, 66]))
        self.assertEqual(self.voices[14][2][134], 31)  # SAW LEAD is classic algorithm 32

    def test_classic_bit_layout_independent_extreme_fixture(self):
        # Every packed field at once: explicit expected bytes, not pack/unpack alone.
        operator = [99] * 11 + [3, 2, 6, 3, 5, 98, 1, 31, 97, 14]
        global_ = [99] * 8 + [31, 7, 1, 98, 97, 96, 95, 1, 5, 7, 48]
        vced = bytes(operator * 6 + global_ + list(b"BOUNDARY  "))
        expected_op = bytes([99] * 11 + [11, 118, 23, 98, 63, 97])
        expected = expected_op * 6 + bytes([99] * 8 + [31, 15, 98, 97, 96, 95, 123, 48]) + b"BOUNDARY  "
        self.assertEqual(bank.pack(vced), expected)
        self.assertEqual(bank.unpack(expected), vced)
        for value in [0, 1]:
            changed = bytearray(vced)
            changed[17] = value  # fixed versus ratio mode must survive unchanged
            self.assertEqual(bank.unpack(bank.pack(changed)), changed)

    def test_all_fields_reject_out_of_range_without_clamping(self):
        maxima = bank.OP_MAX * 6 + bank.GLOBAL_MAX + [126] * 10
        reference = list(self.voices[0][2])
        for offset, maximum in enumerate(maxima):
            for invalid in [-1, maximum + 1, True, 1.5, "0"]:
                with self.subTest(offset=offset, invalid=invalid):
                    values = reference.copy()
                    values[offset] = invalid
                    with self.assertRaises(ValueError):
                        bank.pack(values)
        for malformed in [None, "x" * 155, [], reference[:-1], reference + [0]]:
            with self.assertRaises(ValueError):
                bank.pack(malformed)

    def test_names_and_source_spare_are_not_silently_sanitized(self):
        v = bytearray(self.voices[0][2])
        for invalid in [0, 31, 127]:
            v[145] = invalid
            with self.assertRaises(ValueError):
                bank.validate_vced(v)
        original = self.voices[0][2]
        self.assertEqual(bank.classic(original + b"\x00"), original)
        for malformed in [original, original + b"\x01", original + b"\x00\x00"]:
            with self.assertRaises(ValueError):
                bank.classic(malformed)

    def test_packed_reserved_bits_and_invalid_fields(self):
        reference = bank.pack(self.voices[0][2])
        for offset, mask in [(11, 16), (11, 32), (11, 64), (13, 32), (13, 64), (15, 64), (111, 16)]:
            v = bytearray(reference)
            v[offset] |= mask
            with self.subTest(offset=offset, mask=mask), self.assertRaises(ValueError):
                bank.unpack(v)
        for offset, value in [(0, 100), (12, 120), (14, 100), (16, 100), (110, 32), (116, 12), (117, 49), (118, 31)]:
            v = bytearray(reference)
            v[offset] = value
            with self.subTest(offset=offset, value=value), self.assertRaises(ValueError):
                bank.unpack(v)
        for v in [reference[:-1], reference + b"\x00", bytes([128]) + reference[1:]]:
            with self.assertRaises(ValueError):
                bank.unpack(v)

    def test_valid_field_boundaries_and_deterministic_random_voices(self):
        rng = random.Random(27)
        maxima = bank.OP_MAX * 6 + bank.GLOBAL_MAX
        for values in [[0] * 145, maxima] + [[rng.randint(0, m) for m in maxima] for _ in range(100)]:
            v = bytes(values) + b"SYNTH TEST"
            self.assertEqual(bank.unpack(bank.pack(v)), v)

    def test_bank_schema_identity_and_names(self):
        original = json.loads((bank.CONTENT / "voices.json").read_text())
        mutations = [lambda d: d.update(schema_version=True), lambda d: d.update(extra=0),
                     lambda d: d["voices"].pop(), lambda d: d["operator_fields"].reverse(),
                     lambda d: d["voices"][0].update(id="../escape"),
                     lambda d: d["voices"][0].update(id=d["voices"][1]["id"]),
                     lambda d: d["voices"][0].update(name=d["voices"][1]["name"]),
                     lambda d: d["voices"][0].update(name="é"),
                     lambda d: d["voices"][0].update(name="\n"),
                     lambda d: d["voices"][0].update(name="12345678901"),
                     lambda d: d["voices"][0].update(name=""),
                     lambda d: d["voices"][0].update(source_unused_byte=1),
                     lambda d: d["voices"][0]["operators"].pop(),
                     lambda d: d["voices"][0]["global"].append(0)]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.json"
            for mutate in mutations:
                data = copy.deepcopy(original)
                mutate(data)
                path.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    bank.load_bank(path)

    def test_single_voice_dump_header_checksum_and_payload(self):
        for _, _, v in self.voices:
            syx = bank.single_dump(v)
            self.assertEqual(len(syx), 163)
            self.assertEqual(syx[:6], bytes([240, 67, 0, 0, 1, 27]))
            self.assertEqual(syx[6:161], v)
            self.assertEqual(sum(syx[6:162]) % 128, 0)
            self.assertEqual(syx[-1], 247)
            self.assertTrue(all(x < 128 for x in syx[1:-1]))

    def test_manifest_raw_costs_and_golden_exports(self):
        files = bank.artifacts(self.voices)
        expected = json.loads((bank.CONTENT / "manifest.json").read_text())
        self.assertEqual(bank.manifest(self.voices, files), expected)
        self.assertEqual(len(files["voices.vced"]), 3100)
        self.assertEqual(len(files["voices.vmem"]), 2560)
        self.assertEqual(sum(len(v) for k, v in files.items() if k.endswith(".syx")), 3260)
        self.assertEqual(len(files), 23)

    def test_note_fixture_is_bounded_note_only_midi(self):
        data = bank.note_fixture()
        self.assertEqual(data[:14], b"MThd" + struct.pack(">IHHH", 6, 0, 1, 480))
        self.assertEqual(data[14:18], b"MTrk")
        self.assertEqual(struct.unpack(">I", data[18:22])[0], len(data) - 22)
        offset, ticks, events, active = 22, 0, [], set()
        while offset < len(data):
            delta = 0
            while True:
                value = data[offset]
                offset += 1
                delta = (delta << 7) | (value & 127)
                if not value & 128:
                    break
            ticks += delta
            status = data[offset]
            offset += 1
            if status == 255:
                kind, length = data[offset:offset + 2]
                offset += 2
                self.assertIn(kind, [81, 1, 47])
                offset += length
            else:
                self.assertIn(status, [0x90, 0x80])
                note, velocity = data[offset:offset + 2]
                offset += 2
                events.append((ticks, status, note, velocity))
                if status == 0x90:
                    self.assertNotIn(note, active)
                    active.add(note)
                else:
                    active.remove(note)
        self.assertEqual(events[:6], [(0, 144, 36, 32), (1920, 128, 36, 0),
                                     (4800, 144, 60, 80), (6720, 128, 60, 0),
                                     (9600, 144, 84, 120), (11520, 128, 84, 0)])
        self.assertEqual(ticks, 22080)
        self.assertFalse(active)

    def test_offline_cli_reproduces_every_byte(self):
        with tempfile.TemporaryDirectory() as directory:
            outputs = []
            for n in range(2):
                out = Path(directory) / str(n)
                subprocess.run([sys.executable, str(ROOT / "tools/fm_lab_bank.py"), "--check", "--out", str(out)],
                               cwd=directory, check=True, capture_output=True)
                outputs.append({str(p.relative_to(out)): p.read_bytes() for p in out.rglob("*") if p.is_file()})
            self.assertEqual(outputs[0], outputs[1])
            self.assertEqual(set(outputs[0]), set(bank.artifacts(self.voices)) | {"manifest.json"})

    def test_checked_export_rejects_changed_input_before_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(bank.CONTENT, root / "content/fm-lab")
            (root / "tools").mkdir()
            shutil.copyfile(ROOT / "tools/fm_lab_bank.py", root / "tools/fm_lab_bank.py")
            shutil.copyfile(ROOT / "LICENSE", root / "LICENSE")
            source = root / "content/fm-lab/voices.json"
            data = json.loads(source.read_text())
            data["voices"][0]["operators"][0][16] -= 1
            source.write_text(json.dumps(data))
            output = root / "export"
            result = subprocess.run([sys.executable, str(root / "tools/fm_lab_bank.py"), "--check", "--out", str(output)],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("manifest differs", result.stderr)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
