# Marp 스킬 삽질/포렌식 기록

DAMI Lab Marp 양식을 만들면서 실제로 겪은 버그와 그 원인 분석. `SKILL.md` 본문에는 규칙만 한두 줄로 두고, 재현 맥락과 원인 추적은 여기에 남긴다.

동일 이슈가 재발했을 때 "이게 그때 그거였나?" 를 확인하거나, 규칙을 완화/변경해도 되는지 판단하는 용도.

---

<a id="background-important"></a>
## `background` 가 렌더에 안 보일 때 — `!important` 필수

- **증상**: `section { background: ... }` 또는 `border-left`, `box-shadow`를 써도 PDF 렌더에 아무것도 안 나옴. DevTools에서 CSS는 정상으로 보이는데 화면만 비어 있음.
- **원인**: Marp `default` 테마가 내부적으로 `section { background-color: var(--bgColor-default) }` 를 꽤 높은 specificity(`div#:$p > svg > foreignObject > section`)로 걸어 놓음. 사용자 `style:` 블록이 뒤에 오더라도 cascade로 이기지 못할 때가 있음.
- **해결**: 사용자 section 배경엔 **`!important` 를 반드시 붙인다**. 예:
  ```css
  section          { background: #ffffff !important; }
  section.title    { background: #0b2c5a !important; }
  section.section  { background: #0b2c5a !important; }
  ```
- **주의**: base section에 `!important` 를 쓰면 `.title`/`.section` 등 하위 클래스도 똑같이 `!important` 로 덮어써야 함. 안 그러면 전부 기본 배경이 적용돼 버림.
- **삽질 기록**: `border-left: 10px solid`, `box-shadow: inset`, `div.leftbar`를 DOM에 주입하는 방식 모두 실패했음. 결국 `!important`가 범인이었음.

---

<a id="before-after-재활용"></a>
## `::before` 를 재활용할 때 base 속성 전부 덮어쓰기 — `.section` 네이비 바 함정

- **증상**: `.section` 슬라이드의 상단 네이비 바가 **왼쪽 56px 좁은 막대**로만 나오고, 흰 제목이 안 보인다 (흰 배경 위 흰 글씨).
- **원인**: base `section::before` 가 로고용으로 `width: 56px; height: 46px; background: url(./assets/dami_logo.png) ...; top: 20px; right: 40px` 를 걸어두고 있음. `.section::before` 에서 `top/left/right/height/background` 만 덮으면 **`width: 56px` 가 cascade로 살아남아** 왼쪽 56px 폭 바만 그려진다. h1은 나머지 흰 영역에 걸쳐서 흰 글씨가 묻힌다.
- **해결**: `.section::before` 에 **base의 모든 관련 속성을 명시적으로 리셋**한다.
  ```css
  section.section::before {
    display: block !important;
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    width: auto;              /* base의 width:56px 를 덮음 (left:0+right:0 가 작동하도록) */
    height: 63%;
    background: #0b2c5a;
    background-image: none;   /* base의 url(dami_logo.png) 제거 */
    z-index: 1;
  }
  ```
- **일반 규칙**: base에서 설정된 `::before` / `::after` 를 하위 클래스가 재활용할 때는 **가로(width), 세로(height), 위치(top/right/bottom/left), 배경(background + background-image)** 를 전부 다시 선언한다. shorthand `background: <color>` 는 `background-image` 까지 `initial` 로 되돌리는 것처럼 보여도, 확실하게 `background-image: none` 도 함께 써 주는 편이 안전.

---

<a id="linear-gradient-금지"></a>
## `linear-gradient` 는 쓰지 않는다 — 단색만

- **증상**: `linear-gradient(to right, #0b2c5a 0, #0b2c5a 10px, #fff 10px)` 로 왼쪽 네이비 세로 바를 그렸더니, pdftoppm 렌더(`k-*.png`)와 사용자 PDF 뷰어 캡쳐가 서로 다르게 보임. PDF 뷰어에 따라 경계가 블러/앤티에일리어스 처리되거나 아예 안 보임.
- **원인**: PDF 렌더링 엔진(poppler vs Chromium PDF vs Adobe 등)이 `linear-gradient` 의 hard stop을 각자 다르게 해석. 특히 1px~10px 얇은 구간의 서브픽셀 rounding이 엔진마다 달라짐.
- **해결**: 배경은 **단색만 사용**. 네이비 구간이 필요하면 `.title`/`.section` 같은 전체 네이비 단색 클래스를 만들어서 써라.
- **하지 말 것**:
  - `background: linear-gradient(...)` (렌더 엔진 차이로 출력이 불안정)
  - 얇은 좌측 네이비 바를 `linear-gradient` 로 그리는 트릭 (뷰어마다 경계가 블러됨)
- **대안**: 강조가 필요한 영역은 h1/블록 단위 `border-left` 로 처리 (이미 h1에 6px navy border-left 적용 중).

---

<a id="h1-상단-정렬"></a>
## 모든 본문 슬라이드의 h1 시작 위치를 일치시킨다 — `justify-content: flex-start` 필수

- **증상**: 같은 일반 본문 슬라이드인데도 슬라이드마다 h1 제목이 시작되는 세로 위치(y좌표)가 제각각. 콘텐츠가 짧은 장은 h1이 아래로 밀리고, 콘텐츠가 많은 장은 h1이 상단에 붙는다.
- **원인**: Marp `default` 테마의 base CSS 가 `section { display: flex; flex-direction: column; justify-content: center }` 로 세로 중앙 정렬을 걸어둠. 콘텐츠 총 높이가 작으면 flex가 전체 박스 중앙으로 수렴 → h1이 `padding-top` 값을 무시하고 아래로 밀려 보임.
- **해결**: base `section` 규칙에 **`display: flex !important; flex-direction: column; justify-content: flex-start !important; place-content: flex-start !important;`** 를 모두 추가. `justify-content` 만으로는 부족하다 (아래 주의사항 참고).
- **`justify-content` 만으로 부족한 이유** (2026-04 추적 기록): Marp default 의 실제 section CSS 를 `--format html` 로 dump 해보면 `display: block; place-content: safe center center; padding: 78.5px` 로 되어 있다. `place-content` 는 `align-content` + `justify-content` shorthand 인데, 최신 CSS 스펙에서 **block 컨테이너에도 `align-content` 가 적용**되어 콘텐츠가 세로 중앙으로 모인다. 이 상태에서 `justify-content: flex-start` 만 걸면 block 에서 무효이고 `place-content: center` 가 그대로 이긴다. 따라서 `display: flex !important` 로 명시하고 `place-content: flex-start !important` 도 함께 걸어야 확실히 상단 정렬된다.
- **padding-top 은 `30px` 로 고정**: 현재 `padding: 30px 56px 56px 68px !important`. 이유는 **h1 의 border-bottom(긴 네이비 바)이 우상단 코끼리 로고(y=20~66) 바로 아래에 오도록** 튜닝한 값. h1 박스 높이 약 43px 이므로 30+43=73 에서 border 가 위치해 로고 하단과 7~10px 여유. 값을 키우면 (예전 48px 등) 콘텐츠 양에 따라 flex 정렬이 흔들려 슬라이드마다 제목 Y좌표가 시각적으로 어긋남. 키우지도 0 에 가깝게 내리지도 말 것 (로고랑 붙거나 겹침).
- **왜 `!important` 인가**: default 테마의 `section` selector 와 specificity 가 동일해서 cascade 순서에 따라 밀릴 수 있음. `background` 와 동일한 사유.
- **`.end` 슬라이드 예외**: `.title`, `.section`은 `position: absolute` 로 h1을 배치하므로 base의 `flex-start`에 영향받지 않는다. 하지만 `.end`는 **flex 중앙정렬을 그대로 쓰므로** `justify-content: center !important` 를 **반드시 함께 붙여야** 한다. 안 그러면 base의 `flex-start !important` 에 덮여서 Thank you 제목이 위쪽으로 올라간다 (실제 발생한 버그). `.end`에는 `display: flex !important`, `padding: 48px 56px !important` 도 함께 고정해야 안정적.
- **체크 방법**: 빌드 후 본문 슬라이드 2~3장을 모아 보고 h1 상단 라인이 시각적으로 **같은 y좌표**에 있는지 확인. 어긋나면 base `section` 에서 `justify-content` 가 빠졌을 가능성이 크다.

---

<a id="쌍따옴표-금지"></a>
## 본문에 쌍따옴표·작은따옴표를 쓰지 않는다 — CommonMark emphasis flanking

- **증상**: 슬라이드에 `**"텍스트"**` 또는 `**"텍스트"**조사` 가 그대로 `**"텍스트"**` 로 렌더됨 (별표/따옴표가 기호 그대로 노출).
- **원인**: CommonMark 의 emphasis *flanking* 규칙. `**` 옆에 punctuation(`"`, `'`)이 오고 반대편에 한글(word char)이 오면 left/right-flanking 판정이 깨져서 `**` 가 열림/닫힘으로 인식되지 않음. 특히 `**"…"**조사` 패턴(닫는 `**` 앞이 `"`, 뒤가 한글)에서 거의 항상 실패.
- **규칙**: 본문에서 **쌍따옴표·작은따옴표를 아예 쓰지 않는다**. 강조가 필요하면 `**bold**` 하나로만 해결한다. CSS·HTML 속성(`class="..."`, `url('...')`, `style="..."`) 안의 따옴표는 문법이므로 예외.
- **해결 패턴** (따옴표 제거 + bold 유지):
  ```
  BAD : **"어디서 믿고, 어디서 의심할지"**를 가르친다
  GOOD: **어디서 믿고, 어디서 의심할지**를 가르친다
  ```
  ```
  BAD : 단순 "챗봇 써보기"가 아니라 **업무 재설계** 단계
  GOOD: 단순 챗봇 써보기가 아니라 **업무 재설계** 단계
  ```
  ```
  BAD : 왜 '지금' 시작해야 하는가
  GOOD: 왜 지금 시작해야 하는가
  ```
- **인용·예시처럼 꼭 따옴표 느낌이 필요할 때**: `예: …` 접두어나 blockquote(`>`)로 대체한다. 한글 인용부호 `「…」`, `『…』` 도 OK (flanking 영향 없음).

---

<a id="mermaid-label-clip"></a>
## Mermaid flowchart 라벨 마지막 글자 클리핑

- **증상**: `flowchart` 박스 라벨의 마지막 글자가 1~2 픽셀 잘려 보임 (예: `built` → `buil`, `slides.md` → `slides.mc`, `mermaid 렌더` → `mermaid 렌`).
- **원인**: Mermaid 가 생성하는 SVG 의 `<text>` bbox 계산이 SVG-in-`<img>` 렌더 경로(Chromium 이 data URI 로 받은 SVG 를 렌더할 때) 에서 text advance width 와 mismatch. 특히 마침표 `.` 또는 특정 폰트 glyph 의 trailing advance 가 0 에 가까울 때 마지막 글자가 박스 padding 을 넘어 clip.
- **시도했지만 실패한 우회책**:
  - `flowchart.padding` 확대 → 박스는 커지지만 내부 text 위치 고정되어 여전히 clip
  - `htmlLabels: true` → PDF 렌더에서 `<foreignObject>` 도 같은 문제
  - trailing space / NBSP 추가 → mermaid 가 자동 strip
  - SVG root 에 `overflow="visible"` → clip 은 visual 이 아니라 text rendering 단계라 무효
- **실용 우회**:
  1. **라벨 끝에 긴 영문 + 마침표 조합 피하기** — `slides.md` 대신 `마크다운`, `built` 대신 `빌드 산출물`.
  2. **한글 또는 넓은 CJK 문자로 끝내기** — `slides.md` → `slides md 파일`.
  3. **정 영문이 필요하면 뒤에 여유 문자 추가** — `[marp CLI]` 처럼 의미 있는 단어 2개를 space 로 붙이면 safe.
- **후속 해결 방향** (미구현): SVG 를 data URI 대신 별도 `.svg` 파일로 저장 + `<img src="diagram.svg">` 로 참조. Chromium 이 file URL 로 받은 SVG 는 독립 rendering pipeline 을 써서 text bbox 계산이 정확할 가능성.

---

<a id="flow-box-structure"></a>
## `.flow-box` 는 `.header` + `.body` 구조 필수, 화살표는 CSS 자동 생성

- **증상**: `<div class="flow-box">` 안에 `<strong>제목</strong><br/>본문` 식으로 inline 작성했더니, 렌더 결과에서 박스 내부 제목 텍스트의 **윗부분이 1~2px 잘림** (예: "1. DFS 탐색" 의 숫자 "1" 상단이 박스 border 에 의해 clip). 화살표도 박스 사이에 정상 arrow + 중복된 `→` 문자가 동시에 표시됨.
- **원인 1 (clip)**: `dami-lab.css` 의 `.flow-box` 는 `display: flex; flex-direction: column` 에 `padding: 0` + `border: 1px solid` 만 걸려 있음. 내부 패딩은 `.header` / `.body` 자식 div 에서 책임짐. header/body 없이 raw text 를 넣으면 padding 이 0 이라 텍스트가 box border 에 딱 붙어 clip.
- **원인 2 (중복 화살표)**: `.flow-row > .flow-box:not(:first-child)::before` / `::after` 가 **자동으로 화살표 선 + 삼각형을 그려줌**. 사용자가 수동으로 `<div class="flow-arrow">→</div>` 를 추가하면 CSS arrow + `→` 글리프가 중복 렌더됨.
- **해결**: 공식 패턴 그대로 쓰기.
  ```html
  <div class="flow-row">

  <div class="flow-box">
  <div class="header">1. 제목</div>
  <div class="body">

  - 본문 항목

  </div>
  </div>

  <div class="flow-box">
  <div class="header">2. 제목</div>
  <div class="body">본문</div>
  </div>

  </div>
  ```
  - `<div class="flow-row">` 와 `<div class="flow-box">` 태그 전후에 **빈 줄** (마크다운이 내부 `-` 리스트를 렌더하도록).
  - **`<div class="flow-arrow">` 는 쓰지 않는다** — CSS 가 자동으로 넣음.
  - 짧은 한 줄 본문이면 `.body` 안에 그냥 텍스트만 써도 됨 (리스트 안 쓸 땐 빈 줄 생략 가능).
- **검증 방법**: 빌드 후 `pdftoppm` 으로 PNG 뽑아서 **박스 내부 텍스트 상단 여백** 확인. 네이비 헤더 바가 안 보이면 `.header` 누락 의심.
