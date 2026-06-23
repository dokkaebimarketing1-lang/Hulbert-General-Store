#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
문서 '내용'을 설명하는 다이어그램(SVG)을 생성한다. (네트워크/키 불필요)
- 풍경 장식이 아니라, 각 문서의 핵심 구조를 라벨과 함께 그린 인포그래픽.
- SVG라 한글 텍스트가 또렷하게 렌더(AI 이미지처럼 글자가 깨지지 않음).
- 결과: viewer/assets/<문서>.svg  (build.py가 PNG 없으면 이 SVG 사용)
사용: python3 tools/gen_diagrams.py  ->  python3 viewer/build.py
"""
import os, math, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "viewer", "assets")
W, H = 1600, 700
FONT = "Pretendard,'Apple SD Gothic Neo','Malgun Gothic',sans-serif"

PAL = {
 "idx":dict(bg1="#f6f0e6",bg2="#ece0cf",card="#fffdf8",ink="#4a4133",ac="#9c5b34",ac2="#c79a6a"),
 "A":dict(bg1="#f8eee4",bg2="#f0dcc9",card="#fffdf8",ink="#4d3a2b",ac="#9c5b34",ac2="#c2895f"),
 "B":dict(bg1="#fdf5e3",bg2="#f7e6c4",card="#fffdf6",ink="#5a4528",ac="#c0892c",ac2="#dcad5e"),
 "C":dict(bg1="#eff4e9",bg2="#dde9d0",card="#fbfdf7",ink="#3c4a31",ac="#3f7a52",ac2="#8aad77"),
 "D":dict(bg1="#fdefe8",bg2="#fbdac9",card="#fffaf7",ink="#5a3326",ac="#c2502f",ac2="#e2876a"),
 "E":dict(bg1="#eef1f6",bg2="#dbe2ed",card="#fbfcfe",ink="#363f53",ac="#2f6db0",ac2="#8d9ab5"),
 "F":dict(bg1="#f4edf4",bg2="#e7d6e8",card="#fdfbfd",ink="#43354a",ac="#6b4ea8",ac2="#a682ac"),
 "G":dict(bg1="#f2f0eb",bg2="#e2ded4",card="#fdfcf9",ink="#48433a",ac="#857b6e",ac2="#aaa293"),
 "H":dict(bg1="#eef0f3",bg2="#dde2e8",card="#fbfcfd",ink="#363c44",ac="#59636f",ac2="#919ba7"),
}
SLUG_GROUP = {
 "문서-지도":"idx","README":"idx","작가-소개":"A","브랜드-정의서":"A",
 "홈페이지-사이트맵":"B","홈-랜딩-카피":"B","소개":"B","공간소개":"B","작가들":"B",
 "소식":"B","합류하기":"B","문의":"B",
 "작가-운영정책":"C","입점-동의서":"C","운영-매뉴얼":"C","작가-모집-키트":"D",
 "사업계획서":"E","성과지표-KPI":"E","정관-거버넌스":"E","상표-IP-보호-메모":"E",
 "헐버트작가촌-기획":"F","손님-매장안내":"G","hulbert-en":"G",
 "개인정보처리방침":"H","이용약관":"H","사업자정보":"H",
}

def esc(s): return html.escape(str(s), quote=True)
def T(x,y,s,size,col,weight="400",anchor="start"):
    return (f'<text x="{x:.0f}" y="{y:.0f}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" fill="{col}" text-anchor="{anchor}">{esc(s)}</text>')
def lines_block(x,y,lines,size,lh,col,anchor="start",weight="400"):
    return "".join(T(x,y+i*lh,ln,size,col,weight,anchor) for i,ln in enumerate(lines))
def card(x,y,w,h,fill,stroke,sw=2,rx=18):
    return (f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
def chevron(cx,cy,col):
    return (f'<path d="M{cx-9:.0f},{cy-16:.0f} L{cx+11:.0f},{cy:.0f} L{cx-9:.0f},{cy+16:.0f}" '
            f'fill="none" stroke="{col}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>')

def wrap(title, p, inner):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="{esc(title)}">'
            f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{p["bg1"]}"/><stop offset="1" stop-color="{p["bg2"]}"/>'
            f'</linearGradient></defs>'
            f'<rect width="{W}" height="{H}" fill="url(#bg)"/>'
            f'<rect x="64" y="50" width="9" height="44" rx="4" fill="{p["ac"]}"/>'
            f'{T(88,86,title,40,p["ink"],"800")}'
            f'{inner}</svg>')

def render_row(items, p, numbered, arrows):
    M, top, bot = 70, 170, 624
    n = len(items); gap = 50 if arrows else 32
    cw = (W - 2*M - (n-1)*gap) / n; ch = bot - top
    out = []
    for i, it in enumerate(items):
        x = M + i*(cw+gap); cx = x + cw/2
        out.append(card(x, top, cw, ch, p["card"], p["ac2"], 2, 20))
        head_y = top + (104 if numbered else 74)
        if numbered:
            out.append(f'<circle cx="{x+38:.0f}" cy="{top+42:.0f}" r="26" fill="{p["ac"]}"/>')
            out.append(T(x+38, top+51, i+1, 30, "#fff", "800", "middle"))
        out.append(T(cx, head_y, it["head"], 31, p["ac"], "800", "middle"))
        out.append(f'<line x1="{x+34:.0f}" y1="{head_y+20:.0f}" x2="{x+cw-34:.0f}" y2="{head_y+20:.0f}" stroke="{p["ac2"]}" stroke-width="1.5" stroke-opacity=".5"/>')
        out.append(lines_block(cx, head_y+62, it.get("lines",[]), 23, 38, p["ink"], "middle"))
        if arrows and i < n-1:
            out.append(chevron(x+cw+gap/2, top+ch/2, p["ac"]))
    return "".join(out)

def render_grid(items, p, cols):
    M, top, bot = 70, 168, 628
    n = len(items); rows = math.ceil(n/cols)
    gx, gy = 28, 24
    cw = (W - 2*M - (cols-1)*gx)/cols
    chh = (bot - top - (rows-1)*gy)/rows
    out = []
    for i, it in enumerate(items):
        r, c = divmod(i, cols)
        x = M + c*(cw+gx); y = top + r*(chh+gy)
        out.append(card(x, y, cw, chh, p["card"], p["ac2"], 2, 16))
        out.append(f'<circle cx="{x+30:.0f}" cy="{y+34:.0f}" r="7" fill="{p["ac"]}"/>')
        out.append(T(x+50, y+43, it["head"], 27, p["ink"], "800"))
        out.append(lines_block(x+50, y+80, it.get("lines",[]), 22, 34, p["ink"]))
    return "".join(out)

def render_compare(left, right, p):
    M, top, bot = 70, 168, 628
    gap = 150; cw = (W - 2*M - gap)/2; chh = bot - top
    out = []
    for k,(it,head_col,fill) in enumerate([(left,p["ac2"],"#fbf6ee"),(right,p["ac"],p["card"])]):
        x = M + k*(cw+gap)
        out.append(card(x, top, cw, chh, fill, head_col, 2.5, 20))
        out.append(f'<path d="M{x:.0f},{top+58:.0f} L{x:.0f},{top+20:.0f} Q{x:.0f},{top:.0f} {x+20:.0f},{top:.0f} L{x+cw-20:.0f},{top:.0f} Q{x+cw:.0f},{top:.0f} {x+cw:.0f},{top+20:.0f} L{x+cw:.0f},{top+58:.0f} Z" fill="{head_col}"/>')
        out.append(T(x+cw/2, top+40, it["label"], 28, "#fff", "800", "middle"))
        out.append(lines_block(x+38, top+108, it["lines"], 24, 46, p["ink"]))
    out.append(f'<circle cx="{W/2:.0f}" cy="{top+chh/2:.0f}" r="40" fill="{p["ink"]}"/>')
    out.append(T(W/2, top+chh/2+9, "VS", 26, "#fff", "800", "middle"))
    return "".join(out)

SPEC = {
 "문서-지도":dict(type="grid",cols=3,title="문서 그룹 지도",items=[
   {"head":"개념·브랜드"},{"head":"작가촌 사이트"},{"head":"운영·계약"},
   {"head":"모집"},{"head":"경영·관리"},{"head":"전략·법적"}]),
 "README":dict(type="compare",title="두 개의 브랜드",
   left={"label":"헐버트잡화점","lines":["손님용 매장","(사업체)","경복궁 옆 서촌 한옥"]},
   right={"label":"헐버트작가촌","lines":["작가용 사이트","지금 만드는 것","= 작가 모집 단계"]}),
 "작가-소개":dict(type="steps",title="함께 오르는 3단계 사다리",items=[
   {"head":"위탁","lines":["복지수수료 관계","입점비 0 · 가격 자율","판 만큼만 수수료"]},
   {"head":"너투사","lines":["3.3% 프리랜서 파트너","회사 일을 도우며","월급처럼 추가 소득"]},
   {"head":"나투사","lines":["법인 주주","고정비 공동 부담","끝내 회사의 주인"]}]),
 "브랜드-정의서":dict(type="pillars",title="핵심 가치 — 한 목소리",items=[
   {"head":"함께","lines":["모시지 않고","함께 가는 동료"]},
   {"head":"공평","lines":["좋은 자리가","모두에게 돌아가게"]},
   {"head":"투명","lines":["수수료의 쓰임을","숨기지 않는다"]}]),
 "홈페이지-사이트맵":dict(type="flow",title="작가촌 사이트 흐름",items=[
   {"head":"랜딩","lines":["첫인상·핵심"]},{"head":"소개·공간·작가","lines":["왜 우리인가"]},
   {"head":"합류 폼","lines":["3가지만 제출"]},{"head":"문의","lines":["FAQ"]}]),
 "홈-랜딩-카피":dict(type="pillars",title="세 가지 '0'",items=[
   {"head":"입점비 0원","lines":["들어올 때","내는 돈 없음"]},
   {"head":"월세부담 0원","lines":["판 만큼만","복지수수료"]},
   {"head":"가격간섭 0","lines":["가격은 100%","작가가 결정"]}]),
 "소개":dict(type="pillars",title="우리는 이렇게 다릅니다",items=[
   {"head":"사람·꿈에 투자","lines":["'제품'이 아니라","사람과 꿈"]},
   {"head":"복지수수료","lines":["공간을 함께","공동구매"]},
   {"head":"함께 주인","lines":["끝내 회사의","주주로"]}]),
 "공간소개":dict(type="pillars",title="왜 경복궁 옆 서촌 한옥",items=[
   {"head":"경복궁 옆","lines":["관광객이 흐르는","길목"]},
   {"head":"예술가의 동네","lines":["서촌의 예술","정통성에 합류"]},
   {"head":"한옥 무대","lines":["'상품'이","'작품'이 되는 곳"]}]),
 "작가들":dict(type="pillars",title="이곳의 작가들",items=[
   {"head":"한글 이름","lines":["나이·학벌 대신","꿈을 담은 이름"]},
   {"head":"장르 불문","lines":["한옥에 어울리면","무엇이든"]},
   {"head":"평생 인연","lines":["같은 꿈을 가진","동료를 만남"]}]),
 "소식":dict(type="grid",cols=2,title="지금 소식",items=[
   {"head":"작가 모집 중","lines":["예비 작가를 찾습니다"]},
   {"head":"공간 준비","lines":["서촌 한옥 (상세 TBD)"]},
   {"head":"업데이트 예정","lines":["오픈 소식을 전합니다"]},
   {"head":"문의 환영","lines":["언제든 DM"]}]),
 "합류하기":dict(type="steps",title="지원은 3가지만",items=[
   {"head":"작품 사진","lines":["3~5장"]},
   {"head":'"당신의 꿈"',"lines":["한 문장"]},
   {"head":"한글 이름","lines":["없으면","함께 지어요"]}]),
 "문의":dict(type="grid",cols=2,title="자주 묻는 질문",items=[
   {"head":"입점비?","lines":["0원"]},{"head":"가격은?","lines":["작가가 직접"]},
   {"head":"정산은?","lines":["월 1회 · 판매분만"]},{"head":"자리 빠지면?","lines":["언제든 재입점"]}]),
 "작가-운영정책":dict(type="grid",cols=2,title="운영 규칙 (예시)",items=[
   {"head":"매대 로테이션","lines":["약 4주마다 순환"]},
   {"head":"정산","lines":["월 1회 · 안 팔리면 0"]},
   {"head":"퇴점","lines":["연속 8주 미판매 시"]},
   {"head":"회수·해지","lines":["2주 사전 안내"]}]),
 "입점-동의서":dict(type="pillars",title="핵심 합의 사항",items=[
   {"head":"가격 자율","lines":["100% 작가가","책정"]},
   {"head":"복지수수료","lines":["고정비로 전액","판 만큼만"]},
   {"head":"책임 범위","lines":["경미 손상 회사,","고가품 별도 합의"]}]),
 "운영-매뉴얼":dict(type="flow",title="하루 운영 흐름",items=[
   {"head":"오픈 준비","lines":["진열 점검"]},{"head":"손님 응대","lines":["눈으로 먼저"]},
   {"head":"판매·기록","lines":["가격대로 판매"]},{"head":"마감","lines":["정산 정리"]}]),
 "작가-모집-키트":dict(type="grid",cols=2,title="채널별 모집 메시지",items=[
   {"head":"인스타그램","lines":["작가 모집 헤드라인"]},
   {"head":"네이버 카페","lines":["공예 커뮤니티"]},
   {"head":"오프라인 포스터","lines":["서촌 일대"]},
   {"head":"DM 응대","lines":["문의 → 합류 안내"]}]),
 "사업계획서":dict(type="compare",title="기존 위탁 vs 헐버트",
   left={"label":"기존 위탁·편집숍","lines":["입점비 있음","매달 자릿세","수수료 = 회사 마진","작가는 입점에 머묾"]},
   right={"label":"헐버트잡화점","lines":["입점비 0원","판 만큼만 복지수수료","수수료 = 고정비 회수","파트너 → 주주로 성장"]}),
 "성과지표-KPI":dict(type="grid",cols=3,title="무엇을 측정하나",items=[
   {"head":"작가 잔존율"},{"head":"재입점률"},{"head":"매대 회전"},
   {"head":"복지수수료 전환"},{"head":"고정비 회수율"},{"head":"외국인 구매"}]),
 "정관-거버넌스":dict(type="grid",cols=2,title="거버넌스 핵심",items=[
   {"head":"의사결정 구조","lines":["함께 정하는 원칙"]},
   {"head":"지분·배당","lines":["TBD (신중히)"]},
   {"head":"위장도급 주의","lines":["프리랜서 = 비근로자"]},
   {"head":"투명 운영","lines":["기록·공개"]}]),
 "상표-IP-보호-메모":dict(type="grid",cols=2,title="IP 보호 메모",items=[
   {"head":"상표 출원","lines":["헐버트 명칭"]},
   {"head":"고유 명명","lines":["너투사·나투사"]},
   {"head":"작가 저작권","lines":["작품 권리 = 작가"]},
   {"head":"도용 대응","lines":["모니터링"]}]),
 "헐버트작가촌-기획":dict(type="flow",title="작가 여정 퍼널",items=[
   {"head":"인지","lines":["여기 뭐지?"]},{"head":"지원","lines":["나도 해볼까"]},
   {"head":"활동(1단계)","lines":["잘하고 싶다"]},{"head":"성장(2·3단계)","lines":["더 깊이"]}]),
 "손님-매장안내":dict(type="flow",title="둘러보는 법",items=[
   {"head":"천천히 구경","lines":["눈으로 먼저"]},{"head":"직원께 한마디","lines":["만지기 전"]},
   {"head":"가격 그대로","lines":["작가가 정한 값"]},{"head":"작가 응원","lines":["사람과 꿈에"]}]),
 "hulbert-en":dict(type="pillars",title="Hulbert, in short",items=[
   {"head":"People & dreams","lines":["invest in artists,","not just products"]},
   {"head":"Welfare fee","lines":["covers space,","not company margin"]},
   {"head":"Artist to owner","lines":["consign, partner,","then owner"]}]),
 "개인정보처리방침":dict(type="grid",cols=2,title="개인정보 처리 (초안)",items=[
   {"head":"수집 항목","lines":["성함·연락처 등"]},
   {"head":"이용 목적","lines":["합류 심사·운영"]},
   {"head":"보유 기간","lines":["목적 달성 시 파기"]},
   {"head":"정보주체 권리","lines":["열람·정정·삭제"]}]),
 "이용약관":dict(type="grid",cols=2,title="이용약관 핵심 (초안)",items=[
   {"head":"서비스 범위","lines":["작가 모집·안내"]},
   {"head":"이용자 의무","lines":["도용 금지 등"]},
   {"head":"저작권","lines":["작품 = 작가 100%"]},
   {"head":"분쟁·준거법","lines":["대한민국 법"]}]),
 "사업자정보":dict(type="grid",cols=2,title="사업자 표시 (등록 후)",items=[
   {"head":"상호·대표","lines":["TBD"]},
   {"head":"사업자등록번호","lines":["TBD"]},
   {"head":"통신판매 신고","lines":["중개 여부 확인"]},
   {"head":"연락처","lines":["주소·전화·이메일"]}]),
}

def build_svg(slug):
    g = SLUG_GROUP.get(slug, "idx"); p = PAL[g]
    s = SPEC.get(slug)
    if not s:
        return wrap(slug, p, T(W/2, H/2, slug, 40, p["ink"], "700", "middle"))
    t = s["type"]
    if t == "steps":     inner = render_row(s["items"], p, True, True)
    elif t == "flow":    inner = render_row(s["items"], p, False, True)
    elif t == "pillars": inner = render_row(s["items"], p, False, False)
    elif t == "grid":    inner = render_grid(s["items"], p, s.get("cols", 2))
    elif t == "compare": inner = render_compare(s["left"], s["right"], p)
    else: inner = ""
    return wrap(s["title"], p, inner)

def main():
    os.makedirs(ASSETS, exist_ok=True)
    n = 0
    for slug in SLUG_GROUP:
        with open(os.path.join(ASSETS, slug + ".svg"), "w", encoding="utf-8") as f:
            f.write(build_svg(slug))
        n += 1
    print(f"WROTE {n} diagram SVG -> {ASSETS}")
    print("다음: python3 viewer/build.py")

if __name__ == "__main__":
    main()
