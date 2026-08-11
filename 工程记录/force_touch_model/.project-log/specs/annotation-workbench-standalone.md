# Engineering Spec — Independent Annotation Workbench

## Objective

Deliver `annotation_workbench/` as a self-contained Linux/Ubuntu package. A user can copy only this directory, run its documented installation process, select one local LeRobot v3.0 dataset, perform GUI annotation, run fixed-subtask VLM alignment through an external Ollama service, and reopen the GUI to review and save results.

## Non-goals

- Do not modify or remove the external `visualize_dataset/`, `lerobot_v1.0/`, or `serve_local_dataset.py`; they remain backups.
- Do not package full LeRobot, Node.js, Ollama, or model weights.
- Do not redesign the existing Next.js GUI, add network/multi-user features, or support non-Linux platforms.
- Do not claim VLM semantic quality from an infrastructure smoke test.

## Related business logic

- `BL-TOOL-001`: independent installation and startup.
- `BL-TOOL-002`: preserve manual annotation → VLM → GUI review loop.
- `BL-TOOL-003`: explicit dependency and model boundary.
- `BL-DATA-001`, `BL-DATA-003`: existing local v3 dataset and annotation behavior.

Acceptance derives from `REQ-002` revision 1 and `ARCH-001` under `DEC-007`.

## Current behavior and evidence

- `desktop_app.py` has a functional PySide6 local selector and service manager, but hard-codes external project paths.
- `guided_alignment.py` correctly enforces fixed subtask text/order/range validation but imports the external LeRobot annotation pipeline.
- The external visualizer front end and FastAPI backend have already proved local read/write of `meta/lerobot_annotations.json`.
- Existing code-level tests passed previously; they do not prove isolated deployment.

## Target behavior

### Package layout

```text
annotation_workbench/
├── pyproject.toml
├── requirements.txt
├── install.sh
├── run.sh
├── annotation_workbench/
│   ├── __main__.py
│   ├── desktop_app.py
│   ├── local_dataset_server.py
│   ├── guided_alignment.py
│   └── annotation_core/
│       ├── dataset_reader.py
│       ├── video_frames.py
│       ├── contact_sheet.py
│       └── vlm_client.py
├── visualize_dataset/
│   ├── src/, public/, package.json, package-lock.json
│   └── backend/app.py
└── tests/
```

Exact Python subdirectory names may vary if package installation requires a `src/` layout, but all runtime resources must remain under `annotation_workbench/`.

### Installation and start

- `install.sh` must reject Python below 3.11.
- It creates `.venv`, installs Python requirements, checks Node.js 20/npm, runs `npm install` from the copied lock file and `npm run build`.
- Python or Node installation is never implicit: if missing, the script explains the required `sudo apt` action and asks for confirmation before invoking it.
- It checks that `OLLAMA_API_BASE` responds and `OLLAMA_MODEL` is listed, but never pulls a model.
- `run.sh` and `python -m annotation_workbench` enter the same desktop application using the package `.venv`.

### Runtime

- The desktop application validates one selected LeRobot v3.0 directory.
- It starts a loopback-only range-capable data server, FastAPI annotation backend, and `next start` frontend on dynamically allocated ports.
- It passes only the selected dataset path and service URLs through controlled environment variables.
- It terminates only child process groups it created.
- VLM reads at least one complete human example among the first five episodes, preserves the fixed subtask template, and atomically writes completed episode results directly into the selected dataset.

## Affected components

- New packaging and launcher files: `pyproject.toml`, `install.sh`, `run.sh`, `annotation_workbench/__main__.py`.
- Existing desktop and VLM modules: remove external root, Conda, `PYTHONPATH`, and `--lerobot-src` assumptions.
- Migrated visualizer source and backend: retain existing API and UI behavior; package only source and lock files.
- New `annotation_core`: minimal v3 reader, video extraction, contact-sheet creation and OpenAI-compatible Ollama client.
- Tests: use temporary v3-like metadata for unit tests and a disposable real-data isolation copy for end-to-end proof.

## Interfaces and schemas

- Dataset input: directory containing `meta/info.json`, `meta/episodes/`, `data/`, and v3.0 `codebase_version`.
- Annotation persistence: `<dataset>/meta/lerobot_annotations.json`; preserve unrelated atoms.
- Frontend environment: `NEXT_PUBLIC_DATASET_URL`, `NEXT_PUBLIC_ANNOTATE_BACKEND_URL`, `NEXT_PUBLIC_LOCAL_DATASET_PATH`.
- VLM environment: `OLLAMA_API_BASE` (default `http://127.0.0.1:11434/v1`) and `OLLAMA_MODEL` (default `gemma3:27b`).
- VLM JSON: `{"subtasks":[{"index":0,"text":"fixed text","start":0.0,"end":1.0}]}`. The validator rejects any variation outside the fixed template and source timestamps.

## State, concurrency and lifecycle

- One desktop process has one active dataset session and at most one VLM subprocess.
- Completed VLM episodes are persisted individually; restart uses validation to skip completed items.
- GUI and VLM must not write the same dataset concurrently. The UI disables conflicting actions while VLM is running.
- Service child processes use new sessions/process groups. Graceful terminate precedes bounded forced termination.

## Failure handling

- Invalid dataset, dependency/build error, unavailable Ollama, process startup failure, video decode error, malformed VLM output and write error must stop only the relevant action, preserve prior completed data, and show a specific log message.
- Do not silently switch interpreters, servers, models, dataset versions, or output directories.
- A failed VLM episode remains retryable; its failure reason is visible in the desktop log.

## Security and privacy

- Bind all services to `127.0.0.1`.
- Do not expose an HTTP listener to LAN.
- Treat the selected dataset as local user data. Do not upload it; only selected contact-sheet frames are sent to the user-configured local Ollama endpoint.

## Observability

- Terminal installer messages include command failures and remedies.
- Desktop status identifies the chosen directory, ports, child service outcomes and streamed VLM result per episode.
- Tests assert external-path independence in addition to behavior.

## Compatibility, migration, rollout and rollback

- Migration is additive inside `annotation_workbench`; old directories remain unchanged.
- No existing dataset format migration is performed. The tool rejects non-v3.0 datasets.
- First validate an isolated copied package and disposable dataset clone. Remove only disposable test assets after recording evidence.
- Roll back by continuing to use the preserved external middle-layer stack; do not delete the independent source until acceptance is complete.

## Verification matrix

| Scope | Evidence |
| --- | --- |
| Package/install | Python version rejection, shell syntax check, isolated `.venv` creation, npm production build |
| GUI resources | backend unit smoke, frontend type-check/build, local dataset page and annotation save/read |
| V3 adapter | episode/timestamp reading, video frame extraction using the actual dataset codec, contact-sheet payload test |
| VLM | Ollama availability check, one non-demo episode writes valid fixed subtask atoms, malformed output rejection |
| Independence | isolated directory without external old paths starts both launch entrypoints and no code/runtime path references resolve externally |
| Lifecycle | service start/stop test confirms no owned child processes remain |

## Open questions and authority

- The exact Python decoder library is a B-level technical choice. Select only after a real current-dataset AV1/H.264 decode spike; record the result in `DEC-007` or a successor decision.
- No product-level unresolved questions block implementation.
