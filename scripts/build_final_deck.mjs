// Author the matching bookends, retain all reviewed evidence, then validate.
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';

const root=path.resolve(import.meta.dirname,'..');
const runtime=process.env.G17_ARTIFACT_RUNTIME;
const skill=process.env.G17_PRESENTATION_SKILL;
if(!runtime || !skill) throw new Error('Set G17_ARTIFACT_RUNTIME and G17_PRESENTATION_SKILL');
process.env.RUNTIME_NODE_MODULES=path.join(runtime,'node/node_modules');
const {Presentation,PresentationFile}=await import(pathToFileURL(path.join(runtime,'node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const working=path.join(root,'.build/final_deck');
await fs.mkdir(working,{recursive:true});
const validationDir=await fs.mkdtemp(path.join(working,'validation-'));
await fs.mkdir(path.join(validationDir,'output'));
const presentation=Presentation.create({slideSize:{width:1280,height:720}});
function text(s,value,x,y,w,h,size,bold=false,color='#333333'){
 const sh=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 sh.text=value;sh.text.style={typeface:'Arial',fontSize:size,bold,color};
}
const cover=presentation.slides.add();cover.background.fill='#FFFFFF';
text(cover,'When AI Forgets',80,170,1120,105,76,true);
text(cover,'Percolation and functional robustness\nof knowledge graph retrieval',84,305,1100,135,39);
text(cover,'PC5253  /  Group 17',84,595,1100,45,25,false,'#666666');
const thanks=presentation.slides.add();thanks.background.fill='#FFFFFF';
text(thanks,'Thank you',80,210,1120,120,84,true);
text(thanks,'Questions & discussion',84,365,1100,65,34,false,'#3B8DB5');
text(thanks,'PC5253  /  Group 17',84,595,1100,45,25,false,'#666666');
const bookends=path.join(working,'bookends.pptx');
await (await PresentationFile.exportPptx(presentation)).save(bookends);
const candidate=path.join(working,'candidate.pptx');
execFileSync(path.join(runtime,'python/python.exe'),[path.join(root,'scripts/assemble_final_deck.py'),bookends,candidate],{stdio:'inherit'});
const source=path.join(root,'slides/G17_working_draft_with_D.pptx');
const referenceSha256=createHash('sha256').update(await fs.readFile(source)).digest('hex');
const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,
 finalPath:path.join(validationDir,'output/G17_final.pptx'),
 pythonExecutable:path.join(runtime,'python/python.exe'),
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit',
             '--require-native-table-slide','16','--require-native-table-slide','17'],
 explicitTotalSlideCount:18,requiredNativeTableOwnerSlides:[16,17],requiredNativeChartOwnerSlides:[],
 fontPolicy:{basis:'reference',families:['Arial'],referencePath:source,referenceSha256},
 verifyArtifactToolImport:true,receiptPath:path.join(validationDir,'G17_final.validation.json')});
await fs.copyFile(result.finalPath,path.join(root,'slides/G17_final.pptx'));
console.log('Validated slides/G17_final.pptx');
