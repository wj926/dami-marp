# template-deck — 새 발표 부트스트랩 템플릿

dami-marp 으로 새 발표를 시작할 때 이 폴더를 통째로 복사해서 시작.

## 사용법

```bash
cp -r ~/.claude/skills/dami-marp/examples/template-deck ~/path/to/my-new-deck
cd ~/path/to/my-new-deck

# 1. 슬라이드 파일명 변경 (kebab-case 의미있는 이름)
mv slides.template.md my-new-deck.md

# 2. image-gen 안 쓰면 IMAGE_PROMPTS 삭제, 쓸 거면 이름만 변경
rm IMAGE_PROMPTS.template.md
# 또는
mv IMAGE_PROMPTS.template.md IMAGE_PROMPTS.md

# 3. 자산을 카테고리별로 assets/ 에 배치 (아래 참고)

# 4. (선택) git 초기화 — 슬라이드 자체 버전 관리
git init && git add . && git commit -m "init: template"

# 5. 빌드
python ~/.claude/skills/dami-marp/bin/build.py my-new-deck.md
```

## 폴더 구조

```
my-new-deck/
├── my-new-deck.md           # 슬라이드 (kebab-case)
├── refs.toml                # 논문 인용 (선택)
├── IMAGE_PROMPTS.md         # image-gen 쓸 때만
├── assets/                  # 모든 자산 (self-contained)
│   ├── fonts/               # *.ttf, *.otf
│   ├── logos/               # 기관 로고, 스폰서 로고
│   └── images/              # 사용자 업로드 + AI 생성 + 인물 + 차트 + 스크린샷
│       └── .history/        # AI 재생성 시 이전 버전 백업 (.gitignore)
├── .history/                # markdown 자체 백업 (auto_size.py 가 자동 생성, .gitignore)
├── pages/                   # pdftoppm 슬라이드 PNG (.gitignore)
└── .gitignore
```

## 자산 카테고리 — 3가지

| 카테고리 | 무엇 | 변경 빈도 | 재사용 범위 |
|---|---|---|---|
| `fonts/` | KoPub, Pretendard 등 `.ttf` `.otf` | 거의 0 | 글로벌 (모든 발표) |
| `logos/` | 기관 로고, 스폰서, 협력기관 | 거의 0 | 같은 기관 발표 |
| `images/` | 사용자 업로드 사진·스크린샷·차트 + AI 생성 인포그래픽 + 인물 사진 | 자주 | 그 발표 전용 |

`images/` 안이 어수선해지면 prefix 컨벤션 권장:
- `slide3_pipeline.png` — AI 생성 (slide-prefix)
- `chart_revenue_2024.png` — 사용자 차트
- `screenshot_login.png` — 스크린샷
- `photo_lab.jpg`, `person_홍길동.jpg` — 사진·인물

## 마크다운·CSS 에서 참조

```markdown
![w:760](assets/images/slide3_pipeline.png)
![w:90 h:90](assets/images/person_speaker.jpg)
```

```css
@font-face {
    font-family: 'KoPubDotum';
    src: url('assets/fonts/KoPub Dotum Light.ttf') format('truetype');
}
section::before {
    background-image: url('assets/logos/skku.jpg');
}
```

## 새 발표 부트스트랩 시 재사용 자산 가져오기

```bash
# 이전 발표(prev-deck)에서 fonts·logos 만 통째로 복사
cp -r ~/path/to/prev-deck/assets/fonts ~/path/to/my-new-deck/assets/
cp -r ~/path/to/prev-deck/assets/logos ~/path/to/my-new-deck/assets/
# images/ 는 발표 전용이라 복사 X
```

상세 워크플로우는 [../../image-gen/README.md](../../image-gen/README.md) 참고.
