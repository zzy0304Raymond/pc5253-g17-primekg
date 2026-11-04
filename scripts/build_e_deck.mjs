// Build the current group working deck and E's standalone five-slide contribution.
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

const root=path.resolve(import.meta.dirname,'..');
const runtime=process.env.G17_ARTIFACT_RUNTIME;
const skill=process.env.G17_PRESENTATION_SKILL;
if(!runtime || !skill) throw new Error('Set G17_ARTIFACT_RUNTIME and G17_PRESENTATION_SKILL to the bundled runtime and skill directories');
process.env.RUNTIME_NODE_MODULES=path.join(runtime,'node/node_modules');
const {Presentation,PresentationFile}=await import(pathToFileURL(path.join(runtime,'node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const working=path.join(root,'.build/e_delivery');
const evidence=JSON.parse(await fs.readFile(path.join(working,'evidence.json'),'utf8'));
const eNotes=(await fs.readFile(path.join(root,'slides/E_speaker_notes.md'),'utf8')).replaceAll('\r','');
const cNotes=(await fs.readFile(path.join(root,'slides/C_speaker_notes.md'),'utf8')).replaceAll('\r','');
function notes(source,index){
 const heading=new RegExp('^## Slide '+index+'[^\\n]*\\n','m');
 const match=heading.exec(source);
 if(!match) throw new Error('Missing speaking notes for slide '+index);
 const rest=source.slice(match.index+match[0].length);
 return rest.split(/\n## /)[0].trim();
}
const assets='.build/e_delivery/assets/';
const formal='figures/act3/final/primekg_5000_bfs_v1/';
const cFigures='figures/act2/primekg_5000_bfs_v1/';
let presentation;
function text(s,value,x,y,w,h,size=26,bold=false,color='#333333'){
 const shape=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 shape.text=value;shape.text.style={typeface:'Arial',fontSize:size,bold,color};return shape;
}
function rect(s,x,y,w,h,fill,line='none'){
 return s.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:line,width:1}});
}
async function image(s,relative,x,y,w,h){
 const bytes=await fs.readFile(path.join(root,relative));
 s.images.add({blob:bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),contentType:'image/png',
 alt:path.basename(relative),fit:'contain',position:{left:x,top:y,width:w,height:h}});
}
const specs=[];
function add(title,owner,note,body){specs.push({title,owner,note,body});}
const p1=100*evidence.C_R_f50.R_L2;
const gap=100*evidence.A_edge_GCC_f50-p1;

add('When AI Forgets','E',notes(eNotes,1)+'\nSource: G17_Work_Plan.md.',async s=>{
 text(s,'Percolation and functional robustness\nof knowledge graph retrieval',60,170,1110,125,38);
 ['Network failure','Retrieval reliability','Knowledge restoration'].forEach((label,i)=>{
  rect(s,65+i*405,400,360,95,['#E4EEF4','#ECE6F4','#F5EDD9'][i]);
  text(s,label,82+i*405,424,330,54,26,true);
 });
 text(s,'PC5253 / Group 17',60,590,1100,42,23,false,'#666666');
});
add('Connectivity and retrieval','E',notes(eNotes,2)+'\nConcept schematic, not an observed PrimeKG case.',async s=>{
 await image(s,'figures/act0/fig_query_schematic.png',70,150,1140,380);
 text(s,'The allowed path length changes which relations can help.',75,575,1120,55,29,true);
});
add('PrimeKG and the shared protocol','A','Source: A DATA_CONTRACT, nodes, edges and queries for '+evidence.gid+'. The benchmark contains selected initially successful association paths. Counts are local to this graph. Drug and disease paths do not establish therapeutic efficacy. The degree CCDF is descriptive and does not establish a power law. A owns final wording for this page.',async s=>{
 text(s,`${evidence.n_nodes.toLocaleString('en-US')} nodes\n${evidence.n_edges.toLocaleString('en-US')} semantic edges\n${evidence.n_queries} selected queries`,70,180,480,240,36,true);
 text(s,'Fixed deletion orders\n10 random damage seeds\n70% / 30% query split',70,450,480,145,26);
 await image(s,assets+'fig_degree_dist.png',570,150,640,450);
});
add('Random network failure','A','Source: results/ws1/'+evidence.gid+'__random.csv. Structural fraction divides by original N. Random curves show ten-seed mean and sample SD. Black dashed GF is A’s configuration-model reference pending D’s final implementation. Node removal also deletes endpoints and adjacent edges; equal f does not imply equal lost-edge counts.',async s=>{
 await image(s,assets+'fig_S_random_edge.png',45,150,590,435);
 await image(s,assets+'fig_S_random_node.png',645,150,590,435);
 text(s,'GF curves are configuration-model references.',70,608,1100,38,22,false,'#666666');
});
add('Targeted failure and central nodes','B','Source: B ws2_attack_results_long.csv and ws2_hub_composition.csv. At f=.5, GCC fractions are '+JSON.stringify(evidence.B_node_GCC_f50)+'. Attack curves use one fixed original ranking. B stores construction seeds 0 and 42 on fixed curves; the display treats those as deterministic, without an error band. The random curve has ten-seed SD. The top-1% composition is descriptive. D’s degree-attack theory overlay remains pending.',async s=>{
 await image(s,assets+'fig_B_attack.png',35,150,720,440);
 await image(s,assets+'fig_B_hubs_top1.png',765,165,470,410);
 text(s,'At 50% node loss: GCC ≈ 49% random, 23% degree, 21% betweenness.',65,610,1160,38,23);
});
add('Structural and functional robustness','C',notes(cNotes,6)+'\nSource: results/ws1 and results/ws3 matching edge damage states.',async s=>{
 await image(s,cFigures+'fig_S_vs_R.png',70,145,720,475);
 text(s,`${gap.toFixed(1)} pp`,845,235,365,95,58,true,'#3B8DB5');
 text(s,'GCC–retrieval gap\nat 50% edge loss',845,350,365,120,29);
 text(s,'Same queries and damage states; 10 seeds.',80,620,1100,34,22,false,'#666666');
});
add('Path redundancy and retrieval','C',notes(cNotes,7)+'\nSource: results/ws3/'+evidence.gid+'__retrieval.csv.',async s=>{
 await image(s,cFigures+'fig_R_by_group.png',70,145,720,475);
 text(s,'At 50% edge loss',845,195,365,60,27);
 text(s,`${(100*evidence.C_R_f50.R_L2_multi).toFixed(1)}%`,845,285,365,85,52,true,'#9472C4');
 text(s,'Multi-path queries',845,370,365,45,25);
 text(s,`${(100*evidence.C_R_f50.R_L2_single).toFixed(1)}%`,845,455,365,75,46,true,'#3B8DB5');
 text(s,'Single-path queries',845,535,365,45,25);
});
add('The retrieval horizon','C',notes(cNotes,8)+'\nAll displayed horizons use damage seeds 0–2.',async s=>{
 await image(s,cFigures+'fig_R_L_curves.png',35,150,720,440);
 await image(s,cFigures+'fig_R_L_heatmap.png',765,160,470,425);
 text(s,'Matched three-seed comparison at every hop limit.',65,610,1140,38,23,false,'#666666');
});
for(const [title,name,question] of [
 ['Two-hop survival theory','fig_R_theory_vs_sim','Relate path redundancy to the independent-edge survival model.'],
 ['Dependence under targeted attacks','fig_corr_penalty','Compare the random-removal model with targeted-attack observations.'],
 ['Retrieval across task scales','fig_phase_diagram','Combine C’s hop scan with D’s two theoretical limits.']
]){
 add(title,'D','Reserved for D’s final theory contribution. Required figure: '+name+'. '+question+' No theory result is supplied on this page.',async s=>{
  rect(s,70,165,1140,390,'#F6F8FB','#D9E0E7');
  text(s,'Awaiting D’s final theory contribution',110,210,1060,65,34,true,'#667180');
  text(s,name,110,310,1060,50,27,false,'#3B8DB5');
  text(s,question,110,405,1030,100,26);
 });
}
add('Restoration for two-hop queries','E',notes(eNotes,12)+'\nSource: results/ws5/final/'+evidence.gid+' and report/E_static_score_diagnostics.csv. Formal C Retriever; B edge ranking included.',async s=>{
 await image(s,formal+'fig_restoration_L2.png',65,150,1150,440);
 text(s,'A small positive-score set limits the static task-aware policy.',65,610,1140,38,25,true);
});
add('Restoration for three-hop queries','E',notes(eNotes,13)+'\nSource: results/ws5/final/'+evidence.gid+'. The displayed gains are paired within seed and shaded by sample SD. No significance claim.',async s=>{
 await image(s,formal+'fig_restoration_L3.png',65,150,1150,440);
 text(s,'At 50% damage, 20% budget: 16.5 pp vs 15.7 pp.',65,610,1140,38,24,true);
});
add('Robustness depends on the task','E',notes(eNotes,14)+'\nE report Sections 1 and 7. Full-group theory narrative awaits D. The full fourteen-minute rehearsal has not been measured.',async s=>{
 [['Structure','Global connectivity'],['Function','Allowed semantic paths'],['Intervention','Query horizon and budget']].forEach(([h,b],i)=>{
  rect(s,70+i*403,185,360,220,['#E4EEF4','#ECE6F4','#F5EDD9'][i]);
  text(s,h,90+i*403,220,320,60,36,true);text(s,b,90+i*403,305,320,85,27);
 });
 text(s,'Largest structural and two-hop gains can favor different policies.',75,505,1120,76,27);
 text(s,'Scope: BFS subgraph, positive queries, shared entities across query splits.',75,605,1120,38,21,false,'#666666');
});
if(specs.length!==14) throw new Error('Expected fourteen group slides');

for(const target of [{name:'G17_working_draft',indices:specs.map((_,i)=>i)},
                     {name:'E_slides',indices:specs.map((s,i)=>s.owner==='E'?i:-1).filter(i=>i>=0)}]){
 presentation=Presentation.create({slideSize:{width:1280,height:720}});
 const previews=path.join(working,'previews',target.name);
 await fs.mkdir(previews,{recursive:true});
 for(const i of target.indices){
  const spec=specs[i];const s=presentation.slides.add();s.background.fill='#FFFFFF';
  text(s,spec.title,56,35,1160,88,48,true);
  text(s,`${spec.owner} / ${String(i+1).padStart(2,'0')}`,56,665,1160,28,16,false,'#777777');
  s.speakerNotes.text=spec.note;
  await spec.body(s);
  const blob=await presentation.export({slide:s,format:'png',scale:1});
  await fs.writeFile(path.join(previews,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await blob.arrayBuffer()));
 }
 const build=path.join(working,'build');const validatedDir=path.join(working,'validated');
 await fs.mkdir(build,{recursive:true});await fs.mkdir(validatedDir,{recursive:true});
 const candidate=path.join(build,target.name+'.pptx');const validated=path.join(validatedDir,target.name+'.pptx');
 const receipt=path.join(working,target.name+'.validation.json');
 await (await PresentationFile.exportPptx(presentation)).save(candidate);
 // This is a private, replaceable validation output; the canonical deck is copied only after validation.
 await fs.rm(validated,{force:true});
 await fs.rm(receipt,{force:true});
 const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:validated,
  pythonExecutable:path.join(runtime,'python/python.exe'),
  integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],
  explicitTotalSlideCount:target.indices.length,requiredNativeTableOwnerSlides:[],requiredNativeChartOwnerSlides:[],
  fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,
  receiptPath:receipt});
 await fs.copyFile(validated,path.join(root,'slides',target.name+'.pptx'));
 console.log(JSON.stringify({file:result.finalPath,slides:target.indices.length,status:'validated'}));
}
