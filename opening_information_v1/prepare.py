"""Copy only the read-only inputs needed for this independent opening study."""
from pathlib import Path
import hashlib, json, shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FILES = [
    'claude/engine/gl.py',
    'claude/film/shots/s01_boot.py',
    'claude/film/shots/s02_execute.py',
    'claude/film/shots/s03_self.py',
    'claude/tests/t01_gap_ring/render.py',
    'claude/tests/t01_gap_ring/scene.glsl',
    'claude/tests/t06_teletype/glyphs.png',
    'claude/audio/feat_14_31.npz',
]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    if (HERE / 'source_manifest.json').exists():
        raise SystemExit('Snapshot already exists; originals will not be recopied.')
    records = []
    for rel in FILES:
        source = ROOT / rel
        dest = HERE / 'base' / Path(rel).relative_to('claude')
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
        records.append({'original': rel, 'snapshot': str(dest.relative_to(HERE)), 'sha256': sha(source)})
    gl = HERE / 'base/engine/gl.py'
    text = gl.read_text(encoding='utf-8')
    text = text.replace('ROOT = Path(__file__).resolve().parents[2]', 'ROOT = Path(__file__).resolve().parents[3]')
    gl.write_text(text, encoding='utf-8')
    song = next(ROOT.glob('*.mp3'))
    records.append({'original': song.name, 'snapshot': None, 'sha256': sha(song)})
    for rel in ['claude/film/master.py', 'claude/film/film_full_v1_1080p.mp4']:
        records.append({'original': rel, 'snapshot': None, 'sha256': sha(ROOT / rel)})
    (HERE / 'source_manifest.json').write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding='utf-8')
    print('Independent snapshot created:', len(records), 'protected inputs')

if __name__ == '__main__':
    main()
