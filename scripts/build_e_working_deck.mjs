// E-owned working deck. A material is embedded as supplied; B/C/D gaps are explicit.
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

const root = path.resolve(import.meta.dirname, '..');
const runtime = process.env.G17_ARTIFACT_RUNTIME;
const skill = process.env.G17_PRESENTATION_SKILL;
if (!runtime || !skill) throw new Error('Set G17_ARTIFACT_RUNTIME and G17_PRESENTATION_SKILL to the bundled runtime and skill directories');
process.env.RUNTIME_NODE_MODULES = path.join(runtime, 'node/node_modules');
const {Presentation, PresentationFile} = await import(pathToFileURL(path.join(runtime, 'node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const {finalizePresentation} = await import(pathToFileURL(path.join(skill, 'container_tools/artifact_tool_utils.mjs')).href);
const presentation = Presentation.create({slideSize:{width:1280,height:720}});
const staging = path.join(root, '.build/e_slides');
const output = path.join(root, 'slides/G17_working_draft.pptx');
await fs.mkdir(staging,{recursive:true});
const previews = path.join(staging, 'previews');
await fs.mkdir(previews,{recursive:true});
function text(s, value, x,y,w,h,size=26,bold=false,color='#333333') {
 const shape=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 shape.text=value;shape.text.style={typeface:'Arial',fontSize:size,bold,color};return shape;
}
function rect(s,x,y,w,h,color,line='none') {
 return s.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill:color,line:{fill:line,width:1}});
}
async function image(s, relative, x,y,w,h) {
 const bytes=await fs.readFile(path.join(root,relative));
 s.images.add({blob:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),contentType:'image/png',
  alt:path.basename(relative),fit:'contain',position:{left:x,top:y,width:w,height:h}});
}
function slide(title,owner,notes) {
 const s=presentation.slides.add();s.background.fill='#FFFFFF';
 text(s,title,56,35,1160,88,48,true);
 text(s,`${owner}   /   ${String(presentation.slides.items.length).padStart(2,'0')}`,56,665,1160,28,16,false,'#777777');
 s.speakerNotes.text=notes;
 return s;
}
function waiting(s, owner, figure, question) {
 rect(s,70,160,1140,405,'#F6F8FB','#D9E0E7');
 text(s,`Awaiting ${owner}'s final result`,110,210,1060,60,34,true,'#667180');
 text(s,figure,110,300,1060,55,28,false,'#3B8DB5');
 text(s,question,110,400,1030,110,26);
}

let s=slide('When AI Forgets','E','Opening, about 20 seconds. This presentation studies controlled edge and node losses in a selected PrimeKG subgraph. We ask which network properties track retrieval reliability, and which existing relations should be restored under a limited budget. This is a working assembly: member inputs are shown as awaiting delivery and E restoration results use an explicit independent evaluator. Source: G17_Work_Plan.md.');
text(s,'Percolation and functional robustness\nof knowledge graph retrieval',60,170,1110,125,38);
const stages=['Network failure','Retrieval reliability','Knowledge restoration'];
stages.forEach((label,i)=>{rect(s,65+i*405,400,360,95,['#E4EEF4','#ECE6F4','#F5EDD9'][i]);text(s,label,82+i*405,424,330,54,26,true);});
text(s,'PC5253  /  Group 17  /  Working draft',60,590,1100,45,23,false,'#666666');

s=slide('Connectivity and retrieval','E','About 40 seconds. The upper route supports a two-hop drug–protein–disease query. Removing one relation breaks that route, while the three-hop route through two proteins keeps the graph connected. The same damage can therefore affect a bounded semantic query differently from global connectivity. Restoring the missing upper edge repairs the two-hop query. This is a conceptual illustration, not a measured PrimeKG case.');
await image(s,'figures/act0/fig_query_schematic.png',70,160,1140,365);
text(s,'Allowed query length changes which relations can help.',75,575,1120,55,29,true);

s=slide('PrimeKG and the shared protocol','A','A supplies the shared data foundation. Sources: data/processed/primekg_5000_bfs_v1 nodes, edges, queries, and A speaker notes. The main graph is a 5,000-node BFS induced subgraph with 117,891 semantic edges and 200 selected positive two-hop queries. IDs are local to each graph version. Queries establish paths of association, not therapeutic efficacy. Replace this assembled layout with A’s approved version if requested.');
text(s,'5,000 nodes\n117,891 semantic edges\n200 selected queries',70,180,480,240,36,true);
text(s,'Fixed deletion orders\n10 random damage seeds\n70% / 30% query split',70,450,480,145,26);
await image(s,'figures/act0/e_deck_assets/fig_degree_dist.png',570,150,640,450);

s=slide('Random network failure','A','A owns these random failure curves. Sources: figures/act1/primekg_5000_bfs_v1 and results/ws1. The giant component fraction uses the original node count as denominator. Curves summarize ten random seeds. The black dashed GF curve is A’s configuration-model reference pending D’s final module; it is not an exact empirical-network prediction. The different direct consequences of node and edge deletion must remain explicit in the interpretation.');
await image(s,'figures/act1/primekg_5000_bfs_v1/fig_S_random_edge.png',45,160,590,420);
await image(s,'figures/act1/primekg_5000_bfs_v1/fig_S_random_node.png',645,160,590,420);
text(s,'GF curves are configuration-model references.',70,600,1100,40,22,false,'#666666');

const pending=[
 ['Targeted network failure','B','fig_attack and fig_hub_composition','How do degree and betweenness attacks compare with random failure?'],
 ['Structural and functional robustness','C','fig_S_vs_R','How does the giant component compare with semantic retrieval success?'],
 ['Path redundancy and retrieval','C','fig_R_by_group','How do single-path and multi-path queries respond to damage?'],
 ['The retrieval horizon','C','fig_R_L_curves','How does allowing longer protein paths change retrieval success?'],
 ['Two-hop survival theory','D','fig_R_theory_vs_sim','Compare observed retrieval with the independent-edge survival model.'],
 ['Dependence under targeted attacks','D','fig_corr_penalty','Where do targeted failures depart from the random-removal prediction?'],
 ['Retrieval across task scales','D + C','fig_phase_diagram','Compare finite query horizons with the two-hop and long-path theoretical limits.'],
];
for(const [title,owner,figure,question] of pending){
 s=slide(title,owner,`Owner: ${owner}. Required figure: ${figure}. ${question} This page reserves the agreed position in the 14-slide narrative. It contains no simulated scientific result. Supply the final PNG/PDF, three interpretation points, a 50–80-word English script and likely questions using the handoff format in G17_Work_Plan.md. Replace the awaiting-delivery panel when that contribution is available.`);
 waiting(s,owner,figure,question);
}
s=slide('Restoration for two-hop queries','E','About 60 seconds. These local checks use the frozen query split and ten damage seeds. Rankings use only training queries; the success rate uses the sixty test queries. Task-aware ranks are static completable-path counts. At 20% budget after 50% damage, the mean L2 gains are 13.17 percentage points for random restoration, 48.50 for relation-type restoration, and 24.83 for task-aware restoration. B’s edge ranking and C’s evaluator are not integrated. Source: results/ws5/local_reference/primekg_5000_bfs_v1 summary and provenance.');
await image(s,'figures/act3/local_reference/primekg_5000_bfs_v1/fig_restoration_L2.png',65,155,1150,440);
text(s,'Static task-aware ranking; training queries choose edges, test queries measure gains.',65,608,1150,40,22);

s=slide('Restoration for three-hop queries','E','About 55 seconds. We now allow one protein–protein step. The observed gains and relative gaps differ from the two-hop setting. At 20% budget after 50% edge removal, random, relation-type and static task-aware restoration gain 8.33, 15.67 and 12.33 percentage points respectively. These are preliminary local reference results over ten seeds, with sample SD shading. No claim that the ranking must reverse is imposed. Source: E’s saved result tables; final B/C integration is pending.');
await image(s,'figures/act3/local_reference/primekg_5000_bfs_v1/fig_restoration_L3.png',65,155,1150,440);
text(s,'Protein–protein edges can participate when L = 3.',65,608,1150,40,25,true);

s=slide('Robustness depends on the task','E','About 35 seconds, then questions. The conceptual argument is that structural connectivity and bounded semantic reachability inspect different network properties. E’s independent local results compare restoration policies, but the final four-strategy claim awaits B’s ranking and C’s evaluator. The final conclusion must be updated using every member’s results. Disclose BFS sampling, selected positive queries and entity overlap between training and test sets. Total rehearsal target is fourteen minutes.');
const blocks=[['Structure','Giant component'],['Function','Allowed semantic paths'],['Intervention','Budget and query horizon']];
blocks.forEach(([heading,body],i)=>{rect(s,70+i*403,185,360,220,['#E4EEF4','#ECE6F4','#F5EDD9'][i]);text(s,heading,90+i*403,220,320,60,36,true);text(s,body,90+i*403,305,320,85,27);});
text(s,'Pending integration: B edge ranking and C retrieval evaluation',75,510,1120,65,27);
text(s,'Scope: BFS subgraph, selected positive queries, shared entities across splits.',75,595,1120,42,21,false,'#666666');

for(let i=0;i<presentation.slides.items.length;i++){
 const blob=await presentation.export({slide:presentation.slides.items[i],format:'png',scale:1});
 await fs.writeFile(path.join(previews,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await blob.arrayBuffer()));
}
const candidate=path.join(staging,'candidate.pptx');
await (await PresentationFile.exportPptx(presentation)).save(candidate);
const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:output,
 pythonExecutable:path.join(runtime,'python/python.exe'),
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],
 explicitTotalSlideCount:14,requiredNativeTableOwnerSlides:[],requiredNativeChartOwnerSlides:[],
 fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,
 receiptPath:path.join(staging,'validation.json')});
console.log(JSON.stringify(result));
