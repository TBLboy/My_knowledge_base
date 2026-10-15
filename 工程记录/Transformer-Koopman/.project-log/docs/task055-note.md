# Post-TASK-053 edits, round 3 (not independently reviewed)

- Abstract: removed trailing scope-disclaimer sentence and the filler "We analyze this distinction directly."; "state-preserving" wording removed everywhere (label eq:state_preserving_lifting kept).
- 18 over-defensive sentences trimmed (intro, Sec.III, Sec.IV, conclusion). Experiments section untouched (frozen).
- Bibliography: reordered by first citation (script task055-reorder-bib.py; backups task055-before.tex = before reorder, task055-before-citations.tex = after intro expansion, before pruning).
- Intro extended with citations so 25 -> 40 cited entries (reviews, learned lifting, controlled Koopman, multi-step learning, Transformer-Koopman forecasting, RTI/advanced-step NMPC stability). 12 uncited entries deleted: koopman1932spectra, rowley2009spectral, williams2015kernel, yeung2019learning, morton2019deep, azencot2020forecasting, brunton2016invariant, shi2022deep, klus2018data, rota1960joint, daubechies1992sets, jungers2009joint (recoverable from task055-before.tex).
- Build: build_font/Main.pdf, 7 pages, Overfull 0, Font Warning 0, undefined refs 0, Underfull 10.
- New cited-claim wording not verified against the full text of each added reference (descriptions kept to titles/abstract-level scope). Status implemented-unverified.
