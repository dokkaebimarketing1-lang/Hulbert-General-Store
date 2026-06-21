# 문서 뷰어 (HTML)

`docs/`의 모든 문서를 **한 페이지에서** 보는 뷰어입니다. 상단 **그룹·상태 필터 + 검색**으로
좁히고, 문서 버튼을 누르면 내용이 바로 펼쳐집니다. 외부 라이브러리 없이 **혼자서 열립니다**.

## 여는 법
`viewer/index.html`을 브라우저로 그냥 더블클릭해서 열면 됩니다. (인터넷 연결 불필요)

## 다시 만드는 법 (문서가 바뀌었을 때)
```bash
pip install markdown      # 최초 1회
python3 viewer/build.py   # docs/ 전체를 다시 읽어 index.html 갱신
```

새 문서를 추가했다면 `viewer/build.py`의 `DOCS` 목록에 한 줄(경로·그룹)만 더해 주세요.
