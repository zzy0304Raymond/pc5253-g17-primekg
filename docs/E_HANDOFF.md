# E 工作说明与当前交付

## 已经完成

- 全组绘图工具及 20 个模板，详见 FIGURE_TEMPLATES.md。
- restoration.py 的四种排序和恢复函数。
- run_ws5.py 批量入口：损坏、排序、恢复、GCC、测试查询评价、实际预算统计与可复现记录。
- E 独立的 edge-only L2/L3 核对工具，以及接入 C 的适配器。
- toy、2000、5000 三个图的本地三策略试跑；每图 240 个策略/预算状态，共 720 个状态。
- 主图、每条边收益、GCC、恢复边类型组成，以及按 L 拆分的两张汇报图。
- 14 页英文工作版 PPT：含 A 已有材料、E 本地结果及每页讲稿备注；B/C/D 的页面保留明确的待交付说明。
- 17 项测试，包括小图全部 256 种删边状态与 NetworkX 路径枚举的对照、四种策略端到端测试。

以上本地试跑是实际计算结果，不是此前模板演示数值。评估器明确标记为 reference，
边介数策略未纳入真实图试跑，不能称为全组最终四策略结果。

## 四种策略如何工作

1. random：使用损坏种子 + 100，随机排列被删边。
2. edge_betweenness：过滤 B 提供的原始全边排序，只保留被删边，保持高分优先顺序。
3. relation_type：只随机排列被删的 drug_protein / disease_protein 边，排除 PPI。
4. task_aware：只读取训练查询。对于当前没有完整两跳路径的查询，每条只缺一边的路径给该缺边加 1 分。
   已经成功的查询不再贡献分数，两条边都断的路径也不贡献分数。分数同高时随机，零分边也随机。

任务感知策略在每个最初损坏状态下**只评分一次**。不同预算取同一个排序前缀，恢复集合自然嵌套。
这实现的是工作计划中的静态排序版本，没有额外加入逐条恢复后重评分的贪心算法。

四种方法都调用 restore(edge_alive, ranked_removed_eids, budget_frac)，不会修改原始 mask。
恢复目标数量为 round(预算比例 × 实际被删边数)。候选不足时停止，记录 shortfall，
不会拿 PPI 边来凑 relation_type 的预算。本轮三个图的 5%/10%/20% 预算未发生候选不足。
以上两个未完全指定的细节已明确写入 provenance，供团队复核；若团队改定义，应另开一次实验。

## 现在还需要 B、C 提供什么

**B**：每个 gid 的 orders/edge_betweenness.npy。
必须是原图全部 eid 的排列，高介数边在前，不是仅包含被删边的短列表。

**C**：src/retrieval.py，提供 Retriever(gid).evaluate(queries, edge_alive=..., compute_dist=True)。
返回 query_id、drug_alive、disease_alive、s_alive、d_ppi。只允许蛋白作为中间节点，
d_ppi 是药物相连蛋白集合到疾病相连蛋白集合之间的最短 PPI 距离。

E 只用测试查询报告成功率：L2 对应 s_alive>0，L3 对应有限 d_ppi<=1。
reference 模式不生成完整 d_ppi，只独立判断 L2/L3；不会冒充 C 的检索器。
它保留在 E 自己的 restoration_evaluation.py 中，没有创建 retrieval.py。

## 运行命令

从仓库根目录启动：

```powershell
conda activate D:/CondaEnvs/pc5253-g17-primekg
python -m unittest discover -s tests -v

# B/C 到位后，默认正式入口即要求全部四种策略和 C 的检索器
python -m src.run_ws5 primekg_5000_bfs_v1 --output-dir results/ws5/final/primekg_5000_bfs_v1
python -m src.plot_ws5 results/ws5/final/primekg_5000_bfs_v1 --output-dir figures/act3/final/primekg_5000_bfs_v1

# 明确选择 E 独立评估器，仅运行不依赖 B 的三种策略
python -m src.run_ws5 primekg_5000_bfs_v1 --evaluator reference --strategies random relation_type task_aware --output-dir results/ws5/local_reference_new/primekg_5000_bfs_v1
python -m src.plot_ws5 results/ws5/local_reference_new/primekg_5000_bfs_v1 --allow-partial --output-dir figures/act3/local_reference_new/primekg_5000_bfs_v1
```

输出目录必须为空，避免覆盖已有实验。固定损坏比例为 0.3/0.5，种子默认 0–9，
预算默认 0/0.05/0.10/0.20。不指定 reference 时不会自动切换评估器。
不提供 B 排序时，默认的四策略正式运行也不会自动跳过该策略。

## 输出文件

每次运行保存：

- gid__restoration.csv：统一长表加 damage_frac、budget_frac、实际恢复数、预算缺口、评估器。
- gid__test_perquery.csv：逐测试查询的 s_alive 和 L2/L3 成功指示，便于 C 接入后逐行对照。
- gid__paired_gains.csv：先按同一种子减零预算基线，再计算收益。
- gid__summary.csv：均值、样本标准差、种子数、实际恢复数范围、发生预算不足的种子数。
- gid__restored_edge_types.csv：各类恢复边的计数。
- rankings/*.npz：每个损坏比例和种子的候选边排序，可直接重建恢复状态。
- provenance.json：评估方式、具体策略、种子、训练/测试查询 ID、算法定义、代码版本指纹、运行耗时和状态。

所有随机结果的不确定性单位为损坏种子，使用 ddof=1；不能把依赖的查询行当作独立重复。
训练/测试划分是查询级，可能共享药物、疾病或蛋白，不能宣称实体完全独立的泛化。

## 5000 节点图上的本地读数

恢复预算为被删边的 20%，表中为测试成功率提升的百分点（10 种子均值）：

| 初始损坏 | 检索尺度 | Random | Relation type | Static task-aware |
|---|---|---:|---:|---:|
| 30% | L=2 | 6.00 | 27.50 | 15.50 |
| 50% | L=2 | 13.17 | 48.50 | 24.83 |
| 30% | L=3 | 2.17 | 5.83 | 5.50 |
| 50% | L=3 | 8.33 | 15.67 | 12.33 |

这是同一冻结查询划分上的有限样本描述。不同预算下策略排序可能不同，
不能把这张 20% 预算表概括为所有预算均如此，也不能从误差带重叠与否直接断言显著性。
静态 task-aware 优先补一条边就能补全的训练路径，之后零分边在所有剩余候选中随机选择。
relation_type 始终把预算用于两种终端关系。这个机制差别可以解释当前观察，但最终解释仍需结合完整四策略结果。

## 汇报与报告后续

slides/G17_working_draft.pptx 是工作版，正文 14 页并按任务卡分工。
第 1/2/12/13/14 页属于 E。第 12/13 页已放入本地结果，明确标明独立评估和三策略。
第 5–11 页保留待 B/C/D 交付的位置；不包含模板 DEMO 数值。
图表是高分辨率嵌入图，标题、文字、布局可编辑；图形本身用源 CSV 和 Python 重新导出。

最终还需：接 B/C 跑正式四策略、收齐所有人的结果、更新结论、实际排练并压到 14 分钟、
完成报告第 1/7 节及个人报告。工作版不代表这些步骤已经完成。
英文恢复方法与讲稿提纲见 slides/E_speaker_notes.md。
