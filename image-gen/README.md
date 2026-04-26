# dami-marp / image-gen — 슬라이드 이미지 생성·삽입·자동 사이즈 조정

dami-marp 본 스킬에 부속된 **이미지 워크플로우 헬퍼**. 슬라이드를 만든 다음 → 그림으로 보여줬을 때 더 효과적인 부분을 ChatGPT에게 생성시키고 → 슬라이드에 박은 뒤 → 렌더링/캡쳐 결과를 보면서 사이즈를 자동 조정하는 5단계 루프를 지원한다.

> **⚠️ 이 워크플로우는 전부 선택사항(opt-in)임.** 1단계(슬라이드 작성)만으로도 dami-marp 결과물은 완성되며, **2~5단계는 시간/필요/에러 상황에 따라 자유롭게 건너뛸 수 있음**. 자세한 분기 가이드는 아래 [언제 건너뛰어도 되나](#언제-건너뛰어도-되나) 참고.

## 7단계 워크플로우 (전체 풀 자동화)

1. **[필수] 슬라이드 작성** — 본 스킬(dami-marp)의 본 가이드대로 `slides.md` 작성. **여기까지가 deliverable의 핵심**
2. **[선택] 시각화 후보 추출** — 작성한 슬라이드를 다시 한 번 훑으면서, **그림으로 보여줬을 때 효과적인 콘텐츠**를 골라낸다
   - 아키텍처/플로우 (텍스트 박스 나열보다 도식이 효과적)
   - 포지셔닝 매트릭스 (2×2, 4분면)
   - 팀 구조도, 로드맵 타임라인, 5각형/육각형 강점 그래픽 등
3. **[선택] 이미지 프롬프트 작성** — 별도 `IMAGE_PROMPTS.md` 에 파일별 프롬프트 작성. ChatGPT 로그인 세션은 `~/.cache/chatgpt-image-profile/` 에 영속되므로 재활용
4. **[선택] ChatGPT 이미지 생성** — `chatgpt_image.py` 가 원격 Linux(Xvfb headful Playwright)에서 일괄 생성하고 슬라이드 폴더의 `assets/` 로 다운로드
5. **[선택, 4 후속] 사이즈 자동 조정** — `auto_size.py` 가 슬라이드별 PDF 렌더 → 콘텐츠 bbox 측정 → `![w:N]` 폭 조정 → 재빌드 루프
6. **[선택, 4 후속] 시각 자동 검수** — Claude Code(멀티모달 AI agent) 자신이 슬라이드 PNG 를 `Read` 툴로 직접 보고 체크리스트 평가 (헐루시네이션/위치/구도/톤). 외부 API 호출 0
7. **[선택, 6 후속] 문제 발견 시 자동 재생성·재배치** — 평가 결과별 액션을 자동 실행: 프롬프트 재정제 → 단계 4 재실행, 또는 markdown 레이아웃 수정 → 재빌드 → 단계 6 재평가. 수렴 또는 max_iter 까지 반복

## 풀 자동화 루프 (단계 5~7 통합 실행 가이드)

이 절차는 **Claude Code 같은 멀티모달 AI agent 가 직접 따라가도록 설계됨**. 외부 API 키 불필요. 별도 스크립트 없이 native 툴(Read/Edit/Bash)로 전부 실행 가능.

### 한 사이클 (이미지 1장 기준)

```
loop attempt = 1..N:
  ── A. 빌드 ───────────────────────────────────────
  $ python ~/.claude/skills/dami-marp/bin/build.py slides.md

  ── B. 슬라이드별 PNG 렌더 ─────────────────────────
  $ pdftoppm -r 120 slides.pdf pages/page -png
    # 또는 auto_size.py 가 이미 빌드+렌더 한 결과 활용

  ── C. 사이즈 자동 조정 (수렴할 때까지) ─────────────
  $ python ~/.claude/skills/dami-marp/image-gen/auto_size.py slides.md
    # fill_ratio 가 [lo, hi] 안에 들어올 때까지 ![w:N] 조정·재빌드
    # → 사이즈 차원에서 수렴

  ── D. 시각 검수 (멀티모달, 메인 경로) ────────────
  Claude Code (자기 자신) 가 Read 툴로 pages/page-NN.png 를 직접 봄.
  체크리스트:
    [ ] AI 이미지 안의 한글/영문 텍스트가 의미있고 정확함 (헐루시네이션 X)
    [ ] 슬라이드 본문 텍스트와 이미지가 겹치거나 가리지 않음
    [ ] 이미지 위치(가운데/우측/좌우분할)가 의도와 일치
    [ ] 발표 톤·색감·구도가 다른 슬라이드와 어울림
    [ ] 슬라이드 footer/header 영역을 침범하지 않음

  → 이게 디폴트. 비전 가능한 AI agent (Claude Code, GPT-4V 등) 이면
    외부 API 호출 0개로 native multimodal 만으로 충분.

  (vision 없는 환경이라면 ask-chatgpt-linux 로 캡쳐 첨부해서 같은
   체크리스트 위임 가능. 하지만 메인 경로는 항상 self-vision.)

  ── E. 문제 유형별 자동 액션 ───────────────────────
  PASS                        → 종료, 다음 이미지로
  헐루시네이션·구도 이슈      → IMAGE_PROMPTS.md 의 해당 프롬프트를
                                 LLM 이 재작성 (예: "텍스트 라벨 제거",
                                 "16:9 wide", "minimalist palette" 추가)
                              → bash run.sh generate ... --only <stem>
                                 으로 그 한 장만 재생성
                              → 단계 A 로 돌아감
  위치/레이아웃 이슈          → slides.md 수정:
                                 <center>↔![bg right]↔cols-2 전환
                                 또는 ![w:N] 직접 조정
                              → 단계 A 로 돌아감
  사이즈 미세조정 필요        → auto_size.py --lo 0.90 --hi 0.97
                                 같이 빡빡한 범위로 재실행
                              → 단계 A 로 돌아감

  attempt += 1, max_iter 초과시 마지막 상태 보고하고 사용자에 인계
```

### Claude Code 호출 패턴 (실제 명령 예시)

```bash
# 1. 풀 빌드 + 슬라이드 PNG 렌더
python ~/.claude/skills/dami-marp/bin/build.py slides.md
mkdir -p pages
pdftoppm -r 120 slides.pdf pages/page -png

# 2. 사이즈 수렴
python ~/.claude/skills/dami-marp/image-gen/auto_size.py slides.md

# 3. 이미지 들어간 슬라이드만 Claude 가 Read 로 봄
#    (auto_size.py 의 stdout 에서 어떤 슬라이드에 어떤 이미지 박혔는지 추출)

# 4. 문제 발견 시:
#    a) 프롬프트 재작성 → IMAGE_PROMPTS.md 의 해당 블록 Edit
#    b) 그 한 장만 재생성:
bash ~/.claude/skills/dami-marp/image-gen/run.sh generate \
    IMAGE_PROMPTS.md --output-dir assets/ --only slide3_architecture

# 5. 다시 1번부터
```

### 멈춤 조건

- 모든 이미지 PASS → 정상 종료
- max_iter (per-image 기본 5회) 초과 → 그 이미지만 사용자에 보고하고 다음 이미지 진행
- ChatGPT 세션 만료/한도 도달 → 단계 4·7 스킵하고 텍스트 슬라이드로 fallback (troubleshooting.md §3·§7 참고)

### 비용·복잡도

- **API 호출 0** — Claude Code 가 자기 컨텍스트로 처리. ChatGPT 검수도 기존 ask-chatgpt-linux 프로필 재사용
- **시간** — 이미지 1장당 사이즈 수렴 1~3회 + 검수 1회 + (있다면) 재생성 1~2회 = 평균 3~5분
- **수렴성** — 사이즈는 결정적, 위치는 한두 번 시도면 거의 수렴. 헐루시네이션은 프롬프트 재정제 1~2번에 잡힘. 안 잡히면 라벨 제거가 정답

## 언제 건너뛰어도 되나

**이미지 생성이 불필요/곤란한 흔한 상황**:

| 상황 | 권장 행동 |
|---|---|
| 시간이 부족함 (마감 임박) | **2~5단계 전부 스킵**. 1단계 텍스트 슬라이드만으로 빌드 → 제출 |
| 텍스트만으로 충분히 명확 | 스킵. 억지로 그림 박는다고 더 좋아지지 않음 |
| ChatGPT 로그인 세션 만료/접속 에러 | 4단계 스킵. 빈 자리는 placeholder 박스 또는 텍스트 표/리스트로 대체 |
| 원격 Linux 호스트 다운/SSH 에러 | 4단계 스킵. (또는 사용자가 직접 ChatGPT 웹에서 받아서 `assets/` 에 넣기) |
| AI 이미지에 한글 헐루시네이션 (예: 건기식 → 전기시) 반복 | 한두 번 재생성으로 안 풀리면 스킵 후 텍스트로 우회. 영문/숫자 라벨로 프롬프트 재작성도 옵션 |
| 이미지를 외부 디자이너/포토샵으로 받아옴 | 3·4단계 스킵, **5단계만 사용** (이미 박힌 `![w:N]` 자동 조정) |
| `auto_size.py` 수렴 실패 (max_iter 도달) | 마지막 결과 폭 그대로 두거나, `--lo --hi` 조정 후 재시도. 안 되면 수동으로 `![w:N]` 값 직접 조정 |

**핵심 원칙**:
- **1단계 결과물은 항상 자체 완결**. 본 스킬(dami-marp)의 `## h2 + bullet` 양식을 충실히 따르면 이미지 없이도 발표용으로 충분함
- 2~5단계는 **시간 여유와 효과 기대치가 둘 다 있을 때만** 진행
- 중간 단계에서 막히면 망설이지 말고 **그 시점까지 만들어진 슬라이드로 빌드해 제출/공유**. 이미지는 나중에 추가해서 재빌드 가능
- AI 생성 이미지는 **반드시 사람이 검수** (특히 한글 텍스트 포함 시). 헐루시네이션 슬라이드를 그대로 발표하는 게 텍스트 슬라이드보다 훨씬 나쁜 결과를 부름

## 파일 구성

```
dami-marp/image-gen/
├── README.md            # 이 파일
├── chatgpt_image.py     # ChatGPT 이미지 생성 (Playwright + remote Xvfb)
├── run.sh               # 원격 Linux로 chatgpt_image.py 송출/실행
├── setup_linux.sh       # 원격 Linux에 의존성 설치
└── auto_size.py         # 슬라이드 이미지 폭 자동 조정 (PyMuPDF + numpy)
```

## 단계 4: ChatGPT 이미지 생성

**두 가지 실행 모드** — `IMAGE_GEN_REMOTE` env 로 토글:

| 모드 | 트리거 | 사용 환경 |
|---|---|---|
| **로컬 (디폴트)** | env 미설정 또는 `IMAGE_GEN_REMOTE=local` | 빌드와 ChatGPT 자동화가 같은 리눅스 머신 (dami-marp upstream 환경) |
| **원격 SSH** | `IMAGE_GEN_REMOTE=<your-ssh-alias>` | Windows·Mac 에서 작업 + 별도 리눅스 서버에서 ChatGPT 자동화 |

**전제 (양 모드 공통)**:
- 리눅스 머신에서 `bash run.sh setup` 한 번 실행해 Playwright/Xvfb/x11vnc 설치 + venv 생성 (`~/image-gen/`)
- ChatGPT 로그인 세션을 한 번 띄워서 `~/.cache/chatgpt-image-profile/` 프로필 만들기 (`bash run.sh login`)
- 이후 같은 프로필 재활용

**프롬프트 파일 형식** (`IMAGE_PROMPTS.md`):

```markdown
### `slide3_architecture.png` — 헬스 지식그래프 + LLM 아키텍처

- **Prompt**:
  ```
  깔끔한 인포그래픽 스타일로 …
  ```
```

**실행**:

```bash
./run.sh path/to/IMAGE_PROMPTS.md path/to/output/assets/
```

## 단계 5: 자동 사이즈 조정

`auto_size.py` 가 MD에서 모든 `![w:N](path)` 이미지를 자동 발견 → 각 이미지가 속한 슬라이드 인덱스 추론 → PDF 렌더 → fill_ratio 측정 → 폭 조정.

**기본 사용**:

```bash
python auto_size.py path/to/slides.md
```

**옵션**:

| 옵션 | 기본값 | 설명 |
|---|---|---|
| `--lo` | 0.85 | 목표 fill_ratio 하한 (이보다 낮으면 키움) |
| `--hi` | 0.96 | 목표 fill_ratio 상한 (이보다 높거나 overflow 면 줄임) |
| `--max-iter` | 8 | 이미지 하나당 최대 반복 횟수 |
| `--only` | (전체) | 콤마 구분 파일명만 조정 (예: `slide3_arch.png,slide5_team.png`) |

**알고리즘** (각 이미지마다):
1. 빌드 → PDF 생성
2. 해당 슬라이드 페이지를 100dpi PNG 로 렌더
3. 슬라이드 상단~92% 영역에서 non-white 픽셀의 마지막 row를 찾음 (footer 제외)
4. `fill_ratio = bottom / footer_start`
5. ratio < lo → 폭 ×1.15 / ratio > hi 또는 overflow → 폭 ×0.85
6. `[MIN_W, MAX_W] = [200, 1200]` 으로 클램프, 수렴하면 종료

**튜닝 팁**:
- 글자가 안 보일 만큼 작아지면 `--lo 0.90 --hi 0.97` 처럼 더 빡빡하게
- 텍스트 callout 과 같이 나오는 슬라이드는 이미지가 작아야 하므로 `--hi 0.85` 정도로 낮춰서 사용

## 시행착오 / 트러블슈팅

**호출 전 반드시 [troubleshooting.md](troubleshooting.md) 먼저 읽기**. 자동 로그인 함정, CRD 디스플레이 직접 사용한 수동 로그인 절차, `<stem>.fail.png` 디버그 스크린샷 원인별 대처표, 호출 직전 체크리스트가 정리돼 있음.

핵심 함정 5가지 (상세는 troubleshooting.md):
- **Korean path SSH 깨짐** — 원격 경로에 한글 금지. 워크 디렉토리는 ASCII-only
- **세션 만료 시 자동 로그인 신뢰 금지** — UI 변경 빈번, fail.png 가 로그인 화면이면 즉시 `--display :22` 수동 로그인 경로 (troubleshooting.md §3)
- **언어 관계없이 필요한 라벨은 다 넣음** — 한글·영문·숫자 모두 GPT-4o image gen 이 거의 정확히 그림. 가아아끔 깨지는 글자는 단계 6 시각 자동 검수 (Claude Code 가 PNG 직접 봄) 가 잡음 — 그래서 검수가 필수. 발견 시 단계 7 자동 재생성 또는 영문/숫자/제거 fallback
- **Marp inline `<img style>` 무시** — 반드시 `![w:N](path)` 마크다운 문법 사용
- **CRD 같이 죽이지 말 것** — `pkill -f /opt/google/chrome/chrome` (basename 매칭)으로 좁혀서 chromium만

## 프로젝트 구조 & 백업 정책

### 폴더 구조 (각 발표가 독립된 self-contained 폴더)

```
<프로젝트 폴더, 위치·이름 자유>/
├── <deck-name>.md             # kebab-case 의미있는 이름 (slides.md 같은 generic 금지)
├── <deck-name>.pdf            # 빌드 산출물 (.gitignore)
├── refs.toml                  # 논문 인용 (선택)
├── IMAGE_PROMPTS.md           # image-gen 단계 3 (선택)
├── assets/                    # 모든 자산 (3 카테고리)
│   ├── fonts/                 # *.ttf, *.otf — 거의 안 바뀜, 글로벌 재사용
│   ├── logos/                 # 기관·스폰서 로고 — 거의 안 바뀜
│   └── images/                # 사용자 업로드 + AI 생성 + 인물 + 차트 + 스크린샷
│       └── .history/          # AI 재생성 시 이전 버전 백업 (.gitignore)
├── .history/                  # auto_size.py 의 markdown 백업 (.gitignore)
├── pages/                     # pdftoppm 슬라이드 PNG (.gitignore)
└── .gitignore
```

원칙:
- **각 폴더는 self-contained** — symlink/`../` 상위참조 금지. 옮겨도 안 깨짐
- **3 카테고리 컨벤션** — `assets/{fonts,logos,images}/`. fonts·logos 는 거의 변경 없음, images 만 발표마다 새로
- **재사용 자산만 복사** — 새 발표 부트스트랩 시 `cp -r prev/assets/{fonts,logos} new/assets/` 로 fonts·logos 만 가져옴
- **`images/` 안에서 prefix 로 정렬** — `slide*_*.png` (AI), `chart_*.png`, `screenshot_*.png`, `photo_*.jpg`, `person_*.jpg`
- **위치·이름 자유** — `~/projects/rise/marp/`, `D:\발표\client-x\`, `~/conferences/2026-aaai/poster/` 다 OK

### 새 발표 부트스트랩

```bash
cp -r ~/.claude/skills/dami-marp/examples/template-deck ~/path/to/my-new-deck
cd ~/path/to/my-new-deck
mv slides.template.md my-new-deck.md
# (image-gen 안 쓸 거면 IMAGE_PROMPTS.template.md 삭제)
# 자기 기관 자산을 assets/ 에 추가
git init && git add . && git commit -m "init"   # 선택: 슬라이드 자체 버전관리
```

### 백업·버전 관리 — 3중 안전망

| 대상 | 메커니즘 | 위치 | 트리거 |
|---|---|---|---|
| **슬라이드 markdown** | `auto_size.py` 가 자동 백업 | `<project>/.history/<deck>_<timestamp>.md` | auto_size.py 실행 시 1회 |
| **슬라이드 markdown (수동 편집 포함)** | git | `.git/` | 사용자가 commit |
| **AI 생성 이미지** | 자동 루프가 재생성 직전 백업 | `<project>/assets/images/.history/<stem>_<timestamp>.png` | 자동 루프 단계 7 |

**복구 시나리오**:
- auto_size.py 가 폭 조정을 망쳤을 때 → `.history/<deck>_*.md` 중 가장 최근 것을 본 markdown 위치로 복원
- 재생성된 이미지가 더 나빠졌을 때 → `assets/.history/<stem>_*.png` 중 원하는 것으로 복원
- 더 큰 변경 (이전 발표 상태로 롤백) → git 사용

**git 권장 정책**:
- `git init` 한 번
- `IMAGE_PROMPTS.md` 수정·이미지 재생성·markdown 변경마다 의미있는 commit
- `.gitignore` 는 `template-deck/.gitignore` 그대로 사용 (PDF/built/.history/pages/.fail.png 제외)

**`.history/` 정리**:
- 자동으로 안 지움 — 사용자가 만족하면 수동으로 비우거나 git stash 후 정리
- 디스크 부담은 markdown 수십 KB × 회수 정도라 보통 무시 가능
- 이미지는 1~5 MB × 회수라 누적 시 정리 권장

## 본 스킬과의 관계

이 sub-feature 는 **선택적**. dami-marp 본 가이드만으로 충분하면 굳이 안 써도 되며, 이미지가 많이 들어가는 발표자료(연구 발표, 사업계획서, 학회 포스터 변환 등)에서 가치가 큼.

원본 `chatgpt-image` 스킬은 그대로 살아있고, 이 폴더는 **dami-marp 워크플로우에 맞춰 sanitize/통합한 사본**이다. 두 스킬은 같은 ChatGPT 프로필(`~/.cache/chatgpt-image-profile/`)을 공유하므로 한 번 로그인해두면 둘 다 재활용된다.
