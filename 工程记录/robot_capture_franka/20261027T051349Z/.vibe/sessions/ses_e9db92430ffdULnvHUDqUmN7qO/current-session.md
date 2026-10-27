# Session recovery — franka data to Cybertron cluster

Task: `.vibe/tasks/franka-data-to-cluster-20261026.json` (blocked)
Previous task `nas-upload-mount-20261022` completed (NAS mount + upload proven, 201 sessions on NAS).

## Confirmed this session (read-only)

- `cctl` v0.0.22 installed at `~/.local/bin/cctl`, profile `modelbest`, user `taobailin`,
  token expiry 2026-11-25.
- Cybertron has 74 filesystems: 36 obs, 19 juicefs, 5 gpfs, 3 cephfs, 2 oss, 2 sfs, 2 inspur,
  2 ceph, 1 obs-pvc, 2 obs-pfs. No NFS/SMB endpoint is exposed by any API, so a laptop cannot
  mount a cluster filesystem directly; the clusters are remote datacenters.
- Cybertron offers no local-file upload: web file manager is GET + download only, and cctl
  `file-task` only moves between registered filesystems or object storage.
- The only browser-reachable ingress primitive found is devspace/notebook port exposure:
  a task carries `expose: {enabled, path_prefix: "/<cluster>/job/<id>/expose"}`, and
  `cctl ... create --expose-port 8888` with a jupyter image is the documented example.
- Robot Forge is `http://192.168.10.33:7000` (robo-data-forge 0.1.0, LAN, no login). Its upload
  pipeline is two stages: `huawei_obs` then `training_cluster`.
  - OBS stage: 12 failures `HTTP 403 InvalidAccessKeyId ... access key has been disabled`;
    `/cloud` page states the OBS credential is unconfigured or expired.
  - Cluster stage: single attempt failed with `No such file or directory: 'cctl'`.
  - Forge therefore uses OBS as the staging hop even for the cluster stage (import is
    object-storage -> filesystem), so with OBS broken there is no designed path to the cluster.
- Forge scans piper1/piper2/piper3/arx5 only; franka has a device entry (expects MCAP
  `episode_0000/metadata.json + rosbag/rosbag_0.mcap`) but zero datasets. A `lerobot_v3`
  device type exists that ingests a finished LeRobot v3 directory without conversion.
- The user's Mac has no transfer client, no credential, no mount, and no relevant shell history;
  it is on 192.168.6.80 with Corplink (飞连) installed for identity, not a data tunnel.

## Blocker

Both automated exits from Forge are down (OBS key disabled, cctl missing on the Forge host), so
the colleague's "Mac relay" is a manual workaround. Its exact mechanism is still unconfirmed.
Remaining candidates: (a) upload through an exposed devspace/notebook HTTP port (e.g. Jupyter),
(b) a team bastion / transfer host reachable only from a person's device, (c) an OBS/OSS bucket
with the person's own credentials. Evidence rules out direct NFS/SMB mounting from a laptop.

## Resume steps

1. Ask the colleague one discriminating question: is the data dropped through a web page, or
   copied with a CLI command (scp/rsync/obsutil) to a specific host/bucket?
2. Build the HDF5 -> LeRobot v3 converter regardless; Forge's `lerobot_v3` device can ingest it.
3. Confirm the LeRobot version/fields the training side expects (v3.0 vs v21 both in use).
4. Check quota before bulk transfer; `paratera_train` reports 110% usage.
