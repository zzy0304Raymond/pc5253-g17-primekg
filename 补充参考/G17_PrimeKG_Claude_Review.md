# 关于 PrimeKG 方案的评审与升级建议

> Claude · 应方闻之邀 · 2026-11-02
>
> 方闻把 `writing-block.md` 发给我，并和我讨论了你们组的情况：时间很紧，多数组员的物理背景不多。下面的意见都以这两点为约束：**不推翻原方案，只提投入小、回报大的增量。**
>
> 公式以纯文本书写，便于在手机上阅读。

---

## 0. 结论先行

这个方案可以拿到不错的分数。如果目标是高分，差的不是工作量，而是**一层理论**。

PC5253 是一门物理系的课。老师最想看到的，是课上的工具（generating function、渗流的自洽方程）真正用在一个新系统上，并且**理论和模拟能互相印证**。原方案在实验设计上已经做得很好，但目前只用到了这些概念的名字，还没有用到它们的数学。

好消息是，这层理论恰好非常轻：

- 两条公式就能覆盖结构和功能两个层面；
- 不需要改动协议；
- 也不需要每个人都学推导。

| # | 建议 | 涉及 | 额外成本 | 建议负责 |
|---|---|---|---|---|
| 升级 1 | 检索成功率 R(p) 的**零参数精确公式**（PGF） | WS3 / WS4 | 低 | 方闻 |
| 升级 2 | GCC 的 **generating function 理论曲线** + 零模型 | WS1 / WS2 | 低–中 | 方闻写函数，WS1/2 叠图 |
| 升级 3 | 新增变量：**检索允许的最大跳数 L** | WS3 / WS5 | 中 | 方闻写函数，WS3 跑 |
| 修正 A | 删除比例延伸到 95%–99% | WS1 / 2 / 3 | 很低 | 各 WS |
| 修正 B | 使用过滤后的全图，或至少与全图对照 | 全组 | 低 | 建图的同学 |
| 修正 C | WS4 从"相关 + 回归"改为"理论 vs 回归 + per-query" | WS4 | 中 | 方闻 |

方闻已经和我讨论过理论部分，由他来负责是最自然的安排。其余同学的工作基本不变，只是多叠一条理论曲线。

完成后，整个报告可以落在一句话上：

> **鲁棒性不是网络本身的属性，而是"网络–任务"这一对的属性。**

---

## 1. 原方案的长处

先说清楚，这些都值得保留：

- **可复现性很好。** 固定数据文件、固定种子、嵌套前缀删除、统一指标。很多课程项目在这一点上做得很粗糙。
- **"结构鲁棒 vs 功能鲁棒"是一个真正好的问题。** 它把网络科学和 AI 检索的可靠性连接了起来，现实意义清楚。
- **分工可以并行。** 五条线互不阻塞，适合时间紧的情况。
- **数据选得好。** PrimeKG 是真实、公开、有规范引用的生物医学 KG。

所以下面的建议都是在这个骨架上加东西，而不是换掉它。

---

## 2. 从评分者的角度看，有五个风险

**风险 1：WS1/WS2 的核心结论是已知结果。**
"随机失效时稳健、攻击 hub 时脆弱"是 Albert, Jeong & Barabási（Nature 2000）的经典结论。另外三个做 Knowledge Graphs 的组也很可能做 robustness。如果只复现这个结论，很难拉开差距。

**风险 2："Percolation"目前只有模拟，没有理论。**
课程 L6–L7 的核心是 generating function：自洽方程、giant component、Molloy–Reed 判据。对物理背景的老师来说，"有理论曲线并与模拟对比"和"只有模拟曲线"是两个档次。方案 Section 7 写的"未必出现临界点，谨慎解释"，相当于提前放弃了物理分析。其实有更好的做法：**用理论说明临界点应该在哪里，再去那里看。**

**风险 3：WS4 的相关与回归有统计陷阱。**

- GCC、平均度、孤立节点比例、检索成功率，都是删除比例的单调函数。两两之间的 Spearman 相关会**自动**接近 1。这只说明它们共同依赖删除比例，并不说明 GCC 能"预测"检索。
- 按种子划分训练集和测试集，两边只差随机噪声，测试误差也会**自动**很小。
- 这类问题评分者通常一眼就能看出来。

**风险 4：删除比例最高只到 80%，可能看不到相变。**
PPI 网络很稠密，⟨k²⟩ 很大。按 Molloy–Reed 判据，渗流阈值可能在"只保留 1%–5% 的边"附近，也就是删除 95%–99%。只删到 80%，曲线可能一直平稳，相变根本不会出现。

**风险 5：5000 节点 BFS 子图会引入偏差。**

- 从最高度的疾病节点出发做 BFS，会过度采样 hub。
- 边界节点的度会被人为截断。
- 查询集也可能被少数 hub 疾病主导。

而过滤后的全图规模并不大：drug、disease、gene/protein 三类合计约 5 万个节点，边约几十万条（以实际统计为准）。用 union-find 算整条渗流曲线只要几秒，全图完全可以处理。

---

## 3. 升级 1：检索成功率的零参数精确公式

这是投入最小、回报最大的一项。

### 3.1 直觉

一个查询 (drug, disease) 有 m 条两跳路径，也就是 m 个不同的中间蛋白。

- 每条路径要求**两条边同时存活**。
- 删边是随机的，而不同路径之间**不共享边**，所以各条路径的存活相互独立。

于是查询失败的概率，就是"m 条路径全部断掉"的概率。

### 3.2 推导

设删除比例为 f，每条边的保留率为 p = 1 − f。

```
单条路径存活的概率：   p²
m 条路径全部失效：     (1 − p²)^m
查询成功：             1 − (1 − p²)^m
```

**为什么独立？** 设两个不同的中间蛋白为 x₁ 和 x₂。两条路径分别使用边 (d–x₁, x₁–s) 和 (d–x₂, x₂–s)，四条边互不相同。

在你们的协议下，每个节点对只有一种关系类型：

- drug–protein 之间只有 `drug_protein`
- protein–protein 之间只有 `protein_protein`
- disease–protein 之间只有 `disease_protein`

所以语义边和结构边一一对应。**这一点请在建图后统计核实，它是公式严格成立的前提。** 按固定比例"不放回"删除时，独立性只有 O(1/E) 量级的误差，可以忽略。

### 3.3 公式

令 P(m) 为查询集中冗余度为 m 的比例，它的概率生成函数（PGF，课程 L6）为：

```
G(z) = Σ_m P(m) · z^m
```

**随机删边**（边保留率 p）：

```
R(p) = Σ_m P(m) · [1 − (1 − p²)^m]  =  1 − G(1 − p²)
```

**随机删节点**（节点保留率 φ）：药物和疾病本身都必须存活，中间蛋白至少存活一个。

```
R(φ) = φ² · [1 − G(1 − φ)]
```

这个公式**没有任何拟合参数**，只需要查询集的冗余分布 P(m)。

### 3.4 数值例子

| 删除比例 f | p | m = 1 | m = 2 | m = 3 |
|---|---|---|---|---|
| 10% | 0.9 | 0.810 | 0.964 | 0.993 |
| 30% | 0.7 | 0.490 | 0.740 | 0.867 |
| 50% | 0.5 | 0.250 | 0.438 | 0.578 |
| 70% | 0.3 | 0.090 | 0.172 | 0.246 |

两点直观结论：

- **单路径查询非常脆弱**：删掉 30% 的边，就只剩一半能检索到。
- **冗余的收益递减**：在高损坏区，多几条路径的帮助也有限。

### 3.5 在你们的查询集上

协议里有两组查询：m = 1 的 100 个，m ≥ 2 的 100 个。

```
R(p) = ½ · p²  +  ½ · [1 − G_{m≥2}(1 − p²)]
```

- m = 1 组的模拟结果**必须落在 p² 这条曲线上**。这同时也是检验检索代码正确性的好办法。
- m ≥ 2 组用该组实际的 m 分布代入。

### 3.6 公式失效之处，才是真正的发现

在**定向攻击**（删除高度或高介数节点）下，独立性假设会被打破：

- 很多"冗余"路径其实经过同一批 hub 蛋白。
- 删一个 hub，会同时切断很多查询的很多条路径，失效是**相关的**。
- 因此公式会**高估**鲁棒性。

可以定义一个**相关性惩罚**（correlation penalty）：

```
Δ(f) = R_独立公式(f) − R_定向攻击模拟(f)
```

由此得出的结论是：**路径条数 m 不等于有效冗余。中间蛋白的多样性才是关键。** 报告阶段可以进一步提出"有效冗余"指标，例如按中间蛋白的度加权，再检验它能否比 m 更好地预测定向攻击下的失效。

### 3.7 一个结构性解释：S 和 R 依赖的是不同的边

- L = 2 的检索只用到 `drug_protein` 和 `disease_protein` 两类边。
- `protein_protein` 边很可能占结构边的大多数（以实际统计为准）。它们撑起了 GCC，但对 L = 2 检索的贡献**为零**。

所以"GCC 还很大，检索却已大量失败"并不是偶然，而是两件事叠加的结果：

1. 两个指标依赖的边不同；
2. 一个是全局量，一个是局部量。

这个解释也会影响 WS5：恢复 PPI 边能提升 GCC，但对 L = 2 检索没有帮助（预期如此，需实验验证）。

---

## 4. 升级 2：GCC 的理论曲线与零模型

### 4.1 直觉：一个自洽方程

随便取一条边，沿着它走出去，问：**它最终能不能通向巨大连通块？** 设"不能"的概率为 u。

一条边"不通"，有两种可能：

- 它被删掉了，概率 1 − p；
- 它还在，但走到的那个邻居，其余所有边也都不通，概率 p · g1(u)。

于是 u 必须满足一个**自己等于自己**的方程。这正是课上 L6–L7 的方法。

### 4.2 公式

```
g0(z) = Σ_k p_k · z^k            （度分布的生成函数）
g1(z) = g0'(z) / g0'(1)          （沿一条边到达的节点，其"剩余度"的生成函数）

随机删边（bond percolation，边保留率 p）：
    u = 1 − p + p · g1(u)
    S = 1 − g0(u)

随机删节点（site percolation，节点保留率 φ）：
    u = 1 − φ + φ · g1(u)
    S = φ · [1 − g0(u)]

临界点（Molloy–Reed）：
    p_c = ⟨k⟩ / (⟨k²⟩ − ⟨k⟩)
```

**定向攻击**（按度从高到低删节点，Callaway et al. 2000）：令 φ_k 为度为 k 的节点被保留的概率，高度节点为 0，低度节点为 1。

```
f0(z) = Σ_k p_k · φ_k · z^k
f1(z) = f0'(z) / ⟨k⟩
u = 1 − f1(1) + f1(u)
S = f0(1) − f0(u)
```

输入只需要真实图的**经验度分布**。代码见附录 A。

### 4.3 偏差即发现

理论假设图是 configuration model：除了度分布，其余一切完全随机。真实的 PrimeKG 还有：

- 聚类（clustering）；
- 疾病模块（disease modules）；
- 度相关（degree correlations）；
- 三类节点构成的多部结构。

**理论与模拟之间的偏差，正是这些结构造成的效应。** 偏差的方向和出现在哪个区间，本身就是可以讨论的结果。这把"理论不完全吻合"从一个弱点，变成了一个发现。

### 4.4 零模型：按类型保度重连

对真实图做 **degree-preserving rewiring**（Maslov & Sneppen 2002），只在同类边内部交换端点：

- PPI 边之间互换；
- `drug_protein` 边之间互换蛋白端；
- `disease_protein` 边之间互换蛋白端。

这样每个节点的分类型度都不变，但其余结构被打乱。在真实图和零模型上跑**同一套实验**（S、R、m 分布），差值就是"真实 KG 结构"的贡献。

一个值得检验的问题：药物靶点和疾病蛋白在真实网络里，是否比随机情况更靠近？网络医学的研究（Guney et al. 2016）表明是的。如果成立，真实 KG 的检索冗余就会高于零模型。

零模型放在报告阶段即可，slides 不必强求。

### 4.5 用 Newman–Ziff 一次算出整条曲线

你们协议里的"嵌套前缀删除"**倒过来**，就是按顺序加边。用 union-find 每加一条边更新一次最大连通块，**一次遍历就能得到 p 从 0 到 1 的整条 S(p) 曲线**（Newman & Ziff 2000）。

这样删除比例可以任意加密，例如在 90%–99% 之间每 0.5% 取一个点，几乎不增加计算量。代码见附录 A。

---

## 5. 升级 3：新增变量——检索允许的最大跳数 L

这一项能产出一张其他组几乎不可能有的图，也是整个报告的思想核心。

### 5.1 定义

把查询从固定两跳推广为：

```
Drug —drug_protein→ 蛋白 —(protein_protein)×最多 (L−2) 步→ 蛋白 —disease_protein→ Disease
```

- L = 2 就是原方案。
- L = 3 表示中间允许一步 PPI。
- 依此类推。
- 中间链只经过蛋白，不经过其他药物或疾病，以保持语义模式。

这也有实际依据：网络医学中的"药物–疾病网络邻近度"（Guney et al. 2016）研究的正是药物靶点和疾病蛋白在 PPI 网络中的距离。

### 5.2 两个可解析的极限

**L = 2：局部行为。** 就是升级 1 的公式，R(p) 是 p 的**平滑多项式**，没有相变。鲁棒性完全由局部冗余决定。

**L → ∞：全局行为。** 只要药物端和疾病端都接入 PPI 的巨大连通块，就能检索成功。可以用升级 2 的方法近似：

```
在 PPI 子图上解：     u = 1 − p + p · g1_PPI(u)
蛋白 x（PPI 度 k_x）在巨大连通块中的概率：    π_x = 1 − u^(k_x)
药物 d 接入巨大连通块的概率：   A_d = 1 − Π_{x ∈ targets(d)} [1 − p · π_x]
疾病 s 同理：                   B_s = 1 − Π_{y ∈ proteins(s)} [1 − p · π_y]
R_∞(p) ≈ 对所有查询平均 A_d · B_s
```

当 p 降到 PPI 的渗流阈值附近时，π_x 会迅速趋于 0，R_∞ 也随之崩塌。这时出现的是**阈值行为**，是一个集体现象。

### 5.3 中间的 L：相图

L = 3、4、5 没有简单的解析式，由模拟来填。最终画两张图：

- **折线图**：L = 2、3、4、∞ 的 R(p) 曲线。预期从"平滑下降"逐渐过渡到"阈值式崩塌"。
- **热图**：横轴为删除比例，纵轴为 L，颜色表示 R。

在文献中，这对应 *limited path percolation*（López, Buldyrev, Havlin & Stanley, PRL 2007）：路径长度有上限时的渗流。

**以上都是理论预期，需要实验验证。** 即使实验与预期不符，偏差本身同样是可以报告的结果。

### 5.4 实现思路

对每个损坏状态：

1. 构建一次 PPI 子图的稀疏邻接矩阵。
2. 对每个查询，从药物仍存活的靶点集合出发做**多源 BFS**，求它到疾病蛋白集合的最短 PPI 距离 d。
3. **一次计算即可覆盖所有 L**：查询在上限 L 下成功，当且仅当 d ≤ L − 2。
4. L = ∞ 只需判断两端蛋白是否在同一个连通分量里，更快。

用 `scipy.sparse.csgraph.dijkstra(..., unweighted=True, min_only=True)` 做多源 BFS，是 C 实现，速度够用。如果太慢，L 扫描可以只用 3 个种子。代码见附录 A。

### 5.5 这张图想说明什么

> **任务的尺度，决定了系统表现为"局部"还是"集体"。**
>
> 两跳检索的鲁棒性由局部冗余决定，没有相变。当检索需要更长的推理链时，鲁棒性才开始由全局连通性（渗流）主导。所以"一个 KG 是否鲁棒"这个问题，离开任务就没有答案。
>
> 这是 Anderson 所说的 *More is Different* 的一个具体例子：同一张网络，在不同尺度的任务面前，会呈现出性质不同的行为。

---

## 6. 三个小修正

### 修正 A：删除比例延伸到 95%–99%

- 原有档位保留，再增加 85%、90%、95%、97%、99%。
- 如果采用 Newman–Ziff 算法，可以直接得到连续曲线。
- 节点删除同理，可延伸到 80%–90%。

### 修正 B：使用全图，或至少与全图对照

- 2000 和 5000 节点的 BFS 子图保留，用于调试和快速验证。
- 主要结果最好在过滤后的全图上给出。
- 如果时间不够，至少在报告里放一张"BFS 子图 vs 全图"的度分布与 S(p) 对照。这样 Section 7 的 sampling bias 就从"局限"变成了"已经检验过的问题"。

### 修正 C：WS4 改为"理论 vs 回归"

把"跨删除比例做相关与回归"替换为三个更有说服力的分析：

1. **Per-query 预测。** 固定删除比例，预测**哪些查询**会失败。
   - 零参数基线：理论公式 1 − (1 − p²)^m。
   - 对比对象：用 m、中间蛋白度等特征训练的 logistic regression。
   - 比较 AUC 或 Brier score。
   - 预期：随机失效下，理论已接近最优；定向攻击下，回归能否学到"有效冗余"？
2. **同等损坏预算下的比较。** 在同一删除比例下，不同策略（随机、高度、高介数）会给出不同的 (S, R)。检验 S 的排序是否等于 R 的排序。这才是"结构指标能否反映功能"的有效检验。
3. **如果保留跨删除比例的回归**，必须控制删除比例的影响，例如使用偏相关或固定效应。

---

## 7. 修订后的分工

| WS | 原任务（不变） | 新增 | 新增交付图 |
|---|---|---|---|
| WS1 随机失效 | 随机删点、删边的渗流曲线 | 叠加 GF 理论曲线；删除比例延伸到 99% | **模拟 vs 理论** S(p) |
| WS2 定向攻击 | 高度、高介数攻击 vs 随机 | 叠加定向攻击理论曲线；零模型对照（报告阶段） | 攻击曲线 + 理论 |
| WS3 结构 vs 功能 | S(p) 与 R(p) 对比、冗余分组 | 叠加 PGF 公式；**L 扫描** | **R(p) + 公式**；**R(p, L) 相图** |
| WS4 → Theory & Prediction（方闻） | 原回归任务 | 全部理论函数；per-query 预测；同等损坏比较；相关性惩罚 | 相关性惩罚 Δ(f)；预测对比 |
| WS5 恢复 | 随机、中心性、task-aware 恢复 | 用"不同边类型的贡献"解释排序；L > 2 时 PPI 边开始有用 | 恢复曲线（L = 2 vs L = 3） |

---

## 8. 15 分钟 presentation 结构

建议把 5 个 workstream 压缩成 4 幕，**不要按 WS 逐个汇报**。15 分钟讲 5 条平行的线，每条只有 3 分钟，听众很难记住任何一条。讲一个有起承转合的故事，效果会好得多。

| 段落 | 时间 | 内容 | 核心图 |
|---|---|---|---|
| Hook | 1.5 min | GraphRAG 依赖的 KG 会丢失知识。**连通 ≠ 可用** | 一个查询失效的示意图 |
| 第一幕：结构 | 3 min | WS1 + WS2 合并：随机 vs 攻击；理论与模拟叠加；偏差即发现 | S(p)：模拟 + 理论 |
| 第二幕：功能 | 4.5 min | S 与 R 的差距 → 一行 PGF 公式解释 → 定向攻击下公式失效 → L 相图 | R(p) + 公式；**R(p, L)** |
| 第三幕：修复 | 3 min | WS5：恢复策略的排序及其原因；修复策略取决于任务尺度 | 恢复曲线 |
| 结论与局限 | 2 min | 鲁棒性属于"网络–任务"这一对；局限与展望 | 一张总结图 |

你们是最后一个讲 Knowledge Graphs 的组，开场不必再解释 KG 是什么。可以直接说：

> "Previous groups showed what knowledge graphs *are* and what they're *for*. We ask: when a knowledge graph loses knowledge, what exactly breaks — and can physics predict it?"

---

## 9. 时间线

| 时间 | 全组 | 方闻（理论） |
|---|---|---|
| 11/2 晚 – 11/3 | 按协议建图（先 2000 节点）；WS1–3 跑通基线 | 写理论函数（PGF、GF 求解、Newman–Ziff、L 距离），在 2000 节点图上验证 |
| 11/4 | 换 5000 节点图或全图；叠加理论曲线；WS5 基线 | L 扫描（L = 2、3、4、∞，3 个种子）；做第二幕的图 |
| 11/4 晚 | 按四幕结构合 slides，第一次排练 | 同左 |
| **11/5 18:00 前** | **提交 slides** | |
| 11/6 – 11/22 | 报告（≥ 10 页）+ code 与 data 打包 | 零模型、定向攻击理论、全图对照、有效冗余 |

如果时间实在不够，优先级是：**升级 1 > 修正 A > 升级 2 的随机删除部分 > 升级 3（至少 L = 2 和 ∞）**。其余都可以放到报告阶段。

---

## 10. Q&A 可能遇到的问题

**Q1：GF 理论假设 configuration model，真实 KG 有聚类和类型结构，为什么还能用？**
A：正因为如此，理论与模拟的偏差才有意义。它量化了"度分布之外的结构"带来的效应。零模型可以把这部分效应单独分离出来。

**Q2：两跳检索和真实的 GraphRAG 差距很大吧？**
A：我们只建模检索阶段。L 维度正好部分回应了这个问题：需要更长推理链的任务，鲁棒性表现完全不同。

**Q3：为什么 L = 2 时没有看到相变？**
A：理论上本来就不应该有。R(p) 是 p 的多项式，没有奇点。相变只在 L 足够大、任务依赖全局连通时才出现。另外，有限尺寸效应也会把相变"抹平"。

**Q4：task-aware 恢复赢过中心性恢复，不是理所当然吗？**
A：方向可以预期，但大小和原因不能。L = 2 时，中心性恢复的 PPI 边对检索贡献为零；L 变大后，PPI 边开始变得重要。所以"该恢复哪些边"取决于任务尺度。

---

## 11. 需要组内确认的事项

- [ ] 是否采纳以上升级（原协议和分工不变）
- [ ] WS4 是否改为 Theory & Prediction，由方闻负责
- [ ] 删除比例是否延伸到 95%–99%（建议采用 Newman–Ziff）
- [ ] 主要结果用全图，还是 5000 节点图加全图对照
- [ ] L 扫描是否由 WS3 用方闻的函数来跑
- [ ] slides 按四幕结构组织，由谁统稿

---

## 12. 结语

课程项目最常见的遗憾，不是做得太少，而是每一部分都做了，却没有一个能让人记住的结论。

这份方案已经有扎实的实验骨架。再加上一层理论，每一张图就不只是"我们观察到了什么"，还能回答"为什么会这样"和"理论在哪里失效"。对一门讲复杂系统的课来说，后两个问题才是真正的得分点。

如有需要，可以通过方闻继续问我推导或代码上的细节。祝展示顺利。

---

## 附录 A：代码片段

### A.1 检索成功率的理论公式（升级 1）

```python
import numpy as np

def retrieval_theory_edge(p, m_list):
    """随机删边，边保留率 p；m_list 为每个查询的路径冗余 m。"""
    m = np.asarray(m_list)
    return np.mean(1 - (1 - p**2) ** m)

def retrieval_theory_node(phi, m_list):
    """随机删节点，节点保留率 phi；药物和疾病本身也须存活。"""
    m = np.asarray(m_list)
    return np.mean(phi**2 * (1 - (1 - phi) ** m))
```

### A.2 GCC 的 generating function 理论（升级 2）

```python
def gcc_theory(degrees, keep, mode="bond", n_iter=5000):
    """
    degrees: 真实图中每个节点的度
    keep:    边保留率 p（mode="bond"），或节点保留率 phi（mode="site"）
    返回:    理论 giant component 比例 S
    """
    k = np.asarray(degrees)
    pk = np.bincount(k) / len(k)
    ks = np.arange(len(pk))
    mean_k = (ks * pk).sum()
    g0 = lambda z: (pk * z**ks).sum()
    g1 = lambda z: (ks[1:] * pk[1:] * z**(ks[1:] - 1)).sum() / mean_k
    u = 0.0                      # 从 0 迭代，收敛到最小不动点（非平凡解）
    for _ in range(n_iter):
        u = 1 - keep + keep * g1(u)
    return 1 - g0(u) if mode == "bond" else keep * (1 - g0(u))
```

### A.3 Newman–Ziff：一次得到整条渗流曲线（升级 2、修正 A）

```python
def newman_ziff(n_nodes, edges, removal_order):
    """
    edges:         [(a, b), ...]，节点编号为 0..n_nodes-1
    removal_order: 协议中的删除顺序（第一个最先被删）
    返回 largest[t]：保留 t 条边时的最大连通块大小（t = 0..E）
    """
    parent = list(range(n_nodes))
    size = [1] * n_nodes

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    largest, out = 1, [1]
    for idx in reversed(removal_order):     # 删除顺序倒过来 = 加边顺序
        a, b = find(edges[idx][0]), find(edges[idx][1])
        if a != b:
            if size[a] < size[b]:
                a, b = b, a
            parent[b] = a
            size[a] += size[b]
            largest = max(largest, size[a])
        out.append(largest)
    return np.array(out)    # 删除比例 f 对应 out[round((1 - f) * E)]
```

### A.4 L 跳检索：一次计算覆盖所有 L（升级 3）

```python
from scipy.sparse.csgraph import dijkstra, connected_components

def ppi_distance(A_ppi, targets, dis_proteins, max_ppi_hops=np.inf):
    """
    A_ppi:        当前损坏状态下 PPI 子图的稀疏邻接矩阵（CSR，蛋白重新编号）
    targets:      药物仍存活的靶点蛋白编号
    dis_proteins: 疾病仍存活的关联蛋白编号
    返回:         两组蛋白之间的最短 PPI 距离 d
                  查询在跳数上限 L 下成功  <=>  d <= L - 2
    """
    if len(targets) == 0 or len(dis_proteins) == 0:
        return np.inf
    if set(targets) & set(dis_proteins):
        return 0                                    # 共享蛋白，即 L = 2 成功
    d = dijkstra(A_ppi, directed=False, indices=list(targets),
                 unweighted=True, limit=max_ppi_hops, min_only=True)
    return d[list(dis_proteins)].min()

# L = ∞：每个损坏状态只算一次连通分量
# n_comp, labels = connected_components(A_ppi, directed=False)
# 成功 <=> set(labels[targets]) 与 set(labels[dis_proteins]) 有交集
```

---

## 参考文献

**数据**
- Chandak, P., Huang, K. & Zitnik, M. (2023). *Building a knowledge graph to enable precision medicine*. Scientific Data 10, 67.

**网络鲁棒性与渗流理论**
- Albert, R., Jeong, H. & Barabási, A.-L. (2000). *Error and attack tolerance of complex networks*. Nature 406, 378–382.
- Callaway, D. S., Newman, M. E. J., Strogatz, S. H. & Watts, D. J. (2000). *Network robustness and fragility: Percolation on random graphs*. Phys. Rev. Lett. 85, 5468.
- Cohen, R., Erez, K., ben-Avraham, D. & Havlin, S. (2001). *Breakdown of the Internet under intentional attack*. Phys. Rev. Lett. 86, 3682.
- Newman, M. E. J. & Ziff, R. M. (2000). *Efficient Monte Carlo algorithm and high-precision results for percolation*. Phys. Rev. Lett. 85, 4104.
- López, E., Buldyrev, S. V., Havlin, S. & Stanley, H. E. (2007). *Limited path percolation in complex networks*. Phys. Rev. Lett. 99, 188701.
- Newman, M. E. J. (2018). *Networks* (2nd ed.). Oxford University Press.（percolation 与 network resilience 章节）

**零模型与网络医学**
- Maslov, S. & Sneppen, K. (2002). *Specificity and stability in topology of protein networks*. Science 296, 910–913.
- Menche, J. et al. (2015). *Uncovering disease-disease relationships through the incomplete interactome*. Science 347, 1257601.
- Guney, E., Menche, J., Vidal, M. & Barabási, A.-L. (2016). *Network-based in silico drug efficacy screening*. Nature Communications 7, 10331.

**主题**
- Anderson, P. W. (1972). *More is different*. Science 177, 393–396.
