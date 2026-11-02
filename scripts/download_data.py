"""Resumable, range-checked download of the protocol-pinned public PrimeKG file."""
import concurrent.futures as cf
import hashlib
import json
import subprocess
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
URL = 'https://dataverse.harvard.edu/api/access/datafile/6180620'

def download(workers=16):
    RAW.mkdir(parents=True, exist_ok=True)
    meta = json.loads((RAW / 'dataverse_metadata.json').read_text(encoding='utf-8'))
    files = meta['data']['latestVersion']['files']
    info = next(f['dataFile'] for f in files if f['dataFile']['id'] == 6180620)
    total = info['filesize']
    expected = info['checksum']
    dest = RAW / 'kg.csv'
    if dest.exists():
        h = hashlib.new(expected['type'].lower())
        with dest.open('rb') as f:
            for b in iter(lambda: f.read(8*1024*1024), b''): h.update(b)
        if h.hexdigest() == expected['value']: print('Existing kg.csv verified', flush=True); return
        raise ValueError('Existing kg.csv has wrong checksum; refusing to overwrite')
    chunks = RAW / '.download_chunks'; chunks.mkdir(exist_ok=True)
    step = 8*1024*1024
    def part(i):
        start, end = i*step, min((i+1)*step, total)-1
        p = chunks / f'{i:04d}.bin'
        if p.exists() and p.stat().st_size == end-start+1: return i
        for retry in range(4):
            hdr = chunks / f'{i:04d}.headers'
            r = subprocess.run(['curl.exe','--fail','-sS','-L','--connect-timeout','30',
                '--max-time','600','--range',f'{start}-{end}','-D',str(hdr),'-o',str(p),URL], capture_output=True)
            headers = hdr.read_text(errors='replace') if hdr.exists() else ''
            if r.returncode == 0 and p.stat().st_size == end-start+1 and f'content-range: bytes {start}-{end}/{total}' in headers.lower():
                hdr.unlink(missing_ok=True); return i
            time.sleep(2*(retry+1))
        raise RuntimeError(f'Range {i} failed; resume by rerunning')
    count = (total+step-1)//step
    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        for done, fut in enumerate(cf.as_completed([pool.submit(part,i) for i in range(count)]),1):
            fut.result(); print(f'Download chunks: {done}/{count}',flush=True)
    sha = hashlib.sha256(); official = hashlib.new(expected['type'].lower())
    tmp = RAW / 'kg.csv.assembling'
    with tmp.open('wb') as f:
        for i in range(count):
            b=(chunks/f'{i:04d}.bin').read_bytes(); f.write(b); sha.update(b); official.update(b)
    if official.hexdigest() != expected['value']:
        raise ValueError('Official checksum mismatch; assembled file NOT published')
    tmp.replace(dest)
    (RAW/'source.json').write_text(json.dumps({'url':URL,'file_id':6180620,'bytes':total,
        'sha256':sha.hexdigest(),'official_checksum':expected,'official_checksum_verified':True},indent=2)+'\n')
    print('Published verified kg.csv; SHA256='+sha.hexdigest(),flush=True)

if __name__ == '__main__': download()
