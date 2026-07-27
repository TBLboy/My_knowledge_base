# Business Logic Graph

## Main (Tkinter Mode)

```text
A (GUI Shell Ready) -> B (Arm+Hand Page Ready) -> C (Operations Executed) -> D (State Updated) -> E (Session Closed)
```

## Main (Web Mode)

```text
W0 (Browser Opens) -> W1 (Login/Register) -> W2 (Settings: Arm IPs) -> B (Arm+Hand Page Ready) -> C -> D -> W3 (Logout/Disconnect)
```

## Branches

```text
None yet.
```

## Archived

```text
- A -> Overview Tab -> C (deleted 2026-04-28, replaced by compact Arm+Hand page)
- B -> Advanced Arm Tab -> C (merged into Arm+Hand first tab 2026-04-28)
```

## Notes

- Nodes are state snapshots.
- Edges are execution chains.
- Web mode shares nodes B, C, D with Tkinter mode — same service layer, different UI layer.
- Web mode adds auth/settings nodes (W0-W2) before reaching the shared Arm+Hand page (B).
