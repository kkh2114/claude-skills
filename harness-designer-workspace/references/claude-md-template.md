# CLAUDE.md 작성 가이드 v3

## 핵심 원칙

CLAUDE.md는 **목차(table of contents)**다. 백과사전이 아니다.

> "모든 것이 중요하면, 아무것도 중요하지 않다."
> "모놀리식 instruction file은 예측 가능하게 실패한다." — OpenAI

- **100줄 이내** 유지 (상세 내용은 각 파일로 포인터)
- 에이전트가 첫 번째로 읽는 파일 = **진입점(entry point)**
- Progressive Disclosure: 에이전트는 여기서 시작해서 필요한 곳만 찾아간다
- 업데이트 시 WORKSPACE_TREE.md도 동기화

### 왜 100줄인가

에이전트의 컨텍스트 윈도우는 유한하다. 긴 instruction file은:
1. 작업과 코드를 위한 공간을 밀어낸다
2. 에이전트가 의도적 탐색 대신 로컬 패턴 매칭에 빠진다
3. 즉시 낡고, 무엇이 현행인지 파악 불가
4. 기계적 검증(신선도, 정합성)이 불가능

---

## 표준 섹션 구성

### 필수 섹션 (반드시 포함, 순서 유지)

```markdown
# [프로젝트명]

> [한 줄 설명]

## 워크스페이스 정체성
[이 워크스페이스가 무엇을 위한 공간인가 — 3줄 이내]

## 핵심 원칙
| 원칙 | 설명 |
|------|------|
| [원칙1] | [설명] |
| [원칙2] | [설명] |

## 에이전트 구성
| 페르소나 | 역할 | 핵심 질문 |
|----------|------|----------|
| [역할A] | [설명] | "[질문]" |
| Chairman | 메인 세션 종합 | — |

→ 상세: AGENTS.md

## 참조 라우팅 ← 필수 (Progressive Disclosure 핵심)
| 상황 | 읽을 파일 |
|------|----------|
| 에이전트 역할 확인 | → 00-system/prompts/[role].md |
| 토론 진행 규칙 | → 00-system/protocols/council-protocol.md |
| 독립성 원칙 상세 | → 00-system/protocols/independence-protocol.md |
| 데이터 흐름 | → 00-system/protocols/data-pipeline-architecture.md |
| 유지보수 기준 | → 00-system/protocols/maintenance-protocol.md |
| 세션 상태 확인 | → progress.json |
| 기능 완료 현황 | → feature-status.json |
| 지식 베이스 | → 40-knowledge-index/KNOWLEDGE_INDEX.md |

## 분석 흐름
[간단한 ASCII 또는 번호 순서 — 5줄 이내]

## 커맨드 목록
| 커맨드 | 기능 |
|--------|------|
| /[cmd1] | [설명] |

## 파일 구조
→ WORKSPACE_TREE.md 참조

## 최종 업데이트: YYYY-MM-DD
```

### 선택 섹션 (필요 시만 추가)

```markdown
## ⚠️ 독립성 원칙 (최우선)
→ 00-system/protocols/independence-protocol.md 참조
[여기는 2줄 요약만. 상세는 링크에.]

## 자동 감지 동작
| 사용자 발화 패턴 | 자동 동작 |
|----------------|----------|
| "[패턴]" | [동작] |
```

---

## 참조 라우팅 테이블 설계 원칙

이 테이블이 Progressive Disclosure의 핵심이다.
에이전트는 이 테이블을 보고 **필요한 파일만** 읽는다.

**좋은 라우팅:**
- 상황이 구체적이다 ("에이전트 역할 확인" ✓)
- 파일 경로가 정확하다 (존재하는 파일만)
- 한 상황에 하나의 파일만 가리킨다

**나쁜 라우팅:**
- "자세한 내용은 00-system/ 참조" ← 너무 모호
- 파일이 실제로 없는 경로를 가리킴
- 순환 참조 (A→B→A)

---

## 작성 시 자주 하는 실수

**너무 길게 쓰는 경우**
→ 100줄 넘으면 반드시 파일 분리. "이건 짧으니까 여기 넣어도 되겠지" 금지.
→ 세션 기록 형식, 답변 형식, 데이터 검증 원칙 등은 templates/나 protocols/로.

**참조 라우팅 테이블을 빠뜨리는 경우**
→ 에이전트가 모든 파일을 읽거나, 아무것도 안 읽게 됨. 반드시 포함.

**독립성 원칙을 CLAUDE.md에 전부 쓰는 경우**
→ 포인터만 쓰고 상세는 independence-protocol.md로. 2줄 요약 + 경로.

**업데이트 안 하는 경우**
→ 새 폴더·에이전트 추가 시 CLAUDE.md + WORKSPACE_TREE.md 동기화 필수.
→ maintenance-protocol.md의 검토 주기를 따른다.
