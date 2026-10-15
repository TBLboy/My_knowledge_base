# Post-TASK-053 edits (not independently reviewed)

- Eq.(5) split into (5) lifting + new (6) readout (`eq:state_readout`); three appendices merged into one "Proof Details" with three unnumbered subheadings (labels app:* removed; none were referenced).
- Font warning fix: IEEEtran selects ptm at class load; XeTeX/Tectonic has no TU/ptm definition. Added TU/ptm -> TeX Gyre Termes shape declarations BEFORE \documentclass (guarded by \ifdefined\XeTeXversion); inputenc/fontenc only under non-XeTeX engines. Source starts with BOM (preserved).
- Result (build_font/Main.pdf, 8 pages): Font Warning 0, inputenc warning 0, Overfull 0, undefined refs 0; Underfull 10 (was 9); "Fontconfig error: Cannot load default config" is a Tectonic environment message, not fixable in source.
- Embedded fonts now TeXGyreTermes (Times clone) + CM math. Status: implemented-unverified; no independent review run.
- Compile used network (bundle fetch via 127.0.0.1:10808) instead of --only-cached because the new fonts were not cached.
