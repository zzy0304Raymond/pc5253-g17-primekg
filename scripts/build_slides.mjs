import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const root=path.resolve(import.meta.dirname,'..');
const runtime=process.env.G17_ARTIFACT_RUNTIME ?? 'C:/Users/22050/.cache/codex-runtimes/codex-primary-runtime/dependencies';
process.env.RUNTIME_NODE_MODULES=path.join(runtime,'node/node_modules');
const skill=process.env.G17_PRESENTATION_SKILL ?? 'C:/Users/22050/.codex/plugins/cache/openai-primary-runtime/presentations/26.1026.10807/skills/presentations';
const {Presentation,PresentationFile}=await import(pathToFileURL(path.join(runtime,'node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const {finalizePresentation,applyPresentationChartFont}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const data=JSON.parse(await fs.readFile(path.join(root,'slides/chart_data.json'),'utf8'));
const presentation=Presentation.create({slideSize:{width:1280,height:720}});
const font='Arial';
function text(slide,txt,left,top,width,height,size=25,bold=false,color='#172b4d'){
 const s=slide.shapes.add({geometry:'textbox',position:{left,top,width,height},fill:'none',line:{fill:'none',width:0}});
 s.text=txt;s.text.style={typeface:font,fontSize:size,bold,color};return s;
}
function chart(slide,series,xTitle,yTitle,position,xRange,yRange,title){
 series=series.map(z=>({...z,xValues:z.xValues.map(v=>Number(v.toFixed(8))),values:z.values.map(v=>Number(v.toFixed(8)))}));
 const c=slide.charts.add('scatter',{position,title,titleTextStyle:{fontFamily:font,fontSize:24},
  scatterOptions:{style:'line'},series,hasLegend:true,legend:{position:'bottom',overlay:false,textStyle:{fontFamily:font,fontSize:15}},
  xAxis:{title:{text:xTitle,textStyle:{fontFamily:font,fontSize:18}},position:'bottom',tickLabelPosition:'low',min:xRange[0],max:xRange[1],textStyle:{fontFamily:font,fontSize:16},numberFormatCode:'0.0'},
  yAxis:{title:{text:yTitle,textStyle:{fontFamily:font,fontSize:18}},min:yRange[0],max:yRange[1],textStyle:{fontFamily:font,fontSize:16},numberFormatCode:'0.0',majorGridlines:{style:'solid',fill:'#e5e7eb',width:1}},
  chartFill:'#ffffff',plotAreaFill:'#ffffff'});
 applyPresentationChartFont(c,{fontFamily:font});return c;
}
let s=presentation.slides.add();s.background.fill='#ffffff';
text(s,'PrimeKG and the shared experimental protocol',48,32,1170,64,40,true);
text(s,'5,000 nodes  ·  117,891 undirected semantic edges',48,114,1160,40,27,true);
const table=s.tables.add({rows:4,columns:2,left:48,top:190,width:365,height:198,columnWidths:[235,130],values:[['Entity type','Nodes'],['Drug','74'],['Disease','283'],['Gene / protein','4,643']]});
for(let r=0;r<4;r++)for(let c=0;c<2;c++){let cell=table.getCell(r,c);cell.text.style={typeface:font,fontSize:24,bold:r===0,color:'#172b4d'};cell.fill=r===0?'#eaf0f6':'#ffffff';}
text(s,'A fixed benchmark',48,418,385,38,26,true);
text(s,'100 with one path; 100 with several\nDrug → protein → disease\n10 fixed random removal orders',48,466,405,150,23);
chart(s,data.degree.map(z=>({name:z.name,xValues:z.x,values:z.y,line:{fill:z.color,width:2},marker:{symbol:'none'}})),
 'log10 degree k','log10 P(K ≥ k)',{left:470,top:170,width:760,height:435},[0,3.5],[-4,0],'Degree distribution by node type');
text(s,'BFS induced subgraph; conclusions are checked against the filtered full graph.',48,652,1170,35,20,false,'#526170');
s.speakerNotes.text='Slide 3, about 75 seconds. Source: G17_Work_Plan.md and data/processed/primekg_5000_bfs_v1/manifest.json. PrimeKG: https://github.com/mims-harvard/PrimeKG ; Chandak et al., Scientific Data 10, 67 (2023). Data file 6180620. We keep three entity and relation types. Each semantic relation has a stable ID. The deterministic BFS sample is an induced graph, not a BFS tree. The log-transformed empirical CCDF is descriptive; it does not establish a power law. The benchmark is balanced between single and multiple two-hop paths and contains only initially successful queries. It is not a random sample of all drug-disease pairs. Query paths indicate association, not therapeutic efficacy. See A_speaker_notes.md for full script.';
s=presentation.slides.add();s.background.fill='#ffffff';
text(s,'Random failure and the giant component',48,32,1170,64,40,true);
text(s,'S = largest surviving component / original number of nodes',48,110,1170,45,27);
for(const [i,kind,color] of [[0,'edge','#1f77b4'],[1,'node','#2ca02c']]){
 const a=data.curves[kind];
 const series=[{name:'Simulation mean',xValues:a.x,values:a.mean,line:{fill:color,width:3},marker:{symbol:'none'}},
 {name:'GF theory',xValues:a.x,values:a.theory,line:{fill:'#000000',style:'dashed',width:2},marker:{symbol:'none'}},
 {name:'+1 SD',xValues:a.x,values:a.mean.map((v,j)=>Math.min(1,v+a.std[j])),line:{fill:color,style:'dotted',width:1},marker:{symbol:'none'}},
 {name:'−1 SD',xValues:a.x,values:a.mean.map((v,j)=>Math.max(0,v-a.std[j])),line:{fill:color,style:'dotted',width:1},marker:{symbol:'none'}}];
 chart(s,series,'Fraction removed f','S',{left:35+i*625,top:182,width:610,height:415},[0,1],[0,1.02],kind==='edge'?'Bond: remove relations':'Site: remove nodes');
}
text(s,'At 50% removal: S ≈ 0.982 for edges; S ≈ 0.493 for nodes',48,610,1170,36,26,true);
text(s,'10 seeds; GF is a configuration-model reference. Site removal also removes endpoints.',48,660,1170,30,19,false,'#526170');
s.speakerNotes.text='Slide 4, about 105 seconds. Sources: results/ws1/primekg_5000_bfs_v1__random.csv and its provenance JSON; G17 review appendix GF equations. Newman and Ziff (2000), Physical Review Letters 85, 4104. Lines show mean and ±1 sample SD across seeds, represented as bounds in editable charts; separate PNG/PDF figures use shaded bands. Bond percolation removes relations while retaining all nodes; site percolation removes nodes and their incident relations. S always divides by original N. The lower site curve partly reflects directly removed vertices, so equal f does not mean equal lost-edge budget. GF uses the empirical degree distribution under an ideal configuration-model approximation, computed by A reference module pending D integration. At f=.99 edge S=0.11222 vs GF=0.12578. On the filtered full graph, bond f=.5 gives S=.85830 rather than .98218: BFS sampling changes robustness. Do not present the finite sample as a universal PrimeKG threshold. The next member compares random loss with targeted attacks.';
const staging=path.join(root,'.build/slides');await fs.mkdir(staging,{recursive:true});
for(let i=0;i<presentation.slides.items.length;i++){
 const png=await presentation.export({slide:presentation.slides.items[i],format:'png',scale:1});
 await fs.writeFile(path.join(staging,`slide-${i+3}.png`),new Uint8Array(await png.arrayBuffer()));
}
const candidate=path.join(staging,'candidate.pptx');await (await PresentationFile.exportPptx(presentation)).save(candidate);
const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:path.join(root,'slides/A_slides_3_4_v2.pptx'),
 pythonExecutable:path.join(runtime,'python/python.exe'),integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit','--require-native-table-slide','1'],
 explicitTotalSlideCount:2,requiredNativeTableOwnerSlides:[1],requiredNativeChartOwnerSlides:[1,2],materializeLiteralChartWorkbooks:true,
 fontPolicy:{basis:'design',families:[font]},verifyArtifactToolImport:true,receiptPath:path.join(staging,'validation.json')});
console.log(JSON.stringify(result));
