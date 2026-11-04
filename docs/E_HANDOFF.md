# E 工作说明与正式交付

## 当前完成情况

E 的恢复策略、正式四策略实验、绘图、讲稿及报告第 1/7 节草稿已完成。
B 的原图边介数排序和 C 的 Retriever 已接入。

- 主图与开发图：primekg_5000_bfs_v1 / primekg_2000_bfs_v1。
- 两个图各 320 个策略/预算状态、960 行指标，共 640 个状态。
- 四种策略：random、edge_betweenness、relation_type、静态 task_aware。
- 损坏：随机删边 30% / 50%，每种使用种子 0–9。
- 预算：被删边的 0% / 5% / 10% / 20%，记录实际恢复数量。
- 评价：GCC，以及测试查询 L=2 / L=3 成功率。
- 正式结果由 C 检索器产生，与此前 E 独立评估器逐查询对照一致。

## 文件位置

| 内容 | 位置 |
|---|---|
| 策略与恢复函数 | src/restoration.py |
| 实验与正式 C 适配 | src/run_ws5.py、src/restoration_evaluation.py |
| 统一绘图与结果图 | src/plotting.py、src/figure_templates.py、src/plot_ws5.py |
| 正式结果 | results/ws5/final/{gid}/ |
| 正式图：PNG/PDF/SVG | figures/act3/final/{gid}/ |
| 引言草稿 | report/E_section_1.md |
| 恢复实验章节草稿 | report/E_section_7.md |
| 报告数值、机制诊断 | report/E_results_table.csv、E_static_score_diagnostics.csv、E_edge_type_composition.csv |
| 个人贡献事实草稿 | report/E_individual_contribution_draft.md |
| E 英文讲稿、问答 | slides/E_speaker_notes.md |
| E 独立五页 PPT | slides/E_slides.pptx |
| 全组 14 页工作版 | slides/G17_working_draft.pptx |
| 报告数值和演示资产生成 | scripts/prepare_e_delivery.py |
| 两份 PPT 的生成 | scripts/build_e_deck.mjs |

旧 local_reference/ 数据为早期独立核对结果，保留用于追溯，不作为当前正式图的来源。
A/B/C 的实验代码和提交材料未被替换。演示中 B 的固定攻击曲线不加随机误差带。

## 方法的两个明确约定

**静态评分。** task_aware 在每个最初损坏状态下评分一次。
仅当前失败的训练查询贡献分数；只缺一条边的路径给该缺边加 1。
两条边都缺的路径不加分，已成功的查询不加分。同分与零分候选随机排序。
所有预算都取同一排序的前缀，恢复集合嵌套。

**候选不足。** relation_type 只允许 drug_protein / disease_protein。
候选用尽后停止并记录未花预算，不用 PPI 边凑数。
本次两个正式图的所有预算都足额恢复，无候选不足。
随机排名与同分打破使用损坏种子 + 100。

## 主图上应该讲什么

在删边 50%、恢复预算 20% 时，测试成功率提升为 10 种子的均值 ± 样本 SD：

| 策略 | L=2，百分点 | L=3，百分点 |
|---|---:|---:|
| Random | 13.17 ± 2.77 | 8.33 ± 5.77 |
| Edge betweenness | 42.00 ± 3.99 | 16.50 ± 7.13 |
| Relation type | 48.50 ± 6.69 | 15.67 ± 7.34 |
| Static task-aware | 24.83 ± 6.31 | 12.33 ± 6.63 |

不能只看这一种预算。在删边 30%、恢复 5% 时，L2 的 task-aware 均值为
12.67 个百分点，超过介数的 11.00 和关系类型的 7.00；到 20% 预算时排序不同。
静态评分只给 31–87 条候选正分，5% 预算就足以把它们全部恢复，后续主要在随机补零分边。

结构与功能的最佳均值也不同：删边 50%、预算 20% 时，介数的 GCC 增量为
1.782 个百分点，高于关系类型的 0.610；L2 检索增量则是关系类型更高。
L3 下介数与关系类型的均值差较小，不能表述为经过检验的显著优势。
所有结论限定在当前 BFS 图、正查询集和固定查询划分上；训练/测试可能共享实体。

## 如何运行

先激活项目的 Python 环境，从仓库根目录运行：

```powershell
python -m unittest discover -s tests -v

# 如需重算，请选择新的空目录，程序会默认使用 C 和全部四策略。
python -m src.run_ws5 primekg_5000_bfs_v1 --output-dir results/ws5/reproduction/primekg_5000_bfs_v1
python -m src.plot_ws5 results/ws5/reproduction/primekg_5000_bfs_v1 --output-dir figures/act3/reproduction/primekg_5000_bfs_v1

# 正式结果已就位时，更新报告用数值与演示资产。
python -m scripts.prepare_e_delivery

# 设置 G17_ARTIFACT_RUNTIME 和 G17_PRESENTATION_SKILL 为本机已安装的运行时与演示 skill 目录。
node scripts/build_e_deck.mjs
```

正式输出包含逐测试查询结果、原始指标、逐种子配对收益、样本 SD 汇总、实际预算、边类型、
候选排序 NPZ 与 provenance。报告收益先在同一种子内减零预算基线，再跨种子汇总。
每条边收益按实际恢复数量计算，零预算不参与除法。

## 全组 PPT 仍需完成的工作

全组工作版已经接入 A、B、C 的现有实测图和 E 正式结果。
第 9–11 页等待 D 的理论材料，均有明确状态说明，没有填入演示曲线。
E 独立五页 PPT 对应全组第 1、2、12、13、14 页。

D 交付后需整合其内容、全组确认结论，并进行实际排练，确认总时长在 14 分钟以内。
报告引言与恢复章节已成稿，仍需 B 统稿时统一图号、参考文献和术语。
个人贡献草稿的身份、实际贡献及课程要求需本人核对；peer grading 尚需本人完成。
