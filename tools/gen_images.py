#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
헐버트 프로젝트 문서용 '이해를 돕는' 일러스트 생성기 (OpenAI 이미지 API).

⚠️ 보안: API 키는 코드/깃에 절대 넣지 마세요. 환경변수에서만 읽습니다.
    export OPENAI_API_KEY="sk-...본인 키..."     # macOS/Linux
    setx  OPENAI_API_KEY "sk-...본인 키..."       # Windows(새 터미널부터 적용)

사용법:
    python3 tools/gen_images.py            # 아직 없는 문서 이미지만 생성
    python3 tools/gen_images.py --force    # 전부 다시 생성
    python3 tools/gen_images.py --list     # API 호출 없이 프롬프트만 미리보기(무료)
    python3 tools/gen_images.py 작가-소개 브랜드-정의서   # 특정 문서만
    python3 viewer/build.py                # 생성 후 뷰어에 반영(이미지 삽입)

기본 모델/품질(여러 장이라 저렴하게):
    OPENAI_IMAGE_MODEL   (기본 gpt-image-1)
    OPENAI_IMAGE_QUALITY (기본 low)
    OPENAI_IMAGE_SIZE    (기본 1024x1024)
모두 환경변수로 덮어쓸 수 있습니다. 예: OPENAI_IMAGE_QUALITY=medium

참고: AI 생성 이미지는 (1) 글자가 깨질 수 있어 '글자 없는' 개념 일러스트로 지시하며,
      (2) 실제 (미정) 매장 사진이 아니라 이해를 돕는 콘셉트 그림입니다.
"""
import os, sys, re, json, base64, time, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "viewer", "assets")

MODEL   = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1")
QUALITY = os.environ.get("OPENAI_IMAGE_QUALITY", "low")
SIZE    = os.environ.get("OPENAI_IMAGE_SIZE", "1024x1024")
ENDPOINT = "https://api.openai.com/v1/images/generations"

# build.py의 DOCS와 동기화 유지 (relpath 목록)
DOC_PATHS = [
    "docs/문서-지도.md", "README.md",
    "docs/작가-소개.md", "docs/브랜드-정의서.md",
    "docs/홈페이지-사이트맵.md", "docs/홈-랜딩-카피.md",
    "docs/pages/소개.md", "docs/pages/공간소개.md", "docs/pages/작가들.md",
    "docs/pages/소식.md", "docs/pages/합류하기.md", "docs/pages/문의.md",
    "docs/작가-운영정책.md", "docs/입점-동의서.md", "docs/운영-매뉴얼.md",
    "docs/작가-모집-키트.md",
    "docs/사업계획서.md", "docs/성과지표-KPI.md", "docs/정관-거버넌스.md", "docs/상표-IP-보호-메모.md",
    "docs/헐버트작가촌-기획.md",
    "docs/손님-매장안내.md", "docs/en/hulbert-en.md",
    "docs/legal/개인정보처리방침.md", "docs/legal/이용약관.md", "docs/legal/사업자정보.md",
]

STYLE = (
    "Style: warm, friendly minimal flat editorial illustration with subtle hanji "
    "(Korean mulberry paper) texture; muted earthy palette — terracotta, ink brown, "
    "cream, soft pine-green accent; motifs of a Seochon hanok (Korean traditional house) "
    "next to Gyeongbokgung, and handmade craft (ceramics, fabric, candles). "
    "Clean simple shapes, generous negative space, calm and inviting, easy to understand "
    "at a glance. IMPORTANT: do NOT render any text, letters, words, numbers or logos in the image."
)

def slug_of(relpath):
    base = os.path.basename(relpath)
    return base[:-3] if base.endswith(".md") else base

def extract_concept(relpath):
    """문서에서 제목 + 첫 요약 인용구를 뽑아 개념 설명을 만든다."""
    title, summary = slug_of(relpath), ""
    try:
        with open(os.path.join(ROOT, relpath), encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return title, summary
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip(); break
    for line in text.splitlines():
        s = line.strip()
        if s.startswith(">") and "🏷️" not in s:
            summary = s.lstrip("> ").strip()
            if summary:
                break
    # 마크다운 기호 제거
    clean = lambda s: re.sub(r"[*`#>\[\]]", "", s).replace("—", "-").strip()
    return clean(title), clean(summary)[:300]

def build_prompt(relpath):
    title, summary = extract_concept(relpath)
    concept = f"Core idea: {summary}. " if summary else ""
    return (
        "Create a single clear conceptual illustration that helps a reader instantly "
        f"understand what this document is about. Topic: \"{title}\". {concept}"
        "Make it metaphorical and self-explanatory without relying on any words. " + STYLE
    )

def post_image(prompt):
    body = json.dumps({"model": MODEL, "prompt": prompt, "n": 1,
                       "size": SIZE, "quality": QUALITY}).encode("utf-8")
    req = urllib.request.Request(ENDPOINT, data=body, method="POST", headers={
        "Authorization": "Bearer " + API_KEY,
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.loads(r.read().decode("utf-8"))
    return base64.b64decode(data["data"][0]["b64_json"])

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    force, list_only = "--force" in flags, "--list" in flags

    targets = DOC_PATHS
    if args:  # 특정 문서만 (slug 또는 파일명 일부)
        targets = [p for p in DOC_PATHS if any(a in slug_of(p) or a in p for a in args)]
        if not targets:
            sys.exit("일치하는 문서가 없습니다: " + ", ".join(args))

    if list_only:
        for p in targets:
            print(f"\n■ {slug_of(p)}\n{build_prompt(p)}")
        print(f"\n[미리보기] {len(targets)}개 — API 호출 없음(무료).")
        return

    if not API_KEY:
        sys.exit("❌ OPENAI_API_KEY 환경변수가 없습니다. 키를 코드에 넣지 말고 환경변수로 설정하세요.")

    os.makedirs(ASSETS, exist_ok=True)
    print(f"모델={MODEL} 품질={QUALITY} 크기={SIZE} · 대상 {len(targets)}개\n")
    ok = skip = fail = 0
    for n, relpath in enumerate(targets, 1):
        slug = slug_of(relpath)
        out = os.path.join(ASSETS, slug + ".png")
        if os.path.exists(out) and not force:
            print(f"[{n}/{len(targets)}] · 건너뜀(이미 있음) {slug}.png"); skip += 1; continue
        prompt = build_prompt(relpath)
        for attempt in range(3):
            try:
                png = post_image(prompt)
                with open(out, "wb") as f:
                    f.write(png)
                print(f"[{n}/{len(targets)}] ✅ {slug}.png ({len(png)//1024} KB)"); ok += 1
                break
            except urllib.error.HTTPError as e:
                msg = e.read().decode("utf-8", "ignore")[:200]
                if e.code in (429, 500, 502, 503) and attempt < 2:
                    wait = 2 ** (attempt + 1)
                    print(f"   …{e.code} 재시도 {wait}s"); time.sleep(wait); continue
                print(f"[{n}/{len(targets)}] ❌ {slug}: HTTP {e.code} {msg}"); fail += 1; break
            except Exception as e:
                print(f"[{n}/{len(targets)}] ❌ {slug}: {e}"); fail += 1; break
        time.sleep(0.4)
    print(f"\n완료 — 생성 {ok} · 건너뜀 {skip} · 실패 {fail}")
    if ok:
        print("다음: python3 viewer/build.py  → 뷰어에 이미지 반영 후 커밋/푸시")

API_KEY = os.environ.get("OPENAI_API_KEY", "")

if __name__ == "__main__":
    main()
