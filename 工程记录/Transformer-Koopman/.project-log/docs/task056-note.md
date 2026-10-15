# Figure placeholders (not independently reviewed)

- Added macro \figph{width}{height}{text} (bordered frame with description) in Main.tex preamble; three placeholders, all with captions marked "(Placeholder; figure to be drawn.)":
  - Fig.1 fig:overview, figure* (double column, 5.6 cm), end of Introduction: overall framework (window -> lifting/context -> scheduled A,B -> predictor; lower branch nominal rollout -> frozen matrices -> QP).
  - Fig.2 fig:rollout, single column (4.2 cm), Sec.II: common-history convention and recursive window update.
  - Fig.3 fig:freezing, single column (4.6 cm), Sec.IV: nominal / complete / frozen trajectories, gaps g_i and e_i.
- Each is referenced in text (Fig.~\ref). Existing pictures/ folder not used.
- Build: build_font/Main.pdf, 8 pages, Overfull 0, Font Warning 0, undefined refs 0. Fig.1 lands at top of page 3, Fig.3 at top of page 5.
- Replace \figph with \includegraphics once figures are drawn; no experiment figures added.
