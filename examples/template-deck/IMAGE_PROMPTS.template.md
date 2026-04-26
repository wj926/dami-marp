# IMAGE_PROMPTS — <발표 이름>

image-gen 워크플로우의 단계 3 결과물. `image-gen/run.sh generate` 가 이 파일을 파싱해서 ChatGPT 에 일괄 던짐.

파싱 규칙 (chatgpt_image.py:parse_prompts):
- `### \`filename.png\` — caption`
- 그 다음에 `- **Prompt**:`
- 그 다음에 **들여쓰기 없는** 코드 블록 (백틱 3개가 줄 시작)

---

### `slide3_architecture.png` — 시스템 아키텍처

- **Prompt**:

```
clean modern editorial illustration, 16:9 wide aspect ratio,
navy and warm beige palette, no text or labels,
<구체적 묘사: 무엇을·어떻게·어떤 구도>
```

### `slide5_team.png` — 팀 구조

- **Prompt**:

```
minimalist organizational diagram, 16:9 wide,
same palette as previous,
<구체적 묘사>
```

<!--
프롬프트 작성 팁 (image-gen/troubleshooting.md §4 참고):
- 16:9 wide aspect ratio (배경) / 1:1 square 또는 9:16 portrait (![bg right])
- 텍스트·라벨은 언어 관계없이 다 넣음. 한글·영문·숫자 모두 GPT-4o image gen 이 거의 정확히 그림
  → `labeled exactly "라벨문구" in Korean/English` 식으로 명시
  → 끝에 `Render every label letter exactly as written, no typos, no missing characters` 추가
- 가아아끔 깨지는 글자는 단계 6 시각 자동 검수 (Claude Code 가 PNG 직접 봄) 가 잡음 → 단계 7 자동 재생성
- 발표 톤 일관성: 모든 프롬프트에 같은 스타일 키워드 반복
-->
