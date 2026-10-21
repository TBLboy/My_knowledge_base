"""Runnable T-025 pinned writer/QC smoke test; no hardware."""
from pathlib import Path
from writer_qc_fixture import qc_dataset, write_synthetic_dataset

ROOT = Path(__file__).parent
raw = ROOT / "t025-raw.json"
raw.write_text('{"synthetic": true}\n')
out = write_synthetic_dataset(ROOT / "t025-out", raw_path=raw)
print(qc_dataset(out, raw_path=raw))
