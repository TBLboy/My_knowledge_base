# Threading Model

## Tkinter GUI Threads

| Thread | Type | Purpose | Created By | Lifecycle |
|--------|------|---------|-----------|-----------|
| Main | Tkinter event loop | UI rendering, event handling | `tk.Tk.mainloop()` | Entire GUI lifetime |
| Operation threads | `threading.Thread` (daemon) | Background arm/hand operations | `_run_async()` | Per-operation, exits on completion |
| Joint polling | daemon `threading.Thread` | 500ms interval joint state reading | `_poll_joints()` starts one non-overlapping worker | Recurring while page lives |

## Web GUI Threads/Processes

| Process/Thread | Type | Purpose | Created By | Lifecycle |
|----------------|------|---------|-----------|-----------|
| Uvicorn main | Process | HTTP + WebSocket server | `uvicorn server:app` | Server lifetime |
| Worker subprocess | `subprocess.Popen` | Per-user arm/hand control | `ws_endpoint` in server.py | Per WebSocket connection |
| Worker stdin reader | `asyncio.Task` | Read commands from WebSocket | `WebSocketBridge.start()` | Worker lifetime |
| Worker stdout reader | `asyncio.Task` | Send responses to WebSocket | `WebSocketBridge.start()` | Worker lifetime |
| Worker stderr reader | `asyncio.Task` | Capture worker stderr | `WebSocketBridge.start()` | Worker lifetime |

## Thread Safety Rules

1. **Tkinter main thread only**: All UI updates must use `self.after(0, callback)` from background threads
2. **`_busy` flag**: Prevents concurrent operations in Tkinter GUI (except safe buttons)
3. **Worker isolation**: Each WebSocket connection gets its own subprocess — no shared state between users
4. **Service layer**: `ArmControlService` and `HandControlService` are NOT thread-safe — one instance per thread/process
5. **Joint polling**: SDK reads run on a background thread; UI updates use `after(0, ...)` on the main thread

## Threading Diagram

```
Tkinter:
Main Thread ────────────────────────────────────────────
  ├─ UI events (button clicks, input changes)
  ├─ after(500, _poll_joints) ──→ joint readback update
  └─ after(0, on_success) ──────→ status update from operation thread

Operation Thread ───────────────────────────────────────
  ├─ _run_async worker function
  ├─ ArmControlService / HandControlService call
  └─ after(0, _finish_success) or after(0, _finish_error)

Web:
Uvicorn Main ───────────────────────────────────────────
  ├─ HTTP handlers (login, register, /api/*)
  └─ WebSocket endpoint → spawns worker subprocess

Worker Subprocess ──────────────────────────────────────
  ├─ stdin: read JSON commands
  ├─ stdout: write JSON responses
  ├─ stderr: log output
  ├─ ArmControlService (isolated instance)
  └─ HandControlService (isolated instance)
```
