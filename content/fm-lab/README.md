<!-- SPDX-License-Identifier: GPL-3.0-only -->
# Original FM Lab voices — optional offline content

Copyright (C) 2026 Sven Trogus, GPL-3.0-only: 20 voices designed for sloopDX and
retained by FM Lab. This collection preserves every source voice before selection.
It contains no FM renderer and does not install or select content in Felucca.

Collection owner: [#27](https://github.com/kmplngj/Felucca-Engines-GPL/issues/27).
Native audition/integration: [Felucca #516](https://github.com/kmplngj/Felucca/issues/516),
adoption plan [#517](https://github.com/kmplngj/Felucca/issues/517), exact collection
pin/profile consumption [#360](https://github.com/kmplngj/Felucca/issues/360).
Those firmware gates remain pending. No engine ID, preset slot, flash sector,
profile/default or protocol value is allocated here.

## Build and verify offline

With Python 3.10+ from the repository root:

```sh
python3 -m unittest discover -s tests -v
python3 tools/fm_lab_bank.py --check --out build/fm-lab
```

These commands use only the standard library and local files. They do not execute
the retained donor generator. All 20 names/bytes are checked against the exact
upstream header, alongside strict range/name/reserved-bit checks, an independent
packed-bit fixture, deterministic random round trips, source hashes, checked
manifest output and two clean-directory exports. The checked export rejects
unreviewed input/tool changes before writing artifacts. To propose a deliberate
change, generate a candidate manifest without `--check`, review all input/output
hash changes, and explicitly update the tracked manifest; never overwrite the
original source snapshots or source-byte expectations to make a failing test pass.

| Output under `build/fm-lab/` | Meaning / raw byte cost |
| --- | --- |
| `voices.vced` | 20 consecutive classic 155-byte records: **3,100 B** |
| `voices.vmem` | 20 consecutive classic 128-byte records: **2,560 B**; not a 32-voice bank dump |
| `audition/fm-lab.*.syx` | One classic single-voice dump per content ID, channel 1: **163 B each**, **3,260 B total** |
| `audition/notes.mid` | Format-0 note-only SMF, channel 1, 120 BPM; no program, bank, CC or SysEx messages |
| `manifest.json` | Source pin, file/output hashes, exact byte counts, local IDs and per-voice serialization hashes |

The source records total **3,120 B**, including their 20 unused final zeros.
File sizes above are content arithmetic, not linked firmware app/RAM/POOL costs.
JSON, notices and manifest have additional file bytes. The manifest records the
actual MIDI and other artifact sizes. No code is linked or state allocated in a
target by this change. A host consumer must pin the reviewed collection commit
alongside this content manifest, never a floating branch.

## Classic format contract

`voices.json` declares field order explicitly. Each operator array follows the
21 VCED fields and is stored **OP6 first through OP1**. The global array contains
pitch envelope, zero-based algorithm, feedback, oscillator sync, LFO and transpose.
The 10-byte name is ASCII padded with spaces. The donor's byte at offset 155 must
be zero and is deliberately dropped; a nonzero byte is an error, not an extension.

Rates/levels/depths/speed/fine fields are 0..99; curves and AMS 0..3; rate/velocity
scaling and feedback/PMS 0..7; mode/sync 0..1; coarse/algorithm 0..31; detune 0..14;
LFO wave 0..5; transpose 0..48. Names must contain printable ASCII. Invalid data is
rejected rather than clamped or masked. VMEM uses only classic packed fields;
operator byte 11 bits 4..6 and other reserved bits are rejected on decode. No
FM Lab waveform extension is imported. **SAW LEAD remains its original classic
algorithm-32 patch**, not a non-sine waveform design.

Content IDs are local strings, independent of native slots. Source order remains:
EPIANO 1/2, FM BASS, SLAP BASS, SUB BASS, BRASS, STRINGS, GLASS PAD, BELLS,
MARIMBA, ORGAN, CLAV, PLUCK, FLUTE, SAW LEAD, KOTO, DEEP SUB, 808 SUB, REESE,
INIT VOICE. No curation or duplicate removal has occurred.

## Audition handoff

No MIDI is transmitted by any command here. The SysEx files are offline fixtures
for a separately chosen classic-DX7-compatible software receiver/librarian. Current
Felucca direct SysEx compatibility and bank/profile access are not established by
these files. Do not send them to an FM-1 or overwrite a user's bank as part of this
collection check. Native integration and safe temporary-bank access belong to #516.

For a disposable software audition setup, load one single-voice fixture into an
isolated patch, confirm its exact name, and play `notes.mid`. It holds MIDI notes
36/60/84 at velocities 32/80/120 for two seconds each, with three seconds of release
between them; then holds a 48/55/60 chord for two seconds and leaves six seconds
for release (23 seconds total). Receiver octave labels may vary; note numbers do
not. The file changes no program/bank or controller state. Repeat for all 20 IDs,
including INIT VOICE; leave MIDI sustain off and disable host effects for an initial
reference. Check held, released and repeated notes separately before native curation.
Record receiver/version, content/collection pin, name, note/velocity and observations.

This prepares reproducible musical inputs, not a claimed audible or PCM baseline.
Donor and native engines differ in sine precision, envelope/LFO ownership, control
quantum, mono policy, gain/DC and effects. Level-matched listening, quiet/extreme
notes, one/two/four-part native loads, persistence and real FM-1 qualification remain
the firmware owner's work. No receiver or device was used to qualify sound here.

## Provenance and modifications

Pinned repository: [jsmith13/fm_lab](https://github.com/jsmith13/fm_lab/tree/cf35dc26709ede9c974654dfc2135f8c25a00082).
The original generator and LICENSING explicitly identify Sven Trogus and state
that every factory voice was designed for sloopDX, with no Yamaha or M-VAVE bank.
The complete generator has only `math`/`sys` imports, embedded operator recipes
and an output writer; no external bank, sample, asset loader or transitive data
dependency is used for these 20 synth voices. Its unused noise helper is for drums;
none of the selected synth definitions requests noise. Drum data is not imported.

| Exact upstream path → retained snapshot | SHA-256 |
| --- | --- |
| `tools/gen_voices.py` → `upstream/gen_voices.py` | `275635a493fcc72cb58f797d049a2ea1839e190c44e12c30bfdb83745311b12d` |
| `firmware/src/dx7_voices.h` → `upstream/dx7_voices.h` | `93e13fd62eb7cfbcc4ec5ebe63dde9b0b064e9ff1286983243e9317585fc626f` |
| `LICENSING.md` → `upstream/LICENSING.md` | `4d15c92fb7e1a08ea6ed48e9ed6504203587e54b1d248ba407f9a80a9a5a9b9f` |

These snapshots are byte-for-byte unchanged, including the generator's stale
`gen_dx7_bank.py`/`dx7_bank.h` docstring paths. Use the collection command above;
those inherited paths are not collection instructions. Full GPL-3.0 text is in
[LICENSE](../../LICENSE), byte-identical to the donor's pinned LICENSE. No donor
DSP is copied, so no Apache-derived renderer enters this content closure.

`voices.json` transcribes the header records into labeled operator/global arrays
and local identities without changing parameters or names. The collection tool
adds strict validation, classic packing/unpacking, checksummed single-voice dumps,
a separate note-only MIDI fixture and a content manifest. Original copyright and
notices remain with the sources and exports' accompanying manifest/license. Binary
voice/MIDI payloads cannot carry textual SPDX comments: distribute this README,
manifest, readable sources and LICENSE alongside them.
