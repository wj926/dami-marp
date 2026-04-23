---
marp: true
theme: dami-lab
paginate: true
math: katex
footer: '동국대학교 컴퓨터·AI학과 DAMI Lab'
---

<!-- _class: title -->
<!-- _paginate: false -->

# LLM Wiki 로드맵<br>연구 지식 QA 생태계

<div class="author">이우진<br>동국대학교 DAMI Lab</div>
<div class="date">2026.04.23</div>

---

<!-- _class: toc -->

# Contents

1. Why LLM Wiki
2. 핵심 개념
3. 두 가지 접점
4. 구체 사용 예시
5. share.damilab 과의 관계
6. 단계별 구축 로드맵
7. 세미나 전달 메시지

---

<!-- _class: section -->

# 1. Why LLM Wiki

---

# 한 줄 비전

## 프레임

- 매일 연구 기록을 **던지기만** 하면 되는 시스템
- LLM 이 자동으로 **정리·누적·교차참조**
- 결과적으로 **물어보면 답하는 연구실** 완성

> **매일 연구 기록을 던지면, LLM 이 자동으로 정리·누적·교차참조해서 `물어보면 답하는 연구실` 이 되는 시스템**

<div class="callout">

**핵심 프레임**: 사람이 정리하는 wiki 가 아니라, **사람이 던지고 LLM 이 정리하는 wiki**

</div>

---

# 왜 필요한가, 설문 1순위 고민

## 설문 결과

- Q2 응답 1번: **프로젝트 단위 전체 흐름 유지가 가장 어려움**
- 개별 태스크는 잘 되지만, 맥락 연결이 미숙
- 서로 다른 태스크를 **하나의 맥락으로 통합**하기 어려움

> 개별 작업에는 어려움 없이 활용 가능하나, 프로젝트 단위로 전체 흐름(이전에 무엇을 했고, 왜 했고, 다음에 무엇을 할지)을 유지하며 사용하는 게 아직 잘 안 됨

## 현재 연구 정보는 여기저기

- 논문 메모는 **각자 로컬**
- 아이디어는 **노션 / 메모장 / 대화**
- 실험 로그는 **wandb / 로컬 / md**
- 어제 뭘 했는지는 **본인도 기억 못 함**

---

# Compounding Artifact

## 개념

- **시간이 지날수록 가치가 쌓이는** 자산으로 연구 지식을 관리
- 오늘의 메모가 내일의 cross-link 가 됨
- 3개월 뒤 그때 그 가설 어디까지 갔지? 에 LLM 이 답할 수 있는 구조

## 기존 도구와의 차이

- 노션 / Obsidian: **사람이** 정리 → 안 쓰면 죽은 문서
- LLM Wiki: **LLM 이** 정리 → 사용자는 raw 로그만 던짐

<div class="callout">

**지식은 자산**. 쌓이지 않으면 연구실 바깥으로 새어 나감

</div>

---

<!-- _class: section -->

# 2. 핵심 개념

---

# Karpathy LLM Wiki + 프로젝트 단위

## 출발점

- **Karpathy 의 LLM Wiki gist** 3-layer architecture 를 연구실 운영에 맞게 응용
- 원본은 개인 지식 관리, 본 로드맵은 **연구 프로젝트 단위** 로 재설계

## 단위 설계

- **1 프로젝트 = 1 wiki**
- 프로젝트 종료 시점 = wiki 아카이브 (논문 제출 시점 등)
- 논문 간 횡단 아이디어는 **별도 global 공간**

<div class="callout">

**범위를 좁힌다**: 연구실 전체 하나의 wiki 가 아니라, **작성 중 논문 1편 = 1 wiki** 로 경계를 명확히

</div>

---

# Raw vs Derived 분리

## 구조

- `inbox/` = 사용자가 매일 쓰는 **raw 로그** (immutable)
- `LLM_wiki/` = LLM 이 유지하는 **파생 공간** (재생성 가능)

```
inbox/                          ← raw 로그 (immutable)
  └── YYYY-MM-DD.md

LLM_wiki/                       ← LLM 파생 공간 (재생성 가능)
  ├── INDEX.md                    (네비게이션)
  ├── papers/<slug>.md            (논문별 페이지)
  ├── ideas/<date>_<slug>.md      (아이디어)
  └── experiments/<date>_<slug>.md (실험)
```

<div class="callout">

**핵심 원칙**: `inbox/` 는 원본, `LLM_wiki/` 는 LLM 이 재생성 가능. **꼬이면 다시 만들 수 있음**

</div>

---

# Daily Log, 4 고정 섹션

## 포맷

- 뇌 흐름대로 자유 서술 OK
- 비어 있어도 OK (섹션 생략 가능)
- **고정된 4 섹션** 만 지킴 → ingest 스킬이 라우팅 가능

```markdown
## 논문
(오늘 읽은 / 참조한 논문 메모)

## 아이디어
(오늘 생긴 연구 아이디어 / 가설)

## 실험
(오늘 돌린 실험 / 결과)

## 기타
(일정, 회의 메모 등)
```

---

<!-- _class: section -->

# 3. 두 가지 접점

---

# Homepage vs QA 봇

## 개요

- 같은 wiki md 파일을 **두 가지 방식**으로 노출
- 별도 싱크 불필요, **한 저장소 두 접점**
- 본 로드맵의 핵심은 **QA 봇**, Homepage 는 후속 트랙

| 계층 | 목적 | 언제 쓰나 |
|---|---|---|
| **QA 봇** (핵심) | 질문 / 추론 / 연결 | 이 가설 어디까지 진행됐어? |
| **Homepage** (후속) | 둘러보기 / 시각화 / 검색 | 내가 지난달 뭐 했더라 |

<div class="callout">

**같은 wiki md 파일을 공유** → 데이터 싱크 비용 0

</div>

---

<!-- _class: section -->

# 4. 구체 사용 예시

---

# 예시 1. 매일 저녁 10분 ingest

## 흐름

- 사용자는 **raw 로그만** 작성
- 스킬이 **제안** 을 만들고, 사용자는 **승인** 만
- 승인된 것만 **git commit** + inbox archive

```
사용자: inbox/2026-04-23.md 에 하루 메모 적음
       "오늘치 ingest 해줘"

[wiki-ingest 스킬 자동 실행]
  1. 4 섹션 파싱
  2. 기존 wiki 컨텍스트 확인
  3. 변경 제안 생성 (신규 / 업데이트 / cross-link)
  4. 사용자에게 diff 보여줌

사용자: OK  (또는 이건 아이디어 말고 실험으로 분류해)

[반영]
  - 승인된 것만 파일 쓰기
  - git commit
  - inbox 파일을 daily archive 로 이동
```

---

# 예시 2. QA 봇 대화

## 상호작용

- Cross-link 따라 **관련 페이지 3개** 자동 수집
- **근거 파일 경로** 를 답변에 포함, 환각 방지

```
사용자: relevance-based unlearning 가설 어디까지 갔어?

[QA 봇]
  관련 wiki 페이지 찾기 (INDEX + cross-link 활용)
  → ideas/2026-04-12_relevance_hypothesis.md
  → experiments/2026-04-18_masking_test.md
  → papers/kim2025_klass.md

답변:
  가설은 4/12 에 제안됨. factual token 마스킹 실험으로 검증 시도 중.
  4/18 에 첫 실험 돌렸고 loss 0.42 → 0.38 관찰. 단 seed 1개라 추가 검증 필요.
  klass (Kim et al.) 논문과 구조 유사성을 발견해서 이론적 근거 보강됨.
  다음 할 일: seed 3개 추가 + non-factual 대조 실험
```

---

# 예시 3. 새 논문 연동

## 기존 스킬과의 시너지

- **paper-summary** 스킬이 먼저 summary/raw/abstract 생성
- Daily log 에 한 줄 적기만 하면 ingest 가 자동으로 cross-link
- 연결 **근거 한 줄** 자동 명시, 쓰레기 링크 방지

```
사용자: 새 논문 PDF 를 프로젝트 폴더에 drop
       paper-summary 스킬로 summary/raw/abstract 자동 생성

다음 daily log:
  ## 논문
  이 논문 (§ 3.2) 가 내 가설이랑 유사함...

[Ingest 시 자동으로]
  - papers/<slug>.md 에 우리 연구와의 연결 섹션 추가
  - 관련 ideas / experiments 페이지에 cross-link
  - 근거 한 줄 자동 명시: § 3.2 의 KL 공식과 매칭
```

---

# 예시 4. 주간 리뷰 / 미팅 준비

## 시나리오

- 미팅 직전 **2주치 진행 요약** 생성
- INDEX 의 **status 필드** 로 incomplete / proposed 필터링
- 블로커까지 한 번에 식별

```
사용자: 최근 2주 진행 상황 정리해줘

[QA 봇]
  - daily/ 최근 14개 훑기
  - INDEX 기반 status: incomplete 실험 목록
  - status: proposed 아이디어 중 우선순위

답변:
  지난 2주 아이디어 3개, 실험 5개 진행
  incomplete 상태: 2개 (seed 추가 필요)
  블로커: X 실험의 pretrained checkpoint 접근 문제...
```

---

<!-- _class: section -->

# 5. share.damilab 과의 관계

---

# 도구 vs 내용, 분리 원칙

## 왜 분리하는가

- **도구(스킬)** 는 연구실 전체 공유가 이득 (재사용성)
- **내용(wiki)** 은 프로젝트 비밀 포함 (비공개가 기본)
- 두 축을 섞으면 **공유 vs 비공개** 기준이 무너짐

| 구분 | share.damilab | LLM Wiki |
|---|---|---|
| **다루는 것** | 도구 (Tools) | 내용 (Content) |
| **예시** | `wiki-ingest` 스킬 자체 | 그 스킬로 만들어진 연구 기록 |
| **리드** | 김민석 | 교수님 (본인 프로젝트부터) |
| **가시성** | 스킬 = 공개 | 내용 = 프로젝트 멤버 한정 |

<div class="callout">

**연결 고리**: `wiki-ingest` 스킬은 share 생태계의 일원. 다른 연구원이 **포크·개선** 할 수 있음

</div>

---

<!-- _class: section -->

# 6. 단계별 구축 로드맵

---

# Phase 전체 개관

## 4 단계 구상

- 각 phase 는 **선행 단계의 경험** 위에 쌓임
- **도구 먼저가 아닌, 워크플로우 먼저** 가 설계 철학
- 확산은 마지막 phase, 먼저 쓴 사람의 경험이 기반

| Phase | 이름 | 목표 | 주체 |
|---|---|---|---|
| 🟢 **0** | 수동 실험기 | 워크플로우 체감 | 교수님 1인 |
| 🔵 **1** | Ingest 스킬 MVP | 제안-승인 루프 자동화 | 교수님 + 개발자 |
| 🟣 **2** | QA 봇 통합 | cross-link 기반 답변 | 교수님 + 개발자 |
| 🟡 **3** | 확장 + 확산 | 연구원 전체 | 연구실 전체 |

---

# 🟢 Phase 0. 수동 실험기

## 할 일

- 교수님이 **본인 진행 중 프로젝트 1개** 선택
- `inbox/` + `LLM_wiki/` 폴더 **수동 생성**
- 며칠간 daily log 수기 작성 + 수기 wiki 정리
- **뭐가 귀찮고 반복적인지** 파악

## 목표

- 도구를 만들기 전, **사람이 하면 얼마나 아픈지** 체감
- Phase 1 스킬의 **자동화 우선순위** 가 여기서 도출됨

<div class="callout">

**핵심**: 도구부터 만들지 않음. **워크플로우를 먼저 살아봄**

</div>

---

# 🔵 Phase 1. Ingest 스킬 MVP

## 구축 범위

- `wiki-ingest` 스킬 개발
- **제안 → 승인 → 반영** 3단계 루프
- Cross-link + 근거 명시 규칙 강제
- Daily → Papers / Ideas / Experiments **라우팅**

## 설계 원칙

- 완전 자동 금지 (환각 리스크)
- 모든 변경은 사용자가 **diff 로 검토**
- 승인 단위는 **페이지 단위**, 부분 수정 가능

<div class="callout">

**핵심**: 제안을 사용자가 **반드시 검토**. 완전 자동 아님

</div>

---

# 🟣 Phase 2. QA 봇 통합

## 구축 범위

- Wiki 파일 기반 **retrieval**
- **INDEX 2단계 + cross-link walking** 으로 context 구성
- **Claude API** 기반 답변 생성
- Slack 봇 또는 CLI 인터페이스

## Embedding RAG 대신

- 이미 있는 **cross-link 구조를 활용**, 사람이 만든 명시적 그래프
- Embedding 유사도보다 **근거 추적** 이 쉬움
- 새 인프라(벡터 DB 등) 불필요

<div class="callout">

**핵심**: 이미 있는 cross-link 를 retrieval 신호로 활용

</div>

---

# 🟡 Phase 3. 확장 + 연구원 확산

## 확산 준비

- 교수님 Phase 0~2 **경험을 가이드** 로 문서화
- 연구원별 onboarding 스크립트
- Homepage (`research.damilab`) 과 연동, **같은 wiki md 읽기**
- Lint 시스템 (orphan / stale 페이지 탐지)

## 확산 원칙

- 스킬만 주지 않음. **경험 + 설계 의도** 함께 전달
- 연구원이 **자기 프로젝트에 맞게 fork** 하도록 허용

<div class="callout">

**핵심**: 먼저 써본 사람의 경험이 **설계·가이드**가 됨

</div>

---

<!-- _class: section -->

# 7. 세미나 전달 메시지

---

# 핵심 4 메시지 + 주의사항

## 4 핵심 메시지

- **왜**: 프로젝트 맥락 유지가 설문 1순위 고민
- **뭘**: daily log 던지면 자동 정리 + QA 봇, 프로젝트당 1 wiki
- **어떻게**: 교수님이 먼저 써보며 설계 검증
- **share 연결**: 도구는 share, 내용은 프로젝트

## 주의사항 5가지

- **구상 단계**, 세부 구현은 실제 사용하며 결정
- **Phase 0 수동 실험** 반드시 거치기
- **Homepage 는 별도 트랙**, 접점만 공유
- **완전 자동화 지양**, 제안·승인·반영 루프 유지
- **Cross-link 는 근거 필수**, 없으면 쓰레기 링크

---

<!-- _class: end -->

# Thank you
