# G17 成员 C · WS3 交付

## 怎么跑

C 的新增内容已集成到仓库，拉取最新代码后，从仓库根目录运行即可。使用项目的 Python 3.11+ 环境和依赖文件；本次接入已在 Python 3.11.9 下通过测试。不要使用整份旧压缩包覆盖已有项目。

在 PowerShell 运行：

```powershell
python -B -m unittest discover -s tests -v
python -B -m src.run_ws3 primekg_5000_bfs_v1
python -B -m src.plot_ws3 primekg_5000_bfs_v1
```

第一条核对程序，第二条算实验，第三条出图。小图也可以用，把后两条命令里的 `5000` 换成 `2000`。图表脚本需要 A 已经生成的 `results/ws1/<gid>__random.csv`。如果你手里的副本缺这份表，先运行 `python -B -m src.run_ws1 <gid>`，将 `<gid>` 替换成实际图 ID。另一台电脑如果缺 Python 包，可在自己的 Python 3.11+ 环境中安装项目的 `requirements.txt`。

输入使用 A、B 已有的处理后数据和删除顺序。项目原副本里部分 JSON 文件的换行与冻结清单不同，旧的 `validate_data` 可能因此报哈希错。WS3 直接读取这些文件，并记录实际读到的输入哈希。

## 文件在哪里

- **给 D 的数据**在 `results/ws3`。每套图 1 份汇总表、22 份逐题表、1 份运行记录。汇总表按策略、种子和删减比例保存 R。逐题表以 `query_id` 与同图的 `queries.json` 对接。
- **给 E 的代码**在 `src/retrieval.py`。现有 WS5 会自动使用 `Retriever(gid).evaluate(..., compute_dist=True)`。正式复跑示例为 `python -B -m src.run_ws5 primekg_5000_bfs_v1 --output-dir results/ws5/c_retriever_run`。请选一个空的或尚未创建的结果目录。
- **四张图**在 `figures/act2/<gid>`，每张有 PNG、PDF、SVG。S–R 对照及分组图使用 10 个随机删边种子，跳数曲线和热图固定使用种子 0、1、2。
- **讲稿和问答**在 `slides/C_speaker_notes.md`。三页 PowerPoint 单独交付，可插入全组第 6–8 页。第 8 页同时使用跳数曲线和热图。
- **报告草稿**在 `report/C_section_5.md` 和 `report/C_individual_contribution_draft.md`。个人稿的姓名和个人贡献表述应按实际情况核对后提交。

## 逐题表怎么读

`s_alive` 是该药物和疾病仍然共享的蛋白数。两跳成功等价于 `s_alive > 0`。删掉药物或疾病本身时，这题仍留在分母里并计为失败。`d_ppi` 是两端蛋白之间的最短距离，`0` 表示共享同一蛋白，`inf` 表示已经算过且无路，空白表示这个实验状态只跑了两跳。跳数扫描的 45 个状态保存了实际距离。确定性攻击的种子值为 `-1`。

## 已验证的结果

- 24 项测试通过，包括 toy 与 2,000 节点图在随机删点、删边样例上的逐题核对。
- 5,000 节点图的两组曲线和独立边模型的最大差分别为 2.10 和 3.25 个百分点。2,000 节点图的单路径组最大差为 9.05 个百分点，超出计划中的 5 个百分点经验范围，逐题核对仍通过。
- 两套图都完成了四种破坏策略和跳数扫描。已用正式 C 接口验证 E 的四种修复策略。
