<!-- SPDX-License-Identifier: GPL-3.0-only -->
# Felucca-Engines-GPL

A shared home for GPL synthesis engines that can be selected in a
[Felucca](https://github.com/kmplngj/Felucca) firmware build alongside the MIT
[Felucca-Engines](https://github.com/kmplngj/Felucca-Engines) collection.

**Status:** repository preparation and integration design. No engine is implemented
here yet, and current Felucca builds do not consume this collection. WAVE from
DUELL is the first planned port: [engine implementation #1](https://github.com/kmplngj/Felucca-Engines-GPL/issues/1),
with [Felucca #354](https://github.com/kmplngj/Felucca/issues/354) owning host integration.
The repository is [kmplngj/Felucca-Engines-GPL](https://github.com/kmplngj/Felucca-Engines-GPL).
The first firmware dependency pin and combined-profile integration remain pending
under [Felucca #360](https://github.com/kmplngj/Felucca/issues/360).

## One firmware, several source collections

| Component | Owns |
| --- | --- |
| Felucca-Engines (MIT) | Existing portable engines, shared engine interface and reusable DSP |
| Felucca-Engines-GPL | GPL engine implementations, their exclusive assets, generators and engine tests |
| Felucca firmware (GPL) | Stable engine IDs, build profiles, registration, voices, UI, effects, hardware, persistence and release packaging |

A firmware build profile will select individual engines across these collections
and the firmware-native catalog. The resolver will compile the selected sources
into **one statically linked GPL firmware image**. This is build-time selection;
the device's per-part engine selection chooses among the engines installed in
that image. A startup usage mode is a separate choice of playing workflow.

For example, a future custom profile could include MIT ANALOG and LOFI, GPL WAVE,
and native FM6. That is a design example, not a profile accepted by the current
resolver. Standard firmware will keep its explicit engine set until deliberately
changed. Actual combinations must pass dependencies and flash/RAM/deadline budgets.

The intended checkout locations are `firmware/engines/` for MIT and
`firmware/engines-gpl/` for GPL, each pinned to a reviewed commit. No build will
fetch a floating branch or modify a checked-out dependency.

## Start here

- [Integration design](docs/INTEGRATION.md): contract, profiles, source pins and validation.
- [Licensing and provenance](LICENSING.md): GPL contributions and inherited notices.
- [Contributing](CONTRIBUTING.md): engine and host ownership.
- [DUELL adoption plan](https://github.com/kmplngj/Felucca/issues/359).

`catalog.json` intentionally has no engines. It records collection identity only;
it does not register a stable firmware ID, enable WAVE or claim a usable module.

## MACRO in Felucca

[MACRO/Braids](https://github.com/kmplngj/Felucca/pull/503) is implemented in the
firmware as an opt-in `macro` hardware-test profile with 48 models and 51 factory presets.
It remains firmware-native and is excluded from the standard profile. WAVE/FOLD/FBFM
retain eight-voice operation; the added models use one voice per part. Physical
acceptance is tracked in [Felucca #27](https://github.com/kmplngj/Felucca/issues/27).

[MACRO extraction #25](https://github.com/kmplngj/Felucca-Engines-GPL/issues/25) tracks
the separate work to provide a portable implementation here. The existing wrapper,
generators and firmware tests are GPL-3.0-only; Braids/stmlib, adapted DSP and resource
inputs retain their MIT notices. No MACRO source or firmware dependency pin is
provided by this collection yet. The present firmware integration does not require
that future extraction or change the collection's empty catalog.

## License

New contributions use **GPL-3.0-only**; see [LICENSE](LICENSE). Retain upstream
copyright, SPDX and compatible third-party license notices on imported material.
Combining MIT and GPL code in Felucca does not change the MIT source files' license.
