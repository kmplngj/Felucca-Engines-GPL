<!-- SPDX-License-Identifier: GPL-3.0-only -->
# Combining engine collections in Felucca

This is the agreed direction for a future firmware integration. The current
resolver supports the MIT collection and native engines; GPL collection loading,
WAVE and multi-collection source releases are not implemented by these files.

## Ownership and contract

Use one GPL collection for multiple engines, selected independently. Reuse the
MIT engine API and DSP where applicable; do not fork engine_t or compile duplicate
shared helpers. The firmware owns registration, stable IDs, descriptor/UI identity,
parameters, voice/memory ownership, startup modes, MIDI and persistence.

WAVE needs bounded main-loop table generation, cancellation and publication in
addition to audio rendering. First document those requirements against the current
host; make any service bridge explicit, versioned and context-safe. Do not claim
that the existing portable engine_t alone already supplies this contract. Host
glue stays in firmware; reusable recipe generation/render code belongs here.

## Pins and resolution

1. Add a separate reviewed GPL dependency at `firmware/engines-gpl/`; retain
   `firmware/engines/` for MIT. Check out exact committed pins in setup/CI. Builds
   never fetch branches, edit dependencies or pick their latest heads implicitly.
2. Extend the firmware-owned catalog and resolver with explicit collection/source
   ownership and dependencies. Local collection names are not numeric sound IDs.
   The host assigns one available append-only ID after checking concurrent work.
3. Resolve one selected set for JieLi target, native host and Wasm emulator, with
   identical sources, assets, helpers, tests and licenses. Reject duplicate/unknown
   IDs, missing API/providers/defaults, cycles, conflicting symbols and stale output.
4. A profile excluding GPL engines should not require that optional checkout or
   execute its generators. A profile including one must reject a missing, dirty,
   wrong-pin or incompatible GPL dependency before compilation. Source archives
   validate their declared inventories independently of Git availability.
5. Keep the standard profile explicit. Provide an opt-in mixed example after WAVE
   qualifies, plus a profile omitting it. Do not renumber sounds when changing the
   selection, nor require CPU2 or a particular startup mode for a sound engine.

## Source releases and licensing

Extend resolved-profile provenance, CI, clean-clone setup and source-archive/release
tools together. Record each collection URL and full pin, all build inputs, selection
hashes and per-component license/notice files. Export and verify every selected
dependency and any required generators/helpers; generated artifacts alone are not
complete corresponding source. Define any all-installed-sources archive policy
explicitly and verify every extra declared pin too.

Reproduce an installable package from its unpacked complete source archive without
network or Git. Missing/mismatched GPL sources or omitted notices must fail before
publishing a release. The combined Felucca firmware is GPL-3.0-only; MIT files retain
their notices. No separate permission is needed to combine these compatible terms.

## First implementation: WAVE

Start with DUELL's 26 factory recipe tables and oscillator controls, with no donor
morph, two-part bounds, user-table writes or universal-filter prerequisites. The
host keeps all existing engine IDs and sample storage. Factory sound conversion
must disclose features not available in the native host. User tables, extended
patches and persistent modulation need their own capacity and format owners.

The engine's header/table footprint and the bytes cleared at an arena claim are
different contracts. Guard the full footprint and alignment; prove unbuilt/stale
data cannot be read. Test simultaneous requests on four parts, main-loop service
fairness, cancelled builds and CPU2/fallback publication. No ISR borrows unowned
LCD/restore scratch. Preserve fades, tails and private RNG/phase ordering.

## Acceptance and delivery order

- Collection setup and source provenance first; WAVE engine/service contract and
  reusable implementation next; firmware pin/profile integration after that.
- Standard, mixed and GPL-omitted builds preserve stable IDs and unavailable sound
  records through mixed -> omitted -> mixed project/preset/favorite round trips.
- Engine tests and native/Wasm parity exercise actual source, claims, cancellation,
  reset, render partitions and tails. No golden/budget blanket regeneration.
- Fresh JieLi output reports app, RAM, POOL, RAMTEXT, NOINIT and both core/nested
  interrupt stack margins. Measure frame publication/IRQ-off time and worst render
  halves; separate host counts from FM-1 deadlines and listening observations.
- Default-off firmware sound/control/data/UI remain unchanged. A mixed profile
  must work with CPU2 off, on and fallback, without changing native persistence or
  promising physical timing based only on host/static evidence.
- Complete source/notice inventories and offline archive/package reproduction pass
  before a mixed release. Hardware checks remain explicit until performed.

Firmware coordination: https://github.com/kmplngj/Felucca/issues/28

WAVE integration: https://github.com/kmplngj/Felucca/issues/354

DUELL roadmap: https://github.com/kmplngj/Felucca/issues/359
