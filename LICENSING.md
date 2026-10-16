<!-- SPDX-License-Identifier: GPL-3.0-only -->
# Licensing and source provenance

New original code and documentation in this collection are GPL-3.0-only. The full
license is in LICENSE. Contributions must be available under terms compatible
with distribution in Felucca's GPL-3.0-only firmware.

Preserve each imported file's copyright and license. Compatible MIT, Apache-2.0
or other permissive components retain their own terms and notices; the collection
name is not permission to relabel them. A combined GPL firmware does not relicense
the separate MIT Felucca-Engines project or permit moving GPL additions back there
under an MIT header.

An imported engine must record its repository, full source commit, paths,
copyright/license evidence, modifications and any asset provenance. Include the
required license texts and notices in both this repository and complete firmware
source/release distributions when that engine is used. Do not import unknown or
incompatible material, or donor trademarks/logo artwork as engine assets.

## Planned WAVE source (not imported)

- Repository: https://github.com/oscillr/DUELL
- Source commit: `0bd7f904a18efd20fd6092a8bc645945c3fedf74`
- Engine: `felucca-base/firmware/src/eng_wave.c`, GPL-3.0-only SPDX header.
- Notices: `NOTICE.md` and `felucca-base/LICENSING.md` in that revision.
- Native adoption and qualification: https://github.com/kmplngj/Felucca/issues/354

This initial repository contains no WAVE implementation, factory sounds, donor
tables, logo or other donor assets. The port must preserve attribution and add a
file-level provenance inventory when code is actually imported. Separate rights
permission is not required to adapt GPL code under its GPL terms; offering that
derived code under MIT would require appropriate additional permission.
