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
    ("docs/헐버트작가촌-기획.md", "F", "전략"),
    ("docs/손님-매장안내.md",     "G", "범위 밖"),
    ("docs/en/hulbert-en.md",    "G", "범위 밖"),
    ("docs/legal/개인정보처리방침.md", "H", "법적 고지"),
    ("docs/legal/이용약관.md",        "H", "법적 고지"),
    ("docs/legal/사업자정보.md",       "H", "법적 고지"),
]

GROUP_ORDER = [
    ("idx", "인덱스"), ("A", "개념·브랜드"), ("B", "작가촌 사이트"),
    ("C", "운영·계약"), ("D", "모집"), ("E", "경영·관리"), ("F", "전략"),
    ("G", "범위 밖"), ("H", "법적 고지"),
]
STATUS_ORDER = [
    ("all", "전체"), ("confirmed", "✅ 확정"), ("draft", "📝 초안"),
    ("review", "⚠️ 검토"), ("later", "🕒 다음"), ("out", "🗂 범위 밖"),
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

# 그룹별 사이드바 네비
glabel_map = dict(GROUP_ORDER)
nav_html = []
for gkey, _ in GROUP_ORDER:
    members = [m for m in navmeta if m["group"] == gkey]
    if not members:
        continue
    nav_html.append(f'<div class="nav-group" data-group="{gkey}">')
    nav_html.append(f'<div class="nav-grouphead">{htmllib.escape(glabel_map[gkey])}</div>')
    for m in members:
        sub = m["role"] or (m["badge"] if m["badge"] != "—" else "")
        nav_html.append(
            f'<button class="navitem s-{m["status"]}" data-i="{m["i"]}" '
            f'data-group="{m["group"]}" data-status="{m["status"]}" '
            f'data-title="{htmllib.escape(m["title"], quote=True)}" '
            f'data-role="{htmllib.escape(m["role"], quote=True)}">'
            f'<span class="dot" title="{htmllib.escape(m["badge"])}"></span>'
            f'<span class="navitem-main">'
            f'<span class="navitem-title">{htmllib.escape(m["title"])}</span>'
            f'<span class="navitem-sub">{htmllib.escape(sub)}</span>'
            f'</span></button>'
        )
    nav_html.append("</div>")
nav = "".join(nav_html)

status_pills = "".join(
    f'<button class="pill st s-{k}{" active" if k=="all" else ""}" data-st="{k}">{lbl}</button>'
    for k, lbl in STATUS_ORDER
)

CSS = """
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');
:root{
  --paper:#ece4d5; --sidebar:#f6f1e7; --card:#fffdf9; --ink:#262220; --muted:#7c7264;
  --line:#e3dac9; --line-soft:#efe7d8; --accent:#9c5b34; --accent-soft:#f3e6dc; --accent2:#2f6b63;
  --sidebar-w:298px; --reader-w:744px; --toc-w:208px;
  --c-confirmed:#2f7d4f; --c-draft:#2f6db0; --c-review:#b5791f;
  --c-later:#6b4ea8; --c-out:#9a9082; --c-info:#9a9082;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);
  font-family:"Pretendard Variable","Pretendard","Apple SD Gothic Neo","Malgun Gothic","Noto Sans KR",system-ui,sans-serif;
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}

.layout{display:flex;align-items:flex-start;min-height:100vh}

/* ---------- 사이드바 ---------- */
.sidebar{width:var(--sidebar-w);flex:0 0 var(--sidebar-w);background:var(--sidebar);
  border-right:1px solid var(--line);height:100vh;position:sticky;top:0;
  display:flex;flex-direction:column;z-index:40}
.side-head{padding:18px 18px 14px;border-bottom:1px solid var(--line)}
.brand{font-size:1.18rem;font-weight:800;margin:0;letter-spacing:-.02em}
.brand .sep{color:var(--accent)}
.subtitle{font-size:.71rem;color:var(--muted);margin:.45rem 0 0;line-height:1.55}
.subtitle b{color:var(--ink)}
.side-tools{padding:13px 16px 9px;border-bottom:1px solid var(--line)}
.searchbox{width:100%;border:1px solid var(--line);border-radius:9px;padding:8px 12px;
  font-size:.85rem;font-family:inherit;background:#fff;color:var(--ink)}
.searchbox:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-soft)}
.pillrow{display:flex;flex-wrap:wrap;gap:5px;margin-top:9px}
.pill{border:1px solid var(--line);background:#fff;color:var(--muted);border-radius:999px;
  padding:3px 9px;font-size:.73rem;cursor:pointer;transition:.12s;font-family:inherit}
.pill:hover{border-color:var(--accent);color:var(--accent)}
.pill.st.active{background:var(--ink);color:#fff;border-color:var(--ink)}
.pill.st.s-confirmed.active{background:var(--c-confirmed);border-color:var(--c-confirmed);color:#fff}
.pill.st.s-draft.active{background:var(--c-draft);border-color:var(--c-draft);color:#fff}
.pill.st.s-review.active{background:var(--c-review);border-color:var(--c-review);color:#fff}
.pill.st.s-later.active{background:var(--c-later);border-color:var(--c-later);color:#fff}
.pill.st.s-out.active{background:var(--c-out);border-color:var(--c-out);color:#fff}
.count{font-size:.7rem;color:var(--muted);margin:9px 2px 2px}

.side-nav{flex:1;overflow-y:auto;padding:10px 10px 40px}
.nav-group{margin:2px 0 10px}
.nav-grouphead{font-size:.66rem;font-weight:800;letter-spacing:.09em;color:var(--muted);
  padding:8px 10px 4px;text-transform:uppercase}
.navitem{display:flex;align-items:center;gap:9px;width:100%;text-align:left;cursor:pointer;
  border:none;background:none;border-radius:9px;padding:7px 10px;font-family:inherit;color:var(--ink);
  transition:background .1s,color .1s}
.navitem:hover{background:rgba(156,91,52,.09)}
.navitem.active{background:var(--accent);color:#fff}
.navitem.active .navitem-sub{color:rgba(255,255,255,.82)}
.navitem.active .dot{box-shadow:0 0 0 2px rgba(255,255,255,.85)}
.dot{width:8px;height:8px;border-radius:50%;flex:0 0 auto}
.s-confirmed .dot{background:var(--c-confirmed)} .s-draft .dot{background:var(--c-draft)}
.s-review .dot{background:var(--c-review)} .s-later .dot{background:var(--c-later)}
.s-out .dot{background:var(--c-out)} .s-info .dot{background:var(--c-info)}
.navitem-main{display:flex;flex-direction:column;min-width:0;line-height:1.3}
.navitem-title{font-weight:600;font-size:.855rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.navitem-sub{font-size:.67rem;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.empty{color:var(--muted);font-size:.8rem;padding:20px 12px;text-align:center}

/* ---------- 본문 + 목차 ---------- */
.content{flex:1;min-width:0;display:flex;justify-content:center;gap:46px;padding:0 36px}
.reader{flex:1 1 var(--reader-w);max-width:var(--reader-w);padding:54px 0 140px;
  font-size:17px;line-height:1.78}
.doc{animation:fade .22s ease}
@keyframes fade{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:none}}
.doc :where(h1,h2,h3,h4){scroll-margin-top:74px}
.doc h1{font-size:1.92rem;line-height:1.25;margin:0 0 .55em;letter-spacing:-.022em;font-weight:800}
.doc h2{font-size:1.36rem;margin:2.05em 0 .65em;padding-bottom:.32em;
  border-bottom:1.5px solid var(--line);font-weight:700;letter-spacing:-.01em}
.doc h3{font-size:1.13rem;margin:1.7em 0 .5em;font-weight:700;color:#39332b}
.doc h4{font-size:1.0rem;margin:1.35em 0 .35em;color:var(--accent);font-weight:700}
.doc p{margin:.9em 0}
.doc a{color:var(--accent);text-decoration:none;border-bottom:1px solid rgba(156,91,52,.32)}
.doc a:hover{border-bottom-color:var(--accent)}
.doc a[data-goto]{color:var(--accent2);border-bottom-color:rgba(47,107,99,.4);font-weight:600}
.doc strong{font-weight:700}
.doc blockquote{margin:1.05em 0;padding:.8em 1.15em;background:#faf5ec;
  border-left:4px solid var(--accent);border-radius:0 9px 9px 0;color:#4a4239}
.doc blockquote p{margin:.3em 0}
.doc blockquote:first-child{background:var(--accent-soft);border-left-color:var(--accent);font-size:.96em}
.doc ul,.doc ol{padding-left:1.45em;margin:.7em 0}
.doc li{margin:.34em 0}
.doc li::marker{color:var(--accent)}
.doc code{background:#f0e8d8;padding:.12em .42em;border-radius:5px;font-size:.86em;
  font-family:"SFMono-Regular",Consolas,"Liberation Mono",monospace}
.doc pre{background:#272220;color:#f3ede1;padding:16px 18px;border-radius:11px;overflow:auto;font-size:.85rem;line-height:1.6}
.doc pre code{background:none;padding:0;color:inherit}
.doc table{border-collapse:collapse;width:100%;margin:1.2em 0;font-size:.92rem;display:block;overflow-x:auto}
.doc th,.doc td{border:1px solid var(--line);padding:9px 12px;text-align:left;vertical-align:top}
.doc th{background:#f1e9da;font-weight:700;white-space:nowrap}
.doc tr:nth-child(even) td{background:#fbf7ef}
.doc hr{border:none;border-top:1px solid var(--line-soft);margin:2em 0}
.doc img{max-width:100%}

.toc{flex:0 0 var(--toc-w);width:var(--toc-w);position:sticky;top:0;align-self:flex-start;
  max-height:100vh;overflow-y:auto;padding:60px 0 60px;font-size:.78rem}
.toc-head{font-weight:800;color:var(--muted);text-transform:uppercase;letter-spacing:.09em;
  font-size:.64rem;margin:0 0 9px 12px}
.toc a{display:block;color:var(--muted);text-decoration:none;padding:4px 12px;
  border-left:2px solid var(--line);line-height:1.4;transition:.1s}
.toc a:hover{color:var(--accent)}
.toc a.lvl3{padding-left:24px;font-size:.74rem}
.toc a.active{color:var(--accent);border-left-color:var(--accent);font-weight:700}

/* ---------- 모바일 ---------- */
.menu-toggle{display:none;position:fixed;top:12px;left:12px;z-index:60;
  background:var(--ink);color:#fff;border:none;border-radius:9px;padding:9px 13px;
  font-size:.85rem;font-family:inherit;cursor:pointer;box-shadow:0 3px 12px rgba(0,0,0,.22)}
.scrim{display:none;position:fixed;inset:0;background:rgba(30,24,18,.42);z-index:35}
.scrim.show{display:block}
@media(max-width:1140px){ .toc{display:none} }
@media(max-width:860px){
  .menu-toggle{display:block}
  .sidebar{position:fixed;left:0;top:0;transform:translateX(-100%);
    transition:transform .25s ease;box-shadow:6px 0 24px rgba(40,28,18,.18)}
  .sidebar.open{transform:none}
  .content{padding:0 18px}
  .reader{padding:64px 0 90px;font-size:16.5px}
  .doc h1{font-size:1.62rem}
  .doc h2{font-size:1.24rem}
}
"""

JS = """
const articles=Array.from(document.querySelectorAll('.doc'));
const items=Array.from(document.querySelectorAll('.navitem'));
const groups=Array.from(document.querySelectorAll('.nav-group'));
const stPills=Array.from(document.querySelectorAll('.pill.st'));
const search=document.getElementById('search');
const countEl=document.getElementById('count');
const emptyEl=document.getElementById('empty');
const tocEl=document.getElementById('toc');
const sidebar=document.getElementById('sidebar');
const scrim=document.getElementById('scrim');
const total=items.length;
let curStatus='all', curQuery='', curHeads=[], tocLinks=[];

function applyFilter(){
  let shown=0;
  groups.forEach(g=>{
    let gv=0;
    g.querySelectorAll('.navitem').forEach(c=>{
      const okS=curStatus==='all'||c.dataset.status===curStatus;
      const okQ=!curQuery||(c.dataset.title+' '+c.dataset.role).toLowerCase().includes(curQuery);
      const vis=okS&&okQ; c.style.display=vis?'':'none'; if(vis){gv++;shown++;}
    });
    g.style.display=gv?'':'none';
  });
  countEl.textContent=shown+' / '+total+' 문서';
  emptyEl.style.display=shown?'none':'block';
}

function buildTOC(art){
  curHeads=Array.from(art.querySelectorAll('h2, h3'));
  if(curHeads.length<2){ tocEl.innerHTML=''; tocLinks=[]; return; }
  let h='<div class="toc-head">목차</div>';
  curHeads.forEach(x=>{
    const cls=x.tagName==='H3'?'lvl3':'lvl2';
    h+='<a class="'+cls+'" href="#'+x.id+'">'+x.textContent+'</a>';
  });
  tocEl.innerHTML=h;
  tocLinks=Array.from(tocEl.querySelectorAll('a'));
}

function spy(){
  if(!tocLinks.length) return;
  let idx=0;
  for(let k=0;k<curHeads.length;k++){
    if(curHeads[k].getBoundingClientRect().top<=150) idx=k; else break;
  }
  tocLinks.forEach((a,k)=>a.classList.toggle('active',k===idx));
}

function selectDoc(i){
  articles.forEach(d=>d.hidden=(d.id!=='doc-'+i));
  items.forEach(c=>c.classList.toggle('active',c.dataset.i===String(i)));
  const art=document.getElementById('doc-'+i);
  buildTOC(art);
  window.scrollTo({top:0,behavior:'auto'});
  closeSidebar();
  requestAnimationFrame(spy);
}

function openSidebar(){ sidebar.classList.add('open'); scrim.classList.add('show'); }
function closeSidebar(){ sidebar.classList.remove('open'); scrim.classList.remove('show'); }

items.forEach(c=>c.addEventListener('click',()=>selectDoc(c.dataset.i)));
stPills.forEach(p=>p.addEventListener('click',()=>{
  curStatus=p.dataset.st; stPills.forEach(x=>x.classList.toggle('active',x===p)); applyFilter();
}));
search.addEventListener('input',()=>{ curQuery=search.value.trim().toLowerCase(); applyFilter(); });
document.addEventListener('click',e=>{
  const a=e.target.closest('a[data-goto]');
  if(a){ e.preventDefault(); selectDoc(a.dataset.goto); }
});
document.getElementById('menu').addEventListener('click',openSidebar);
scrim.addEventListener('click',closeSidebar);
window.addEventListener('scroll',spy,{passive:true});

applyFilter();
selectDoc(0);
"""

HTML = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>헐버트 프로젝트 · 문서</title>
<style>{CSS}</style>
</head>
<body>
<button class="menu-toggle" id="menu" aria-label="문서 목록 열기">☰ 문서</button>
<div class="scrim" id="scrim"></div>
<div class="layout">
  <aside class="sidebar" id="sidebar">
    <div class="side-head">
      <h1 class="brand">헐버트 <span class="sep">·</span> 문서</h1>
      <p class="subtitle"><b>헐버트잡화점</b> = 손님용 매장 · <b>헐버트작가촌</b> = 작가용 사이트(모집 단계)</p>
    </div>
    <div class="side-tools">
      <input id="search" class="searchbox" type="search" placeholder="문서 이름·역할 검색…" autocomplete="off">
      <div class="pillrow">{status_pills}</div>
      <p class="count" id="count"></p>
    </div>
    <nav class="side-nav">
      {nav}
      <p class="empty" id="empty" style="display:none">조건에 맞는 문서가 없어요.</p>
    </nav>
  </aside>

  <div class="content">
    <main class="reader" id="reader">
      {"".join(articles)}
    </main>
    <aside class="toc" id="toc"></aside>
  </div>
</div>
<script>{JS}</script>
</body>
</html>
"""

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(HTML)

print("WROTE", OUT)
print("docs:", len(DOCS), "| size:", round(len(HTML)/1024, 1), "KB")
