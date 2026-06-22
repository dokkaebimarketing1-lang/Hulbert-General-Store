#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""헐버트 프로젝트 문서 → 단일 HTML 뷰어 빌드 (외부 의존성 없음)."""
import re, os, html as htmllib
import markdown

# 저장소 루트 = 이 스크립트(viewer/build.py)의 상위 폴더
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, "viewer", "index.html")

# (relpath, group_key, group_label) — 문서-지도.md §2 그룹 순서
DOCS = [
    ("docs/문서-지도.md",        "idx", "인덱스"),
    ("README.md",                "idx", "인덱스"),
    ("docs/작가-소개.md",        "A", "개념·브랜드"),
    ("docs/브랜드-정의서.md",     "A", "개념·브랜드"),
    ("docs/홈페이지-사이트맵.md", "B", "작가촌 사이트"),
    ("docs/홈-랜딩-카피.md",      "B", "작가촌 사이트"),
    ("docs/pages/소개.md",       "B", "작가촌 사이트"),
    ("docs/pages/공간소개.md",    "B", "작가촌 사이트"),
    ("docs/pages/작가들.md",      "B", "작가촌 사이트"),
    ("docs/pages/소식.md",       "B", "작가촌 사이트"),
    ("docs/pages/합류하기.md",    "B", "작가촌 사이트"),
    ("docs/pages/문의.md",       "B", "작가촌 사이트"),
    ("docs/작가-운영정책.md",     "C", "운영·계약"),
    ("docs/입점-동의서.md",       "C", "운영·계약"),
    ("docs/운영-매뉴얼.md",       "C", "운영·계약"),
    ("docs/작가-모집-키트.md",    "D", "모집"),
    ("docs/사업계획서.md",        "E", "경영·관리"),
    ("docs/성과지표-KPI.md",      "E", "경영·관리"),
    ("docs/정관-거버넌스.md",     "E", "경영·관리"),
    ("docs/상표-IP-보호-메모.md", "E", "경영·관리"),
    ("docs/헐버트작가촌-기획.md", "F", "작가촌 전략"),
    ("docs/손님-매장안내.md",     "G", "범위 밖"),
    ("docs/en/hulbert-en.md",    "G", "범위 밖"),
    ("docs/legal/개인정보처리방침.md", "H", "법적 고지"),
    ("docs/legal/이용약관.md",        "H", "법적 고지"),
    ("docs/legal/사업자정보.md",       "H", "법적 고지"),
]

GROUP_ORDER = [
    ("all", "전체"), ("idx", "인덱스"), ("A", "개념·브랜드"), ("B", "작가촌 사이트"),
    ("C", "운영·계약"), ("D", "모집"), ("E", "경영·관리"), ("F", "전략"), ("G", "범위 밖"),
    ("H", "법적 고지"),
]
STATUS_ORDER = [
    ("all", "전체 상태"), ("confirmed", "✅ 확정"), ("draft", "📝 초안"),
    ("review", "⚠️ 검토 필요"), ("later", "🕒 다음 시점"), ("out", "🗂 범위 밖"),
]

def gh_slug(text, sep="-"):
    """GitHub식 앵커 슬러그(유니코드/한글 보존)."""
    s = htmllib.unescape(text).strip().lower()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    s = re.sub(r"\s", sep, s.strip())
    return s

def status_key(label):
    if "✅" in label: return "confirmed"
    if "📝" in label: return "draft"
    if "⚠️" in label: return "review"
    if "🕒" in label: return "later"
    if "🗂" in label: return "out"
    return "info"

def parse_meta(md_text):
    title, badge, role = "(제목 없음)", "", ""
    for line in md_text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    m = re.search(r"🏷️\s*\*\*(.+?)\*\*(.*)", md_text)
    if m:
        badge = m.group(1).strip()
        parts = [p.strip() for p in m.group(2).split("·") if p.strip()]
        role = parts[-1] if parts else ""
    # 굵게/코드 마크업 제거(칩 표시용)
    title = re.sub(r"[*`]", "", title)
    role  = re.sub(r"[*`]", "", role)
    return title, badge, role

# basename → doc index (내부 .md 링크 해석용)
basemap = {}
for i, (rel, _g, _gl) in enumerate(DOCS):
    base = os.path.basename(rel)
    if base.endswith(".md"): base = base[:-3]
    basemap[base] = i

def rewrite_md_links(s):
    def repl(m):
        href = m.group(1)
        path = href.split("#", 1)[0]
        base = path.rsplit("/", 1)[-1]
        if base.endswith(".md"): base = base[:-3]
        if base in basemap:
            return f'href="#" data-goto="{basemap[base]}"'
        return m.group(0)
    return re.sub(r'href="([^"]+\.md(?:#[^"]*)?)"', repl, s)

def prefix_anchors(s, n):
    s = re.sub(r'id="([^"]+)"',     lambda m: f'id="d{n}-{m.group(1)}"', s)
    s = re.sub(r'href="#([^"]+)"',  lambda m: f'href="#d{n}-{m.group(1)}"', s)
    return s

articles, navmeta = [], []
for i, (rel, gkey, glabel) in enumerate(DOCS):
    p = os.path.join(ROOT, rel)
    with open(p, encoding="utf-8") as f:
        md_text = f.read()
    title, badge, role = parse_meta(md_text)
    skey = status_key(badge) if badge else "info"
    md = markdown.Markdown(
        extensions=["extra", "toc", "sane_lists", "attr_list"],
        extension_configs={"toc": {"slugify": gh_slug, "separator": "-"}},
    )
    body = md.convert(md_text)
    body = rewrite_md_links(body)
    body = prefix_anchors(body, i)
    articles.append(
        f'<article class="doc" id="doc-{i}" data-group="{gkey}" data-status="{skey}" hidden>\n{body}\n</article>'
    )
    navmeta.append({"i": i, "title": title, "badge": badge or "—", "role": role,
                    "group": gkey, "glabel": glabel, "status": skey})

# 네비 버튼
nav_html = []
for m in navmeta:
    nav_html.append(
        f'<button class="navchip s-{m["status"]}" data-i="{m["i"]}" '
        f'data-group="{m["group"]}" data-status="{m["status"]}" '
        f'data-title="{htmllib.escape(m["title"], quote=True)}" '
        f'data-role="{htmllib.escape(m["role"], quote=True)}">'
        f'<span class="dot"></span>'
        f'<span class="navtitle">{htmllib.escape(m["title"])}</span>'
        f'<span class="navrole">{htmllib.escape(m["role"])}</span>'
        f'</button>'
    )

group_pills = "".join(
    f'<button class="pill grp{" active" if k=="all" else ""}" data-grp="{k}">{lbl}</button>'
    for k, lbl in GROUP_ORDER
)
status_pills = "".join(
    f'<button class="pill st s-{k}{" active" if k=="all" else ""}" data-st="{k}">{lbl}</button>'
    for k, lbl in STATUS_ORDER
)

CSS = """
:root{
  --paper:#f6f2ea; --card:#fffdf8; --ink:#2b2723; --muted:#6f665b; --line:#e6ded0;
  --accent:#9c5b34; --accent2:#2f6b63;
  --c-confirmed:#2f7d4f; --c-draft:#2f6db0; --c-review:#b5791f;
  --c-later:#6b4ea8; --c-out:#8a8278; --c-info:#6f665b;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);
  font-family:"Pretendard","Apple SD Gothic Neo","Malgun Gothic","Noto Sans KR",system-ui,sans-serif;
  line-height:1.7;-webkit-font-smoothing:antialiased}
header.top{background:linear-gradient(180deg,#fffdf8,#f3ede1);border-bottom:1px solid var(--line);
  padding:22px 20px 10px;position:sticky;top:0;z-index:20;backdrop-filter:saturate(1.2) blur(2px)}
.wrap{max-width:980px;margin:0 auto}
.brand{font-size:1.5rem;font-weight:800;letter-spacing:-.02em;margin:0}
.brand .sep{color:var(--accent)}
.subtitle{margin:.35rem 0 0;color:var(--muted);font-size:.92rem}
.subtitle b{color:var(--ink)}
.filters{margin-top:14px;display:flex;flex-direction:column;gap:8px}
.filterrow{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.rowlabel{font-size:.72rem;color:var(--muted);min-width:42px;font-weight:700}
.pill{border:1px solid var(--line);background:#fff;color:var(--ink);border-radius:999px;
  padding:5px 12px;font-size:.82rem;cursor:pointer;transition:.12s;font-family:inherit}
.pill:hover{border-color:var(--accent);color:var(--accent)}
.pill.active{background:var(--ink);color:#fff;border-color:var(--ink)}
.pill.st.active{background:#fff}
.pill.st.s-confirmed.active{border-color:var(--c-confirmed);color:var(--c-confirmed);box-shadow:inset 0 0 0 1px var(--c-confirmed)}
.pill.st.s-draft.active{border-color:var(--c-draft);color:var(--c-draft);box-shadow:inset 0 0 0 1px var(--c-draft)}
.pill.st.s-review.active{border-color:var(--c-review);color:var(--c-review);box-shadow:inset 0 0 0 1px var(--c-review)}
.pill.st.s-later.active{border-color:var(--c-later);color:var(--c-later);box-shadow:inset 0 0 0 1px var(--c-later)}
.pill.st.s-out.active{border-color:var(--c-out);color:var(--c-out);box-shadow:inset 0 0 0 1px var(--c-out)}
.pill.st.s-all.active{background:var(--ink);color:#fff;border-color:var(--ink)}
.searchbox{flex:1;min-width:160px;border:1px solid var(--line);border-radius:999px;
  padding:6px 14px;font-size:.85rem;font-family:inherit;background:#fff;color:var(--ink)}
.searchbox:focus{outline:none;border-color:var(--accent)}
.navwrap{max-width:980px;margin:0 auto;padding:14px 20px 6px}
.navhint{font-size:.74rem;color:var(--muted);margin:0 0 8px}
.navgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px}
.navchip{display:flex;align-items:center;gap:8px;text-align:left;cursor:pointer;
  border:1px solid var(--line);background:var(--card);border-radius:12px;padding:10px 12px;
  font-family:inherit;color:var(--ink);transition:.12s}
.navchip:hover{border-color:var(--accent);transform:translateY(-1px);box-shadow:0 3px 10px rgba(60,40,20,.06)}
.navchip.active{border-color:var(--ink);box-shadow:0 0 0 2px rgba(43,39,35,.12)}
.navchip .dot{width:9px;height:9px;border-radius:50%;flex:0 0 auto}
.s-confirmed .dot{background:var(--c-confirmed)} .s-draft .dot{background:var(--c-draft)}
.s-review .dot{background:var(--c-review)} .s-later .dot{background:var(--c-later)}
.s-out .dot{background:var(--c-out)} .s-info .dot{background:var(--c-info)}
.navtitle{font-weight:700;font-size:.9rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.navrole{margin-left:auto;color:var(--muted);font-size:.72rem;white-space:nowrap;overflow:hidden;
  text-overflow:ellipsis;max-width:46%}
.count{color:var(--muted);font-size:.74rem;margin:10px 0 0}
main{max-width:880px;margin:8px auto 80px;padding:0 22px}
.empty{color:var(--muted);text-align:center;padding:60px 0}
.doc{background:var(--card);border:1px solid var(--line);border-radius:16px;
  padding:34px 40px 44px;box-shadow:0 6px 22px rgba(60,40,20,.05);animation:fade .25s ease}
@keyframes fade{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
.doc h1{font-size:1.7rem;margin:.1em 0 .5em;letter-spacing:-.02em;line-height:1.3}
.doc h2{font-size:1.28rem;margin:1.7em 0 .5em;padding-bottom:.25em;border-bottom:2px solid var(--line)}
.doc h3{font-size:1.08rem;margin:1.4em 0 .4em;color:#403a32}
.doc h4{font-size:.98rem;margin:1.2em 0 .3em;color:var(--accent)}
.doc p{margin:.6em 0}
.doc a{color:var(--accent);text-decoration:none;border-bottom:1px solid rgba(156,91,52,.3)}
.doc a:hover{border-bottom-color:var(--accent)}
.doc a[data-goto]{color:var(--accent2);border-bottom-color:rgba(47,107,99,.35);font-weight:600}
.doc blockquote{margin:.9em 0;padding:.7em 1.1em;background:#faf6ee;border-left:4px solid var(--accent);
  border-radius:0 8px 8px 0;color:#4a4339}
.doc blockquote p{margin:.25em 0}
.doc ul,.doc ol{padding-left:1.4em;margin:.5em 0}
.doc li{margin:.25em 0}
.doc code{background:#f0e9da;padding:.12em .42em;border-radius:5px;font-size:.88em;
  font-family:"SFMono-Regular",Consolas,"Liberation Mono",monospace}
.doc pre{background:#2b2723;color:#f3ede1;padding:16px 18px;border-radius:12px;overflow:auto;font-size:.86rem}
.doc pre code{background:none;padding:0;color:inherit}
.doc table{border-collapse:collapse;width:100%;margin:1em 0;font-size:.9rem;display:block;overflow-x:auto}
.doc th,.doc td{border:1px solid var(--line);padding:8px 11px;text-align:left;vertical-align:top}
.doc th{background:#f3ede1;font-weight:700}
.doc tr:nth-child(even) td{background:#fbf8f1}
.doc hr{border:none;border-top:1px dashed var(--line);margin:1.8em 0}
.doc img{max-width:100%}
.backtop{position:fixed;right:18px;bottom:18px;background:var(--ink);color:#fff;border:none;
  width:44px;height:44px;border-radius:50%;cursor:pointer;font-size:1.1rem;box-shadow:0 4px 14px rgba(0,0,0,.2);
  opacity:0;pointer-events:none;transition:.2s}
.backtop.show{opacity:.9;pointer-events:auto}
@media(max-width:640px){
  .doc{padding:24px 18px 32px}
  .navrole{display:none}
  .brand{font-size:1.25rem}
}
"""

JS = """
const docs = Array.from(document.querySelectorAll('.doc'));
const chips = Array.from(document.querySelectorAll('.navchip'));
const grpPills = Array.from(document.querySelectorAll('.pill.grp'));
const stPills  = Array.from(document.querySelectorAll('.pill.st'));
const search = document.getElementById('search');
const countEl = document.getElementById('count');
const emptyEl = document.getElementById('empty');
const backtop = document.getElementById('backtop');
let curGroup='all', curStatus='all', curQuery='';

function applyFilter(){
  let shown=0;
  chips.forEach(c=>{
    const okG = curGroup==='all' || c.dataset.group===curGroup;
    const okS = curStatus==='all' || c.dataset.status===curStatus;
    const okQ = !curQuery || (c.dataset.title+' '+c.dataset.role).toLowerCase().includes(curQuery);
    const vis = okG && okS && okQ;
    c.style.display = vis ? '' : 'none';
    if(vis) shown++;
  });
  countEl.textContent = shown + ' / ' + chips.length + ' 문서';
  emptyEl.style.display = shown? 'none':'block';
}
function selectDoc(i){
  docs.forEach(d=>d.hidden = (d.id!=='doc-'+i));
  chips.forEach(c=>c.classList.toggle('active', c.dataset.i===String(i)));
  const main = document.getElementById('main');
  // 헤더 높이만큼 여유를 두고 스크롤
  window.scrollTo({top: main.offsetTop - 8, behavior:'smooth'});
}
chips.forEach(c=>c.addEventListener('click',()=>selectDoc(c.dataset.i)));
grpPills.forEach(p=>p.addEventListener('click',()=>{
  curGroup=p.dataset.grp; grpPills.forEach(x=>x.classList.toggle('active',x===p)); applyFilter();
}));
stPills.forEach(p=>p.addEventListener('click',()=>{
  curStatus=p.dataset.st; stPills.forEach(x=>x.classList.toggle('active',x===p)); applyFilter();
}));
search.addEventListener('input',()=>{ curQuery=search.value.trim().toLowerCase(); applyFilter(); });

// 문서 내부 .md 링크 → 해당 문서로 전환
document.addEventListener('click',e=>{
  const a=e.target.closest('a[data-goto]');
  if(a){ e.preventDefault(); selectDoc(a.dataset.goto); }
});
// 맨 위로
backtop.addEventListener('click',()=>window.scrollTo({top:0,behavior:'smooth'}));
window.addEventListener('scroll',()=>backtop.classList.toggle('show', window.scrollY>500));

applyFilter();
selectDoc(0); // 문서 지도부터
"""

HTML = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>헐버트 프로젝트 · 문서 뷰어</title>
<style>{CSS}</style>
</head>
<body>
<header class="top">
  <div class="wrap">
    <h1 class="brand">헐버트 프로젝트 <span class="sep">·</span> 문서 뷰어</h1>
    <p class="subtitle"><b>헐버트잡화점</b> = 손님용 매장(사업체) · <b>헐버트작가촌</b> = 작가용 사이트(지금 만드는 것, 모집 단계)</p>
    <div class="filters">
      <div class="filterrow"><span class="rowlabel">그룹</span>{group_pills}</div>
      <div class="filterrow"><span class="rowlabel">상태</span>{status_pills}</div>
      <div class="filterrow"><span class="rowlabel">검색</span>
        <input id="search" class="searchbox" type="search" placeholder="문서 이름·역할로 검색…" autocomplete="off"></div>
    </div>
  </div>
</header>

<section class="navwrap">
  <p class="navhint">아래 문서를 누르면 내용이 바로 펼쳐집니다. 위 필터로 좁힐 수 있어요.</p>
  <div class="navgrid">
    {"".join(nav_html)}
  </div>
  <p class="count" id="count"></p>
</section>

<main id="main">
  <p class="empty" id="empty" style="display:none">조건에 맞는 문서가 없어요. 필터를 바꿔보세요.</p>
  {"".join(articles)}
</main>

<button class="backtop" id="backtop" title="맨 위로">↑</button>
<script>{JS}</script>
</body>
</html>
"""

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(HTML)

print("WROTE", OUT)
print("docs:", len(DOCS), "| size:", round(len(HTML)/1024, 1), "KB")
