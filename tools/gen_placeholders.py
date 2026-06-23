#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네트워크/키 없이 문서마다 브랜드 톤의 히어로 일러스트(SVG)를 생성한다.
- 그룹별 색·엠블럼으로 구분되는 '경복궁 옆 서촌 한옥' 콘셉트 장면(해+능선+한옥 지붕).
- 결과: viewer/assets/<문서>.svg
- AI 사진(<문서>.png)을 나중에 넣으면 build.py가 PNG를 우선 사용(자동 업그레이드).
사용: python3 tools/gen_placeholders.py  →  python3 viewer/build.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "viewer", "assets")

# (relpath, group) — build.py의 DOCS와 동기화
DOCS = [
    ("docs/문서-지도.md","idx"), ("README.md","idx"),
    ("docs/작가-소개.md","A"), ("docs/브랜드-정의서.md","A"),
    ("docs/홈페이지-사이트맵.md","B"), ("docs/홈-랜딩-카피.md","B"),
    ("docs/pages/소개.md","B"), ("docs/pages/공간소개.md","B"), ("docs/pages/작가들.md","B"),
    ("docs/pages/소식.md","B"), ("docs/pages/합류하기.md","B"), ("docs/pages/문의.md","B"),
    ("docs/작가-운영정책.md","C"), ("docs/입점-동의서.md","C"), ("docs/운영-매뉴얼.md","C"),
    ("docs/작가-모집-키트.md","D"),
    ("docs/사업계획서.md","E"), ("docs/성과지표-KPI.md","E"),
    ("docs/정관-거버넌스.md","E"), ("docs/상표-IP-보호-메모.md","E"),
    ("docs/헐버트작가촌-기획.md","F"),
    ("docs/손님-매장안내.md","G"), ("docs/en/hulbert-en.md","G"),
    ("docs/legal/개인정보처리방침.md","H"), ("docs/legal/이용약관.md","H"), ("docs/legal/사업자정보.md","H"),
]

PAL = {
 "idx":dict(s1="#f4eee2",s2="#e7d6bd",h1="#dcc8a6",h2="#c4a87d",h3="#a4855b",sun="#e8b15e",roof="#574635",ac="#9c5b34"),
 "A":dict(s1="#f8ede2",s2="#f0d9c4",h1="#e3b894",h2="#cc8f61",h3="#aa683e",sun="#ea9a4c",roof="#583826",ac="#9c5b34"),
 "B":dict(s1="#fdf4df",s2="#f8e3bb",h1="#edcf8f",h2="#daad5e",h3="#bf8940",sun="#f1b549",roof="#5d4626",ac="#c0892c"),
 "C":dict(s1="#eef3e7",s2="#dde8cd",h1="#bcce9e",h2="#92ad73",h3="#6c8a52",sun="#cdda86",roof="#3d4c33",ac="#2f6b63"),
 "D":dict(s1="#fdeee6",s2="#fbd7c4",h1="#f4b398",h2="#e28765",h3="#c46141",sun="#f69a68",roof="#5d3225",ac="#c2502f"),
 "E":dict(s1="#eef0f5",s2="#dbe0ec",h1="#b8c2d4",h2="#8d9ab5",h3="#697693",sun="#adbad4",roof="#383f53",ac="#2f6db0"),
 "F":dict(s1="#f3ecf4",s2="#e7d4e8",h1="#ccb0ce",h2="#a682ac",h3="#815d88",sun="#c79bcc",roof="#453649",ac="#6b4ea8"),
 "G":dict(s1="#f1efea",s2="#e1ddd3",h1="#cdc6b8",h2="#aaa293",h3="#847c6f",sun="#d0c8b6",roof="#4a453c",ac="#8a8278"),
 "H":dict(s1="#eceef1",s2="#d9dde3",h1="#bbc3cc",h2="#919ba7",h3="#6d7782",sun="#b6c0ca",roof="#373d45",ac="#59636f"),
}

def emblem(g, cx, cy, col):
    """그룹별 작은 엠블럼(추상 도형)."""
    o = f'<circle cx="{cx}" cy="{cy}" r="50" fill="#fff" fill-opacity=".34"/>'
    o += f'<circle cx="{cx}" cy="{cy}" r="50" fill="none" stroke="{col}" stroke-width="2.5" stroke-opacity=".7"/>'
    s = ""
    if g == "idx":
        for dx in (-14,14):
            for dy in (-14,14):
                s += f'<circle cx="{cx+dx}" cy="{cy+dy}" r="6.5" fill="{col}"/>'
    elif g == "A":
        for k,dx in enumerate((-16,0,16)):
            s += f'<circle cx="{cx+dx}" cy="{cy-10+k*10}" r="6.5" fill="{col}"/>'
    elif g == "B":
        s += f'<path d="M{cx-18},{cy+16} V{cy-2} L{cx},{cy-18} L{cx+18},{cy-2} V{cy+16} Z" fill="none" stroke="{col}" stroke-width="3.5" stroke-linejoin="round"/>'
    elif g == "C":
        s += f'<circle cx="{cx-9}" cy="{cy}" r="13" fill="none" stroke="{col}" stroke-width="3.5"/>'
        s += f'<circle cx="{cx+9}" cy="{cy}" r="13" fill="none" stroke="{col}" stroke-width="3.5"/>'
    elif g == "D":
        s += f'<path d="M{cx},{cy+16} V{cy-16} M{cx-11},{cy-5} L{cx},{cy-16} L{cx+11},{cy-5}" fill="none" stroke="{col}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>'
    elif g == "E":
        for k,dx in enumerate((-15,0,15)):
            h = (12,22,16)[k]
            s += f'<rect x="{cx+dx-4}" y="{cy+16-h}" width="8" height="{h}" rx="2" fill="{col}"/>'
    elif g == "F":
        s += f'<path d="M{cx},{cy-18} L{cx+5},{cy-5} L{cx+18},{cy} L{cx+5},{cy+5} L{cx},{cy+18} L{cx-5},{cy+5} L{cx-18},{cy} L{cx-5},{cy-5} Z" fill="{col}"/>'
    elif g == "G":
        s += f'<rect x="{cx-14}" y="{cy-14}" width="28" height="28" rx="4" fill="none" stroke="{col}" stroke-width="3.5"/>'
    elif g == "H":
        s += f'<path d="M{cx},{cy-18} L{cx+16},{cy-10} V{cy+2} Q{cx+16},{cy+16} {cx},{cy+20} Q{cx-16},{cy+16} {cx-16},{cy+2} V{cy-10} Z" fill="none" stroke="{col}" stroke-width="3.2" stroke-linejoin="round"/>'
    return o + s

def hill(base, amp, color, phase=0):
    c1 = base - amp
    c2 = base - amp*0.35 + phase
    return (f'<path d="M0,{base} Q400,{c1} 800,{c2} T1600,{base} L1600,700 L0,700 Z" '
            f'fill="{color}"/>')

def svg_for(g, idx):
    p = PAL[g]
    sun_x = 1140 + (idx*53 % 230)          # 해 위치를 문서마다 살짝 다르게
    ph = (idx*37 % 60) - 30                 # 능선 위상 변화
    cx = 740 + (idx*29 % 160)               # 한옥 위치 변화
    ry, rw, rh = 452, 150, 78
    body_top, body_bot = ry, 520
    parts = []
    parts.append(f'<rect width="1600" height="700" fill="url(#sky)"/>')
    # 해 + 은은한 후광
    parts.append(f'<circle cx="{sun_x}" cy="190" r="115" fill="{p["sun"]}" fill-opacity=".18"/>')
    parts.append(f'<circle cx="{sun_x}" cy="190" r="72" fill="{p["sun"]}"/>')
    # 능선 3겹 (뒤→앞)
    parts.append(hill(470, 150, p["h1"], ph))
    parts.append(hill(516, 120, p["h2"], -ph))
    # 한옥: 기둥(몸체) + 지붕 실루엣
    parts.append(f'<rect x="{cx-rw*0.5:.0f}" y="{body_top}" width="{rw:.0f}" height="{body_bot-body_top}" fill="{p["roof"]}" fill-opacity=".92"/>')
    parts.append(f'<rect x="{cx-12:.0f}" y="{body_top+18}" width="24" height="{body_bot-body_top-18}" fill="{p["s1"]}" fill-opacity=".55"/>')
    roof = (f'M{cx-rw},{ry} C{cx-rw*0.5:.0f},{ry-rh} {cx+rw*0.5:.0f},{ry-rh} {cx+rw},{ry} '
            f'C{cx+rw*0.55:.0f},{ry-rh*0.46:.0f} {cx-rw*0.55:.0f},{ry-rh*0.46:.0f} {cx-rw},{ry} Z')
    parts.append(f'<path d="{roof}" fill="{p["roof"]}"/>')
    parts.append(f'<rect x="{cx-rw-14:.0f}" y="{ry-6}" width="{rw*2+28:.0f}" height="9" rx="4" fill="{p["roof"]}"/>')
    # 맨 앞 능선이 한옥 아랫부분을 자연스럽게 덮음
    parts.append(hill(560, 96, p["h3"], ph*0.5))
    # 그룹 엠블럼
    parts.append(emblem(g, 1410, 110, p["ac"]))
    inner = "".join(parts)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 700" '
            f'role="img" aria-label="헐버트 문서 일러스트">'
            f'<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{p["s1"]}"/><stop offset="1" stop-color="{p["s2"]}"/>'
            f'</linearGradient></defs>{inner}</svg>')

def main():
    os.makedirs(ASSETS, exist_ok=True)
    n = 0
    for idx, (rel, g) in enumerate(DOCS):
        base = os.path.basename(rel)
        slug = base[:-3] if base.endswith(".md") else base
        out = os.path.join(ASSETS, slug + ".svg")
        with open(out, "w", encoding="utf-8") as f:
            f.write(svg_for(g, idx))
        n += 1
    print(f"WROTE {n} SVG → {ASSETS}")
    print("다음: python3 viewer/build.py")

if __name__ == "__main__":
    main()
