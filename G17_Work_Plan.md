# G17 分工与行动计划（可并行版）

> Claude · 2026-11-02 · 配合《关于 PrimeKG 方案的评审与升级建议》使用
>
> 组里已经同意了升级方案。这份文档把它落实成**每个人具体做什么、何时交付、交给谁、怎样算做完**。
>
> **阅读建议**：每个人先读第 1–5 节和第 11–14 节，再读自己的任务卡（第 6–10 节）。时间点可以按各自课表微调，但 **M1、M5、M7 三个里程碑不能动**。

---

## 目录

1. 并行的设计原则
2. 角色一览
3. 里程碑与依赖关系
4. 共享约定：目录、数据格式、损坏设置、结果格式
5. 接口契约：每个模块对外提供什么函数
6. 任务卡 A：数据基建 + WS1 随机失效
7. 任务卡 B：WS2 定向攻击 + 中心性
8. 任务卡 C：WS3 检索引擎 + 结构 vs 功能 + L 扫描
9. 任务卡 D（方闻）：WS4 理论与预测
10. 任务卡 E：WS5 恢复 + slides 统稿
11. Slides 分页与讲者安排
12. 报告分工与 11/22 前的时间线
13. 协作规则与风险预案
14. 同步会议安排
15. 附录：toy 数据脚本、结果文件示例、作图风格、图表交接模板

---

## 1. 并行的设计原则

五个人要在三天内并行推进，关键是消除互相等待。这份计划基于三条原则：

**原则一：唯一的串行瓶颈是数据基建，所以最先做，并且拆给两个人。**
所有人都依赖标准图、查询集和删除顺序。成员 A 负责建图、查询和随机顺序，成员 B 同时负责中心性顺序。两部分在 11/3 下午前全部交付。

**原则二：模块之间只通过固定的文件格式和函数接口对接。**
接口在第 4、5 节一次性定死。拿到真实数据之前，每个人都可以先用 **toy 数据**（附录 A，格式与正式数据完全一致）写代码、调试。真实数据一到，换一个图的 ID 就能直接运行。

**原则三：每个人只改自己的文件。**
共享的只有 `common.py`（A 维护）和 `plotting.py`（E 维护）。修改任何接口，必须先在群里说明。

---

## 2. 角色一览

| 成员 | 角色 | 主要产出 | 依赖谁 | 谁依赖他 |
|---|---|---|---|---|
| **A**（姓名：____） | 数据基建 + WS1 随机失效 | 标准图、查询集、随机删除顺序；`common.py`；`percolation.py`；随机失效曲线 | — | 所有人 |
| **B**（姓名：____） | WS2 定向攻击 + 中心性 | 中心性删除顺序（节点、边）；攻击曲线；hub 组成分析；零模型（报告阶段） | A | C、D、E |
| **C**（姓名：____） | WS3 检索引擎 + 结构 vs 功能 | `retrieval.py`；per-query 结果；S–R 差距图；L 扫描 | A、B | D、E |
| **D**（方闻） | WS4 理论与预测 | `theory.py`；相关性惩罚；per-query 预测；同等损坏比较；R(p, L) 相图的理论部分 | A、C | A、B、C |
| **E**（姓名：____） | WS5 恢复 + slides 统稿 | `plotting.py`；slides 模板；`restoration.py`；恢复曲线；最终 slides | A、B、C | 全组 |

**预估工作量**：A 约 12 小时（集中在 11/3 中午前），B 约 8 小时，C 约 12 小时，D 约 12 小时，E 约 10 小时（含统稿）。

A 在 11/3 上午压力最大。如果需要帮忙，B 可以接手 `make_queries.py`。

---

## 3. 里程碑与依赖关系

### 3.1 里程碑

| 编号 | 时间 | 交付内容 | 负责 |
|---|---|---|---|
| M0 | 11/2 23:00 | 代码仓库骨架、`common.py`、`toy_v1` 数据 | A |
| **M1** | **11/3 12:00** | `primekg_2000_bfs_v1` 与 `primekg_5000_bfs_v1`：节点、边、查询、随机删除顺序、manifest | A |
| M2 | 11/3 15:00 | 中心性删除顺序（2000 与 5000 两个图） | B |
| M3 | 11/3 18:00 | `theory.py` v1、`retrieval.py` v1、`plotting.py` 与 slides 模板 | D、C、E |
| M4 | 11/3 21:00 | 在 2000 节点图上完成 sanity check（同步会议） | 全组 |
| **M5** | **11/4 16:00** | **图表冻结**：每人交付 5000 节点图上的最终图和讲稿要点 | 全组 |
| M6 | 11/4 21:00 | 第一次完整排练 | 全组 |
| **M7** | **11/5 17:00** | **提交 slides**（截止 18:00，留 1 小时缓冲） | E |

### 3.2 依赖关系

```
A: 图 / 查询 / 随机顺序 (M1)
 ├──> A: 随机渗流曲线
 ├──> B: 中心性顺序 (M2) ──> B: 攻击曲线
 │                       └──> E: edge betweenness 恢复策略
 ├──> C: 检索引擎 (M3) ──┬──> D: per-query 分析、相关性惩罚
 │                       └──> E: 恢复效果评估
 └──> D: R_∞ 理论（需要 PPI 度分布）

D: theory.py (M3) ──> A / B / C 叠加理论曲线

所有人的图 (M5) ──> E: 组装 slides (M7)
```

**并行窗口**：从 11/2 晚到 M1 之间，B、C、D、E 都用 toy 数据开发各自的代码，不需要等待 A。

---

## 4. 共享约定

### 4.1 目录结构

建议使用 GitHub 私有仓库；如果有人不熟悉 git，也可以用共享网盘，但目录结构保持一致。

```
g17-kg/
├── data/
│   ├── raw/kg.csv                      # 原始数据，不提交到 git
│   └── processed/{gid}/
│       ├── nodes.csv
│       ├── edges.csv
│       ├── queries.json
│       ├── manifest.json
│       └── orders/
│           ├── edge_random_s{0..9}.npy
│           ├── node_random_s{0..9}.npy
│           ├── node_degree.npy
│           ├── node_betweenness.npy
│           └── edge_betweenness.npy
├── src/
│   ├── common.py          # A：读取数据、常量
│   ├── build_graph.py     # A
│   ├── make_queries.py    # A
│   ├── make_orders.py     # A（随机顺序）
│   ├── centrality.py      # B（中心性顺序）
│   ├── percolation.py     # A（Newman–Ziff）
│   ├── attack.py          # B
│   ├── retrieval.py       # C
│   ├── theory.py          # D
│   ├── prediction.py      # D
│   ├── restoration.py     # E
│   └── plotting.py        # E（统一作图风格）
├── results/{ws1..ws5}/    # 各人的结果 CSV
├── figures/{act0..act3}/  # 各人的最终图（PNG + PDF）
├── slides/
├── report/
└── requirements.txt       # python 3.11, numpy, pandas, scipy, networkx, matplotlib, scikit-learn
```

### 4.2 图的 ID（gid）

| gid | 用途 |
|---|---|
| `toy_v1` | 合成小图，开发调试用（附录 A） |
| `primekg_2000_bfs_v1` | 快速验证 |
| `primekg_5000_bfs_v1` | **标准图，slides 的主要结果都用它** |
| `primekg_full_v1` | 过滤后的全图。slides 阶段可选，报告阶段用于对照 |

协议中的 `queries_v1.json`，就是 `primekg_5000_bfs_v1/queries.json`。

### 4.3 数据格式

**nodes.csv**：按 `x_index` 升序排列，`nid` 为 0 到 N−1 的连续编号。

| 列 | 含义 |
|---|---|
| `nid` | 内部编号，直接作为数组下标使用 |
| `x_index` | PrimeKG 原始 ID（协议规定的唯一标识） |
| `node_type` | `drug` / `disease` / `gene/protein` |
| `node_name` | 名称，仅供展示 |

**edges.csv**：每条规范化语义关系占一行，按 `(relation, u, v)` 排序后编号。

| 列 | 含义 |
|---|---|
| `eid` | 0 到 E−1 的编号 |
| `u`, `v` | 两端的 `nid`，且 u < v |
| `relation` | `drug_protein` / `disease_protein` / `protein_protein` |

**queries.json**：列表，每个元素的格式如下。

```json
{
  "query_id": 0,
  "drug_nid": 12, "disease_nid": 345,
  "drug_x_index": 14113, "disease_x_index": 27165,
  "relation_pattern": ["drug_protein", "disease_protein"],
  "max_hops": 2,
  "redundancy_m": 3,
  "group": "multi",
  "intermediates": [1020, 2210, 3301],
  "split": "train"
}
```

- `group`：`single` 表示 m = 1，`multi` 表示 m ≥ 2。
- `intermediates`：中间蛋白的 `nid` 列表。
- `split`：按协议，以种子 42 对 query_id 做 70% / 30% 的训练 / 测试划分（供 WS5 使用）。

**manifest.json**：节点数、边数、各类型节点数、各关系边数、两组查询的数量、文件的 SHA-256。

此外必须包含一个字段 **`pairs_with_multiple_relations`**：同一节点对上出现多种关系的数量。**它应该等于 0**，这是升级 1 中公式严格成立的前提。

### 4.4 损坏设置

```python
EDGE_LEVELS = [0, .05, .10, .20, .30, .40, .50, .60, .70, .80, .85, .90, .95, .97, .99]
NODE_LEVELS = [0, .05, .10, .20, .30, .40, .50, .60, .70, .80, .90]
SEEDS       = range(10)        # 随机策略用 0–9；L 扫描只用 0–2
# 删除比例 f 对应删除的数量：round(f × 总数)
```

**删除顺序文件**（`orders/*.npy`）是一个 eid 或 nid 的数组，**前 k 个就是被删的 k 个**。这样不同删除比例的损坏状态天然嵌套。

| 文件 | 生成方法 | 负责 |
|---|---|---|
| `edge_random_s{s}.npy` | `np.random.default_rng(s).permutation(E)` | A |
| `node_random_s{s}.npy` | `np.random.default_rng(s).permutation(N)` | A |
| `node_degree.npy` | 按 (−degree, nid) 排序 | B |
| `node_betweenness.npy` | `nx.betweenness_centrality(G, k=100, seed=42, normalized=True)`，按 (−bc, nid) 排序 | B |
| `edge_betweenness.npy` | `nx.edge_betweenness_centrality(G, k=100, seed=42, normalized=True)`，按 (−ebc, eid) 排序 | B |

### 4.5 结果文件格式（统一的长表）

所有人的汇总结果都存成 `results/{ws}/{gid}__{实验名}.csv`，列名统一如下：

```
gid, strategy, seed, frac_removed, n_removed, metric, value
```

| 列 | 取值说明 |
|---|---|
| `strategy` | `edge_random`、`node_random`、`node_degree`、`node_betweenness`、`theory_bond`、`theory_site`、`theory_attack`、`restore_random` 等 |
| `seed` | 确定性策略和理论曲线填 −1 |
| `metric` | `gcc_frac`、`n_components`、`isolated_frac`、`avg_degree`、`R_L2`、`R_L2_single`、`R_L2_multi`、`R_L3`、`R_L4`、`R_Linf` 等 |

统一格式的好处：任何人都能用同一段代码画任何人的结果，E 统稿时不需要逐个适配。

C 额外输出 **per-query 结果**，供 D 和 E 使用：

```
results/ws3/{gid}__perquery__{strategy}__s{seed}.csv
列：query_id, frac_removed, drug_alive, disease_alive, s_alive, d_ppi
```

- `s_alive`：存活的两跳路径数。
- `d_ppi`：最短 PPI 距离（无路径时为 inf）。查询在跳数上限 L 下成功，当且仅当 `d_ppi ≤ L − 2`。

### 4.6 作图约定

所有图都用 E 的 `plotting.py`（附录 C）：统一配色、字号、尺寸，同时保存 PNG 和 PDF。

- **图中文字一律用英文**，因为 slides 是英文的。
- 横轴统一为 `Fraction removed f`。
- 随机策略画均值，并加 ±1 标准差的阴影带。
- 确定性攻击画单条曲线，不加误差带。
- 理论曲线统一用黑色虚线。

---

## 5. 接口契约

函数名和返回格式一旦确定，就不能单方面修改。内部实现各人自由。

**`common.py`（A）**

```python
load_nodes(gid) -> pd.DataFrame
load_edges(gid) -> pd.DataFrame
load_queries(gid) -> list[dict]
load_order(gid, name) -> np.ndarray          # name 例如 "edge_random_s3"
n_removed(frac, total) -> int                # round(frac * total)
edge_alive_mask(gid, order_name, frac) -> np.ndarray[bool]   # 长度 E，True 表示存活
node_alive_mask(gid, order_name, frac) -> np.ndarray[bool]   # 长度 N
```

**`percolation.py`（A）**

```python
nz_edges(n_nodes, edges_uv, order) -> dict      # 按顺序逐条删边
nz_nodes(n_nodes, edges_uv, order) -> dict      # 按顺序逐个删节点（B 也用它）
# 返回的 dict 含 "gcc_size"、"n_components"、"n_isolated" 三个数组，
# 下标 t 表示"已删除 t 个"
to_levels(nz_out, levels, total, gid, strategy, seed) -> pd.DataFrame   # 转成 4.5 的长表
```

**`retrieval.py`（C）**

```python
class Retriever:
    def __init__(self, gid): ...
    def evaluate(self, queries, edge_alive=None, node_alive=None,
                 compute_dist=False) -> pd.DataFrame
        # 每个查询一行：query_id, drug_alive, disease_alive, s_alive, d_ppi
```

**`theory.py`（D）**

```python
R_edge(p, m_list) -> float                   # 1 − G(1 − p²)
R_node(phi, m_list) -> float                 # φ² · [1 − G(1 − φ)]
gcc_bond(degrees, p) -> float
gcc_site(degrees, phi) -> float
gcc_degree_attack(degrees, f) -> float       # Callaway et al. 2000
R_inf_edge(p, gid, queries) -> float         # L → ∞ 的 PPI 近似
```

**`restoration.py`（E）**

```python
restore(edge_alive, ranked_removed_eids, budget_frac) -> np.ndarray[bool]
rank_random(removed_eids, seed) / rank_edge_betweenness(...) /
rank_relation_type(...) / rank_task_aware(...)
```

---

## 6. 任务卡 A：数据基建 + WS1 随机失效

**目标**：

1. 让全组尽早拿到统一、可验证的数据。
2. 给出随机失效的渗流曲线，并与 generating function 理论对比。

### 步骤

| # | 截止 | 任务 |
|---|---|---|
| A1 | 11/2 23:00 | 建仓库骨架、`requirements.txt`、`common.py`；运行附录 A 生成 `toy_v1`；在群里通知 **M0 完成** |
| A2 | 11/3 12:00 | `build_graph.py`：严格按原协议 4.3–4.5 节（过滤三类节点和三类关系、规范化、去重去自环、确定性 BFS）。同一个脚本同时输出 2000 和 5000 两个图，顺便保存过滤后的全候选网络 `primekg_full_v1` |
| A3 | 11/3 12:00 | `make_queries.py`：按原协议 4.6 节生成查询（逻辑可参考附录 A 的 toy 脚本），补充 `redundancy_m`、`group`、`intermediates`、`split` 字段 |
| A4 | 11/3 12:00 | `make_orders.py`：随机删除顺序（边、节点，种子 0–9）；写 `manifest.json`；**检查 `pairs_with_multiple_relations` 并告诉 D 结果**。通知 **M1 完成** |
| A5 | 11/3 18:00 | `percolation.py`：实现 Newman–Ziff 的 `nz_edges` 和 `nz_nodes`（代码可参考评审文档附录 A.3）。**在 3 个删除比例上与 networkx 的直接计算结果核对** |
| A6 | 11/3 21:00 | 在 2000 节点图上跑随机删边、删节点，输出长表，叠加 D 的 `gcc_bond` 和 `gcc_site` |
| A7 | 11/4 16:00 | 在 5000 节点图上重跑；画度分布（log-binned CCDF）；**可选**：在全图上跑随机删边（Newman–Ziff 很快），作为对照 |

### 交付物

- `data/processed/` 下的全部数据文件
- `results/ws1/*.csv`
- 图：
  - `fig_degree_dist`：度分布，按节点类型着色
  - `fig_S_random_edge`：模拟 + `theory_bond`
  - `fig_S_random_node`：模拟 + `theory_site`

### 验收标准

- [ ] `pairs_with_multiple_relations == 0`（如果不为 0，立即告诉 D）
- [ ] f = 0 时，S 等于原图 GCC 所占比例
- [ ] Newman–Ziff 与 networkx 的结果在抽查点上一致
- [ ] 删除集合嵌套：10% 删除的集合是 20% 删除的集合的子集
- [ ] 在 5000 节点图上，所有查询在 f = 0 时都成功

**Slides**：第 3 页（数据与协议）、第 4 页（随机失效 + 理论）。
**报告**：第 2 节（数据与协议）、第 4.1 节（随机失效）、附录（可复现性说明）。

---

## 7. 任务卡 B：WS2 定向攻击 + 中心性

**目标**：

1. 提供中心性删除顺序。
2. 给出定向攻击的渗流曲线并叠加理论。
3. 回答"hub 是谁"。

### 步骤

| # | 截止 | 任务 |
|---|---|---|
| B1 | 11/3 12:00 | 在 toy 数据上写好 `centrality.py`：节点度顺序、节点 betweenness 顺序、边 betweenness 顺序，记录运行时间 |
| B2 | 11/3 15:00 | M1 一到，计算 2000 和 5000 两个图的 `node_degree`、`node_betweenness`；通知 **M2 完成** |
| B3 | 11/3 21:00 | 计算 5000 节点图的 `edge_betweenness`（交给 E）；用 A 的 `nz_nodes` 跑度攻击和 betweenness 攻击，在 2000 节点图上与随机删节点对比 |
| B4 | 11/4 12:00 | 在 5000 节点图上重跑；叠加 D 的 `gcc_degree_attack`；**hub 组成分析**：排名前 1%、5%、10% 的节点中 drug、disease、protein 各占多少；度排名与 betweenness 排名前 k 名的 Jaccard 重合度 |
| B5 | 11/4 16:00 | 定稿图 |

### 交付物

- `orders/node_degree.npy`、`node_betweenness.npy`、`edge_betweenness.npy`
- `results/ws2/*.csv`
- 图：
  - `fig_attack`：随机、度攻击、betweenness 攻击三条曲线，加度攻击的理论曲线
  - `fig_hub_composition`：hub 的类型组成

### 验收标准

- [ ] 两条攻击曲线都明显低于随机删节点
- [ ] 理论曲线已叠加；偏差的方向写在讲稿要点里
- [ ] 确定性攻击只画单条曲线

**报告阶段的额外任务**：零模型。按类型做保度重连（PPI 边之间互换端点；`drug_protein` 和 `disease_protein` 各自内部互换蛋白端），每种重连生成 3 个随机版本，各存成一个新的 gid，格式与原图完全相同。这样所有人的代码不用改就能直接在零模型上运行。

**Slides**：第 5 页（定向攻击）。
**报告**：第 4.2 节（定向攻击 + 零模型）。B 同时担任**报告统稿**。

---

## 8. 任务卡 C：WS3 检索引擎 + 结构 vs 功能 + L 扫描

**目标**：

1. 提供全组共用的检索引擎。
2. 给出 S 与 R 之间的差距。
3. 完成 L 扫描（全场最重要的图之一）。

### 步骤

| # | 截止 | 任务 |
|---|---|---|
| C1 | 11/3 12:00 | 在 toy 数据上写 `retrieval.py`：按类型的邻接表、两跳存活路径计数 `s_alive`、PPI 距离 `d_ppi`（用 `scipy.sparse.csgraph.dijkstra(..., unweighted=True, min_only=True)` 做多源 BFS，参考评审文档附录 A.4） |
| C2 | 11/3 18:00 | 单元测试（见下方验收标准），在 2000 节点图上通过；通知 **M3 完成** |
| C3 | 11/3 21:00 | 批量运行脚本：对 4 种策略和所有删除比例输出 per-query 结果（L = 2 时 `compute_dist=False`，速度快）；汇总出 `R_L2`、`R_L2_single`、`R_L2_multi` |
| C4 | 11/4 12:00 | 在 5000 节点图上重跑；**L 扫描**：随机删边，种子 0–2，L ∈ {2, 3, 4, ∞}（L = ∞ 用连通分量判断） |
| C5 | 11/4 16:00 | 定稿图；把 per-query 结果交给 D |

### 交付物

- `src/retrieval.py`（E 也要用）
- `results/ws3/` 下的汇总表和 per-query 表
- 图：
  - `fig_S_vs_R`：同一张图上画 S(f) 和 R(f)，突出两者的差距
  - `fig_R_by_group`：single 组与 multi 组的 R(f)
  - `fig_R_L_curves`：L = 2、3、4、∞ 的 R(f)
  - `fig_R_L_heatmap`：横轴 f，纵轴 L，颜色表示 R

### 验收标准

- [ ] f = 0 时所有查询成功，且 `s_alive == redundancy_m`
- [ ] `d_ppi == 0` 当且仅当 `s_alive > 0`
- [ ] 随机删边时，single 组的 R 落在 p² 附近，multi 组落在 D 的公式曲线附近。只用 10 个种子、每组 100 个查询时，偏差在 ±0.05 以内都属正常；需要更严格核对时，可临时多跑一些种子
- [ ] L 越大，R 越高（同一损坏状态下单调）

**Slides**：第 6 页（S vs R 的差距）、第 7 页（冗余分组）、第 8 页（L 扫描曲线）。
**报告**：第 5 节（功能鲁棒性与任务尺度）。

---

## 9. 任务卡 D（方闻）：WS4 理论与预测

**目标**：

1. 为全组提供理论曲线。
2. 用理论解释和预测检索失效。
3. 给出理论在哪里失效。

### 步骤

| # | 截止 | 任务 |
|---|---|---|
| D1 | 11/3 15:00 | `theory.py`：`R_edge`、`R_node`、`gcc_bond`、`gcc_site`、`gcc_degree_attack`。**先在 configuration model 随机图上验证**：理论与模拟在这里必须吻合，用来检查代码本身是否正确 |
| D2 | 11/3 18:00 | 推送 `theory.py` v1，在群里写清楚调用方法；通知 **M3 完成** |
| D3 | 11/3 21:00 | 确认 A 的 `pairs_with_multiple_relations`；和 C 一起核对 single 组是否落在 p² 上 |
| D4 | 11/4 12:00 | 实现 `R_inf_edge`（PPI 近似，见评审文档 5.2 节）；计算**相关性惩罚** Δ(f) = `R_node`(φ = 1 − f) − R_模拟(f)，分别针对度攻击和 betweenness 攻击 |
| D5 | 11/4 16:00 | **Per-query 预测**：随机删边，f ∈ {0.3, 0.5}，样本为 (查询, 种子)，按种子 0–6 训练、7–9 测试。理论概率 1 − (1 − p²)^m 与 logistic regression（特征：m、中间蛋白度的均值和最小值、药物度、疾病度）比较 AUC 和 Brier score。**同等损坏比较**：在相同 f 下，三种节点删除策略的 S 排序与 R 排序是否一致 |
| D6 | 11/4 16:00 | 与 C 合作：在 R(p, L) 相图上叠加两个理论极限（L = 2 的公式和 L = ∞ 的近似） |

### 交付物

- `src/theory.py`、`src/prediction.py`
- `results/ws4/*.csv`
- 图：
  - `fig_R_theory_vs_sim`：两组查询的模拟 + 理论
  - `fig_corr_penalty`：两种攻击下的 Δ(f)
  - `fig_phase_diagram`：与 C 共同完成，叠加理论极限
  - `fig_prediction`：理论与回归的 AUC 对比，可以做成一张小表

### 验收标准

- [ ] 在 configuration model 上，理论与模拟吻合
- [ ] 在真实图上，single 组 R ≈ p²
- [ ] 理论与模拟的每一处偏差，都有一句解释或一个待检验的假设

**Slides**：第 9 页（一行公式）、第 10 页（定向攻击打破独立性）、第 11 页（相图的含义）。Q&A 中主答理论问题。
**报告**：第 3 节（理论）、第 6 节（预测）。

---

## 10. 任务卡 E：WS5 恢复 + slides 统稿

**目标**：

1. 回答"有限预算下该先修哪些边"，以及答案为什么取决于任务尺度。
2. 把全组的图组装成一份连贯的 slides。

### 步骤

| # | 截止 | 任务 |
|---|---|---|
| E1 | 11/3 12:00 | `plotting.py`（附录 C）；英文 slides 模板，按四幕结构，先放好占位页（见第 11 节）；分享给全组 |
| E2 | 11/3 21:00 | 在 toy 数据上写 `restoration.py`，实现四种恢复策略（见下表） |
| E3 | 11/4 14:00 | 在 5000 节点图上运行：损坏状态取随机删边 30% 和 50%（种子 0–9）；恢复预算为被删边的 5%、10%、20%；评估 GCC，以及**测试查询**在 L = 2 和 L = 3 下的 R（用 C 的 `Retriever`） |
| E4 | 11/4 16:00 | 定稿图 |
| E5 | 11/4 16:00–20:00 | 收集所有人的图和讲稿要点（附录 D 的模板），组装 slides |
| E6 | 11/5 17:00 | 吸收排练反馈，定稿，**提交** |

### 四种恢复策略

| 策略 | 做法 | 想说明什么 |
|---|---|---|
| `random` | 随机恢复（种子为损坏种子 + 100） | 基线 |
| `edge_betweenness` | 按 B 提供的边 betweenness 从高到低恢复 | 全局结构上的重要性 |
| `relation_type`（新增） | 只在被删的 `drug_protein` 和 `disease_protein` 边中随机恢复 | 分离出"边的类型"这一个因素 |
| `task_aware` | 对每条被删的边打分：当前一条存活路径都没有的训练查询中，这条边能补全多少条路径（路径的另一条边必须存活）。按分数从高到低恢复，分数相同时随机 | 任务相关的重要性 |

`relation_type` 是一个很便宜但很有说服力的对照。如果它已经能拿到 `task_aware` 的大部分收益，就说明 L = 2 时"修哪类边"比"修哪条边"更重要。

### 交付物

- `src/plotting.py`、`src/restoration.py`
- `results/ws5/*.csv`
- 图：
  - `fig_restoration`：左右两个面板，分别为 L = 2 和 L = 3；横轴为预算，纵轴为测试查询 R 的提升量；每种策略一条线
  - `fig_gain_per_edge`：每恢复一条边带来的收益
- `slides/G17_final.pptx`

### 验收标准

- [ ] 预算为 0 时，四种策略结果相同
- [ ] 评估只用测试查询
- [ ] slides 总时长在排练中控制在 14 分钟以内

**Slides**：第 1–2 页（标题与 Hook）、第 12–13 页（恢复）、第 14 页（结论）。
**报告**：第 1 节（引言）、第 7 节（恢复）。

---

## 11. Slides 分页与讲者安排

### 11.1 分页（正文约 14 页，另加备份页）

| 页 | 内容 | 核心图 | 负责 |
|---|---|---|---|
| 1 | 标题 | — | E |
| 2 | Hook：连通 ≠ 可用（GraphRAG 示意） | 一个查询失效的示意图 | E |
| 3 | PrimeKG 与实验协议 | 图规模表、度分布 | A |
| 4 | 第一幕：随机失效 + GF 理论 | `fig_S_random_edge` / `_node` | A |
| 5 | 第一幕：定向攻击 + 理论；hub 是谁 | `fig_attack`、`fig_hub_composition` | B |
| 6 | 第二幕：S 与 R 的差距 | `fig_S_vs_R` | C |
| 7 | 第二幕：冗余分组 | `fig_R_by_group` | C |
| 8 | 第二幕：任务尺度 L | `fig_R_L_curves` | C |
| 9 | 第二幕：一行公式 R = 1 − G(1 − p²) | `fig_R_theory_vs_sim` | D |
| 10 | 第二幕：定向攻击打破独立性 | `fig_corr_penalty` | D |
| 11 | 第二幕：相图——从局部到集体 | `fig_phase_diagram` | D |
| 12 | 第三幕：恢复策略对比 | `fig_restoration`（L = 2） | E |
| 13 | 第三幕：恢复策略取决于任务尺度 | `fig_restoration`（L = 3） | E |
| 14 | 结论：鲁棒性属于"网络–任务"这一对 | 总结图 | E |
| 备份 | 协议细节、sanity check、预测表、零模型（如果已完成） | — | 各自 |

### 11.2 讲者顺序（每人都上台，体现个人贡献）

| 顺序 | 讲者 | 页 | 时长 |
|---|---|---|---|
| 1 | E | 1–2 | 1:00 |
| 2 | A | 3–4 | 3:00 |
| 3 | B | 5 | 2:30 |
| 4 | C | 6–8 | 3:00 |
| 5 | D | 9–11 | 3:00 |
| 6 | E | 12–14 | 2:30 |
| | | **合计** | **15:00** |

第二幕的分工是：C 先讲"观察到了什么"（差距、冗余分组、L 的影响），D 再讲"为什么会这样"（公式、公式何时失效、相图的两个理论极限）。这样每人只上台一次，叙事也是先现象、后解释。

**排练目标**：14 分钟。正式讲时总会比排练慢一些。

**Q&A 分工**：理论问题由 D 回答，检索和任务尺度由 C 回答，数据与协议由 A 回答，攻击与 hub 由 B 回答，恢复由 E 回答。

---

## 12. 报告分工与 11/22 前的时间线

### 12.1 章节分工（要求至少 10 页，不含代码、数据、参考文献）

| 节 | 标题 | 负责 | 预计页数 |
|---|---|---|---|
| 1 | Introduction & Motivation | E | 1 |
| 2 | Data & Experimental Protocol | A | 1.5 |
| 3 | Theory：GF 渗流、PGF 检索公式、L → ∞ 极限、limited path percolation | D | 2 |
| 4.1 | Structural Robustness：随机失效（含全图对照） | A | 1.5 |
| 4.2 | Structural Robustness：定向攻击与零模型 | B | 1.5 |
| 5 | Functional Robustness & Task Horizon | C | 2 |
| 6 | Predicting Retrieval Failure | D | 1 |
| 7 | Network-informed Restoration | E | 1.5 |
| 8 | Discussion, Limitations & Conclusion | B 统稿，全组提供要点 | 1 |
| 附录 | Reproducibility：数据校验和、种子、运行方法 | A | — |

合计约 13 页，留有余量。

### 12.2 时间线

| 时间 | 任务 | 负责 |
|---|---|---|
| 11/6 – 11/12 | 报告阶段的补充实验：零模型（B）、全图对照（A）、有效冗余与定向攻击理论（D）、L = 3 的恢复分析（E）、L 扫描补足种子（C） | 各自 |
| 11/13 | 各节初稿 | 各自 |
| **11/15 23:59** | **Peer grading 截止（每人都要完成）** | 全组 |
| 11/17 | 统稿 v1：统一术语、图号、符号 | B |
| 11/19 | 交叉审阅：A↔C、B↔D、E↔A，每人审一节 | 全组 |
| 11/21 | 定稿；代码和数据打包，附 README 运行说明 | B、A |
| **11/22 20:00 前** | **提交报告、代码与数据**；**每人提交 individual report** | 全组 |

---

## 13. 协作规则与风险预案

### 13.1 协作规则

1. 每个人只改自己负责的 `src/` 文件和 `results/{自己的 ws}/`。
2. 修改共享接口（第 4、5 节）之前，先在群里说明，得到受影响的人确认后再改。
3. 每完成一个里程碑就推送一次，提交说明写清楚做了什么。
4. 原始数据 `kg.csv` 不提交到仓库，各自下载，用 manifest 里的 SHA-256 核对。
5. 遇到阻塞超过 1 小时，立刻在群里说，不要独自硬扛。

### 13.2 风险预案

| 风险 | 预案 |
|---|---|
| M1 延误 | 其他人继续用 toy 数据开发。**11/4 12:00 是决策点**：如果 5000 节点图还没稳定，slides 统一改用 2000 节点图，5000 节点图留到报告阶段 |
| 5000 节点图的 betweenness 太慢 | 先把 k 降到 50；仍然太慢就在 11/3 晚上挂机运行；slides 中 betweenness 攻击可以用 2000 节点图的结果 |
| L 扫描太慢 | 只做 L ∈ {2, 3, ∞}、种子 0–2；必要时在 2000 节点图上做 |
| `pairs_with_multiple_relations > 0` | D 把公式改为近似，并在报告中说明；其余工作不受影响 |
| 理论与模拟不吻合 | 先在 configuration model 上排除代码错误（D1）。如果代码没问题，偏差就是结果，写进讲稿 |
| 有人临时无法投入 | 互为备份：A↔B、C↔E、D↔C。备份者提前读一遍对方的任务卡 |

---

## 14. 同步会议安排（每次线上 15 分钟）

| 时间 | 议题 |
|---|---|
| **11/2 22:00** | 启动会：确认角色和姓名、仓库链接、第 4–5 节的约定；有异议当场改 |
| 11/3 21:00（M4） | 2000 节点图的 sanity check：Newman–Ziff 与 networkx 一致、single 组 ≈ p²、configuration model 上理论吻合；暴露阻塞问题 |
| 11/4 16:00（M5） | 图表冻结：每人展示最终图和三条讲稿要点 |
| 11/4 21:00（M6） | 第一次完整排练并计时 |
| 11/5 12:00 | 第二次排练与最终检查；17:00 前提交 |

---

## 15. 附录

### 附录 A：toy 数据生成脚本（`make_toy.py`）

格式与正式数据完全一致，用于 M1 之前的开发。查询生成逻辑也可以供 A 写 `make_queries.py` 时参考。

这个脚本我已经实际运行过：生成 720 个节点、约 3000 条边，能抽满 100 个 single 和 100 个 multi 查询。在这份 toy 数据上，我还核对了三件事，结果都符合预期：

- 随机删边时，single 组的 R 与 p² 吻合；multi 组在 2000 次随机损坏的平均下，与公式 1 − G(1 − p²) 的差距小于 0.002。
- Newman–Ziff（评审文档附录 A.3）与 networkx 直接计算的最大连通块大小完全一致。
- 在 configuration model 随机图上，GF 理论（评审文档附录 A.2）与模拟的 GCC 差距在 0.01 以内。

所以评审文档附录里的代码片段可以放心直接用。

```python
import json, os
from collections import defaultdict
import numpy as np, pandas as pd, networkx as nx

gid = "toy_v1"
out = f"data/processed/{gid}"
os.makedirs(f"{out}/orders", exist_ok=True)
rng = np.random.default_rng(42)

# 节点：60 个药物、60 个疾病、600 个蛋白
n_drug, n_dis, n_prot = 60, 60, 600
types = ["drug"] * n_drug + ["disease"] * n_dis + ["gene/protein"] * n_prot
N = len(types)
nodes = pd.DataFrame({"nid": range(N), "x_index": range(N),
                      "node_type": types, "node_name": [f"n{i}" for i in range(N)]})
drugs = np.arange(n_drug)
diseases = n_drug + np.arange(n_dis)
prots = n_drug + n_dis + np.arange(n_prot)

# 边
edge_set = set()
ppi = nx.barabasi_albert_graph(n_prot, 3, seed=42)
for a, b in ppi.edges():
    u, v = sorted((int(prots[a]), int(prots[b])))
    edge_set.add((u, v, "protein_protein"))
# 药物、疾病按 PPI 度的比例挑选蛋白（hub 蛋白更常被选中，查询才会有足够的冗余）
w = np.array([ppi.degree(i) for i in range(n_prot)], dtype=float)
w /= w.sum()
for d in drugs:
    for p in rng.choice(prots, rng.integers(2, 13), replace=False, p=w):
        u, v = sorted((int(d), int(p)))
        edge_set.add((u, v, "drug_protein"))
for s in diseases:
    for p in rng.choice(prots, rng.integers(5, 26), replace=False, p=w):
        u, v = sorted((int(s), int(p)))
        edge_set.add((u, v, "disease_protein"))
edges = pd.DataFrame(sorted(edge_set, key=lambda e: (e[2], e[0], e[1])),
                     columns=["u", "v", "relation"])
edges.insert(0, "eid", range(len(edges)))
nodes.to_csv(f"{out}/nodes.csv", index=False)
edges.to_csv(f"{out}/edges.csv", index=False)

# 查询：按节点类型判断哪一端是药物或疾病（正式数据中不能假设 u 一定是药物）
ntype = nodes.node_type.values
def entity_protein_pairs(df, etype):
    u, v = df.u.values, df.v.values
    is_u = ntype[u] == etype
    return np.where(is_u, u, v), np.where(is_u, v, u)

targets, dprots = defaultdict(set), defaultdict(set)
for a, b in zip(*entity_protein_pairs(edges[edges.relation == "drug_protein"], "drug")):
    targets[int(a)].add(int(b))
for a, b in zip(*entity_protein_pairs(edges[edges.relation == "disease_protein"], "disease")):
    dprots[int(a)].add(int(b))

pairs = []
for d, T in targets.items():
    for s, D in dprots.items():
        inter = sorted(T & D)
        if inter:
            pairs.append((d, s, inter))
pairs.sort(key=lambda x: (x[0], x[1]))
single = [p for p in pairs if len(p[2]) == 1]
multi = [p for p in pairs if len(p[2]) >= 2]

def pick(lst, k=100):
    idx = np.random.default_rng(42).permutation(len(lst))[:k]
    return [lst[i] for i in sorted(idx)]

chosen = [(p, "single") for p in pick(single)] + [(p, "multi") for p in pick(multi)]
perm = np.random.default_rng(42).permutation(len(chosen))
train_ids = set(perm[: int(round(0.7 * len(chosen)))].tolist())
xi = nodes.x_index.values
queries = [{"query_id": i, "drug_nid": d, "disease_nid": s,
            "drug_x_index": int(xi[d]), "disease_x_index": int(xi[s]),
            "relation_pattern": ["drug_protein", "disease_protein"], "max_hops": 2,
            "redundancy_m": len(inter), "group": g, "intermediates": inter,
            "split": "train" if i in train_ids else "test"}
           for i, ((d, s, inter), g) in enumerate(chosen)]
with open(f"{out}/queries.json", "w") as f:
    json.dump(queries, f, indent=1)

# 随机删除顺序
E = len(edges)
for sd in range(10):
    np.save(f"{out}/orders/edge_random_s{sd}.npy", np.random.default_rng(sd).permutation(E))
    np.save(f"{out}/orders/node_random_s{sd}.npy", np.random.default_rng(sd).permutation(N))
print(f"toy_v1: {N} nodes, {E} edges, {len(single)} single / {len(multi)} multi pairs")
```

### 附录 B：结果文件示例（数值仅为示意）

```
gid,strategy,seed,frac_removed,n_removed,metric,value
primekg_5000_bfs_v1,edge_random,3,0.30,15000,gcc_frac,0.97
primekg_5000_bfs_v1,edge_random,3,0.30,15000,R_L2_single,0.48
primekg_5000_bfs_v1,node_degree,-1,0.05,250,gcc_frac,0.61
primekg_5000_bfs_v1,theory_bond,-1,0.30,,gcc_frac,0.98
```

### 附录 C：统一作图风格（`plotting.py`，E 维护）

```python
import matplotlib.pyplot as plt

STYLE = {
    "edge_random":      dict(color="#1f77b4", label="Random edge removal"),
    "node_random":      dict(color="#2ca02c", label="Random node removal"),
    "node_degree":      dict(color="#d62728", label="Degree attack"),
    "node_betweenness": dict(color="#ff7f0e", label="Betweenness attack"),
    "theory":           dict(color="black", ls="--", label="Theory"),
}

def setup():
    plt.rcParams.update({"font.size": 12, "figure.figsize": (6, 4),
                         "savefig.dpi": 300, "axes.spines.top": False,
                         "axes.spines.right": False})

def save(fig, act, name):
    for ext in ("png", "pdf"):
        fig.savefig(f"figures/{act}/{name}.{ext}", bbox_inches="tight")
```

### 附录 D：图表交接模板（M5 时每人交给 E）

```
图：figures/act2/fig_R_theory_vs_sim.png
要点 1：……
要点 2：……
要点 3：……
讲稿（英文，50–80 词）：……
可能被问到的问题及回答：……
```

---

如在推导、代码或分工上遇到具体问题，可以通过方闻继续问我。祝顺利。
