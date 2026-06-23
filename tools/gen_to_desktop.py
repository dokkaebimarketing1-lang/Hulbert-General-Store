#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
헐버트 — 생성형 이미지를 '내 컴퓨터 바탕화면 폴더'에 저장하는 단독 실행 스크립트.

이 파일 하나만 있으면 됩니다(저장소 불필요). 인터넷 + 파이썬 3 + OpenAI 키 필요.

[실행 방법]
1) 이 파일을 바탕화면에 둡니다.
2) 터미널(또는 명령 프롬프트)에서:
       python3 gen_to_desktop.py          # 샘플 4장만 (품질 확인용)
       python3 gen_to_desktop.py --all     # 전체 생성
   * 키를 미리 환경변수로 두면 입력 안 해도 됩니다:
       (mac/Linux)  export OPENAI_API_KEY="sk-..."
       (Windows)    setx  OPENAI_API_KEY "sk-..."
     안 두면 실행 시 안전하게 물어봅니다(입력 화면에 안 보임).

저장 위치: 바탕화면/헐버트-이미지/  (자동 생성)
모델: gpt-image-1 · 품질 low(여러 장이라 저렴) · 1024x1024
※ 채팅에 한 번 노출된 키는 폐기하고 새 키를 쓰세요.
"""
import os, sys, json, base64, time, pathlib, urllib.request, urllib.error

MODEL   = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1")
QUALITY = os.environ.get("OPENAI_IMAGE_QUALITY", "low")
SIZE    = os.environ.get("OPENAI_IMAGE_SIZE", "1024x1024")
ENDPOINT = "https://api.openai.com/v1/images/generations"

STYLE = (
    " Warm, friendly editorial illustration with subtle hanji (Korean mulberry paper) "
    "texture; muted earthy palette of terracotta, ink brown, cream and soft pine-green; "
    "a Seochon hanok (Korean traditional house) near Gyeongbokgung and handmade crafts "
    "(ceramics, fabric, candles); clean, calm, inviting. No text, letters, numbers or logos."
)

# (저장 파일명, 그릴 개념) — 앞 4개가 기본 샘플
DOCS = [
    ("01_작가-소개",     "An artist's handmade work displayed inside a sunlit hanok, valuing the person and their dream over the product"),
    ("02_공간소개",      "A cozy hanok craft shop right beside Gyeongbokgung palace in Seochon, tourists strolling by"),
    ("03_홈-랜딩",       "Warm welcome scene: a maker freed from worry, joyfully creating crafts in a hanok"),
    ("04_합류하기",      "An artist sending a photo of their work and a one-line dream to join a hanok community"),
    ("05_작가들",        "Diverse handmade-craft makers gathered as lifelong companions in a hanok courtyard"),
    ("06_브랜드",        "Together, fair and transparent: hands supporting an artist from behind, hanok motif"),
    ("07_복지수수료",    "A shared hanok display shelf like a community park bench, gentle and fair"),
    ("08_3단계성장",     "Three rising stepping stones in a hanok garden symbolizing growth from tenant to owner"),
    ("09_서촌위치",      "Map-like scene of Seochon alleys between Gyeongbokgung and Inwangsan mountain, galleries and workshops"),
    ("10_소식",          "A small hanok shop preparing to open, lantern glowing, announcement mood"),
]

def desktop_dir():
    home = pathlib.Path.home()
    for c in (home/"Desktop", home/"바탕 화면", home/"OneDrive"/"Desktop", home/"OneDrive"/"바탕 화면"):
        if c.exists():
            return c
    return home  # 못 찾으면 홈 폴더

def get_key():
    k = os.environ.get("OPENAI_API_KEY", "").strip()
    if k:
        return k
    try:
        import getpass
        return getpass.getpass("OpenAI API 키를 붙여넣고 Enter (화면에 안 보임): ").strip()
    except Exception:
        return input("OpenAI API 키: ").strip()

def generate(key, prompt):
    body = json.dumps({"model": MODEL, "prompt": prompt + STYLE,
                       "n": 1, "size": SIZE, "quality": QUALITY}).encode("utf-8")
    req = urllib.request.Request(ENDPOINT, data=body, method="POST", headers={
        "Authorization": "Bearer " + key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.loads(r.read().decode("utf-8"))
    return base64.b64decode(data["data"][0]["b64_json"])

def main():
    do_all = "--all" in sys.argv
    targets = DOCS if do_all else DOCS[:4]
    out = desktop_dir() / "헐버트-이미지"
    out.mkdir(parents=True, exist_ok=True)
    print(f"저장 위치: {out}")
    print(f"모델={MODEL} 품질={QUALITY} 크기={SIZE} · {len(targets)}장\n")

    key = get_key()
    if not key:
        print("키가 없어 종료합니다."); return

    ok = fail = 0
    for i, (name, concept) in enumerate(targets, 1):
        dest = out / (name + ".png")
        for attempt in range(3):
            try:
                png = generate(key, concept)
                dest.write_bytes(png)
                print(f"[{i}/{len(targets)}] OK  {dest.name}  ({len(png)//1024} KB)"); ok += 1
                break
            except urllib.error.HTTPError as e:
                msg = e.read().decode("utf-8", "ignore")[:160]
                if e.code == 401:
                    print("키가 올바르지 않습니다(401). 새 키를 확인하세요."); return
                if e.code in (429, 500, 502, 503) and attempt < 2:
                    print(f"   …{e.code} 잠시 후 재시도"); time.sleep(2**(attempt+1)); continue
                print(f"[{i}/{len(targets)}] 실패 {name}: HTTP {e.code} {msg}"); fail += 1; break
            except urllib.error.URLError as e:
                print(f"[{i}/{len(targets)}] 네트워크 오류({e.reason}). 인터넷 연결을 확인하세요."); fail += 1; break
            except Exception as e:
                print(f"[{i}/{len(targets)}] 실패 {name}: {e}"); fail += 1; break
        time.sleep(0.4)

    print(f"\n완료 — 성공 {ok} · 실패 {fail}")
    print(f"바탕화면의 '헐버트-이미지' 폴더를 열어 확인하세요: {out}")
    if not do_all and ok:
        print("전체(10장) 만들려면:  python3 gen_to_desktop.py --all")

if __name__ == "__main__":
    main()
