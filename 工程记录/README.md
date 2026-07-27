# 工程记录汇总（扁平去重版）

本目录对原有工程记录进行了**同层级整理和完全重复去重**。每个外层工程目录下，唯一日志均直接作为同级子目录保存；不再保留 `project-logs/.../.project-log` 的嵌套结构。

## 统计

- 原始 `.project-log` 副本：441 个
- 去重后唯一日志：87 个
- 删除的完全重复副本：354 个
- 去重后日志文件：1,656 个
- 去重后文件总大小：31,680,056 字节

## 目录规则

- 每个工程目录下的日志目录均为同一级别，例如 `001__dexbot_ros2_ws__src__cuttofo_xcore/`。
- 日志目录内部仍保留 `.project-log` 原有内容结构；只扁平化日志目录之间的外层嵌套。
- 仅删除内容完全一致的日志副本；内容有任何差异的版本均保留。
- `整理清单.tsv` 记录每个保留日志的来源、哈希、文件数和重复来源。
- `重复删除清单.tsv` 记录被去掉的重复来源及其对应保留目录。

## 工程分组

| 工程分组 | 原始副本 | 去重后 | 删除重复 |
|---|---:|---:|---:|
| [ShangHai_718](./ShangHai_718/README.md) | 1 | 1 | 0 |
| [Transformer-Koopman](./Transformer-Koopman/README.md) | 1 | 1 | 0 |
| [boss_electrics](./boss_electrics/README.md) | 1 | 1 | 0 |
| [cucumber](./cucumber/README.md) | 183 | 34 | 149 |
| [data_collect](./data_collect/README.md) | 2 | 2 | 0 |
| [gr00t-finetune](./gr00t-finetune/README.md) | 2 | 2 | 0 |
| [lerobot_v1.0](./lerobot_v1.0/README.md) | 1 | 1 | 0 |
| [tofu](./tofu/README.md) | 226 | 35 | 191 |
| [vibe-coding](./vibe-coding/README.md) | 1 | 1 | 0 |
| [worktrees](./worktrees/README.md) | 1 | 1 | 0 |
| [人物画像](./人物画像/README.md) | 1 | 1 | 0 |
| [切黄瓜项目跟踪](./切黄瓜项目跟踪/README.md) | 21 | 7 | 14 |

> 去重依据：日志目录内的相对文件路径、文件类型、文件大小和文件内容 SHA-256 完全一致。
