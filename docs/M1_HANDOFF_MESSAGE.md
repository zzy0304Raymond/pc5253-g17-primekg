# 可直接发送给组员的 A 交接说明

这是准备好的文字；尚未代用户发送。

> A 的 M1 数据与 WS1 已完成。标准数据 `primekg_5000_bfs_v1`：5000 节点、117891 条规范化语义关系、200 个固定查询（single/multi 各100）；`pairs_with_multiple_relations=0`。开发图 `primekg_2000_bfs_v1` 只有3个药物，查询是46个 single + 66个 multi，代码请读取实际数量。过滤后全图 `primekg_full_v1` 仅供结构对照，尚未定义功能查询集。
>
> 使用前请运行 `python -m src.validate_data primekg_5000_bfs_v1` 并阅读 `docs/DATA_CONTRACT.md`。不同 gid 的 nid/eid 不能混用。随机删边/删点顺序0–9和查询训练/测试划分已固定。A 的 `common.py` 与 `percolation.py` 可直接调用。`results/validation/*__retrieval_reference.csv` 是给 C/E 的独立核对样例。
>
> `results/ws1` 与 `figures/act1` 已给出随机失效、度分布和全图对照。5000 图在50%随机删边时 GCC 占原始节点比例约0.982；全图约0.858，展示和报告应注明 BFS 采样偏差。理论曲线当前是 A 的 configuration-model 参考实现；D 的正式 `theory.py` 到位后可通过 `--theory-module src.theory` 重新出图。E 的 `plotting.py` 到位后，A 出图脚本会调用其 `setup()`。
>
> 请各自保留数据版本与 manifest SHA-256。按 `docs/HANDOFF.md` 的 B/C/D/E 对接清单联调；目前独立参考检查已过，尚未声称 B–E 的正式模块都通过。原始 kg.csv 不在交接包里，README 有固定下载方法和校验值。A 的 slides 第3–4页、讲稿及报告第2/4.1节草稿也已准备。

