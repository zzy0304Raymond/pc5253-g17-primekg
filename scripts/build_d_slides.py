"""Insert D's slides 9-11 and backups into the group deck, and write D's notes.

Run from the repository root: python scripts/build_d_slides.py
Writes slides/G17_working_draft_with_D.pptx, slides/D_slides_9-11.pptx and
slides/D_speaker_notes.md. The input working draft is left unchanged.
"""
import copy
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
GID = "primekg_5000_bfs_v1"
ACT1, ACT2 = ROOT / "figures/act1" / GID, ROOT / "figures/act2" / GID
INK, MUTED, BLUE, PURPLE, RED = "333333", "666666", "3B8DB5", "9472C4", "D62728"


def rgb(value):
    return RGBColor.from_string(value)


def add_runs(paragraph, parts, size, color, bold=False):
    """parts is a string or a list of strings and (text, baseline) pairs."""
    for part in [parts] if isinstance(parts, str) else parts:
        text, baseline = (part, None) if isinstance(part, str) else part
        run = paragraph.add_run()
        run.text = text
        run.font.name = "Arial"
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = rgb(color)
        if baseline:
            run.font._element.set("baseline", str(baseline))


def text(slide, x, y, w, h, parts, size, color=INK, bold=False, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.word_wrap = True
    frame.vertical_anchor = anchor
    frame.margin_left = frame.margin_right = frame.margin_top = frame.margin_bottom = 0
    add_runs(frame.paragraphs[0], parts, size, color, bold)
    return box


def stat(slide, x, y, w, value, label, color, value_size=32, label_size=15, label_h=.8):
    text(slide, x, y, w, .6, value, value_size, color, bold=True)
    text(slide, x, y + value_size / 72 + .14, w, label_h, label, label_size)


def picture(slide, path, x, y, w, h, alt):
    with Image.open(path) as image:
        ratio = image.width / image.height
    width, height = (w, w / ratio) if w / ratio <= h else (h * ratio, h)
    pic = slide.shapes.add_picture(str(path), Inches(x + (w - width) / 2), Inches(y + (h - height) / 2),
                                   Inches(width), Inches(height))
    pic._element.nvPicPr.cNvPr.set("descr", alt)
    return pic


def clear_body(slide):
    for shape in list(slide.shapes)[2:]:
        shape._element.getparent().remove(shape._element)


def set_text(shape, value):
    runs = [run for paragraph in shape.text_frame.paragraphs for run in paragraph.runs]
    runs[0].text = value
    for run in runs[1:]:
        run.text = ""


def table(slide, x, y, widths, rows, size=13, row_h=.46):
    shape = slide.shapes.add_table(len(rows), len(widths), Inches(x), Inches(y),
                                   Inches(sum(widths)), Inches(row_h * len(rows)))
    grid = shape.table
    style = grid._tbl.tblPr
    style.set("bandRow", "0")
    style.set("firstRow", "0")
    for col, width in enumerate(widths):
        grid.columns[col].width = Inches(width)
    for r, row in enumerate(rows):
        grid.rows[r].height = Inches(row_h)
        for c, value in enumerate(row):
            cell = grid.cell(r, c)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.margin_left = cell.margin_right = Inches(.08)
            cell.fill.solid()
            cell.fill.fore_color.rgb = rgb("EEF1F5" if r == 0 else "FFFFFF")
            add_runs(cell.text_frame.paragraphs[0], value, size, INK, bold=r == 0)
    return shape


NOTES = {
    9: """Why do the curves on the last slides look the way they do? A two-hop query with m shared proteins has m routes. Each route needs two edges, so it survives with probability p squared. Routes through different proteins share no edge, so they fail independently. The query fails only if all m routes fail. Averaging over the query set gives one line: R equals one minus G of one minus p squared, where G is the generating function of path counts. There are no fitted parameters. The dashed lines match both query groups, and over five thousand fresh damage orders the difference is below 0.001. A logistic regression with degree features does no better at predicting which query fails.""",
    10: """That formula assumes damage ignores the graph. A targeted attack does not. This plot shows the gap between the random-removal formula and measured success under attack. Removing the top five percent of nodes by degree leaves 30 percent of queries working, while the formula predicts 88 percent. That is a penalty of 57 points. It has two channels. About 17 points come from lost endpoints, mostly hub diseases. About 40 come from lost paths, because query paths run through hubs: the median path protein has degree 188, against 25 for all proteins. So path count is not effective redundancy: 53 percent of multi-path queries fail. The giant component hides this: compared with random removal it falls 7 points, while retrieval falls 56.""",
    11: """Finally, the hop limit. We have two analytic limits. At L equals two, retrieval is local, and our formula applies. At L equals infinity, a query only needs both endpoints to reach the protein–protein giant component. Generating functions give that probability with no fit, and it matches the mean over 600 fresh damage orders to within 0.01. In between, each extra hop delays the damage at which the limit matters: about ten, fifty and eighty-five percent edge loss for two, three and four hops. We expected a sharp percolation collapse at L infinity, and we did not see one. The protein giant component still holds 75 percent of proteins at 90 percent edge loss. Up to that point, over 90 percent of L-infinity failures are drugs that have lost every target. So on this benchmark, longer horizons move the bottleneck from shared proteins to the drug's own target links.""",
}

QA = [
    ("Why are the routes independent?",
     "Two routes through different proteins use four different edges, and every node pair carries one relation (pairs_with_multiple_relations = 0). Removing a fixed number of edges adds only an O(1/E) correction."),
    ("Why does the simulation sit a little above the dashed line at 30–50% damage?",
     "Sampling. The seed SD is about 0.05 and the ten seeds are nested across damage levels, so one offset persists along a curve. The mean over 5,000 fresh orders is within 0.001 of the formula."),
    ("Why is the per-query AUC only 0.72?",
     "That is close to the ceiling. If the formula is true, failure is still random given m, and the expected AUC is 0.72 at 30% and 0.71 at 50% damage. Formula and regression both reach it."),
    ("Why is there no phase transition at L = 2?",
     "Each query depends on a fixed handful of edges, so R(p) stays the same smooth function as the graph grows. A giant component depends on an unbounded number of edges, which is why it can become singular as N → ∞."),
    ("Why no sharp collapse at L = ∞?",
     "The PPI network is hub-heavy. The Molloy–Reed estimate is p_c = ⟨k⟩/(⟨k²⟩ − ⟨k⟩) ≈ 0.006, or 0.0054 on the filtered full graph. Our scan stops at p = 0.01, so we did not measure the threshold itself. Drug links fail long before that: at p = 0.01 only 8% of queries keep a terminal link at both ends, whatever the PPI network does."),
    ("Is the drug bottleneck a sampling artefact?",
     "It is specific to this benchmark, so we do not generalise it. The BFS graph keeps 78% of its drugs' target links, yet the median query drug has 2 targets in both the BFS graph and the full graph. Also, 31.5% of queries use a drug with at most three targets."),
    ("GF assumes a configuration model. Why use it on a real graph?",
     "Because the difference is informative. On stub-matched graphs with the same degrees, our code agrees with simulation to about 0.001. On the real PPI network the gap stays within 0.009 up to f = 0.97 and reaches 0.020 at f = 0.99. For the degree attack, theory sits up to 0.11 above simulation below f ≈ 0.58, so the real graph is more fragile there; above that a small remnant survives where theory gives zero. Our null-model test of the cause is planned for the report."),
    ("How unique is the 17 + 40 split?",
     "R is a product of an endpoint factor and a path factor, so a sequential split depends on which factor changes first. We average both orders: Δ = (φ² − E)(C_th + C)/2 + (C_th − C)(φ² + E)/2. At 5% degree attack, endpoints give 11–24 points and paths 34–46, depending on order."),
    ("Why do slides 8 and 11 differ slightly?",
     "Slide 8 uses seeds 0–2, and the heatmap on slide 11 uses all ten. Damage-order noise is visible at this size: L = 3 at 50% loss is 84.5% with three seeds, 81.9% with ten, and 79.2% over 600 fresh orders."),
    ("Does the logistic regression beat theory under attack?",
     "Yes. At a 5% degree attack the AUC is 0.88 against 0.66 in cross-validation over queries, and 0.83 when folds are split by drug. Treat it as exploratory: the features include the degree that defines the attack."),
]

CHINESE = {
    9: "把一个查询想成 m 根并联的“保险丝”，每根由两条边串联。串联存活 p²，并联全断 (1 − p²)^m，对查询集取平均就是 PGF。这和课上求 giant component 是同一个工具，但这里没有自洽方程，因为路径之间互不共享边。",
    10: "公式假设破坏是“盲”的。攻击专挑 hub，而查询恰好挂在 hub 上，因为一个蛋白要同时连到药物和疾病，天然偏向高度节点。R 可以写成“端点存活 × 路径存活”，所以损失分成两路，17 和 40 是两种拆分顺序的平均。",
    11: "原先预期 L = ∞ 会在渗流阈值附近塌缩，数据不支持。PPI 骨架极其耐打，先断的主要是药物到靶点的那几条边，因为查询里的药物靶点很少。所以结论应说这个查询集上瓶颈转移，不要说出现了相变；0.006 只是 Molloy–Reed 估计，我们没有测到阈值本身。",
}


def fill_slide_9(slide):
    set_text(slide.shapes[0], "One formula predicts two-hop retrieval")
    clear_body(slide)
    picture(slide, ACT2 / "fig_R_theory_vs_sim.png", .58, 1.5, 7.9, 4.6,
            "Single-path and multi-path retrieval success against fraction removed. Simulation follows the dashed formula in both panels.")
    x, w = 8.85, 3.95
    text(slide, x, 1.55, w, .5, ["R(p) = 1 − G(1 − p", ("2", 30000), ")"], 25, BLUE, bold=True)
    text(slide, x, 2.1, w, .35, ["G(z) = Σ P(m) z", ("m", 30000), ", m = paths per query"], 14, MUTED)
    stat(slide, x, 2.68, w, "0", "fitted parameters", PURPLE, label_h=.3)
    stat(slide, x, 3.66, w, "< 0.001", "gap to the mean of 5,000 fresh damage orders", PURPLE, label_h=.55)
    stat(slide, x, 4.9, w, "0.72 vs 0.71", "per-query AUC at 50% loss: formula vs logistic regression", PURPLE, label_h=.55)
    text(slide, .73, 6.35, 11.9, .4, "Ten-seed mean ± SD. The dashed formula is not fitted to these data.", 16.5, MUTED)
    slide.notes_slide.notes_text_frame.text = NOTES[9] + "\n\nSource: results/ws4/primekg_5000_bfs_v1__theory.csv, __monte_carlo_check.csv, __prediction.csv."


def fill_slide_10(slide):
    set_text(slide.shapes[0], "Targeted attacks break independence")
    clear_body(slide)
    picture(slide, ACT2 / "fig_corr_penalty.png", .5, 1.5, 4.7, 4.6,
            "Gap between the random-removal formula and measured retrieval under degree and betweenness attacks. It peaks near 60 percentage points at 5 to 10 percent removal.")
    picture(slide, ACT2 / "fig_corr_channels.png", 5.25, 1.5, 4.5, 4.6,
            "Stacked bars splitting the penalty into lost endpoints and lost paths for both attacks at 5 and 10 percent removal.")
    x, w = 10.05, 2.75
    stat(slide, x, 1.6, w, "57 pp", "above the formula after a 5% degree attack", RED, label_h=.55)
    stat(slide, x, 3.0, w, "188 vs 25", "median degree: per query path vs all proteins", RED, 28, label_h=.8)
    stat(slide, x, 4.45, w, "53%", "of multi-path queries fail; only 22% lose every shared protein", RED, label_h=.85)
    text(slide, .73, 6.35, 11.9, .4, "At 5% node loss, the degree attack costs 7 pp more GCC than random removal, but 56 pp more retrieval.", 16.5, MUTED)
    slide.notes_slide.notes_text_frame.text = NOTES[10] + "\n\nSource: results/ws4/primekg_5000_bfs_v1__corr_penalty.csv, __provenance.json, __equal_damage_summary.csv. The split averages both orders of the two factors. 188 is per query path; the median over the 133 unique proteins is 106."


def fill_slide_11(slide):
    set_text(slide.shapes[0], "Longer horizons move the bottleneck")
    clear_body(slide)
    picture(slide, ACT2 / "fig_phase_diagram.png", .55, 1.5, 8.75, 4.6,
            "Heatmap of retrieval success by edge survival and hop limit, with panels comparing the L = 2 and L = infinity theory limits with simulation.")
    x, w = 9.6, 3.2
    stat(slide, x, 1.7, w, "10 → 50 → 85%", "edge loss where L = 2, 3, 4 first fall 5 pp below L = ∞", PURPLE, 25, label_h=.8)
    stat(slide, x, 3.55, w, "> 90%", "of L = ∞ failures, up to 90% edge loss, are a drug with no surviving target", PURPLE, label_h=1.1)
    text(slide, .73, 6.35, 11.9, .4, ["PPI giant at 90% edge loss: 75.0% simulated, 75.1% GF. Molloy–Reed p", ("c", -25000), " ≈ 0.006. Markers use 600 fresh orders."], 16.5, MUTED)
    slide.notes_slide.notes_text_frame.text = NOTES[11] + "\n\nSource: results/ws4/primekg_5000_bfs_v1__hop_scan_10seeds.csv, __theory.csv, __hop_boundary.csv, __hop_fresh_orders.csv. The heatmap uses all ten seeds; slide 8 uses seeds 0–2. The 5 pp marker is a display choice, not a phase boundary. p_c is an estimate: the scan stops at p = 0.01."


def update_structural_slides(slides):
    slide4, slide5 = slides[3], slides[4]
    frame = slide4.notes_slide.notes_text_frame
    frame.text = frame.text.replace("Black dashed GF is A’s configuration-model reference pending D’s final implementation.",
                                    "Black dashed GF is the configuration-model prediction; D's theory.py reproduces A's curve to within 1e-12.")
    old = [s for s in slide5.shapes if s.shape_type == 13][0]
    box = old.left, old.top, old.width, old.height
    new = picture(slide5, ACT1 / "fig_attack_theory.png", box[0] / 914400, box[1] / 914400, box[2] / 914400, box[3] / 914400,
                  "Largest component fraction under random removal and two attacks, with the Callaway degree-attack theory as a dashed line.")
    old._element.addprevious(new._element)
    old._element.getparent().remove(old._element)
    frame = slide5.notes_slide.notes_text_frame
    frame.text = frame.text.replace("D’s degree-attack theory overlay remains pending.",
                                    "The dashed line is the Callaway degree-attack theory. It sits up to 11 points above the measured curve for f below about 0.58, so the real graph is more fragile there than its degree sequence alone implies.")


def update_conclusion_note(slide):
    frame = slide.notes_slide.notes_text_frame
    value = frame.text.replace("D's theory pages still need integration before the complete group presentation\nand the fourteen-minute rehearsal can be finalized.\n", "")
    frame.text = value.replace(" Full-group theory narrative awaits D.", "")


def backup(prs, source, title, footer):
    slide = prs.slides.add_slide(source.slide_layout)
    for shape in list(slide.shapes):
        shape._element.getparent().remove(shape._element)
    background = source._element.cSld.find("{http://schemas.openxmlformats.org/presentationml/2006/main}bg")
    if background is not None:
        slide._element.cSld.insert(0, copy.deepcopy(background))
    for shape in list(source.shapes)[:2]:
        slide.shapes._spTree.append(copy.deepcopy(shape._element))
    set_text(slide.shapes[0], title)
    set_text(slide.shapes[1], footer)
    return slide


def add_backups(prs, source):
    one = backup(prs, source, "Backup: predicting which query fails", "D / B1")
    picture(one, ACT2 / "fig_prediction.png", .55, 1.5, 5.6, 4.5,
            "AUC and Brier score for the formula and logistic regression at 30 and 50 percent random edge removal.")
    table(one, 6.35, 1.9, [2.2, .98, .98, .98, .98],
          [["Damage", "AUC formula", "AUC logistic", "Brier formula", "Brier logistic"],
           ["Random edges, 30%", "0.713", "0.712", "0.186", "0.186"],
           ["Random edges, 50%", "0.720", "0.712", "0.204", "0.204"],
           ["Degree attack, 5%", "0.658", "0.884", "0.535", "0.138"],
           ["Betweenness, 5%", "0.686", "0.874", "0.585", "0.129"]], row_h=.66)
    text(one, .73, 6.35, 11.9, .4, "Random: test seeds 7–9. Attacks: 5-fold CV over queries, exploratory; degree-attack AUC is 0.83 with folds split by drug.", 16.5, MUTED)
    one.notes_slide.notes_text_frame.text = "Under random damage the formula sits at the AUC ceiling of about 0.72, so degree features add nothing. Under attack, degree features help a great deal, but they include the quantity that defines the attack, so this is exploratory. Source: results/ws4/primekg_5000_bfs_v1__prediction_detail.csv."
    two = backup(prs, source, "Backup: how the theory was checked", "D / B2")
    picture(two, ACT2 / "fig_ppi_giant.png", .55, 1.5, 5.6, 4.6,
            "PPI giant component and L = infinity success against fraction removed, with GF theory and the terminal-edge bound.")
    table(two, 6.4, 1.6, [4.55, 1.75],
          [["Check", "Largest gap"],
           ["Configuration model, bond and site", "0.0012"],
           ["Configuration model, degree attack, f ≤ 0.5", "0.0009"],
           ["Two-hop formulas vs 5,000 fresh orders", "0.0010"],
           [["GF vs A’s separate solver"], ["< 10", ("−12", 30000)]],
           ["PPI giant, GF vs ten seeds, f ≤ 0.97", "0.009"],
           ["L = ∞ formula vs 600 fresh orders", "0.009"]], row_h=.58)
    text(two, .73, 6.35, 11.9, .4, "Largest absolute difference in fraction units. Configuration-model graphs share the real degree sequence.", 16.5, MUTED)
    two.notes_slide.notes_text_frame.text = "The configuration-model check tests the code; the other rows test the assumptions. The attack check excludes f = 0.6, where the theory is at its threshold and the finite graph gives 0.025. The PPI gap reaches 0.020 at f = 0.99. Source: results/ws4/primekg_5000_bfs_v1__configuration_model_check.csv and __monte_carlo_check.csv."
    three = backup(prs, source, "Backup: equal damage, different outcomes", "D / B3")
    picture(three, ACT2 / "fig_equal_damage.png", .55, 1.5, 7.4, 4.6,
            "Bars for random, degree and betweenness removal at five percent: GCC stays near 0.9 while retrieval falls from 0.87 to about 0.3.")
    x, w = 8.3, 4.4
    text(three, x, 1.75, w, 1.1, "Attacks are worse than random on both metrics at every damage level above zero.", 18)
    text(three, x, 3.0, w, 1.1, "The size differs: 7 pp in GCC against 56 pp in retrieval at 5% damage.", 18)
    text(three, x, 4.25, w, 1.5, "Beyond 10% damage, degree and betweenness differ by at most 2 of 200 queries, so we do not rank them.", 18)
    text(three, .73, 6.35, 11.9, .4, "Random bars show ten-seed mean ± SD. Attacks are deterministic.", 16.5, MUTED)
    three.notes_slide.notes_text_frame.text = "Source: results/ws4/primekg_5000_bfs_v1__equal_damage.csv and __equal_damage_summary.csv."


def keep_only(prs, wanted):
    ids = prs.slides._sldIdLst
    for index, item in reversed(list(enumerate(list(ids)))):
        if index not in wanted:
            prs.part.drop_rel(item.rId)
            ids.remove(item)


def write_notes():
    lines = ["# D · Slides 9–11", "",
             "Target 3:00 in total, about 130 words per minute. Every number comes from `results/ws4/` for `primekg_5000_bfs_v1`.", ""]
    heads = {9: "Slide 9 · One formula predicts two-hop retrieval", 10: "Slide 10 · Targeted attacks break independence",
             11: "Slide 11 · Longer horizons move the bottleneck"}
    for number in (9, 10, 11):
        lines += [f"## {heads[number]}", "", f"**Script:** {NOTES[number]}", "", f"**中文要点：** {CHINESE[number]}", ""]
    lines += ["## Theory Q&A", ""]
    for question, answer in QA:
        lines += [f"**{question}**  ", answer, ""]
    (ROOT / "slides/D_speaker_notes.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    prs = Presentation(ROOT / "slides/G17_working_draft.pptx")
    slides = list(prs.slides)
    update_structural_slides(slides)
    update_conclusion_note(slides[13])
    add_backups(prs, slides[8])
    fill_slide_9(slides[8])
    fill_slide_10(slides[9])
    fill_slide_11(slides[10])
    prs.save(ROOT / "slides/G17_working_draft_with_D.pptx")
    prs = Presentation(ROOT / "slides/G17_working_draft_with_D.pptx")
    keep_only(prs, {8, 9, 10, 14, 15, 16})
    prs.save(ROOT / "slides/D_slides_9-11.pptx")
    write_notes()
    print("Saved D slides and notes")


if __name__ == "__main__":
    main()
