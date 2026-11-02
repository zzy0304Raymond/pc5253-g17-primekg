"""Create a reviewed A-only handoff ZIP without raw CSV or local runtimes."""
import json
from pathlib import Path
import sys
import zipfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.common import ROOT,sha256,write_json

root_files=['README.md','G17_Work_Plan.md','A_Data_Foundation_Audit_and_Plan.md','requirements.txt','requirements-lock.txt','.gitignore']
dirs=['src','scripts','tests','docs','data/processed','results','figures','slides','report']
files=[ROOT/p for p in root_files]
for d in dirs:
    files.extend(p for p in (ROOT/d).rglob('*') if p.is_file() and not any(x in p.parts for x in ['__pycache__','node_modules','.build','.venv','.tools']))
files=sorted(set(files),key=lambda p:p.relative_to(ROOT).as_posix())
dest=ROOT/'dist/G17_A_handoff.zip';dest.parent.mkdir(exist_ok=True)
if dest.exists(): raise FileExistsError('Version the handoff before packaging again; refusing overwrite')
with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
    for f in files: z.write(f,f.relative_to(ROOT).as_posix())
with zipfile.ZipFile(dest) as z:
    bad=z.testzip(); assert bad is None,bad
    names=z.namelist(); assert not any(n.startswith(('data/raw/','.venv/','.tools/','.build/')) for n in names)
    assert all(p in names for p in ['README.md','slides/A_slides_3_4.pptx','data/processed/primekg_5000_bfs_v1/manifest.json','results/ws1/primekg_5000_bfs_v1__random.csv'])
write_json(ROOT/'dist/G17_A_handoff_manifest.json',{'archive':str(dest),'sha256':sha256(dest),'bytes':dest.stat().st_size,
    'file_count':len(files),'raw_csv_included':False,'archive_crc_passed':True})
print(f'HANDOFF PACKAGE PASS: {len(files)} files, {dest.stat().st_size:,} bytes, sha256={sha256(dest)}')

