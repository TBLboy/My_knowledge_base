# Unfinished timestamp collection work

Active balanced Task: release-timestamp-alignment-20261020. Release worktree remains uncommitted and not hardware-ready.

Corrected a prior false diagnosis: RealWorldEnv._wrap_obs runs AFTER NoAutoResetSyncVectorEnv, so raw_state need not be declared in FrankaEnv's observation space. Removed the erroneous raw_state space entry (actual Franka observations never supplied it). Regression now exercises actual vector batching followed by RealWorldEnv._wrap_obs, including independent state copy. Two focused tests pass; full robotics/real-env/Release suite launched as sh_1584283e600199sMH2JT2fpIpN, result pending.

RawEpisode append snapshot semantics restored after regression caught aliasing; seal avoids an additional copy. Raw UVC frames now retain the full 1344x376 stereo image; prior delivery estimate based on 672px single-eye images was wrong. Memory and disk need sizing for full stereo and duplicate frame storage in infos/raw_streams plus flush copies.

Remaining: actual full wrapper/collector/PKL/writer integration (not handcrafted batches only); raw state coordinate contract (current raw_state copies already-transformed policy state); exact Pico event receive timestamps (currently events call monotonic_ns separately); period provenance (collector hardcodes all streams to 30Hz); memory/serialization limits and conversion output failure cleanup; final tests and documentation. Do not claim only a commit and retest remain. Hardware not started.
