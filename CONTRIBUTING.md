<!-- SPDX-License-Identifier: GPL-3.0-only -->
# Contributing GPL engines

Use this collection for GPL engines and their exclusive DSP, tables, generators
and tests. Keep hardware access, stable numeric engine IDs, UI identity, MIDI,
storage, voice allocation and firmware policy in Felucca. Existing firmware-native
engines stay in their current home until an explicit, tested extraction is agreed.

1. Read LICENSING.md, docs/INTEGRATION.md and Felucca's AGENTS.md,
   docs/extending.md and docs/performance.md.
2. Record the exact upstream source and its license before importing code or data.
   New original source files use the GPL-3.0-only SPDX header. Preserve existing
   attribution and compatible third-party terms.
3. Reuse the reviewed MIT engine contract and common DSP through the host's pinned
   dependency. Do not create a second copy or let the GPL collection mutate the
   MIT checkout. Propose contract changes explicitly if required.
4. Declare resource footprint, reset/claim/service lifetimes, helper reachability,
   tests and assets. Use bounded fixed-point processing and private state/RNG.
   No allocation, blocking I/O or storage in render callbacks.
5. Test the actual implementation, including silence, retrigger, releases,
   switches, state publication and relevant render partitions. Report target,
   host and device evidence separately; no unchecked speed or fit claims.
6. Land the engine source and tests here, then propose an explicit firmware pin,
   registry/profile integration and host qualification. Adding a file here must
   never silently add an instrument to the standard firmware.

The optional FM Lab content harness runs with `python3 -m unittest discover -s tests -v`
and `python3 tools/fm_lab_bank.py --check`. It validates offline voice serialization,
not engine DSP or device behavior. There is no standalone engine build yet; document
the actual supported harness with the first implementation rather than adding a
success-only placeholder or presenting the design catalog as a working module.
