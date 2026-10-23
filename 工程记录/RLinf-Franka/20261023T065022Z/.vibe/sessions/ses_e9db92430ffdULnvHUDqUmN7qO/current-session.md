# Session recovery — NAS upload mount (blocked)

Task: `.vibe/tasks/nas-upload-mount-20261022.json` (`nas-upload-mount-20261022`, status blocked)

## Done

- `nfs-common` installed with `pkexec` (passwordless here; `sudo` needs a password).
- `robot_capture_franka/scripts/setup_nas_mount.sh` created (new, untracked): installs
  NFS client, probes the export, mounts with `vers=4.1/4/3` fallback, writes an fstab
  entry with `nofail,x-systemd.automount,x-systemd.device-timeout=10,x-systemd.mount-timeout=30`,
  starts `mnt-nas.automount`, and runs a write probe as `embody`.
  Modes: default apply, `--check`, `--unmount`.
- `config/workbench.yaml` upload switched to `enabled: true`, `transport: local`,
  `remote_raw_dir: /mnt/nas/forge/franka/raw`, `robot_name: franka-pico` (only change in that file).
- Fail-closed confirmed: with the NAS absent, `probe_sink` returns `down` with
  `Permission denied: /mnt/nas/forge`, so upload is refused instead of writing locally.
- Offline suite: 98 tests OK, 3 skipped.

## Blocker

NAS `192.168.10.35`, export `/volume1/robo-data-warehouse`, allow-list is only
`192.168.10.37, .36, .34, .33`. This host is `192.168.10.158` (DHCP on enp3s0, /22).
`mount` therefore returns `access denied by server` for NFS v4 and v3. Needs a NAS
administrator to add this client or the subnet with read/write.

## Resume steps

1. `export DISPLAY=:1; pkexec bash -c 'NAS_PROBE_USER=embody bash /home/embody/Project/robot_capture_franka/robot_capture_franka/scripts/setup_nas_mount.sh'`
2. Confirm `findmnt -M /mnt/nas` and that the write probe passes; if the share squashes
   ownership, fix directory permissions on the NAS side rather than opening nobody-write.
3. Restart the workbench (operator-initiated; PID ran as `.venv/bin/python main.py`) so the
   new upload config is loaded, then confirm the upload status chip reports OK.
4. Optional first real transfer with one existing recording to exercise rsync/size check.
5. Consider a DHCP reservation for `192.168.10.158` so the allow-list entry stays valid.
