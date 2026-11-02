import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const root=path.resolve(import.meta.dirname,'..');
const runtime=process.env.G17_ARTIFACT_RUNTIME ?? 'C:/Users/22050/.cache/codex-runtimes/codex-primary-runtime/dependencies';
const {FileBlob,PresentationFile}=await import(pathToFileURL(path.join(runtime,'node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const p=await PresentationFile.importPptx(await FileBlob.load(path.join(root,'slides/A_slides_3_4.pptx')));
for(let i=0;i<p.slides.items.length;i++){
 const b=await p.export({slide:p.slides.items[i],format:'png',scale:1});
 await fs.writeFile(path.join(root,`slides/A_slide_${i+3}.png`),new Uint8Array(await b.arrayBuffer()));
}
console.log('Rendered final PPTX: two slides');
