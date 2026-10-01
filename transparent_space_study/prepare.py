"""A separate, immutable-input snapshot for the translucent background study."""
from pathlib import Path
import hashlib, json, shutil
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
INPUTS=[
    'claude/engine/gl.py',
    'claude/film/shots/s03_self.py',
    'claude/film/shots/s02_execute.py',
    'claude/audio/feat_14_31.npz',
]
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()
def main():
    manifest=HERE/'source_manifest.json'
    if manifest.exists(): raise SystemExit('Snapshot already exists.')
    records=[]
    for rel in INPUTS:
        src=ROOT/rel; dest=HERE/'base'/Path(rel).relative_to('claude')
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,dest)
        records.append({'original':rel,'sha256':digest(src)})
    gl=HERE/'base/engine/gl.py'
    gl.write_text(gl.read_text(encoding='utf-8').replace('ROOT = Path(__file__).resolve().parents[2]',
        'ROOT = Path(__file__).resolve().parents[3]'),encoding='utf-8')
    for src in [next(ROOT.glob('*.mp3')),ROOT/'claude/film/master.py',ROOT/'claude/film/film_full_v1_1080p.mp4']:
        records.append({'original':str(src.relative_to(ROOT)),'sha256':digest(src)})
    manifest.write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Protected inputs:',len(records))
if __name__=='__main__': main()
