# 큰 marp 덱 작성 워크플로우

25장 이상의 대형 마르프 덱을 만들 때 context 관리를 위한 **outline → chunk 분할 → subagent → 병합** 패턴.

---

## 언제 쓰는가

| 덱 규모 | 방식 |
|---|---|
| ~10장 | 한 번에 (분할 불필요, 단일 세션) |
| 10~25장 | 한 번에 작성하되 **outline 먼저** 잡고 시작 |
| 25장 이상 | **반드시 이 패턴으로 분할** |

작은 덱에 이 패턴을 기계적으로 적용하면 subagent 오버헤드가 단일 세션보다 커져서 오히려 손해.

---

## 전체 워크플로우

```
[1. Outline]      main agent 가 전체 구조를 한 화면 분량으로 정리
      ↓
[2. Chunks]       10장 단위로 분할 (섹션 경계 우선)
      ↓
[3. Subagent]     각 chunk 를 subagent 에 dispatch (병렬 가능)
      ↓
[4. 병합]          main agent 가 결과를 이어붙임, frontmatter/title/end 추가
      ↓
[5. 빌드 + 검증]    한 번 빌드 후 PDF 렌더 확인
```

---

## Step 1. Outline 먼저 (main agent)

전체 덱의 slide-by-slide 구조를 한 화면에 담는다. 각 슬라이드마다:

- 번호
- 제목
- 핵심 한 줄 (주장/결론/show 할 것)
- 사용할 유틸리티 (`cols-2`, `flow-row`, `callout` 등)
- 소스 문서의 해당 섹션 (있으면)

**예시 outline**:
```
01. [title]     Safety + Planning for Industrial Embodied Agent
02. [toc]       Contents (5 sections)
03. [section]   1. Introduction
04. Embodied AI — 정의 + 3단 불릿 (roadmap.md §1)
05. Disembodied vs Embodied — cols-2 + callout (roadmap.md §1.2)
06. 적용 사례 — flow-row 4 boxes
07. [section]   2. Environment and Tasks
08. Task 분류 — 테이블 + scoped font-size 0.85em
...
```

Outline 자체는 50장 덱이어도 100~150 줄 내외라서 main context 에 부담 없음.

---

## Step 2. Chunks 로 분할 (main agent)

슬라이드를 10장 단위로 묶되, **섹션 경계를 우선**해서 자른다.

- Chunk 1: 01~10 (Intro section 전체)
- Chunk 2: 11~20 (Environment section 전체)
- Chunk 3: 21~30 (Safety section 전체)
- ...

한 섹션이 15장이면 그 chunk 는 15장, 섹션이 짧으면 다음 섹션과 합쳐도 OK. 경계에서 어색한 끊김 방지.

---

## Step 3. Subagent dispatch (main agent)

각 chunk 마다 subagent 에 다음 4가지를 전달:

### A. 전체 outline

앞뒤 문맥 파악용. 내 chunk 가 전체에서 어디 위치하는지 알 수 있어야 중복/누락 방지.

### B. 해당 chunk 의 상세 내용

원본 소스 문서(roadmap.md 같은)의 해당 섹션 발췌.

### C. 스타일 가이드 (아래 블록 그대로 복붙)

```
### 사용 가능한 유틸리티

- `.cols-2` / `.cols-3`: N 분할 grid 레이아웃
- `.callout`: 빨간 왼쪽 바 + 연한 빨간 배경 강조 박스
- `.flow-box`: 네이비 헤더 + 흰 본문 박스 (내부 `.header` + `.body` 구조)
- `.flow-row`: `.flow-box` 들을 가로 나열 + 사이에 화살표 자동 생성

### 슬라이드 클래스

- `<!-- _class: title -->`: 표지 (네이비 풀블리드)
- `<!-- _class: toc -->`: 목차
- `<!-- _class: section -->`: 섹션 전환 (상단 63% 네이비)
- `<!-- _class: end -->`: 마지막 (Thank you)
- 클래스 없음: 일반 본문

### 엄격한 원칙

- 각 슬라이드 h1 은 정확히 1개
- 본문에 쌍따옴표 `"..."` 나 작은따옴표 `'...'` 사용 금지 (CommonMark flanking 이슈)
- 강조는 `**bold**` 로만
- 테이블이 공간을 넘치면 슬라이드 상단에 `<style scoped>section table { font-size: 0.85em; }</style>` 등으로 override
- 코드 블록은 언어 명시: ```yaml, ```bash 등
- div 블록 내부에 마크다운 쓰려면 여는 태그 뒤 + 닫는 태그 앞에 빈 줄 필수
```

### D. 출력 형식 지정

```
완성된 marp markdown 본문만 반환 (frontmatter 제외).
슬라이드 구분은 `---` 로.
슬라이드 번호 N ~ M 만 포함.
```

**Subagent 호출은 병렬 가능**. 예: 5-chunk 덱이면 5개 subagent 를 동시에 dispatch 하면 시간 절약.

---

## Step 4. 병합 (main agent)

subagent 들이 반환한 슬라이드 블록들을 순서대로 이어 붙임:

```markdown
---
marp: true
theme: dami-lab
paginate: true
math: katex
footer: '동국대학교 컴퓨터·AI학과 DAMI Lab'
---

<!-- _class: title -->
<!-- _paginate: false -->

# <덱 제목>
<div class="author">...</div>
<div class="date">...</div>

---

[chunk 1 결과]

---

[chunk 2 결과]

---

...

---

<!-- _class: end -->

# Thank you
```

---

## Step 5. 빌드 + 검증

```bash
python3 .claude/skills/marp/bin/build.py temp_works/<project>/<deck-name>.md
```

PDF 렌더 확인. 문제가 특정 chunk 에만 있으면 해당 chunk 만 subagent 로 재수정하고 병합만 다시.

---

## 함정 / 트레이드오프

**1. 스타일 불일치**
subagent 마다 같은 상황에서 다른 유틸리티를 고를 수 있음 (한 명은 `.callout` 다른 명은 인라인 HTML). 스타일 가이드를 **반드시 프롬프트에 포함**, 모호하면 "이 상황에는 X 를 써라" 구체 예시 추가.

**2. 이음새 어색**
chunk 경계에서 슬라이드 간 흐름이 끊길 수 있음. outline 에 **앞 chunk 의 마지막 슬라이드 제목과 다음 chunk 첫 슬라이드 제목** 을 포함해서 subagent 가 자연스러운 연결 문구 쓸 수 있게.

**3. 중복 내용**
subagent 는 outline 만 보고 자기 chunk 밖에 뭐가 있는지 모름. 프롬프트에 "앞 N번까지 이미 다뤘으니 중복 금지, 뒷 M번 이후에 나올 내용은 여기서 언급만 하고 상세 설명은 거기서" 를 명시.

**4. 오버헤드**
20장 미만 덱에 이 패턴 적용하면 outline 잡고 dispatch 하고 병합하는 비용이 단일 세션 작성보다 비쌈. "25장 이상" 기준 지키기.

**5. PDF 파일명**
덱 내용 반영한 영문 kebab-case 로 (예: `share-damilab-roadmap.md`). `slides.md` 같은 generic 이름 쓰지 말기.

---

## 체크리스트 (큰 덱 작업 전)

- [ ] 덱 규모 확인 (25장 이상인가?)
- [ ] 소스 문서 확인 (roadmap.md, spec.md 등 원본이 있는가?)
- [ ] Outline 작성 (한 화면 분량)
- [ ] Chunks 경계 설정 (섹션 우선)
- [ ] 스타일 가이드 준비 (subagent 프롬프트에 복붙용)
- [ ] 파일명 결정 (kebab-case 영문, 내용 반영)
- [ ] 작업 완료 후 PDF 렌더 전수 확인
