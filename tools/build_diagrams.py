"""Build the draw.io file and SVG diagrams for the College Registration System.

One set of model data drives every output, so the draw.io diagram, the SVG
images and the one-page specification always agree.

Usage:  python3 tools/build_diagrams.py
Writes: diagrams/college_registration.drawio
        diagrams/conceptual_model.svg
        diagrams/relational_schema.svg
"""
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "diagrams"

# ---------------------------------------------------------------- relational
# (key, column, data type + constraints)
TABLES = {
    "DEPARTMENT": [
        ("PK", "department_id", "INT"),
        ("UQ", "department_code", "VARCHAR(10)"),
        ("", "department_name", "VARCHAR(100)"),
        ("", "office_location", "VARCHAR(100) NULL"),
        ("", "phone", "VARCHAR(20) NULL"),
    ],
    "PROGRAMME": [
        ("PK", "programme_id", "INT"),
        ("UQ", "programme_code", "VARCHAR(10)"),
        ("", "programme_name", "VARCHAR(120)"),
        ("", "award_level", "VARCHAR(20)"),
        ("", "duration_years", "SMALLINT"),
        ("FK", "department_id", "INT"),
    ],
    "LECTURER": [
        ("PK", "lecturer_id", "INT"),
        ("UQ", "staff_number", "VARCHAR(20)"),
        ("", "title", "VARCHAR(10) NULL"),
        ("", "first_name", "VARCHAR(50)"),
        ("", "last_name", "VARCHAR(50)"),
        ("UQ", "email", "VARCHAR(100)"),
        ("", "phone", "VARCHAR(20) NULL"),
        ("FK", "department_id", "INT"),
    ],
    "STUDENT": [
        ("PK", "student_id", "INT"),
        ("UQ", "reg_number", "VARCHAR(20)"),
        ("", "first_name", "VARCHAR(50)"),
        ("", "last_name", "VARCHAR(50)"),
        ("", "gender", "CHAR(1)"),
        ("", "date_of_birth", "DATE"),
        ("UQ", "email", "VARCHAR(100)"),
        ("", "phone", "VARCHAR(20) NULL"),
        ("", "admission_date", "DATE"),
        ("", "status", "VARCHAR(15)"),
        ("FK", "programme_id", "INT"),
    ],
    "PROGRAMME_COURSE": [
        ("PK,FK", "programme_id", "INT"),
        ("PK,FK", "course_id", "INT"),
        ("", "year_of_study", "SMALLINT"),
        ("", "semester_no", "SMALLINT"),
        ("", "is_core", "BOOLEAN"),
    ],
    "COURSE": [
        ("PK", "course_id", "INT"),
        ("UQ", "course_code", "VARCHAR(10)"),
        ("", "course_title", "VARCHAR(120)"),
        ("", "credit_units", "SMALLINT"),
        ("FK", "lecturer_id", "INT"),
    ],
    "REGISTRATION": [
        ("PK", "registration_id", "INT"),
        ("FK", "student_id", "INT"),
        ("FK", "course_id", "INT"),
        ("", "academic_year", "CHAR(9)"),
        ("", "semester_no", "SMALLINT"),
        ("", "registration_date", "DATE"),
        ("", "status", "VARCHAR(15)"),
        ("", "final_grade", "VARCHAR(2) NULL"),
    ],
}

TW, HEAD, ROW = 250, 28, 21          # table width, header height, row height
POS = {
    "PROGRAMME": (40, 20),
    "DEPARTMENT": (430, 20),
    "LECTURER": (820, 20),
    "PROGRAMME_COURSE": (430, 235),
    "COURSE": (820, 300),
    "STUDENT": (40, 280),
    "REGISTRATION": (430, 440),
}
REL_W, REL_H = 1110, 670


def box(name):
    x, y = POS[name]
    return x, y, TW, HEAD + ROW * len(TABLES[name])


# (parent "one" table, child "many" table, child-end marker, route, label)
# route: list of points from the parent edge to the child edge.
def _rel_routes():
    def b(n):
        return box(n)
    px, py, pw, ph = b("PROGRAMME")
    dx, dy, dw, dh = b("DEPARTMENT")
    lx, ly, lw, lh = b("LECTURER")
    sx, sy, sw, sh = b("STUDENT")
    cx, cy, cw, ch = b("COURSE")
    qx, qy, qw, qh = b("PROGRAMME_COURSE")
    rx, ry, rw, rh = b("REGISTRATION")
    return [
        ("DEPARTMENT", "PROGRAMME", "many0", [(dx, dy + 70), (px + pw, dy + 70)], "offers"),
        ("DEPARTMENT", "LECTURER", "many0", [(dx + dw, dy + 70), (lx, dy + 70)], "employs"),
        ("PROGRAMME", "STUDENT", "many0", [(px + 125, py + ph), (px + 125, sy)], "enrols"),
        ("PROGRAMME", "PROGRAMME_COURSE", "many1",
         [(px + pw, py + ph - 20), (px + pw + 70, py + ph - 20), (px + pw + 70, qy + 50), (qx, qy + 50)], "includes"),
        ("COURSE", "PROGRAMME_COURSE", "many0",
         [(cx, cy + 40), (cx - 70, cy + 40), (cx - 70, qy + 50), (qx + qw, qy + 50)], "belongs to"),
        ("LECTURER", "COURSE", "many0", [(lx + 125, ly + lh), (lx + 125, cy)], "coordinates"),
        ("STUDENT", "REGISTRATION", "many0",
         [(sx + sw, sy + 200), (sx + sw + 70, sy + 200), (sx + sw + 70, ry + 60), (rx, ry + 60)], "makes"),
        ("COURSE", "REGISTRATION", "many0",
         [(cx + 125, cy + ch), (cx + 125, ry + 60), (rx + rw, ry + 60)], "is taken in"),
    ]


REL_EDGES = _rel_routes()

# ---------------------------------------------------------------- conceptual
ENTITIES = {
    "DEPARTMENT": ["department_id (PK)", "department_name"],
    "PROGRAMME": ["programme_id (PK)", "programme_name", "award_level", "duration_years"],
    "LECTURER": ["lecturer_id (PK)", "staff_number", "name", "email"],
    "STUDENT": ["student_id (PK)", "reg_number", "name", "date_of_birth", "email", "status"],
    "COURSE": ["course_id (PK)", "course_code", "course_title", "credit_units"],
    "REGISTRATION": ["registration_id (PK)", "academic_year", "semester_no", "status", "final_grade"],
}
EW, EHEAD, EROW = 210, 30, 19
EPOS = {
    "PROGRAMME": (40, 30), "DEPARTMENT": (450, 30), "LECTURER": (860, 30),
    "STUDENT": (40, 330), "REGISTRATION": (450, 400), "COURSE": (860, 330),
}
CON_W, CON_H = 1110, 560
DW, DH = 112, 56   # diamond


def ebox(n):
    x, y = EPOS[n]
    return x, y, EW, EHEAD + EROW * len(ENTITIES[n])


def _con_rels():
    """(name, diamond centre, (entity A, point, card), (entity B, point, card))."""
    px, py, pw, ph = ebox("PROGRAMME")
    dx, dy, dw, dh = ebox("DEPARTMENT")
    lx, ly, lw, lh = ebox("LECTURER")
    sx, sy, sw, sh = ebox("STUDENT")
    cx, cy, cw, ch = ebox("COURSE")
    rx, ry, rw, rh = ebox("REGISTRATION")
    return [
        ("offers", (345, dy + 45), ("DEPARTMENT", (dx, dy + 45), "1"), ("PROGRAMME", (px + pw, dy + 45), "N")),
        ("employs", (765, dy + 45), ("DEPARTMENT", (dx + dw, dy + 45), "1"), ("LECTURER", (lx, dy + 45), "N")),
        ("enrols in", (px + 105, 250), ("PROGRAMME", (px + 105, py + ph), "1"), ("STUDENT", (px + 105, sy), "N")),
        ("includes", (555, 250), ("PROGRAMME", (px + pw, py + ph - 20), "M"), ("COURSE", (cx, cy + 20), "N")),
        ("coordinates", (cx + 105, 250), ("LECTURER", (cx + 105, ly + lh), "1"), ("COURSE", (cx + 105, cy), "N")),
        ("makes", (345, ry + 50), ("STUDENT", (sx + sw, ry + 50), "1"), ("REGISTRATION", (rx, ry + 50), "N")),
        ("is for", (765, ry + 20), ("COURSE", (cx, ry + 20), "1"), ("REGISTRATION", (rx + rw, ry + 20), "N")),
    ]


CON_RELS = _con_rels()

# ---------------------------------------------------------------- colours
C = {
    "head": "#1f4e79", "headtext": "#ffffff", "body": "#ffffff", "line": "#1f4e79",
    "pk": "#fff2cc", "fk": "#dae8fc", "text": "#1a1a1a", "muted": "#5b6470",
    "ent": "#dae8fc", "diam": "#fff2cc", "diamline": "#b38600",
}


# ================================================================ SVG output
def _svg_defs():
    l = C["line"]
    return f"""<defs>
<marker id="one" viewBox="0 0 20 20" refX="0" refY="10" markerWidth="20" markerHeight="20" orient="auto-start-reverse" markerUnits="userSpaceOnUse">
  <path d="M6 3 V17 M11 3 V17" stroke="{l}" stroke-width="1.6" fill="none"/></marker>
<marker id="many0" viewBox="0 0 26 20" refX="26" refY="10" markerWidth="26" markerHeight="20" orient="auto" markerUnits="userSpaceOnUse">
  <path d="M26 2 L14 10 L26 18 M14 10 H26" stroke="{l}" stroke-width="1.6" fill="none"/>
  <circle cx="8" cy="10" r="4.5" fill="#fff" stroke="{l}" stroke-width="1.6"/></marker>
<marker id="many1" viewBox="0 0 26 20" refX="26" refY="10" markerWidth="26" markerHeight="20" orient="auto" markerUnits="userSpaceOnUse">
  <path d="M26 2 L14 10 L26 18 M14 10 H26 M9 3 V17" stroke="{l}" stroke-width="1.6" fill="none"/></marker>
</defs>"""


def relational_svg():
    font = "font-family=\"Segoe UI, Helvetica, Arial, sans-serif\""
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="30 10 {REL_W - 50} {REL_H - 15}" {font}>', _svg_defs(),
         f'<rect width="{REL_W}" height="{REL_H}" fill="#ffffff"/>']
    for parent, child, mk, pts, label in REL_EDGES:
        d = "M" + " L".join(f"{x} {y}" for x, y in pts)
        p.append(f'<path d="{d}" fill="none" stroke="{C["line"]}" stroke-width="1.6" '
                 f'marker-start="url(#one)" marker-end="url(#{mk})"/>')
        (x1, y1), (x2, y2) = pts[len(pts) // 2 - 1], pts[len(pts) // 2]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        if x1 == x2:        # vertical segment: label to the right
            p.append(f'<text x="{mx + 6}" y="{my + 4}" font-size="11" font-style="italic" fill="{C["muted"]}">{label}</text>')
        else:
            p.append(f'<text x="{mx}" y="{my - 6}" font-size="11" font-style="italic" text-anchor="middle" fill="{C["muted"]}">{label}</text>')
    for name, cols in TABLES.items():
        x, y, w, h = box(name)
        p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{C["body"]}" stroke="{C["line"]}" stroke-width="1.4"/>')
        p.append(f'<path d="M{x} {y + HEAD} V{y + 4} Q{x} {y} {x + 4} {y} H{x + w - 4} Q{x + w} {y} {x + w} {y + 4} V{y + HEAD} Z" fill="{C["head"]}"/>')
        p.append(f'<text x="{x + w / 2}" y="{y + 19}" font-size="13" font-weight="700" text-anchor="middle" fill="{C["headtext"]}">{name}</text>')
        for i, (k, col, typ) in enumerate(cols):
            ry = y + HEAD + i * ROW
            fill = C["pk"] if "PK" in k else (C["fk"] if k == "FK" else None)
            if fill:
                p.append(f'<rect x="{x + 1}" y="{ry}" width="{w - 2}" height="{ROW}" fill="{fill}"/>')
            if i:
                p.append(f'<line x1="{x}" y1="{ry}" x2="{x + w}" y2="{ry}" stroke="#e3e7ec"/>')
            bold = ' font-weight="700"' if "PK" in k else ""
            under = ' text-decoration="underline"' if "PK" in k else ""
            p.append(f'<text x="{x + 6}" y="{ry + 15}" font-size="10" font-weight="700" fill="{C["muted"]}">{k}</text>')
            p.append(f'<text x="{x + 44}" y="{ry + 15}" font-size="11.5"{bold}{under} fill="{C["text"]}">{col}</text>')
            p.append(f'<text x="{x + w - 6}" y="{ry + 15}" font-size="10.5" text-anchor="end" fill="{C["muted"]}">{escape(typ)}</text>')
    p.append("</svg>")
    return "\n".join(p)


def conceptual_svg():
    font = "font-family=\"Segoe UI, Helvetica, Arial, sans-serif\""
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="25 15 {CON_W - 45} {CON_H - 25}" {font}>',
         f'<rect width="{CON_W}" height="{CON_H}" fill="#ffffff"/>']
    for name, (cx, cy), (ea, pa, ca), (eb, pb, cb) in CON_RELS:
        for (px_, py_), card in ((pa, ca), (pb, cb)):
            p.append(f'<line x1="{px_}" y1="{py_}" x2="{cx}" y2="{cy}" stroke="{C["line"]}" stroke-width="1.6"/>')
            # place the cardinality just outside the entity
            ox = 10 if px_ < cx else (-10 if px_ > cx else 8)
            oy = -6 if py_ == cy else (16 if py_ < cy else -6)
            anchor = "start" if px_ <= cx else "end"
            p.append(f'<text x="{px_ + ox}" y="{py_ + oy}" font-size="13" font-weight="700" text-anchor="{anchor}" fill="#c0392b">{card}</text>')
        pts = f"{cx},{cy - DH / 2} {cx + DW / 2},{cy} {cx},{cy + DH / 2} {cx - DW / 2},{cy}"
        p.append(f'<polygon points="{pts}" fill="{C["diam"]}" stroke="{C["diamline"]}" stroke-width="1.6"/>')
        p.append(f'<text x="{cx}" y="{cy + 4}" font-size="11.5" font-style="italic" text-anchor="middle" fill="{C["text"]}">{name}</text>')
    for name, attrs in ENTITIES.items():
        x, y, w, h = ebox(name)
        p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{C["ent"]}" stroke="{C["line"]}" stroke-width="1.6"/>')
        p.append(f'<text x="{x + w / 2}" y="{y + 20}" font-size="14" font-weight="700" text-anchor="middle" fill="{C["head"]}">{name}</text>')
        p.append(f'<line x1="{x}" y1="{y + EHEAD - 2}" x2="{x + w}" y2="{y + EHEAD - 2}" stroke="{C["line"]}"/>')
        for i, a in enumerate(attrs):
            key = "(PK)" in a
            txt = a.replace(" (PK)", "")
            deco = ' text-decoration="underline" font-weight="700"' if key else ""
            p.append(f'<text x="{x + 12}" y="{y + EHEAD + 12 + i * EROW}" font-size="12"{deco} fill="{C["text"]}">{txt}</text>')
    p.append("</svg>")
    return "\n".join(p)


# ============================================================= draw.io output
def _cell(id_, value, style, x, y, w, h, parent="1"):
    return (f'<mxCell id="{id_}" value="{escape(value, {chr(34): "&quot;"})}" style="{style}" vertex="1" parent="{parent}">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')


def _edge(id_, src, tgt, style, value="", points=()):
    pts = ""
    if points:
        pts = '<Array as="points">' + "".join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in points) + "</Array>"
    return (f'<mxCell id="{id_}" value="{escape(value)}" style="{style}" edge="1" parent="1" source="{src}" target="{tgt}">'
            f'<mxGeometry relative="1" as="geometry">{pts}</mxGeometry></mxCell>')


def _anchor(name, pt, boxfn):
    """Express an absolute point on a box edge as draw.io exit/entry fractions."""
    x, y, w, h = boxfn(name)
    return round((pt[0] - x) / w, 3), round((pt[1] - y) / h, 3)


def drawio_relational():
    cells = []
    tid = {n: f"t_{n.lower()}" for n in TABLES}
    for name, cols in TABLES.items():
        x, y, w, h = box(name)
        cells.append(_cell(tid[name], name,
                           "swimlane;fontStyle=1;childLayout=stackLayout;horizontal=1;startSize=28;horizontalStack=0;"
                           "resizeParent=1;resizeLast=0;collapsible=1;marginBottom=0;rounded=1;arcSize=4;"
                           f"fillColor={C['head']};fontColor=#ffffff;strokeColor={C['line']};swimlaneFillColor=#ffffff;fontSize=13;",
                           x, y, w, h))
        for i, (k, col, typ) in enumerate(cols):
            fill = C["pk"] if "PK" in k else (C["fk"] if k == "FK" else "none")
            fs = "fontStyle=5;" if "PK" in k else ""
            label = f"{k:<6}" if k else ""
            cells.append(_cell(f"{tid[name]}_{i}", f"{label}{col} : {typ}",
                               f"text;strokeColor=none;fillColor={fill};align=left;verticalAlign=middle;spacingLeft=6;"
                               f"spacingRight=4;overflow=hidden;rotatable=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;"
                               f"fontSize=11;fontFamily=Helvetica;{fs}",
                               0, HEAD + i * ROW, w, ROW, parent=tid[name]))
    for j, (parent, child, mk, pts, label) in enumerate(REL_EDGES):
        ex, ey = _anchor(parent, pts[0], box)
        nx, ny = _anchor(child, pts[-1], box)
        end = "ERoneToMany" if mk == "many1" else "ERzeroToMany"
        style = (f"edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;startArrow=ERmandOne;endArrow={end};"
                 f"startFill=0;endFill=0;strokeWidth=1.5;strokeColor={C['line']};fontStyle=2;fontSize=11;"
                 f"exitX={ex};exitY={ey};exitDx=0;exitDy=0;entryX={nx};entryY={ny};entryDx=0;entryDy=0;"
                 f"labelBackgroundColor=#ffffff;")
        cells.append(_edge(f"r{j}", tid[parent], tid[child], style, label, pts[1:-1]))
    return cells


def drawio_conceptual():
    cells = []
    eid = {n: f"e_{n.lower()}" for n in ENTITIES}
    for name, attrs in ENTITIES.items():
        x, y, w, h = ebox(name)
        body = "<br>".join(f"<u><b>{a.replace(' (PK)', '')}</b></u>" if "(PK)" in a else a for a in attrs)
        value = f"<b style='font-size:14px;color:{C['head']}'>{name}</b><hr>{body}"
        cells.append(_cell(eid[name], value,
                           f"rounded=1;arcSize=6;whiteSpace=wrap;html=1;fillColor={C['ent']};strokeColor={C['line']};"
                           "align=left;verticalAlign=top;spacingLeft=10;spacingTop=4;fontSize=12;strokeWidth=1.5;",
                           x, y, w, h))
    for j, (name, (cx, cy), a, b) in enumerate(CON_RELS):
        did = f"d{j}"
        cells.append(_cell(did, name,
                           f"rhombus;whiteSpace=wrap;html=1;fillColor={C['diam']};strokeColor={C['diamline']};"
                           "fontStyle=2;fontSize=11;strokeWidth=1.5;",
                           cx - DW / 2, cy - DH / 2, DW, DH))
        for k, (ent, pt, card) in enumerate((a, b)):
            ex, ey = _anchor(ent, pt, ebox)
            style = (f"endArrow=none;html=1;strokeWidth=1.5;strokeColor={C['line']};fontStyle=1;fontSize=13;"
                     f"fontColor=#c0392b;exitX={ex};exitY={ey};exitDx=0;exitDy=0;labelBackgroundColor=#ffffff;")
            e = _edge(f"d{j}_{k}", eid[ent], did, style)
            # cardinality label sits next to the entity end of the line
            e = e.replace("</mxGeometry>",
                          "</mxGeometry></mxCell>"
                          f'<mxCell id="d{j}_{k}_l" value="{card}" style="edgeLabel;html=1;align=center;verticalAlign=middle;'
                          f'fontStyle=1;fontSize=13;fontColor=#c0392b;labelBackgroundColor=#ffffff;" vertex="1" connectable="0" parent="d{j}_{k}">'
                          '<mxGeometry x="-0.75" relative="1" as="geometry"><mxPoint as="offset"/></mxGeometry>', 1)
            cells.append(e)
    return cells


def _diagram(id_, name, cells, w, h):
    return (f'<diagram id="{id_}" name="{name}"><mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" '
            f'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{w}" pageHeight="{h}" '
            f'math="0" shadow="0"><root><mxCell id="0"/><mxCell id="1" parent="0"/>{"".join(cells)}</root>'
            f'</mxGraphModel></diagram>')


def drawio_file():
    return ('<mxfile host="app.diagrams.net" agent="build_diagrams.py" version="24.0.0">'
            + _diagram("conceptual", "1. Conceptual Model (ERD)", drawio_conceptual(), CON_W + 40, CON_H + 40)
            + _diagram("relational", "2. Relational Schema", drawio_relational(), REL_W + 40, REL_H + 40)
            + "</mxfile>\n")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "college_registration.drawio").write_text(drawio_file(), encoding="utf-8")
    (OUT / "conceptual_model.svg").write_text(conceptual_svg(), encoding="utf-8")
    (OUT / "relational_schema.svg").write_text(relational_svg(), encoding="utf-8")
    print("wrote", ", ".join(p.name for p in sorted(OUT.iterdir())))
