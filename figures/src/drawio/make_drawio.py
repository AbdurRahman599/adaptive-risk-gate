"""Editable draw.io schematics (Figs. 1-3). Writes <name>.drawio next to this script; export with export_drawio.py.
Figures carry labels only; titles and explanations belong in the manuscript captions.
Every element is a plain draw.io shape, so each figure can be opened and edited at app.diagrams.net or in draw.io desktop."""
import math
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
NAVY, BLUE, TEAL, OCHRE, BRICK, GREY = '#17344D', '#3A7FB5', '#00918A', '#C08232', '#B5534A', '#66788A'
LBLUE, LTEAL, LOCHRE, LGREY, PALE = '#A9C6DE', '#D8EEEB', '#F1DDBE', '#E3E8ED', '#F2F5F8'
XRAY, LUNG = '#21394D', '#9FB1BF'
FONT = 'fontFamily=Helvetica;'


class Diagram:
    def __init__(self, name, width, height):
        self.name, self.w, self.h, self.cells, self.n = name, width, height, [], 2

    def _id(self):
        self.n += 1
        return f'c{self.n}'

    def shape(self, x, y, w, h, style, value=''):
        i = self._id()
        self.cells.append(f'<mxCell id="{i}" value="{escape(value, {chr(34): "&quot;"})}" style="{style}" vertex="1" parent="1">'
                          f'<mxGeometry x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" as="geometry"/></mxCell>')
        return i

    def text(self, x, y, w, h, value, size=16, color=NAVY, bold=False, align='center', valign='middle', italic=False):
        fs = (1 if bold else 0) + (2 if italic else 0)
        return self.shape(x, y, w, h, f'text;html=1;whiteSpace=wrap;{FONT}fontSize={size};fontColor={color};fontStyle={fs};'
                                      f'align={align};verticalAlign={valign};strokeColor=none;fillColor=none;', value)

    def line(self, pts, color=GREY, width=2, arrow=True, dashed=False, curved=False):
        i = self._id()
        (x1, y1), (x2, y2), mid = pts[0], pts[-1], pts[1:-1]
        st = (f'html=1;rounded={1 if curved else 0};curved={1 if curved else 0};strokeColor={color};strokeWidth={width};'
              f'endArrow={"block" if arrow else "none"};endFill=1;endSize=7;' + ('dashed=1;dashPattern=6 4;' if dashed else ''))
        way = ''.join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in mid)
        self.cells.append(f'<mxCell id="{i}" value="" style="{st}" edge="1" parent="1"><mxGeometry relative="1" as="geometry">'
                          f'<mxPoint x="{x1}" y="{y1}" as="sourcePoint"/><mxPoint x="{x2}" y="{y2}" as="targetPoint"/>'
                          + (f'<Array as="points">{way}</Array>' if mid else '') + '</mxGeometry></mxCell>')
        return i

    def save(self):
        xml = (f'<mxfile host="drawio"><diagram name="{self.name}" id="{self.name}"><mxGraphModel dx="1400" dy="900" grid="0" gridSize="10" '
               f'guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{self.w}" pageHeight="{self.h}" '
               f'background="#FFFFFF" math="0" shadow="0"><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
               + ''.join(self.cells) + '</root></mxGraphModel></diagram></mxfile>')
        (HERE/f'{self.name}.drawio').write_text(xml, encoding='utf8')
        print('wrote', self.name)


# ------------------------------------------------------------------ icons (centre-anchored, scale s)
def ic_people(d, cx, cy, s=1.0, color=NAVY):
    for dx, sc in [(-24, 0.75), (24, 0.75), (0, 1.0)]:
        r = 10*s*sc; bw, bh = 32*s*sc, 24*s*sc; x = cx+dx*s
        d.shape(x-r, cy-20*s*sc-r-6*s, 2*r, 2*r, f'ellipse;fillColor={color};strokeColor=#FFFFFF;strokeWidth=2;')
        d.shape(x-bw/2, cy-7*s*sc, bw, bh, f'rounded=1;arcSize=35;fillColor={color};strokeColor=#FFFFFF;strokeWidth=2;')


def ic_xray(d, cx, cy, s=1.0, lateral=False):
    w, h = 58*s, 70*s
    d.shape(cx-w/2, cy-h/2, w, h, f'rounded=1;arcSize=8;fillColor={XRAY};strokeColor=#10202C;')
    d.shape(cx-w/2+5*s, cy-h/2+5*s, 8*s, 3*s, 'rounded=0;fillColor=#FFFFFF;strokeColor=none;')
    if lateral:
        d.shape(cx-15*s, cy-23*s, 25*s, 46*s, f'ellipse;fillColor={LUNG};strokeColor=#DCE4EA;')
        for k in range(6):
            d.shape(cx+17*s, cy-21*s+k*8*s, 5*s, 5*s, 'rounded=0;fillColor=#DCE4EA;strokeColor=none;')
    else:
        d.shape(cx-22*s, cy-25*s, 19*s, 46*s, f'ellipse;fillColor={LUNG};strokeColor=#DCE4EA;')
        d.shape(cx+3*s, cy-25*s, 19*s, 46*s, f'ellipse;fillColor={LUNG};strokeColor=#DCE4EA;')
        d.shape(cx-1*s, cy-29*s, 2*s, 52*s, 'rounded=0;fillColor=#DCE4EA;strokeColor=none;')


def ic_doc(d, cx, cy, s=1.0, color=OCHRE, mode='plain'):
    """mode plain | sections: kept sections highlighted, findings and impression struck through."""
    w, h = 58*s, 72*s
    d.shape(cx-w/2, cy-h/2, w, h, f'shape=note;size={13*s};whiteSpace=wrap;fillColor=#FFFFFF;strokeColor={color};strokeWidth=2;')
    for k in range(5):
        y = cy-h/2+18*s+k*10*s
        keep = mode == 'sections' and k < 3
        if keep:
            d.shape(cx-w/2+7*s, y-3.5*s, w-18*s, 7*s, f'rounded=0;fillColor={LOCHRE};strokeColor=none;')
        d.line([(cx-w/2+9*s, y), (cx+w/2-13*s, y)], color=color if keep else '#9AA8B4', width=1.5, arrow=False)
    if mode == 'sections':
        d.line([(cx-w/2+4*s, cy-h/2+48*s), (cx+w/2-6*s, cy-h/2+66*s)], color=BRICK, width=2.5, arrow=False)
        d.line([(cx-w/2+4*s, cy-h/2+66*s), (cx+w/2-6*s, cy-h/2+48*s)], color=BRICK, width=2.5, arrow=False)


def ic_network(d, cx, cy, s=1.0, color=BLUE, light=LBLUE, lock=True):
    cols = [(-32, [-22, 0, 22]), (0, [-31, -10, 10, 31]), (32, [-20, 0, 20])]
    pts = [[(cx+x*s, cy+y*s) for y in ys] for x, ys in cols]
    for a, b in [(0, 1), (1, 2)]:
        for p in pts[a]:
            for q in pts[b]:
                d.line([p, q], color=light, width=1, arrow=False)
    for col in pts:
        for x, y in col:
            d.shape(x-5.5*s, y-5.5*s, 11*s, 11*s, f'ellipse;fillColor={color};strokeColor=none;')
    if lock:
        ic_lock(d, cx+48*s, cy-34*s, s)


def ic_check(d, cx, cy, s=1.0, color=TEAL):
    w, h = 54*s, 64*s
    d.shape(cx-w/2, cy-h/2, w, h, f'rounded=1;arcSize=6;fillColor=#FFFFFF;strokeColor={color};strokeWidth=2;')
    for k in range(3):
        y = cy-h/2+14*s+k*18*s
        d.text(cx-w/2+3*s, y-8*s, 18*s, 16*s, '&#10003;', size=int(15*s), color=color, bold=True)
        d.line([(cx-2*s, y), (cx+w/2-8*s, y)], color='#9AA8B4', width=1.5, arrow=False)


def ic_reviewer(d, cx, cy, s=1.0, color=OCHRE):
    d.shape(cx-15*s, cy-38*s, 30*s, 30*s, f'ellipse;fillColor={color};strokeColor=none;')
    d.shape(cx-26*s, cy-4*s, 52*s, 42*s, f'rounded=1;arcSize=14;fillColor={color};strokeColor=none;fontColor=#FFFFFF;fontSize={int(28*s)};fontStyle=1;{FONT}', '+')


def ic_lock(d, cx, cy, s=1.0):
    d.shape(cx-8*s, cy-19*s, 16*s, 18*s, f'ellipse;fillColor=none;strokeColor={GREY};strokeWidth=2;')
    d.shape(cx-12*s, cy-10*s, 24*s, 20*s, f'rounded=1;arcSize=15;fillColor={LGREY};strokeColor={GREY};strokeWidth=1.5;')


def chip(d, x, y, w, h, color, txt, filled=True, size=15):
    d.shape(x, y, w, h, f'rounded=1;arcSize=30;fillColor={color if filled else "#FFFFFF"};strokeColor={color};strokeWidth=2;'
                        f'fontColor={"#FFFFFF" if filled else color};fontSize={size};fontStyle=1;{FONT}', txt)


def glyphs(d, x, y, has, s=0.42):
    """availability glyphs: frontal, lateral, history; absent ones faded."""
    for k, (kind, ok) in enumerate(zip(['f', 'l', 'h'], has)):
        cx = x+k*34
        if kind == 'h':
            ic_doc(d, cx, y, s, OCHRE)
        else:
            ic_xray(d, cx, y, s, lateral=(kind == 'l'))
        if not ok:
            d.shape(cx-15, y-18, 30, 36, 'rounded=0;fillColor=#FFFFFF;opacity=75;strokeColor=none;')


# ------------------------------------------------------------------ Figure 1: cohorts and rotating cross-fitting
def fig1():
    d = Diagram('Fig1_cohorts_crossfitting', 1500, 640)
    d.shape(30, 175, 300, 290, f'rounded=1;arcSize=6;fillColor={PALE};strokeColor=none;')
    ic_people(d, 120, 245, 1.0, NAVY); ic_xray(d, 235, 240, 0.9)
    d.text(40, 300, 280, 32, 'MIMIC-CXR-JPG', 22, NAVY, True)
    d.text(40, 334, 280, 30, '5,994 patients', 19, NAVY)
    glyphs(d, 146, 405, (True, True, True))
    d.line([(330, 320), (448, 320)], color=NAVY, width=3)
    cx, cy, R = 640, 320, 175
    roles = [('Fit', BLUE), ('Fit', BLUE), ('Fit', BLUE), ('Tune', '#6FA0C8'), ('Calibrate', OCHRE), ('Evaluate', TEAL)]
    for k, (lab, col) in enumerate(roles):
        a0, a1 = k/6+0.004, (k+1)/6-0.004
        d.shape(cx-R, cy-R, 2*R, 2*R, f'shape=mxgraph.basic.partConcEllipse;startAngle={a0:.4f};endAngle={a1:.4f};arcWidth=0.44;'
                                      f'fillColor={col};strokeColor=none;')
        th = 2*math.pi*(k+0.5)/6; r = R*0.78
        d.text(cx+r*math.sin(th)-60, cy-r*math.cos(th)-15, 120, 30, lab, 15 if lab != 'Calibrate' else 13, '#FFFFFF', True)
    ic_people(d, cx, cy+4, 1.15, NAVY)
    pts = [(cx+(R+26)*math.sin(t), cy-(R+26)*math.cos(t)) for t in [math.radians(a) for a in range(-60, 61, 15)]]
    d.line([(round(x), round(y)) for x, y in pts], color=GREY, width=2.5, curved=True)
    d.text(cx-90, cy-R-78, 180, 28, '&#215;6 rotations', 16, GREY, True)
    d.text(cx-120, cy+R+22, 240, 28, '&#215;3 group assignments', 16, GREY, True)
    d.line([(832, 320), (930, 320)], color=TEAL, width=3, arrow=False)
    ic_lock(d, 882, 300, 1.0)
    for y in [125, 320, 515]:
        d.line([(930, 320), (930, y), (990, y)], color=TEAL, width=3)
    vals = [(125, 'Additional MIMIC', '2,000 patients', (True, True, True), False),
            (320, 'NIH ChestX-ray14', '6,000 patients', (True, False, False), True),
            (515, 'CheXpert Plus', '6,000 patients', (True, True, True), True)]
    for y, name, n, has, ext in vals:
        d.shape(990, y-80, 480, 160, f'rounded=1;arcSize=8;fillColor=#FFFFFF;strokeColor={TEAL if ext else LGREY};strokeWidth=2;')
        d.text(1010, y-66, 300, 30, name, 20, TEAL if ext else NAVY, True, align='left')
        d.text(1010, y-34, 300, 28, n, 18, NAVY, align='left')
        glyphs(d, 1030, y+38, has)
        if ext:
            chip(d, 1330, y-56, 120, 34, OCHRE, 'source t', filled=False, size=14)
            chip(d, 1330, y-10, 120, 34, TEAL, 'local t', filled=True, size=14)
    d.save()


# ------------------------------------------------------------------ Figure 2: converging embedding pipeline
def fig2():
    d = Diagram('Fig2_embedding_pipeline', 1500, 560)
    lanes = [(95, 'frontal', BLUE, LBLUE), (270, 'lateral', TEAL, '#9DD3CD'), (445, 'history', OCHRE, '#E6C79A')]
    ic_xray(d, 90, 95, 1.1); ic_xray(d, 90, 270, 1.1, lateral=True); ic_doc(d, 90, 445, 1.1, OCHRE)
    for y, lab, col, _ in lanes:
        d.text(20, y+44, 140, 26, lab, 16, col, True)
    d.line([(130, 445), (215, 445)], color=OCHRE, width=2.5)
    ic_doc(d, 265, 445, 1.1, OCHRE, mode='sections')
    d.shape(400, 40, 200, 290, f'rounded=1;arcSize=8;fillColor={PALE};strokeColor=none;')
    ic_network(d, 495, 185, 1.25, BLUE, LBLUE)
    d.text(400, 290, 200, 30, 'BiomedCLIP', 18, NAVY, True)
    d.shape(400, 370, 200, 160, f'rounded=1;arcSize=8;fillColor={PALE};strokeColor=none;')
    ic_network(d, 495, 440, 1.1, OCHRE, '#E6C79A')
    d.text(400, 490, 200, 30, 'BiomedBERT', 18, NAVY, True)
    d.line([(130, 95), (400, 95)], color=BLUE, width=2.5); d.line([(130, 270), (400, 270)], color=TEAL, width=2.5); d.line([(315, 445), (400, 445)], color=OCHRE, width=2.5)
    for y, lab, col, light in lanes:
        d.line([(600, y), (660, y)], color=col, width=2.5)
        n = 10 if lab != 'history' else 14
        for k in range(n):
            d.shape(670+k*15, y-16, 12, 32, f'rounded=0;fillColor={col if k % 3 == 0 else light};strokeColor=none;')
        d.text(670, y+20, n*15, 24, '768' if lab == 'history' else '512', 15, col, True)
    sx, sw = 960, 54
    segs = [(80, 150, BLUE, False), (150, 260, TEAL, True), (260, 430, OCHRE, True)]
    d.shape(sx-10, 70, sw+20, 380, f'rounded=1;arcSize=10;fillColor=none;strokeColor={NAVY};strokeWidth=2;')
    for y0, y1, col, _ in segs:
        d.shape(sx, y0, sw, y1-y0-6, f'rounded=0;fillColor={col};strokeColor=none;')
    for (y, lab, col, _), (y0, y1, _, _) in zip(lanes, segs):
        ex = 670+(10 if lab != 'history' else 14)*15+6
        d.line([(ex, y), (sx-14, (y0+y1)/2)], color=col, width=2.5)
    d.text(sx-50, 455, sw+100, 30, '0 if absent', 14, GREY, italic=True)
    d.line([(sx+sw+12, 260), (1110, 260)], color=NAVY, width=3)
    ic_network(d, 1175, 260, 1.15, NAVY, '#9AA8B4', lock=False)
    d.text(1095, 320, 160, 50, 'logistic heads<br>+ temperature', 15, NAVY)
    d.line([(1245, 260), (1300, 260)], color=NAVY, width=3)
    for k, wv in enumerate([0.85, 0.2, 0.62, 0.1, 0.45, 0.93, 0.3]):
        d.shape(1315, 185+k*22, 150, 14, f'rounded=0;fillColor={LGREY};strokeColor=none;')
        d.shape(1315, 185+k*22, 150*wv, 14, f'rounded=0;fillColor={NAVY};strokeColor=none;')
    d.text(1300, 345, 180, 28, '14 findings', 15, NAVY, True)
    d.save()


# ------------------------------------------------------------------ Figure 3: referral threshold and workload budget
def fig3():
    d = Diagram('Fig3_routing', 1070, 510)

    def rule(x1, y1, x2, y2, color=GREY, width=2, arrow=True):
        d.line([(x1, y1), (x2, y2)], color=color, width=width, arrow=arrow)

    def panel(letter, name, y):
        d.text(2, y, 34, 32, letter, 26, NAVY, True)
        d.text(40, y, 960, 32, name, 23, NAVY, True, 'left')

    panel('A', 'Referral at a specified missed-finding target', 0)
    ic_xray(d, 53, 103, 0.77)
    ic_doc(d, 109, 103, 0.68)
    d.text(1, 149, 165, 48, 'Frontal image and<br>available history', 17)
    rule(160, 103, 208, 103, NAVY, 2.5)
    for k, p in enumerate([0.87, 0.22, 0.51, 0.3, 0.78, 0.42, 0.17]):
        d.shape(228, 68 + k * 10, 84, 6, 'fillColor=' + LGREY + ';strokeColor=none;')
        d.shape(228, 68 + k * 10, 84 * p, 6, 'fillColor=' + NAVY + ';strokeColor=none;')
    d.text(199, 149, 145, 48, '14 calibrated<br>probabilities', 17)
    rule(325, 103, 366, 103, NAVY, 2.5)
    d.shape(378, 72, 62, 62, 'ellipse;fillColor=' + LTEAL + ';strokeColor=' + NAVY + ';strokeWidth=2.4;')
    d.text(378, 73, 62, 60, '<i>s</i>', 27, NAVY, True)
    d.text(344, 149, 131, 48, 'Patient-level<br>risk score', 17)
    rule(450, 103, 503, 103, NAVY, 2.5)
    d.shape(518, 88, 238, 30, 'fillColor=' + LTEAL + ';strokeColor=none;')
    d.shape(756, 88, 257, 30, 'fillColor=' + LOCHRE + ';strokeColor=none;')
    d.shape(518, 88, 495, 30, 'fillColor=none;strokeColor=' + NAVY + ';strokeWidth=1.4;')
    rule(756, 76, 756, 130, NAVY, 3, False)
    d.text(643, 39, 226, 33, 'Calibrated threshold <i>t</i>', 18, NAVY, True)
    ic_check(d, 550, 161, 0.52)
    d.text(578, 140, 150, 41, 'ANSWER', 20, TEAL, True, 'left')
    d.text(578, 176, 140, 27, '<i>s</i> &lt; <i>t</i>', 18, NAVY, False, 'left')
    ic_reviewer(d, 807, 161, 0.55)
    d.text(842, 140, 172, 41, 'ESCALATE', 20, OCHRE, True, 'left')
    d.text(842, 176, 140, 27, '<i>s</i> &#8805; <i>t</i>', 18, NAVY, False, 'left')
    rule(8, 220, 1039, 220, LGREY, 1.4, False)

    panel('B', 'Action selection under a workload budget', 238)
    d.text(14, 279, 535, 29, 'Expected workload per eligible action', 18, GREY, False, 'left')
    actions = [
        (73, 'Answer', '0', TEAL),
        (211, 'Escalate', '1.00', OCHRE),
        (350, 'Ask for history', '0.15', OCHRE),
        (494, 'Ask for lateral', '0.40', BLUE),
    ]
    ic_check(d, actions[0][0], 357, 0.76)
    ic_reviewer(d, actions[1][0], 356, 0.78)
    ic_doc(d, actions[2][0], 357, 0.74)
    ic_xray(d, actions[3][0], 357, 0.74, lateral=True)
    for x, label, units, color in actions:
        d.text(x - 74, 399, 148, 32, label, 17, color, True)
        d.text(x - 65, 432, 130, 30, units, 20, NAVY, True)
    rule(580, 365, 624, 365, NAVY, 2.5)
    d.shape(634, 292, 402, 155, 'rounded=1;arcSize=10;fillColor=' + PALE + ';strokeColor=none;')
    d.text(648, 306, 375, 34, 'Select the lowest-cost action', 19, NAVY, True)
    d.text(650, 350, 370, 32, 'Expected loss + &#955; &#215; workload', 19, NAVY)
    d.text(652, 393, 365, 30, 'Mean budget: 0.30 reviews per patient', 17, GREY)
    d.save()


if __name__ == '__main__':
    fig1(); fig2(); fig3()
