# C 交付接入记录（2026-11-04）

来源：成员提供的 pc5253-g17-primekg-main.zip。
只导入 C 的新文件，不使用整个压缩包覆盖仓库。

## 导入范围

- src/retrieval.py、src/run_ws3.py、src/plot_ws3.py。
- tests/test_retrieval.py、C_README.md。
- results/ws3 下两个图的汇总表、逐查询表、运行记录。
- figures/act2 下两个图的四类 PNG/PDF/SVG。
- slides/C_WS3_slides_6-8.pptx、slides/C_speaker_notes.md。
- report/C_section_5.md、report/C_individual_contribution_draft.md。

共导入 81 个 C 文件。没有导入 .idea 配置、补充参考重复文件，
也没有覆盖压缩包中较旧的 E_HANDOFF.md 和 plot_ws5.py。
Python 和 Markdown 文件规范为 UTF-8 / LF；结果和已有附件保持原交付内容。
C_README 的整包覆盖说明改为仓库内运行说明。
E 绘图标题按实际策略数显示，防止四策略结果仍出现旧的三策略标签。

## 检查结果

1. 仓库完整测试通过：24 项。
2. 两个图的全部 C 逐查询表可复算对应汇总指标，未发现重复指标行、非有限成功率或分组汇总不一致。
3. 2 跳路径计数与 d_ppi=0 的对应关系通过核对；距离未计算与不可达分别保留为空白和 inf。
4. 查看了主图四种可视化，无明显遮挡或裁切。C 的 PPTX 可读取且包含三页。
5. 使用默认 evaluator=c 的 E 正式接口，在 2000/5000 节点图各运行 320 个四策略/预算状态。
   逐查询的 s_alive、L2/L3 成功指示及全部恢复指标，与 E 先前的独立评估结果一致，浮点容差 1e-12。
6. E 接入核对运行保存在本地 .build/c_review/ws5，属于验证产物；原有实验目录未被覆盖。

检查没有要求修改 C 的检索算法。图表保持其交付的实验结果，不使用演示数值替换。
较小开发图的单路径模型偏差已由 C 在说明和报告中如实记录，不作为代码错误强行消除。

## 使用

```powershell
python -m unittest discover -s tests -v
python -m src.run_ws3 primekg_5000_bfs_v1
python -m src.plot_ws3 primekg_5000_bfs_v1

# 选择新的空目录，E 会默认调用 C 的 Retriever 和全部四种恢复策略。
python -m src.run_ws5 primekg_5000_bfs_v1 --output-dir results/ws5/NEW_C_RETRIEVER_RUN
python -m src.plot_ws5 results/ws5/NEW_C_RETRIEVER_RUN --output-dir figures/act3/NEW_C_RETRIEVER_RUN
```

当前 C 接口已可供 E 和 D 使用。D 的最终 theory.py / prediction.py 尚未包含在此交付中。
C 的个人贡献文件保持草稿性质，姓名等仍需本人完成后提交。
全组工作版 PPT 尚需把 C 的三页与最新恢复图正式整合。
