# PC5253 Group Project Proposal & Task Specification

## When AI Forgets: Percolation and Functional Robustness of Knowledge Graph Retrieval

**基于渗流理论的知识图谱结构与检索功能鲁棒性研究**

**Project Type:** Complex Networks / Knowledge Graphs  
**Dataset:** PrimeKG  
**Team Size:** 5  
**Core Methods:** Percolation Theory, Centrality, Network Robustness, Semantic Retrieval

---

## 1. Research Background and Objectives

Knowledge Graphs（KGs）将实体与语义关系组织成复杂网络，是 GraphRAG、知识检索及 AI for Science 系统的重要知识基础。

现实中的 KG 可能因为知识缺失、数据源故障或维护不完整而失去部分节点和关系。这些损坏不仅可能影响网络连通性，也可能影响下游 AI 检索特定知识的能力。

传统复杂网络理论通过 Giant Connected Component、Percolation 和 Centrality 衡量网络结构的可靠性。然而，网络仍然连通，并不代表所有语义检索任务仍然能够成功。

本项目以 PrimeKG 为研究对象，系统分析网络结构失效与知识检索功能失效之间的联系，并探索利用复杂网络方法提高知识检索鲁棒性的可能性。

### Research Questions

**RQ1 — Structural Robustness**

How do random and targeted failures affect the percolation behavior and structural robustness of PrimeKG?

**RQ2 — Functional Robustness**

Can classical network measures explain or predict the degradation of semantic knowledge retrieval?

**RQ3 — Network Intervention**

Can structural information guide more effective knowledge restoration under limited budgets?

---

## 2. Connection to PC5253

项目的理论核心是 Complex Networks、Percolation Theory、Centrality 和 Network Robustness。

| PC5253 Concepts | Application in This Project |
|---|---|
| Complex Network Topology | 分析 PrimeKG 的 Degree Distribution 和 Hub |
| Giant Connected Component | 测量网络损坏后的最大连通结构 |
| Percolation Theory | 研究节点和关系失效比例与网络结构变化的关系 |
| Critical Phenomena | 分析是否存在明显的快速失效区域 |
| Degree Centrality | 衡量实体的直接连接重要性 |
| Betweenness Centrality | 衡量实体的网络桥梁作用 |
| Network Robustness | 比较随机故障与针对性攻击 |
| Path Redundancy | 研究替代知识路径对功能可靠性的作用 |
| Network Intervention | 指导有限预算下的关键关系恢复 |

### Theoretical Framework

设知识图谱为：

\[
G=(V,E)
\]

对于边或节点的保留比例 \(p\)，定义：

**Structural Robustness**

\[
S(p)=\frac{|G_{\mathrm{largest}}(p)|}{|V_0|}
\]

其中 \(V_0\) 是原始节点集合。

**Functional Robustness**

\[
R(p)=\frac{N_{\mathrm{successful}}(p)}{N_{\mathrm{queries}}}
\]

其中 \(N_{\mathrm{successful}}\) 是损坏后仍能找到有效语义路径的查询数量。

通过比较 \(S(p)\) 与 \(R(p)\)，分析传统网络连通性指标能否反映 KG 的知识检索能力。

利用 Centrality、Path Redundancy 等指标进一步解释两类鲁棒性的差异。

---

## 3. Real-world Significance

### Knowledge Graph Reliability

真实 KG 存在关系缺失、知识更新不及时和数据源不完整等问题。

依赖知识图谱进行检索的 AI 系统可能因此失去有效的知识关联路径。

项目可以揭示不同知识损坏机制对 KG 检索能力的影响。

### Structural vs. Functional Reliability

传统网络指标衡量整体连通性，而知识检索通常需要特定类型的实体及关系。

因此，Structural Connectivity 不一定等同于 Semantic Retrieval Reliability。

理解二者的联系可以帮助判断哪些网络结构指标能够有效评估 KG 的功能可靠性。

### Knowledge Maintenance

知识图谱维护存在有限的人工、计算和数据处理预算。

识别关键关系并制定合理的恢复优先级，有助于减少知识缺失对下游检索任务的影响。

本项目通过模拟关系损坏与恢复，评价基于网络拓扑的维护策略。

---

## 4. Unified Dataset and Experimental Protocol

本节规定全组共同使用的数据、图构建方式、检索任务、随机性控制和评价方法。所有 Workstreams 使用同一套实验协议。

### 4.1 Dataset Source

**Dataset Name:** PrimeKG — Precision Medicine Knowledge Graph

**Official Repository**

https://github.com/mims-harvard/PrimeKG

**Harvard Dataverse**

https://doi.org/10.7910/DVN/IXA7BM

**Fixed Data File**

`kg.csv`

**Direct Download**

https://dataverse.harvard.edu/api/access/datafile/6180620

**Reference**

Chandak, P., Huang, K., & Zitnik, M. (2023). *Building a knowledge graph to enable precision medicine*. Scientific Data.

### 4.2 Data Schema

使用 PrimeKG 原始数据中的以下字段：

| Field | Meaning |
|---|---|
| `x_index` | 起点节点 ID |
| `y_index` | 终点节点 ID |
| `x_type` | 起点实体类型 |
| `y_type` | 终点实体类型 |
| `x_name` | 起点名称 |
| `y_name` | 终点名称 |
| `relation` | 关系类别 |
| `display_relation` | 用于展示的关系标签 |

`x_index`、`y_index` 作为节点唯一标识，不使用实体名称代替 ID。

### 4.3 Graph Scope

统一选取三种实体类型：

- `drug`
- `disease`
- `gene/protein`

统一保留三种关系：

- `drug_protein`
- `disease_protein`
- `protein_protein`

该图谱能够支持药物—蛋白质—疾病的知识关联检索，同时包含足够的网络结构供中心性与渗流分析使用。

### 4.4 Graph Construction Rules

所有实验遵循以下处理标准：

1. 从固定 `kg.csv` 读取数据。
2. 仅保留上述三种节点类型和三种关系类型。
3. 使用 `x_index` 和 `y_index` 作为节点标识。
4. 保留关系类型信息。
5. 将相同节点对、相同关系类型的反向存储记录规范化为一条无向语义关联边。
6. 删除完全重复的关系及自环。
7. 不将原始 CSV 的 X/Y 存储方向解释为医学因果关系。
8. 不添加不存在于原始 PrimeKG 的新关系。

统一使用两种图表示：

**Structural Graph**

`networkx.Graph`

用于 Degree、GCC、Centrality、Percolation 等复杂网络分析。同一对节点之间的多种关系在结构投影中视为一条连接。

**Semantic Graph**

保留每条规范化关系的节点对和 `relation` 标签，用于语义路径检索。

删除某个语义关系时，同步更新对应的结构图；如果同一节点对仍存在其他保留关系，则结构连接仍然存在。

### 4.5 Unified Subgraph Sampling

标准实验采用包含 5,000 个节点的 PrimeKG 子图。

统一采样方法：

**Deterministic Breadth-First Sampling**

1. 从过滤后的三类实体、三类关系构建完整候选网络。
2. 计算候选网络中所有 Disease 节点的 Degree。
3. 选择 Degree 最高的 Disease 节点作为 BFS 起点；并列时取最小 `x_index`。
4. 按节点 ID 升序访问邻居，进行 BFS。
5. 保留前 5,000 个不同节点。
6. 保留原始候选网络中这 5,000 个节点之间的全部符合条件的关系，形成 Induced Subgraph。
7. 对所得子图统一规范化关系和节点排序。

**Standard Graph ID:** `primekg_5000_bfs_v1`

**Sampling Seed:** `42`（涉及随机操作时使用）。

另外使用 `primekg_2000_bfs_v1` 作为小规模验证集，方法一致，但只保留前 2,000 个节点。

两个图谱使用同样的节点访问顺序，保证小图是大图的前缀节点集合。

所有成员使用相同的采样代码规则和固定原始数据文件。

标准图构建完成后记录节点数、结构边数、语义关系数、各类实体数量和关系数量，并计算文件 SHA-256，以便校验数据一致性。

### 4.6 Unified Retrieval Task

**Task:** Drug–Protein–Disease Relation Retrieval

给定一个 Drug 和一个 Disease，检索是否存在符合以下关系约束的两跳路径：

`Drug — drug_protein — Gene/Protein — disease_protein — Disease`

这条路径表示药物与疾病通过共同关联的基因或蛋白质形成知识关联，不代表药物具有被证实的治疗效果。

**Query Definition**

```json
{
  "query_id": 1,
  "drug_id": 123,
  "disease_id": 456,
  "relation_pattern": [
    "drug_protein",
    "disease_protein"
  ],
  "max_hops": 2
}
```

`drug_id` 和 `disease_id` 为格式示例，实际 ID 从 PrimeKG 中获取。

**Query Generation**

1. 从完整标准子图中寻找所有满足上述关系模式的 Drug–Disease 节点对。
2. 按不同中间 Gene/Protein 的数量计算 Path Redundancy。
3. 将查询分成两组：只有 1 条有效中间蛋白路径的查询，以及至少 2 条不同中间蛋白路径的查询。
4. 每组按 `(drug_id, disease_id)` 排序后，以随机种子 42 进行固定抽样。
5. 每组目标 100 个查询，总目标 200 个。
6. 如果某组不足 100 个，保留该组全部有效查询，记录实际数量，不使用重复查询补足。

**Fixed Dataset:** `queries_v1.json`

原始完整标准子图中，所有选定查询必须能够成功。

检索成功条件：损坏后仍存在至少一条满足上述关系模式的两跳路径。

同一查询可以拥有多条有效替代路径。查询节点被删除时，按检索失败处理。

### 4.7 Unified Failure Settings

**Edge Removal Levels**

`0%, 5%, 10%, 20%, 30%, 40%, 50%, 60%, 70%, 80%`

**Node Removal Levels**

`0%, 5%, 10%, 20%, 30%, 40%, 50%`

**Random Seeds**

`0, 1, 2, 3, 4, 5, 6, 7, 8, 9`

**Failure Models**

- Random Edge Removal。
- Random Node Removal。
- High-degree Node Removal。
- High-betweenness Node Removal。

删除比例以原始规范化实体关系数或节点数作为分母。

同一删除策略下，逐步损坏实验使用固定删除顺序的前缀，形成嵌套的损坏状态。

Targeted Removal 使用原始图上的中心性排序，并列时按节点 ID 升序处理。

中心性采用：

- Degree：原始结构图中的节点度。
- Betweenness：使用 NetworkX 的采样近似算法，`k=100, seed=42, normalized=True`，原始图上计算一次。

对于节点删除，所有相连语义关系随节点一起移除。

对于边删除，删除单位是规范化后的语义关系，不是 CSV 中的重复存储行。

不同故障策略分别报告损坏比例、节点损失和关系损失，保证解释公平。

### 4.8 Unified Metrics

**Structural Metrics**

- Giant Component Fraction。
- Number of Connected Components。
- Average Degree。
- Fraction of Isolated Nodes。

**Functional Metrics**

- Retrieval Success Rate。
- Query Path Redundancy。
- Successful Query Fraction by Redundancy Group。

**Comparison Metrics**

- Structural–Functional Robustness Gap。
- Performance Drop under Equal Damage Budget。
- Restoration Gain under Equal Edge Budget。

曲线使用多随机种子的均值，并标注标准差或置信区间。对于完全确定的针对性攻击，报告单条确定性轨迹，不人为制造随机误差。

---

## 5. Five Parallel Research Workstreams

五个 Workstreams 分别围绕一个独立的科学问题开展实验，均使用 Section 4 中规定的 PrimeKG 数据与标准实验协议。

每条研究线包含完整的实验实现、评价、结果分析及课程理论解释。

### Workstream 1 — Percolation and Random Network Failure

**Research Question**

How robust is PrimeKG against random node and edge failures?

**PC5253 Topics**

Percolation Theory, Giant Connected Component, Degree Distribution, Network Robustness.

**Tasks**

1. 根据统一协议构建标准结构图。
2. 分析节点 Degree Distribution 和原始 GCC。
3. 实现 Random Node Removal 与 Random Edge Removal。
4. 在统一删除比例下模拟网络损坏。
5. 测量不同损坏程度下的 Giant Component 和连通分量数量。
6. 分析随机节点失效和关系失效之间的差异。

**Expected Deliverables**

- Degree Distribution Plot。
- Random Node Percolation Curve。
- Random Edge Percolation Curve。
- Network Fragmentation Analysis。

**Core Contribution**

从渗流理论角度描述 PrimeKG 在随机知识损失条件下的结构鲁棒性。

### Workstream 2 — Centrality and Targeted Failure

**Research Question**

Do structurally important entities cause disproportionately large damage when removed?

**PC5253 Topics**

Degree Centrality, Betweenness Centrality, Hub Structure, Targeted Attack.

**Tasks**

1. 根据统一协议构建标准结构图。
2. 计算 Degree 和近似 Betweenness Centrality。
3. 对节点进行中心性排序。
4. 实现 High-degree Node Removal。
5. 实现 High-betweenness Node Removal。
6. 与 Random Node Removal 进行对照。
7. 分析关键节点失效对网络连通性的影响。

**Expected Deliverables**

- Centrality Distribution。
- Random vs. High-degree Attack Curve。
- Random vs. High-betweenness Attack Curve。
- Critical Node Analysis。

**Core Contribution**

评价不同中心性指标对网络关键节点的识别能力，解释网络拓扑如何影响鲁棒性。

### Workstream 3 — Structural vs. Functional Robustness

**Research Question**

Does network connectivity reliably indicate semantic retrieval reliability?

**PC5253 Topics**

Percolation, Reachability, Path Redundancy, Network Functionality.

**Tasks**

1. 根据统一协议构建标准语义图与结构图。
2. 使用固定 Drug–Protein–Disease 查询任务。
3. 实现两跳语义路径检索器。
4. 按统一 Random Edge Removal 设置模拟损坏。
5. 测量 Retrieval Success Rate。
6. 同时测量 Giant Component Fraction。
7. 比较两条失效曲线并分析路径冗余的影响。

**Expected Deliverables**

- Semantic Retrieval Evaluation。
- Retrieval Success Rate Curve。
- Giant Component vs. Retrieval Success Comparison。
- Low-redundancy vs. High-redundancy Query Analysis。

**Core Contribution**

研究 KG 的结构性连通与语义检索能力之间的关系，揭示传统连通性指标的适用边界。

### Workstream 4 — Structural Prediction of Retrieval Failure

**Research Question**

Which network indicators best explain and predict semantic retrieval degradation?

**PC5253 Topics**

Network Topology, Centrality, Path Redundancy, Reliability.

**Tasks**

1. 根据统一协议构建标准图谱与查询集。
2. 在统一损坏配置下产生结构与检索指标。
3. 计算 GCC、平均度、连通性等结构特征。
4. 计算查询相关 Path Redundancy。
5. 使用 Pearson / Spearman Correlation 分析指标关系。
6. 建立简单线性回归模型。
7. 比较全局结构指标与任务相关指标的预测表现。

按随机种子对应的完整损坏轨迹划分训练和测试，例如训练种子 `0–6`，测试种子 `7–9`；固定划分避免重复轨迹泄漏。

**Expected Deliverables**

- Structural Feature Analysis。
- Correlation Matrix。
- Prediction Comparison。
- MAE / RMSE Results。

**Core Contribution**

评价复杂网络指标能否作为知识检索可靠性的预测信号。

### Workstream 5 — Network-informed Restoration

**Research Question**

Can network topology improve knowledge restoration efficiency under limited budgets?

**PC5253 Topics**

Network Intervention, Centrality, Robustness Optimization.

**Tasks**

1. 根据统一协议构建标准图谱与查询集。
2. 以 30%、50% 的 Random Edge Removal 作为主要损坏场景。
3. 实现 Random Edge Restoration。
4. 实现 Centrality-based Edge Restoration。
5. 实现基于训练查询的 Task-aware Restoration。
6. 比较不同恢复预算下的 GCC 与 Retrieval Success。
7. 分析全局结构重要性与任务重要性之间的差异。

**Restoration Budgets**

恢复被删除语义关系的：

`5%, 10%, 20%`

Centrality-based 策略按原始结构图中的 Edge Betweenness 排序，允许通过近似方法控制计算开销。

Task-aware 策略根据训练查询涉及的关系和有效路径冗余评估边的重要性。

固定查询集通过 `query_id` 按种子 42 随机划分 70% 训练查询、30% 测试查询。策略仅利用训练查询决定优先级，在测试查询上报告收益。

**Expected Deliverables**

- Restoration Performance Curves。
- Random vs. Centrality-based Restoration。
- Random vs. Task-aware Restoration。
- Performance Improvement per Restored Edge。

**Core Contribution**

检验复杂网络结构信息是否能够指导有限预算下的知识恢复，提高功能鲁棒性。

---

## 6. Computational Cost and Implementation

### 6.1 Recommended Environment

| Component | Configuration |
|---|---|
| Language | Python 3.11 |
| Graph Analysis | NetworkX |
| Data Processing | Pandas / NumPy |
| Statistical Analysis | SciPy / Scikit-learn |
| Visualization | Matplotlib |
| CPU | 4–8 cores recommended |
| RAM | 16 GB recommended |
| GPU | Not required |

### 6.2 Estimated Cost

| Operation | Relative Cost |
|---|---|
| Data Filtering and Graph Construction | Low |
| Degree / GCC | Low |
| Random Percolation | Low–Medium |
| Approximate Betweenness | Medium |
| Semantic Two-hop Retrieval | Low–Medium |
| Correlation / Linear Regression | Low |
| Restoration Experiments | Medium |

主要计算瓶颈是 Centrality 的重复计算和大量路径搜索。

为控制开销：

- 标准图控制在 5,000 节点。
- 使用近似 Betweenness。
- 使用固定随机种子。
- 缓存重复实验结果。
- 检索时使用关系过滤和局部邻接索引。
- 不在每一次删除或恢复操作后重新计算全部中心性。

第一轮使用 2,000 节点进行验证，再扩展到 5,000 节点。

各 Workstream 的批量实验以 CPU 为主，预计无需额外 GPU 费用。实际运行时间通过第一次 Benchmark 确认。

---

## 7. Research Challenges

### Dataset Sampling Bias

BFS 子图可能过度代表高连接区域，导致 Degree Distribution 和 Percolation Behavior 与完整 PrimeKG 不完全一致。

记录子图与候选网络的基本统计，解释结论的适用范围。

### Semantic Retrieval Validity

两跳语义检索只是 GraphRAG 的检索阶段近似，不等同于完整 LLM 问答能力。

使用固定关系模式及多路径查询，提高功能评价的实际意义。

### Structural–Functional Relationship

知识丢失造成检索失败属于预期现象。

研究重点是不同损坏策略、路径冗余和结构指标之间的差异，而不仅是检索成功率下降。

### Centrality Computation

精确 Betweenness 可能产生较高计算开销。

统一使用近似 Betweenness 作为主要实验设置。

### Percolation Threshold

有限规模 KG 未必出现明确的渗流临界点。

通过完整曲线描述网络退化过程，对临界现象采取谨慎解释。

### Intervention Validity

任意新增边可能产生错误的生物医学关系。

恢复实验只从原始 KG 已存在、但被模拟删除的真实关系中选择。

### Reproducibility

所有实验固定数据来源、子图构建规则、查询生成方法、参数、随机种子和评价指标。

不同工作包的主要结果必须可以从统一协议复现。

---

## 8. Integration and Final Presentation

五项工作共同构成以下研究逻辑：

| Workstream | Scientific Question | Main PC5253 Connection |
|---|---|---|
| 1. Random Failure | 网络如何随知识丢失而碎裂？ | Percolation |
| 2. Targeted Failure | 为什么关键节点造成更大影响？ | Centrality |
| 3. Functional Failure | 连通性是否等于检索可靠性？ | Structural–Functional Robustness |
| 4. Prediction | 网络指标能否预测检索失效？ | Network Reliability |
| 5. Restoration | 能否利用网络理论提高鲁棒性？ | Network Intervention |

### Suggested 15-minute Presentation

1. Motivation and Research Questions — 2 min
2. PrimeKG and Complex Network Theory — 2 min
3. Random and Targeted Percolation — 3 min
4. Structural vs. Functional Robustness — 3 min
5. Prediction and Network Intervention — 3 min
6. Conclusions and Limitations — 2 min

---

## 9. Feasibility and Expected Contributions

| Dimension | Assessment |
|---|---|
| PC5253 Alignment | High |
| Real-world Relevance | Medium–High |
| Dataset Availability | High |
| Computational Cost | Low–Medium |
| Implementation Difficulty | Medium |
| Parallel Work Feasibility | High |
| Scientific Uncertainty | Medium |

### Expected Contributions

1. 描述 PrimeKG 在不同失效机制下的网络渗流行为。
2. 分析结构连通性与语义检索能力之间的关系。
3. 评价中心性和路径冗余对检索鲁棒性的解释能力。
4. 探索基于网络结构的关系恢复策略。

### Central Research Question

**Can classical percolation theory and network centrality explain, predict, and improve the functional robustness of knowledge graph retrieval?**

本项目利用 PrimeKG 这一真实生物医学知识网络，将 PC5253 中的 Percolation、Centrality 和 Network Robustness 理论应用于 AI 检索可靠性问题，形成从网络结构、故障机制、功能评价到干预改进的完整研究框架。