# image-gen 시행착오 — 반드시 읽고 시작할 것

`image-gen/run.sh`(또는 동치 호출)로 슬라이드 이미지를 생성할 때 **이미 한번 부딪힌 함정들**. 처음부터 다시 시행착오 반복하지 말 것.

> **실행 모드** — `IMAGE_GEN_REMOTE` env 로 토글. 본 문서 명령은 양쪽 다 동작:
> - **로컬 (디폴트)**: env 미설정 → 같은 리눅스 머신에서 직접 실행. SSH·SCP 단계 모두 생략됨.
> - **원격 SSH**: `IMAGE_GEN_REMOTE=<your-ssh-alias>` 설정 → Windows·Mac → 리눅스 forwarding.
>
> 아래 `ssh <REMOTE> <명령>` 표기는 원격 모드 한정. 로컬 모드면 `<명령>` 부분만 직접 실행.

---

## 1. 호출 한 줄

```bash
bash ~/.claude/skills/dami-marp/image-gen/run.sh generate \
    "<프로젝트 폴더>/IMAGE_PROMPTS.md" \
    --output-dir "<프로젝트 폴더>/assets/" \
    --timeout 240
```

- 경로는 Windows 경로 그대로 OK. `run.sh`가 내부에서 Linux 경로로 매핑함
- 이미 존재하는 파일은 자동 스킵 → 실패 후 재실행 안전
- 일부만 다시 만들고 싶으면 `--only <stem>` (확장자 제외, 콤마 구분)
- 산출물은 Dropbox/iCloud 등 동기화 폴더에 떨어뜨려야 Windows·Mac 측에 자동 동기화됨

## 2. 절대 하지 말 것

### 2.1 자동 로그인을 신뢰하지 말 것

`chatgpt_image.py` 안에 `_ensure_logged_in()` 헬퍼가 있지만 **ChatGPT UI가 자주 바뀌어 자주 깨짐**. 실제로 만난 케이스:

- "로그인" 버튼이 사이드바(`#stage-slideover-sidebar`) 또는 `#thread-bottom-container`에 가려져서 클릭 retry만 무한 반복
- 클릭해도 어떨 때는 페이지 내 모달, 어떨 때는 `auth.openai.com`으로 풀 페이지 리다이렉트 (분기 처리 필요)
- "Google 계정으로 계속하기" 버튼이 `<button>` / `<a>` / `<div role="button">` 사이에서 왔다갔다
- 로그인 후 `#modal-no-auth-login` 오버레이가 textbox 클릭을 가로채는 시점 추가

**증상**: `[1/N] xxx.png`만 출력되고 한참 뒤 `❌ timed out` + `<stem>.fail.png` 디버그 스크린샷 생성. 스크린샷이 로그인 화면이면 100% 이 문제.

**대처**: 자동 로그인 고치려고 시간 쓰지 말고 **즉시 사용자에게 수동 로그인 요청** (다음 항목).

### 2.2 동시에 두 번 호출하지 말 것

`~/.cache/chatgpt-image-profile/`은 한 번에 한 Chromium 프로세스만 락. 백그라운드로 돌리거나 병렬 호출하면 둘 다 깨짐. 같은 프로필을 쓰는 `ask-chatgpt-linux` 등 다른 스킬도 동시 사용 금지.

### 2.3 한 번에 너무 많이 던지지 말 것

순차 처리이므로 장당 30~60초 + 모델 부하 시 더. 10장 정도가 한 배치로 안전. 그 이상은 `--only`로 나눠 호출.

## 3. 세션 만료(로그인 풀림) 대처 절차

증상이 보이면 사용자에게 다음 안내:

```bash
# 1. 원격 호스트에서 CRD(chrome-remote-desktop)가 켜져 있는지, 어느 디스플레이인지 확인
ssh <REMOTE> 'ps -ef | grep chrome-remote-desktop-host | grep -oP ":\d+" | head -1'

# 2. 그 디스플레이로 직접 로그인 창 띄우기 (보통 :22)
ssh <REMOTE> '~/image-gen/.venv/bin/python ~/image-gen/chatgpt_image.py login --display :22'
```

(`<REMOTE>` 는 `IMAGE_GEN_REMOTE` env 에 설정한 SSH alias. 미설정이면 로컬 모드라 ssh 자체 생략)

사용자는 **CRD 화면(이미 보고 있는 그 화면)** 에 새로 뜬 Chromium에서 ChatGPT 로그인 → SSH 세션으로 돌아가 Ctrl-C → 세션 저장 완료.

> ⚠️ `bash run.sh login`(인자 없음)은 새 Xvfb + x11vnc 띄우는 경로라서 사용자에게 VNC 뷰어 설치/SSH 터널을 강요. CRD가 있으면 무조건 `--display :22` 경로 사용.

CRD 자체가 검게 변하거나 오프라인이면 (zombie xfconfd가 새 xfce4 세션의 singleton check를 막는 게 원인):

```bash
ssh <REMOTE> 'pkill -9 -u agent -f xfconfd; pkill -9 -u agent -f xfce4'
ssh <REMOTE> '/opt/google/chrome-remote-desktop/chrome-remote-desktop --stop'   # sudo 필요
ssh <REMOTE> '/opt/google/chrome-remote-desktop/chrome-remote-desktop --start'
```

> ⚠️ `pkill -f /opt/google/chrome` 은 chromium·chrome-remote-desktop 둘 다 잡아버림. chromium 만 죽이려면 `/opt/google/chrome/chrome` (basename 매칭) 으로 좁혀서 사용.

## 4. 슬라이드 통합 워크플로 (5단계 루프 상세)

1. `slides.md` (Marp) 작성/수정
2. 이미지로 보여줬을 때 더 효과적인 슬라이드 식별 → **"왜 이게 텍스트보다 이미지여야 하는지"** 한 줄로 적어두기 (나중에 검증용)
3. `IMAGE_PROMPTS.md` 에 추가 (포맷: `` ### `filename.png` — 캡션 `` + `- **Prompt**:` + 코드 펜스)
4. §1의 명령어로 생성 → `assets/` 에 저장
5. `slides.md` 에 `![bg right](assets/filename.png)` 또는 일반 `![w:N](assets/filename.png)` 삽입
6. Marp 렌더 → PDF/PNG 캡처 → 사이즈/위치 확인 (또는 `auto_size.py` 자동 조정)
7. 어색하면 **프롬프트의 aspect ratio·구도·여백을 수정 후 4번부터 재실행** (Marp 쪽 CSS 조정보다 프롬프트 수정이 더 유연한 경우 많음)

### 프롬프트 작성 팁

- Marp 슬라이드는 16:9. 배경 이미지로 쓸 거면 프롬프트에 `16:9 wide aspect ratio` 명시
- 좌/우 절반(`![bg right]`)에 들어갈 거면 `1:1 square` 또는 `9:16 portrait` 명시
- **텍스트·라벨은 디폴트로 다 넣음** — 한글·영문·숫자 모두 GPT-4o image gen 이 거의 정확히 그림 (오타 거의 X). 의미 전달에 필요한 라벨은 프롬프트에 `labeled exactly "라벨문구" in Korean/English` 식으로 명시. 끝에 `Render every label letter exactly as written, no typos, no missing characters` 추가하면 더 안정적
- **다만 가끔 깨지는 글자가 있을 수 있음** — 그래서 단계 6 시각 자동 검수 (Claude Code 가 PNG 직접 봄) 가 필수. 발견 시 단계 7 로 자동 재생성 또는 영문/숫자/제거 fallback
- 텍스트 위에 얹을 배경 이미지(decorative bg)로 쓸 거면 그 한정해서 `dark muted background, low contrast, no text or labels` 추가 → 가독성 보장. 일반 인포그래픽엔 이 옵션 X
- 발표 톤 일관성을 위해 **모든 프롬프트에 같은 스타일 키워드** 반복 (예: `clean modern editorial illustration, navy and warm beige palette`)

## 5. 디버깅 빠른 시작

`generate` 가 실패하면 출력 폴더에 `<stem>.fail.png` 디버그 스크린샷이 남음. 먼저 이걸 확인:

```bash
# Windows 측에서 (동기화 폴더면 그대로 보임)
explorer "<프로젝트 폴더>/assets/"
# 또는 직접 SCP
scp <REMOTE>:/tmp/img_out/<stem>.fail.png /tmp/
```

흔한 원인:

| 스크린샷에 보이는 것 | 원인 | 대처 |
|---|---|---|
| 로그인 화면 | 세션 만료 | §3 수동 로그인 절차 |
| Cloudflare 챌린지 | Chromium 자동화 탐지 | `run.sh logout` 후 재로그인 |
| "오늘 한도 도달" | 무료/플러스 일일 제한 | 다음 날 재시도 또는 플랜 업그레이드 |
| 정상 채팅 화면, 이미지만 없음 | 이미지 셀렉터 mismatch | `chatgpt_image.py:wait_for_image()` selector 점검 |
| AI가 일부 글자 깨뜨림 (한글·영문 모두 가끔) | 프롬프트 한계 (전체적으론 잘 그림) | 단계 6 검수에서 발견 → 단계 7 자동 재생성 1~2회. 끝까지 안 잡히면 그 라벨만 영문/숫자/제거로 프롬프트 fallback |

스크린샷이 정상인데도 실패하면 stdout 마지막 `URL:` 라인을 같이 확인.

## 6. 짧은 체크리스트 (호출 직전)

- [ ] CRD/원격 디스플레이 켜져 있고 화면 정상으로 보임
- [ ] `~/.cache/chatgpt-image-profile/` 있음 (없거나 비었으면 §3 로그인부터)
- [ ] `IMAGE_PROMPTS.md` 포맷 검증: `bash run.sh list <prompts.md>` 로 파싱 결과 확인
- [ ] `--output-dir` 동기화 폴더 경로로 지정 (Windows·Mac 양방향 동기화)
- [ ] 같은 프로필 쓰는 다른 스킬(`ask-chatgpt-linux` 등) 동시 실행 안 함
- [ ] 한 배치 10장 이하

## 7. 안 풀리면 — 그냥 스킵

§1 워크플로우는 전부 선택사항. ChatGPT 쪽이 막히면 더 시간 쓰지 말고:
- 그 시점까지 만들어진 텍스트 슬라이드로 빌드해 제출
- 이미지가 정 필요하면 사용자가 ChatGPT 웹에서 수동으로 받아서 `assets/` 에 넣고 `auto_size.py` 만 실행

전체 분기 가이드는 [README.md#언제-건너뛰어도-되나](README.md#언제-건너뛰어도-되나) 참고.
