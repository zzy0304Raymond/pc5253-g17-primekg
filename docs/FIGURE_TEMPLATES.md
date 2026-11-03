# G17 全组绘图模板使用说明

本套模板由 E 维护，覆盖工作计划中 A–E 的 15 种主要图，以及 5 种补充图。
使用现有 Python 3.11 环境与 matplotlib、pandas、numpy，无新增依赖。
文件和中文说明统一 UTF-8。运行命令的当前位置应为仓库根目录。

## 先看这三件事

1. `src/plotting.py` 定义全组颜色、字体、点形和导出方式。
2. `src/figure_templates.py` 实现各张图。`scripts/render_figure.py` 是统一入口。
3. 每人把自己的测量结果整理成下述 CSV，再调用对应模板。模板不生成实验结果。

参考图只借鉴白底、细轴线、柔和填色、低透明度误差带与清晰留白，所有布局由本项目代码绘制。
现有实验策略颜色保留工作计划附录 C；四种恢复策略使用灰、蓝、金、紫。

## 图单与输入要求

下表中的 `long` 指下节定义的统一实验长表。可传多个 CSV 合并，但同一条记录不能重复。

| 成员 | 模板名 | 必需数据 / 说明 |
|---|---|---|
| A | `fig_degree_dist` | node_features.csv 的 node_type、degree；按类型画经验 CCDF |
| A | `fig_S_random_edge` | long：edge_random、theory_bond 的 gcc_frac |
| A | `fig_S_random_node` | long：node_random、theory_site 的 gcc_frac |
| B | `fig_attack` | long：node_random、node_degree、node_betweenness、theory_attack 的 gcc_frac |
| B | `fig_hub_composition` | hubs 表：两种中心性排序的前三个比例、三类节点的组成 |
| C | `fig_S_vs_R` | long：edge_random 的 gcc_frac 和 R_L2；可以分别来自 A、C 两份 CSV |
| C | `fig_R_by_group` | long：edge_random 的 R_L2_single、R_L2_multi |
| C | `fig_R_L_curves` | long：edge_random 的 R_L2、R_L3、R_L4、R_Linf |
| C | `fig_R_L_heatmap` | 同上；固定 R 色标 0–1，保留非等距删除比例，L 为离散类别 |
| D | `fig_R_theory_vs_sim` | long：edge_random、theory_bond 的 R_L2_single、R_L2_multi |
| D | `fig_corr_penalty` | long：node_degree、node_betweenness 的 corr_penalty，允许负值 |
| D | `fig_phase_diagram` | C 的四种 L 测量值，另加 theory_bond 的 R_L2、R_Linf；左边 p–L 热图，右边分别叠加两个理论极限与模拟 |
| D | `fig_prediction` | prediction 表：理论和 logistic 的测试 AUC、Brier；不虚构误差条 |
| E | `fig_restoration` | recovery 表：30%/50% 损坏、L=2/3，输出 2×2 面板的配对收益 |
| E | `fig_gain_per_edge` | 同上；输出每恢复 1,000 条边的成功率增量 |
| A 补充 | `fig_fragmentation` | long：两种随机策略的 n_components、isolated_frac、avg_degree |
| A 补充 | `fig_sampling_comparison` | 最多三个 gid 的 edge_random / gcc_frac，支持全图和两个 BFS 子图 |
| B 补充 | `fig_rank_overlap` | overlap 表：度排序和介数排序的前 k 名 Jaccard 重合度 |
| D 补充 | `fig_equal_damage` | long：仅一个 f，两种确定性攻击和随机删点的 gcc_frac、R_L2 |
| E 示意 | `fig_query_schematic` | 无需 CSV。仅表示连通性与 L=2 检索不同，不是观测数据 |

## 统一长表 long

沿用组内约定：

```text
gid,strategy,seed,frac_removed,n_removed,metric,value
```

- `seed=0..9`：随机实验；L 扫描可以使用 0..2。每个删除比例必须使用相同种子集合。
- `seed=-1`：确定性攻击或理论值。与随机测量分开保存，不混入同一条曲线。
- `value` 为原始指标值，成功率是 0–1，不是百分数。
- `(gid,strategy,metric,seed,frac_removed)` 唯一；不要把汇总均值与逐种子结果混在一起。
- 随机曲线为种子均值 ± 样本标准差（ddof=1），确定性结果无误差带。
- 同一输入有多个 gid 时，除采样对照外必须用 `--gid` 选择一个。
- 模板只展示指定指标；其余指标不会作为重复样本参与汇总。
- `corr_penalty` 由 D 按工作计划计算。模板不拟合模型、不推导理论、不计算中心性。
- 相图中的 L=∞ 是独立类别，不能被理解成与 4 等间距的数值跳数。

## 另外四种 CSV 格式

### hubs：节点组成

```text
strategy,top_frac,node_type,fraction
```

strategy 为 node_degree 或 node_betweenness；top_frac 通常为 0.01、0.05、0.10。
每组都提供 drug、disease、gene/protein 三行，fraction 相加为 1；某类为零也需填 0。
这是原始图上确定性排名的组成，不加随机种子误差带。

### prediction：测试预测表现

```text
model,damage_frac,metric,value
```

model 为 theory、logistic；damage_frac 为 0.3、0.5；metric 为 AUC、Brier。
每个单元格填一个测试集汇总值。按计划使用训练种子 0–6、测试种子 7–9。
AUC 越大越好，Brier 越小越好；不对查询行当独立重复计算误差条。

### recovery：恢复原始测量值

在 long 表基础上增加三列：

```text
gid,strategy,seed,frac_removed,n_removed,metric,value,damage_frac,budget_frac,n_restored
```

- frac_removed 与 damage_frac 均为最初删边比例 0.3 或 0.5。
- strategy 为 restore_random、restore_edge_betweenness、restore_relation_type、restore_task_aware。
- metric 为 R_L2、R_L3；**value 是测试查询恢复后的原始成功率**，不要提前减基线。
- 每种策略、每个种子都要提供 budget_frac=0 的基线，四种策略基线一致。
- budget_frac 通常为 0、0.05、0.10、0.20，分母是被删的边数。
- n_restored 填实际补回的边数。候选不足时不能谎报预算已全部用完。
- 先在同一种子内计算 ΔR，再对种子汇总，避免把基线差异当作恢复效果的波动。
- fig_restoration 纵轴单位为百分点：100×ΔR。
- fig_gain_per_edge 为 1000×ΔR/n_restored，单位为成功率增量/千条恢复边；零预算不参与除法。
- 在测量端保留 GCC 指标与其他结果。上述两张正式恢复图按任务卡展示检索收益。

### overlap：排名重合度

```text
top_frac,jaccard
```

每个 top_frac 一行，jaccard 在 0–1；应由 B 对同一图中的两个排名计算。

## 运行例子

激活已有环境后，从仓库根目录运行：

```powershell
conda activate D:/CondaEnvs/pc5253-g17-primekg

# A：直接使用已有结果
python -m scripts.render_figure fig_S_random_edge --csv results/ws1/primekg_5000_bfs_v1__random.csv --output-dir figures/act1/template_preview

# C：把 A 的结构结果和自己的检索结果共同传入
python -m scripts.render_figure fig_S_vs_R --csv results/ws1/primekg_5000_bfs_v1__random.csv results/ws3/YOUR_RETRIEVAL_RESULTS.csv --gid primekg_5000_bfs_v1 --output-dir figures/act2

# D：在同一损坏程度下比较，不能把所有 f 平均在一起
python -m scripts.render_figure fig_equal_damage --csv YOUR_COMBINED_LONG_TABLE.csv --gid primekg_5000_bfs_v1 --damage 0.3 --output-dir figures/act2

# E：用逐种子的恢复后测量值，自动计算配对收益
python -m scripts.render_figure fig_restoration --csv YOUR_RECOVERY_TABLE.csv --output-dir figures/act3

# 开场示意图不需要数据
python -m scripts.render_figure fig_query_schematic --output-dir figures/act0
```

YOUR 开头的文件名需要换成各自真正的文件。每次导出 PNG、PDF、可编辑文本 SVG，另存 plot_metadata.json 记录输入文件、过滤条件和行数。

也可以在自己的脚本里直接使用，不走命令行：

```python
import pandas as pd
import matplotlib.pyplot as plt
from src.figure_templates import render
from src.plotting import save

data = pd.read_csv("results/ws1/primekg_5000_bfs_v1__random.csv")
fig = render("fig_S_random_edge", data)
save(fig, "act1", "fig_S_random_edge", formats=("png", "pdf", "svg"))
plt.close(fig)
```

## 预览与演示数据

交付包 A–E 文件夹各有独立预览，example_data 中有对应的 CSV 示例。
带 DEMO 的图使用人工构造数值，只用于看版式、测试输入格式，不能写成实验结论。
演示 CSV 带 demo_only=true，命令行重画也会保留 DEMO 标识。
A 的五张预览使用仓库现有存档，其他定量预览为 DEMO；开场图为概念示意。

重建全部预览：

```powershell
python -m scripts.preview_all_templates --output-dir D:/G17_previews
```

正式渲染器没有自动补齐结果的逻辑：缺序列、重复样本、混合图版本、种子集合不一致等情况会报错，需要修正输入后重画。
模板不会覆盖 A–D 的实验代码，也没有上传或发送给组员；由大家按各自图单调用。
