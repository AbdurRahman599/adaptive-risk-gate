"""Export every .drawio file in this folder to vector PDF (draw.io desktop CLI) and to a 450-dpi PNG rendered from that PDF.
The PNG is rasterised from the PDF because the CLI's direct PNG export clips the drawing when Windows display scaling is above 100%.
Needs: draw.io desktop (winget install JGraph.Draw) and pymupdf."""
import os, subprocess
from pathlib import Path
import pymupdf

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[1]/'final'
EXE = os.path.join(os.environ['LOCALAPPDATA'], 'Programs', 'draw.io', 'draw.io.exe')
for f in sorted(HERE.glob('*.drawio')):
    pdf = OUT/f'{f.stem}.pdf'
    subprocess.run([EXE, '-x', '-f', 'pdf', '--crop', '-b', '12', '-o', str(pdf), str(f)], check=True, capture_output=True)
    with pymupdf.open(pdf) as doc:
        doc[0].get_pixmap(dpi=450).save(OUT/f'{f.stem}.png')
    print('exported', f.stem, '(pdf, png)')
