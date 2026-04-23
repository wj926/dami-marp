---
marp: true
theme: dami-lab
paginate: true
math: katex
footer: '동국대학교 컴퓨터·AI학과 DAMI Lab'
style: |
  /* 우측 빨간 강조 callout */
  .callout-r {
    background: #FFF0F0;
    border: 2px solid #C93C3C;
    border-radius: 6px;
    padding: 10px 14px;
    color: #8A1F1F;
    font-size: 0.9em;
    line-height: 1.45;
  }
  .callout-r b { color: #C93C3C; }
  /* 일반 회색 정보 박스 */
  .cat {
    background: #F8F9FB;
    border: 1px solid #D8DDE5;
    border-radius: 6px;
    padding: 8px 12px;
    margin: 6px 0;
    font-size: 0.9em;
    line-height: 1.5;
  }
  .cat .tag {
    display: inline-block;
    background: #1F3864;
    color: white;
    font-size: 0.82em;
    padding: 2px 8px;
    border-radius: 10px;
    margin-right: 8px;
    font-weight: 600;
  }
  .cat .tag.red { background: #C93C3C; }
  .cat .tag.green { background: #2E7D4F; }
  /* 2열 그리드 (진짜 비교용) */
  .two {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    margin-top: 4px;
  }
  .two h3 {
    margin: 0 0 6px 0;
    padding: 4px 10px;
    background: #1F3864;
    color: white;
    font-size: 0.92em;
    border-radius: 4px;
    display: inline-block;
  }
  .two.red h3 { background: #C93C3C; }
  .two h3.alt { background: #2E7D4F; }
  /* 사람 카드 */
  .person {
    background: white;
    border: 1px solid #1F3864;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 8px;
    font-size: 0.9em;
    line-height: 1.5;
  }
  .person .name {
    color: #1F3864;
    font-weight: 700;
    font-size: 1.05em;
    margin-right: 8px;
  }
  .person .role {
    display: inline-block;
    background: #E8EDF5;
    color: #1F3864;
    font-size: 0.8em;
    padding: 2px 8px;
    border-radius: 10px;
    font-weight: 600;
  }
  .person ul { margin: 6px 0 0 0; padding-left: 18px; }
  .person ul li { margin: 2px 0; }
  /* 타임라인 행 */
  .tl {
    display: grid;
    grid-template-columns: 120px 1fr;
    gap: 10px;
    align-items: start;
    border-bottom: 1px solid #E0E4EB;
    padding: 8px 0;
  }
  .tl:last-child { border-bottom: none; }
  .tl .when {
    background: #1F3864;
    color: white;
    font-size: 0.85em;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 4px;
    text-align: center;
  }
  .tl .when.now { background: #C93C3C; }
  .tl .when.soon { background: #E07B00; }
  .tl .when.mid { background: #2E7D4F; }
  .tl .when.ongoing { background: #555; }
  .tl .what { font-size: 0.92em; line-height: 1.5; }
  /* flow-row: 가로 단계 박스 */
  .flow-row {
    display: grid;
    grid-auto-flow: column;
    grid-auto-columns: 1fr;
    gap: 10px;
    margin: 10px 0;
  }
  .flow-box {
    background: #F4F6FA;
    border: 1px solid #1F3864;
    border-radius: 6px;
    padding: 10px 12px;
    font-size: 0.88em;
    line-height: 1.45;
    position: relative;
  }
  .flow-box b { color: #1F3864; }
---

<!-- _class: title -->
<!-- _paginate: false -->

# AX 전환<br>앞으로의 방향

<div class="author">DAMI Lab<br>AX 전환 점검 세미나</div>
<div class="date">2026.04.23</div>

---

<!-- _class: toc -->

# Contents

1. 설문이 말해준 것 — 왜 이 방향인가
2. 우리만의 원칙과 폴더 구조
3. 소통/정보 공간 시스템화
4. 정기 세미나 — 스킬 공유 문화
5. 팀/개인별 역할 배분
6. 홈페이지 2분화 구상

---

<!-- _class: section -->

# 1. 설문이 말해준 것<br>— 왜 이 방향인가

---

# 설문에서 읽어낸 공통 니즈

## 핵심 명제

- 개개인이 필요한 **스킬이 많이 겹친다** — 같이 만들어 쓰는 편이 효율적
- **하네스 세팅이 어렵다** 는 토로가 다수 → 별도 공부/가이드 필요
- 슬랙/홈페이지에 스킬이 **너무 많이 쌓여** 뭘 써야 할지 모르겠다는 의견
- 정보 공간은 노션보다 **웹페이지** 로의 전환을 선호

| 니즈 | 응답 경향 | 시사점 |
|---|---|---|
| 스킬 중복 | 여러 명 | 공통 개발 여력 있음 |
| 하네스 난이도 | 다수 | 학습 자료·세미나 필요 |
| 정보 범람 | 다수 | 큐레이션·노출 구조 재설계 |
| 웹 전환 | 선호 | 노션 의존도 축소 |

<div class="callout-r">

**이 덱의 방향성**: 설문의 네 가지 니즈를 각각 **구조(§2) · 공간(§3) · 문화(§4) · 역할(§5) · 채널(§6)** 로 나누어 액션으로 연결한다.

</div>

---

<!-- _class: section -->

# 2. 우리만의 원칙과<br>폴더 구조

---

# 지금 구조의 문제와 앞으로 필요한 것

## 상황

- 메인 `CLAUDE.md` 위에 **개인 `CLAUDE.md` · 서브 스킬 · 개인 스킬** 이 계속 덧붙는 중
- 지금은 굴러가지만, 사람/프로젝트가 늘면 **관리 불가능한 상태** 로 감
- 각자 로컬 룰을 따로 두다 보니 **합의된 원칙이 없음**

<div class="two red">
<div>

### 지금

- 메인에 `CLAUDE.md` 하나
- 그 밑에 중간중간 **개인 `CLAUDE.md`**
- **서브 스킬 + 개인 스킬** 이 섞여 있음
- 계속 이 상태면 **관리 비용 폭증**

</div>
<div>

### 앞으로

- 연구를 잘 할 수 있는 **폴더 구조**
- 연구실 공통의 **원칙/가이드**
- 개인 영역과 공통 영역의 **경계 합의**
- **진행형 과제** — 오늘 결론 아님

</div>
</div>

<div class="callout-r">

**중요**: 이번 세미나에서 결론을 내는 항목이 아니라, **계속 고민하고 조율해 나갈 과제**. 오늘은 「이걸 과제로 올려둔다」 는 합의까지만.

</div>

---

<!-- _class: section -->

# 3. 소통/정보 공간<br>시스템화

---

# 가장 빠르게 해야 할 일

## 문제 인식

- 자유로운 소통과 쉬운 정보 접근이 있어야 **연구실 전체가 함께 성장**함
- 지금은 **슬랙에 쌓이기만** 해서 잘 안 보이고, **노션은 정리 시간이 너무 길음**
- 김민석 학생 혼자 끌기에는 부담이 크다

## 방향 — 홈페이지 개선

- **초기 구조 세팅 팀 3명** 이 먼저 「사람들이 잘 쓸 수 있는 구조」 를 만든다
- 이후 다른 학생들은 본인 스킬을 **자유롭게 공유/설명** 하는 문화로 합류

<div class="two">
<div>

### 초기 구조 세팅 팀

<div class="person">
<span class="name">교수님</span><span class="role">방향성</span>
</div>

<div class="person">
<span class="name">이윤석</span><span class="role">시스템</span>

- 컴퓨터공학 전공 — 시스템 이해 있음

</div>

<div class="person">
<span class="name">김민석</span><span class="role">AX 주도</span>

- AX 전환을 가장 앞에서 끌고 있음

</div>

</div>
<div>

### 나머지 학생들

- 본인이 만든 스킬을 **자유롭게 공유/설명**
- **강요 아닌 자발적 공유** 가 핵심
- 옆 사람 파이프라인을 보고 내 것에 응용
- 공유 부담을 낮추는 템플릿 필요

<div class="callout-r">

**원칙**: 초기엔 3명이 구조를 세우고, 이후 모두가 **채워 넣는** 방식으로 확장.

</div>

</div>
</div>

---

<!-- _class: section -->

# 4. 정기 세미나<br>— 스킬 공유 문화

---

# 매주 스킬 공유 루틴

## 포맷

- **주기**: 매주 정기 (목요일 오전 워크샵 자리 활용 검토)
- **형식**: 한 주 동안 쓰면서 좋았던/안 좋았던 스킬을 짧게 공유
- **기대 효과**: 옆 동료 파이프라인을 보며 내 것에 응용하는 **브레인스토밍 문화**

<div class="flow-row">
<div class="flow-box">

**① 주간 회고**
내가 만든 스킬,
누가 만든 스킬 써봤는데…

</div>
<div class="flow-box">

**② 공유**
써보니 이렇더라,
이 부분이 안 좋아서 이렇게 바꿨다

</div>
<div class="flow-box">

**③ 응용**
옆 사람 워크플로우를 보고
내 것에 녹이기

</div>
</div>

<div class="cat">
<span class="tag">공유 내용 예시</span> 내가 만들어 본 스킬 / 써보니 이렇더라 / 이 부분이 안 좋아서 이렇게 바꿨다 / 바꿔서 쓰고 있다 / 아니면 안 쓰고 있다
</div>

<div class="callout-r">

**설문 근거**: Q12 에서 「다른 사람의 활용 사례를 보고 싶다」 는 의견이 **다수**. 공유 루틴은 이 니즈에 대한 **직접적 응답**.

</div>

---

<!-- _class: section -->

# 5. 팀/개인별<br>역할 배분

---

# 정승현 / 김민석

## 배치

- **개인 연구** 와 **AX 공통 기여** 를 함께 가져가는 그룹
- FAVOR TDI 논문 리비전이 공동 작업 축

<div class="two">
<div>

### 정승현

<div class="person">
<span class="name">AX 기여</span><span class="role">완료</span>

- **보고서 자동 완성** 구축 완료

</div>

<div class="person">
<span class="name">현재</span>

- 새 연구 주제 구상 중
- FAVOR TDI 논문 리비전 (김민석 공동)

</div>

<div class="callout-r">

**AX 관점 역할**: 리비전을 하면서 **논문 작성 관련 시스템** 에 대한 이야기를 자연스럽게 꺼내 보기.

</div>

</div>
<div>

### 김민석

<div class="person">
<span class="name">AX 역할</span><span class="role">시스템팀</span>

- 시스템 구상 팀 합류
- 홈페이지 관리
- 스킬을 **GitHub 에 어떻게 공유할지** 고민

</div>

<div class="person">
<span class="name">현재 연구</span>

- FAVOR TDI 논문 리비전 (정승현 공동)
- 빅데이터 팀 초반 실험

</div>

</div>
</div>

---

# CUA 팀 — 이윤석 / 김윤지

## 배치

- 지금 **가장 활발히 연구가 돌고 있는** 팀
- 이미 **md 파일 기반 소통** 을 실험 중 → 홈페이지 전환의 **선행 사례** 로 활용

<div class="two">
<div>

### 이윤석

<div class="person">
<span class="name">집중</span><span class="role">research.damilab 리드</span>

- 컴퓨터공학 → 시스템/홈페이지 공동 작업
- **학생들이 노션을 벗어나 홈페이지에서 연구를 공유하는 시스템** 구상
- 활발한 아이디어 제시 기대

</div>

</div>
<div>

### 김윤지

<div class="person">
<span class="name">일정</span><span class="role">ICML 워크숍</span>

- **~5월 8일** 제출 예정 (간단한 것 하나 더 예약)

</div>

<div class="person">
<span class="name">AX 집중 포인트</span>

- 논문 구조를 잡을 때 **AI 를 라이팅에 어떻게 활용할지**
- 라이팅 관련 스킬은 **로봇팀** 이 만들 가능성 ↑
- 그 스킬을 본인 워크플로우에 **녹이는 쪽**

</div>

</div>
</div>

<div class="callout-r">

**팀 공통**: md 기반 소통을 **더 잘할 수 있는 방법** 을 계속 실험하기. 성과는 홈페이지 시스템에 피드백.

</div>

---

# 로봇팀 / 브라질 학회 팀

## 배치

- 두 팀 모두 **당장은 다른 톤** 으로 참여
- 로봇팀: 외부 협업 특수성 반영
- 학회 팀: 5월 초 학회 후 합류

<div class="two">
<div>

### 로봇팀 (2명)

<div class="person">
<span class="name">상황</span>

- 클로드 코드를 적극적으로 쓰고 있는지 **아직 불확실** → 더 공부 필요
- 외부 교수님과 협업 → **PPT 중심** 커뮤니케이션

</div>

<div class="person">
<span class="name">집중 포인트</span>

- 실제로 많이 쓰는 **PPT 작성 스킬** 개선
- 외부 협업 특성에 맞는 **자기들만의 스킬** 개발

</div>

<div class="callout-r">

우리 내부의 HTML/웹 시스템으로 **바로 전환하기 어려움**. 무리하지 않기.

</div>

</div>
<div>

### 브라질 학회 팀 (2명)

<div class="person">
<span class="name">상황</span><span class="role">5월 초 학회</span>

- 학회 준비에 집중

</div>

<div class="person">
<span class="name">방침</span>

- 당장은 AX 전환에 **적극 참여시키지 않음**
- 학회 후 서로 **도와주는 형태로 합류**

</div>

</div>
</div>

---

<!-- _class: section -->

# 6. 홈페이지 구조<br>— 2분화

---

# share vs research — 개요

## 전략

- **2개 홈페이지** 로 분리해서 시작 — 성격이 다르면 공간도 다르게
- 나중에 합쳐야 할 이유가 생기면 합친다, 일단은 분리
- **외부 노출 가능성** 이 분리 기준

<div class="two">
<div>

### share.damilab

- **정보 공유용** — 외부 개방 가능 영역
- 스킬 공유 + 외부 자료 큐레이션
- 글 작성은 **간단 로그인** 필요

</div>
<div>

### research.damilab

- **연구용** — 내부 정보 → **로그인 필수**
- 노션 대신 **md 기반 연구 공유**
- **이윤석 리드**, 다른 학생 합류

</div>
</div>

<div class="callout-r">

**원칙**: 공개 가능한 것(share) 과 **내부에서만 봐야 할 것(research)** 의 경계를 먼저 긋는다. 합치는 건 언제든 가능하지만, 섞여 있으면 되돌리기 어렵다.

</div>

---

# research.damilab — 상세

## 핵심

- 내부 정보가 들어가므로 **외부 노출 방지** 가 1순위
- 노션을 대체하는 **md 기반 연구 공유** 공간
- 지금 가장 활발한 **CUA 팀** 이 먼저 쓰면서 다듬는다

| 항목 | 내용 |
|---|---|
| **접근** | 로그인 필수 (외부 차단) |
| **개발 주도** | 이윤석 — 컴공 기반, 시스템 이해 |
| **공동 발전** | 다른 학생들도 함께 발전시킴 |
| **핵심 사용자** | 이윤석, 김윤지 (가장 활발한 연구 진행) |
| **핵심 기능** | 노션 대신 md 기반 연구 공유/소통 |

<div class="callout-r">

**단기 목표**: CUA 팀이 이미 하고 있는 **md 소통** 을 research.damilab 위에서 먼저 돌려보고, 다른 팀에 확산.

</div>

---

# share.damilab — 상세

## 두 축

- **스킬 공유** — 「내가 만든 것」 과 「남이 만든 좋은 것」 을 **성격상 분리**
- **외부 자료 큐레이션** — 슬랙에 쌓여서 안 보이는 것들을 여기로
- **간단한 로그인** — 누가 작성했는지만 식별하면 충분

<div class="two">
<div>

### 스킬 공유

- **내가 만든 스킬** vs **남이 만든 좋은 스킬** 구분
- 스킬마다 사람이 직접 적어줄 내용
  - **왜 만들었는지**
  - **어떻게 쓰는지**
- 발전 논의는 **매주 목요일 오전 워크샵** 에서

</div>
<div>

### 외부 자료 큐레이션

- 남이 만든 좋은 스킬, GitHub 좋은 글, 슬랙의 유용한 공유
- 지금은 슬랙에 너무 쌓여서 **안 보임**
- 홈페이지로 옮겨 **깔끔하게 노출**
- 품 많이 들면 당장은 X → **간단한 버전부터**

</div>
</div>

<div class="callout-r">

**로그인**: 글 작성 시 **누가 올렸는지** 만 식별하면 됨. 여기는 **가벼운 수준** 으로 시작.

</div>

---

# 종합 — 우선순위 타임라인

## 지금부터 진행형까지

- **지금 당장** 움직이는 것, **이번 주 / 이 달** 에 시도하는 것, **계속 안고 가는 과제** 를 분리
- 누구 하나에게 몰지 않고 **3인 세팅팀 + 팀별 분산** 으로

<div class="tl">
<div class="when now">NOW</div>
<div class="what">

**3인 초기 팀 가동** — 교수님 + 이윤석 + 김민석. 사람들이 쓸 수 있는 기본 구조 설계부터.

</div>
</div>

<div class="tl">
<div class="when soon">이번 주</div>
<div class="what">

**매주 스킬 공유 세미나** 시간 확보 (목요일 오전 워크샵). 공유 템플릿 초안 — 「왜 만들었는지 / 어떻게 쓰는지」.

</div>
</div>

<div class="tl">
<div class="when mid">이 달</div>
<div class="what">

**share / research 2개 홈페이지** 최소 버전 기동. CUA 팀이 research 에서 md 소통 시험. 로봇팀은 PPT 스킬에 집중.

</div>
</div>

<div class="tl">
<div class="when ongoing">진행형</div>
<div class="what">

**연구실 공통 폴더 구조/원칙** 지속 조율. 브라질 학회 팀은 5월 초 학회 후 합류.

</div>
</div>

---

<!-- _class: end -->

# Thank you
