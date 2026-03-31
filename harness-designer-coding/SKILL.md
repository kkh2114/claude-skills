---
name: harness-designer-coding
description: |
  코딩 에이전트가 코드를 안정적으로 생성·테스트·배포할 수 있는 하네스 구조를 설계하는 메타 스킬.
  Layer 1(메타): Planner→Generator→Evaluator 순환으로 코딩 하네스를 설계·구축·검증한다.
  Layer 2(운영): 완성된 하네스 안에서 코딩 에이전트가 실제 개발을 수행한다.
  "코딩 하네스 만들어줘", "개발 워크스페이스 설계", "에이전트 코딩 환경 구축",
  "CLAUDE.md 코딩 프로젝트용", "CI 파이프라인 설계", "코드 리뷰 루프 구축",
  "자율 코딩 환경", "에이전트 개발 환경", "coding harness", "agent-first development",
  "build harness for coding", "dev workspace setup", "autonomous coding environment"
  표현 시 반드시 사용.
---

# Coding Harness Designer v1

> "에이전트가 못한 건 능력 부족이 아니라, 환경이 부족했기 때문이다." — OpenAI
> "생성자가 자기 작업을 평가하게 하지 마라." — Anthropic
> "에이전트가 실수하면, 그 실수를 다시는 하지 못하도록 엔지니어링하라." — Mitchell Hashimoto

## 이 스킬과 harness-designer의 관계

```
┌─────────────────────────────────────────────────────────────┐
│  공통 기반: 하네스 설계 5대 기둥                                │
│  Progressive Disclosure / Mechanical Enforcement /           │
│  Feedback Loop / Session Continuity / Entropy Management     │
├──────────────────────────┬──────────────────────────────────┤
│  harness-designer (기존)  │  coding-harness-designer (이것)  │
│  분석·의사결정 워크스페이스  │  코딩·개발 워크스페이스            │
│  에이전트 = 관점 역할       │  에이전트 = 코딩 작업자            │
│  산출물 = 보고서·결정       │  산출물 = 소스 코드·테스트          │
│  검증 = 체크리스트·토론     │  검증 = CI·린터·브라우저 테스트     │
│  "회의실 설계"             │  "공장 라인 설계"                  │
└──────────────────────────┴──────────────────────────────────┘
```

---

## 코딩 하네스 7대 기둥

기존 5대 기둥에 코딩 전용 2개를 추가한다:

| 기둥 | 핵심 질문 | 원칙 |
|------|----------|------|
| **Progressive Disclosure** | 에이전트가 필요한 것만 볼 수 있는가? | AGENTS.md ~100줄 목차 → docs/ |
| **Mechanical Enforcement** | 아키텍처가 기계적으로 강제되는가? | 린터·구조 테스트·CI |
| **Feedback Loop** | 실패 시 에이전트가 자체 수정하는가? | 에러 메시지가 수정법을 가르침 |
| **Session Continuity** | 세션 간 핸드오프가 깨끗한가? | progress + feature-status + git |
| **Entropy Management** | 시간이 지나도 코드 품질이 유지되는가? | 자동 스캔·리팩터링·품질 등급 |
| **Architectural Rigidity** ← 신규 | 모듈 경계가 강제되는가? | 레이어 규칙·의존성 방향 검증 |
| **Observable Runtime** ← 신규 | 에이전트가 실행 결과를 볼 수 있는가? | 로그·메트릭·DOM·스크린샷 접근 |

---

## 두 레이어의 관계

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: 메타 (이 스킬의 역할)                                │
│                                                             │
│  Planner ──→ Generator ──→ Evaluator                        │
│     ↑         (단방향 순차, 역참조 금지)                      │
│     └──── 미흡 시 피드백 ─────────────────────────────┘      │
│                                                             │
│  목적: 코딩 하네스 구조를 설계·생성·검증                         │
└─────────────────────────┬───────────────────────────────────┘
                          │ 승인 후 하네스 완성
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: 운영 (완성된 코딩 하네스의 역할)                      │
│                                                             │
│  ┌ Initializer (첫 실행) ─→ 스캐폴드 + 환경 설정              │
│  │                                                          │
│  └ Coding Agent (반복 실행):                                 │
│    1. progress 읽기 → 다음 작업 선택                          │
│    2. 구현 (코드 생성)                                        │
│    3. 자체 검증 (테스트·린터·브라우저)                          │
│    4. 리뷰 요청 (에이전트 간 코드 리뷰)                        │
│    5. 피드백 반영 → 반복                                      │
│    6. clean state로 커밋                                     │
│                                                             │
│  목적: 실제 코드 작성·테스트·리팩터링·배포                       │
└─────────────────────────────────────────────────────────────┘
```

---

# LAYER 1: 메타 — 코딩 하네스 설계 프로세스

## L1 에이전트 3종 (단방향 순차, 역참조 금지)

### Planner (기획)
사용자 요구를 분석해서 코딩 하네스 구조를 설계한다.
- 인풋: 프로젝트 요구사항 (질문으로 수집)
- 아웃풋: 아키텍처 설계 + 폴더 구조 + 강제 규칙 + 평가 기준

### Generator (구축)
Planner 설계안을 실제 파일과 설정으로 만든다.
- 인풋: Planner 승인된 설계안
- 아웃풋: AGENTS.md, docs/, 린터 규칙, CI 설정, 테스트 구조

### Evaluator (검증)
Generator 산출물을 7대 기둥 기반으로 독립 검증한다.
- 인풋: Generator 생성 파일 + Planner 평가 기준
- 아웃풋: 기둥별 점수 + 기능적 검증 + 개선 피드백

---

## L1 Phase 1: Discovery — Planner 작동

Discovery는 4단계 질문으로 구성된다.
각 단계를 순서대로 진행하되, 사용자 답변에 따라 후속 질문이 분기된다.
**한 단계의 답변을 받은 후 다음 단계로 넘어간다.** 한꺼번에 묻지 않는다.

### 1-1. Stage 1 — 목적과 맥락 (WHY / WHO)

> 기술이 아닌, 이 프로젝트가 존재하는 이유를 파악한다.

```
P1. 이 프로젝트가 해결하려는 문제는 무엇인가?
    (어떤 불편함/비효율을 없애려 하는가?)

P2. 누가 사용하는가?
    (내부 직원 / 고객 / 개발자 / 불특정 다수)
    → 후속: 사용자 수는? IT 숙련도는?

P3. 이 프로젝트의 성공 기준은?
    (무엇이 되어야 "잘 만들었다"고 할 수 있는가?)

P4. 비슷한 기존 시스템이 있는가?
    (대체하는 것인가 / 새로 만드는 것인가)
    → 후속 [대체]: 기존 시스템의 가장 큰 문제점은?
    → 후속 [신규]: 벤치마크하는 서비스가 있는가?
```

**후속 질문 분기:**
- P2에서 "내부 직원" → "몇 명? 부서 구조가 있는가? 권한 체계가 필요한가?"
- P2에서 "고객" → "가입 방식은? 결제가 있는가? 개인정보 처리는?"
- P3에서 구체적 수치 언급 → "그 수치를 측정하는 방법은?"
- P3에서 모호한 답변 → "구체적으로 어떤 화면/기능이 동작하면 성공인가?"

### 1-2. Stage 2 — 기능과 내용 (WHAT)

> 무엇을 담는가, 핵심 기능은 무엇인가.

```
F1. 핵심 기능 3가지를 우선순위로 나열하면?
    (가장 먼저 동작해야 하는 것부터)

F2. 데이터의 성격은?
    (관계형 / 문서형 / 시계열 / 파일 / 복합)
    → 후속: 데이터 간 관계가 복잡한가? 집계/통계가 중요한가?

F3. 인증/권한 요구사항이 있는가?
    (없음 / 단순 로그인 / 역할 기반 / 조직 계층 권한)
    → 후속 [역할 기반 이상]: 권한 레벨은 몇 단계? 데이터 격리가 필요한가?

F4. 외부 시스템 연동이 있는가?
    (없음 / API 연동 / 파일 import/export / 결제 / 알림)

F5. 오프라인 또는 모바일 지원이 필요한가?
```

**후속 질문 분기:**
- F1에서 3개 이상 기능 → "각 기능의 복잡도를 상/중/하로 평가하면?"
- F2에서 "복합" → "어떤 종류가 섞이는가? 저장소를 분리해야 하는가?"
- F3에서 "조직 계층" → "부서 추가/변경이 잦은가? 코드 변경 없이 확장 가능해야 하는가?"

### 1-3. Stage 3 — 기술과 구조 (HOW)

> 어떻게 만들 것인가. Stage 1~2의 답변을 반영하여 적합한 기술을 제안한다.

```
T1. 기술 스택 선호가 있는가?
    (있으면 명시 / 없으면 "추천해줘")
    → "보링 테크놀로지" 권장: 에이전트는 안정적이고 학습 데이터가
      풍부한 기술로 더 잘 작동한다 (OpenAI 원안)
    → Stage 1~2 답변 기반으로 적합한 스택을 제안한다

T2. 배포 환경은?
    (Vercel / AWS / 사내 서버 / 모름)

T3. 코딩 에이전트 도구는?
    (Claude Code / Codex / Cursor / 기타)
    → 도구에 따라 하네스 설정 방식이 다름

T4. 에이전트의 자율성 수준은?
    (사람이 리뷰 후 머지 / 에이전트 간 리뷰 후 자동 머지 / 완전 자율)

T5. 프로젝트 규모와 기간은?
    (프로토타입 1~2주 / 중규모 1~3개월 / 대규모 장기)

T6. 기존 코드베이스가 있는가?
    (신규 / 기존 코드에 하네스 적용)
    → 기존 코드라면 점진적 적용 전략 설계
```

**후속 질문 분기:**
- T1에서 "추천해줘" → Stage 1~2 답변 기반으로 2~3개 옵션 비교표 제시 후 선택
- T2에서 "모름" → 사용자 규모와 기능 기반으로 추천
- T5에서 "대규모" → "팀 규모는? 동시 작업하는 에이전트 수는?"

### 1-4. Stage 4 — 품질과 평가 기준 (QUALITY / EVALUATE)

> 사용자가 중요하게 생각하는 가치를 파악하고, 평가 기준을 합의한다.

```
E1. 이 프로젝트에서 가장 중요한 품질 속성은? (상위 3개 선택)
    □ 보안 (권한, 데이터 격리, 인증)
    □ 성능 (응답 속도, 동시 접속)
    □ 확장성 (코드 변경 없이 규모 확장)
    □ 유지보수성 (다른 사람/에이전트가 쉽게 수정)
    □ 사용자 경험 (직관적 UI, 빠른 반응)
    □ 테스트 가능성 (자동 테스트로 품질 보증)
    □ 빠른 출시 (MVP 우선, 완성도는 나중에)
    □ 데이터 정합성 (정확한 기록, 누락 방지)

E2. 향후 확장 계획이 있는가?
    (없음 / 기능 추가 / 다른 시스템과 결합 / 사용자 규모 확장)
    → 후속: 구체적으로 어떤 확장? 시기는?

E3. 이 프로젝트에서 절대 타협하면 안 되는 것은?
    (예: "권한 격리가 깨지면 안 된다", "데이터가 유실되면 안 된다")

E4. 반대로, 초기에는 없어도 괜찮은 것은?
    (예: "모바일 대응은 나중에", "통계 대시보드는 2차에")
```

**후속 질문 분기:**
- E1에서 "보안" 선택 → "어떤 종류의 보안? 인증/권한/데이터 암호화/감사 로그?"
- E2에서 "다른 시스템과 결합" → "어떤 시스템? 데이터 형식은 호환되는가?"
- E3의 답변 → Evaluator 가중치의 핵심 입력으로 사용

### 1-5. 평가 가중치 합의 (Stage 4 완료 후)

Stage 1~4의 답변을 분석하여 **7대 기둥의 가중치를 제안**한다.
사용자와 합의하여 최종 확정한다.

```
[가중치 제안 프로세스]

STEP 1. Stage 1~4 답변에서 키워드 추출
  - "권한 격리" → Mechanical Enforcement, Architectural Rigidity ↑
  - "코드 변경 없이 확장" → Architectural Rigidity ↑
  - "빠른 출시" → Entropy Management ↓, Observable Runtime ↑
  - "데이터 정합성" → Feedback Loop ↑, Mechanical Enforcement ↑

STEP 2. 기본 가중치에서 조정하여 제안

  기본 가중치 (프로젝트 특성 반영 전):
  | 기둥 | 기본 | 조정 근거 | 제안 |
  |------|------|----------|------|
  | Progressive Disclosure | 15% | (변동 근거) | ?% |
  | Mechanical Enforcement | 20% | (변동 근거) | ?% |
  | Feedback Loop | 15% | (변동 근거) | ?% |
  | Session Continuity | 10% | (변동 근거) | ?% |
  | Entropy Management | 10% | (변동 근거) | ?% |
  | Architectural Rigidity | 20% | (변동 근거) | ?% |
  | Observable Runtime | 10% | (변동 근거) | ?% |

  "이 프로젝트에서는 [근거]를 고려하여
   [기둥]의 가중치를 [기본]% → [제안]%로 조정했습니다.
   의견이나 수정 사항이 있으시면 말씀해주세요."

STEP 3. 사용자 피드백 반영
  - 동의 → 확정
  - "보안을 더 높여줘" → 관련 기둥 가중치 상향, 다른 기둥 하향 후 재제안
  - "이 기둥은 필요 없어" → 0%로 설정, 나머지 재분배 후 재제안

STEP 4. 최종 승인
  "최종 가중치를 확정합니다. 이 가중치로 Evaluator가 채점합니다."
  → evaluator-protocol.md의 기본 가중치 대신 이 합의된 가중치를 사용
```

### 1-6. 아키텍처 패턴 자동 매핑

→ `references/architecture-patterns.md` 참조
→ Stage 2~3 답변 기반으로 가장 적합한 패턴을 제안한다

| 애플리케이션 유형 | 추천 레이어 구조 |
|-----------------|-----------------|
| 풀스택 웹앱 | Types→Config→Repo→Service→Runtime→UI |
| API 서비스 | Types→Config→Repo→Service→Runtime |
| CLI 도구 | Types→Config→Core→CLI |
| 라이브러리 | Types→Core→Public API |

### 1-7. Planner 산출물

**① 프로젝트 컨텍스트 요약** — 목적, 사용자, 성공 기준, 핵심 제약 (Stage 1~2 기반)
**② 아키텍처 설계안** — 레이어 구조, 모듈 경계, 의존성 방향
**③ 폴더 구조 초안** — references/coding-folder-patterns.md 기반
**④ 강제 규칙 설계** — 어떤 규칙을 린터/CI/구조 테스트로 강제하는가
**⑤ 테스트 전략** — 유닛/통합/E2E 범위와 커버리지 기준
**⑥ 에이전트 자율성 설계** — 리뷰 루프, 승인 게이트, 에스컬레이션 기준
**⑦ 확장 전략** — 향후 확장에 대비한 설계 결정 (Stage 4 E2 기반)
**⑧ 평가 기준 + 합의된 가중치** — 7대 기둥 체크리스트 + 가중치 테이블

```
[Planner 완료 — 사용자 승인 요청]
①~⑧을 검토 후 수정 사항 말씀해주세요.
승인되면 Generator가 구축을 시작합니다.
```

---

## L1 Phase 2: Build — Generator 작동

### 2-1. 핵심 산출물 생성 (순서대로)

| 순번 | 산출물 | 설명 |
|------|--------|------|
| 2-1a | 아키텍처 다이어그램 | Mermaid — 레이어·모듈·의존성 방향 |
| 2-1b | AGENTS.md (~100줄) | 목차 역할, 참조 라우팅 포함 |
| 2-1c | docs/ 디렉터리 | 아래 상세 |
| 2-1d | 아키텍처 강제 규칙 | 린터 규칙 + 구조 테스트 |
| 2-1e | CI/CD 파이프라인 설계 | 검증 게이트 정의 |
| 2-1f | 테스트 구조 | 테스트 디렉터리 + 기본 설정 |
| 2-1g | 세션 핸드오프 산출물 | progress.json + feature-status.json |
| 2-1h | 코드 리뷰 루프 설정 | 에이전트 간 리뷰 프로토콜 |
| 2-1i | 관찰 가능성 설정 | 로그·메트릭·DOM 접근 방법 |
| 2-1j | README.md | 개발자 가이드 |
| 2-1k | bkit 프로젝트 초기화 | T3에서 Claude Code + bkit 환경이면 필수 실행 (아래 상세) |

### 2-1b. AGENTS.md 작성 규칙 (최중요)

→ `references/agents-md-template.md` 참조

OpenAI 원안의 핵심 교훈을 그대로 적용:

**~100줄 목차.** 백과사전이 아니다.
```markdown
# [프로젝트명]

> [한 줄 설명]

## 아키텍처 개요
[레이어 구조 3줄 요약]
→ 상세: docs/architecture.md

## 참조 라우팅
| 상황 | 읽을 파일 |
|------|----------|
| 아키텍처 규칙 | → docs/architecture.md |
| 코딩 컨벤션 | → docs/conventions.md |
| 도메인 설계 | → docs/design/[domain].md |
| 실행 계획 | → docs/exec-plans/[plan].md |
| 품질 등급 | → docs/quality-grades.md |
| 기술 부채 | → docs/exec-plans/tech-debt-tracker.md |
| 세션 상태 | → progress.json |
| 기능 현황 | → feature-status.json |

## 핵심 규칙 (5가지 이내)
1. [불변 규칙 1 — 예: "모든 경계에서 데이터 형태를 검증"]
2. [불변 규칙 2 — 예: "레이어 역방향 의존 금지"]
3. [불변 규칙 3]

## 테스트 규칙
→ docs/testing-strategy.md

## 커맨드
| 커맨드 | 기능 |
|--------|------|
| /implement [기능] | 기능 구현 |
| /review | 코드 리뷰 실행 |
| /test | 테스트 실행 |
| /refactor [대상] | 리팩터링 |

## 최종 업데이트: YYYY-MM-DD
```

### 2-1c. docs/ 디렉터리 (System of Record)

→ `references/docs-structure.md` 참조

```
docs/
├── architecture.md         ← 레이어 구조, 모듈 경계, 의존성 규칙
├── conventions.md          ← 코딩 컨벤션, 네이밍, 파일 구조
├── quality-grades.md       ← 도메인/레이어별 품질 등급 (A~F)
├── testing-strategy.md     ← 테스트 유형, 커버리지 기준, 실행 방법
├── design/                 ← 도메인별 설계 문서
│   ├── [domain-a].md
│   └── [domain-b].md
├── exec-plans/             ← 실행 계획, 기술 부채 추적
│   ├── tech-debt-tracker.md
│   └── [plan-name].md
└── review-protocol.md      ← 에이전트 간 코드 리뷰 규칙
```

**핵심:** 이 디렉터리가 에이전트의 "유일한 진실의 원천(single source of truth)"이다.
Google Docs, Slack, 사람 머릿속에 있는 지식은 에이전트에게 존재하지 않는다.

### 2-1d. 아키텍처 강제 규칙

→ `references/enforcement-coding.md` 참조

문서화가 아닌 **기계적 강제**:

| 규칙 | 강제 수단 | 예시 |
|------|----------|------|
| 레이어 의존성 방향 | 구조 테스트 | UI가 Repo를 직접 import 하면 실패 |
| 경계 데이터 검증 | 린터 규칙 | 외부 입력은 반드시 스키마 검증 |
| 유틸리티 중앙화 | 린터 규칙 | 중복 헬퍼 함수 생성 시 경고 |
| 커밋 메시지 형식 | git hook | conventional commit 강제 |
| 테스트 커버리지 | CI 게이트 | 커버리지 미달 시 머지 차단 |

**에러 메시지 원칙:**
린터/테스트 에러 메시지는 **수정 방법을 가르쳐야** 한다.
에이전트가 에러를 보고 즉시 수정할 수 있도록:

```
❌ 나쁜 에러: "Layer violation detected"
✅ 좋은 에러: "Layer violation: UI layer cannot import from Repo layer.
   Move this logic to a Service layer function, then import from Service.
   See docs/architecture.md#layer-rules"
```

### 2-1e. CI/CD 파이프라인 설계

```
PR 생성
    │
    ▼
┌──────────────────────────────────────┐
│  Gate 1: 린트 + 타입 체크             │
│  (구조 테스트, import 규칙, 형식)      │
├──────────────────────────────────────┤
│  Gate 2: 유닛 테스트                  │
│  (커버리지 기준 충족 확인)             │
├──────────────────────────────────────┤
│  Gate 3: 통합/E2E 테스트              │
│  (브라우저 자동화, API 테스트)         │
├──────────────────────────────────────┤
│  Gate 4: 에이전트 코드 리뷰           │
│  (또는 사람 리뷰 — 자율성 수준에 따라)  │
└──────────────────────────────────────┘
    │
    ▼
  머지 승인
```

### 2-1f~g. 테스트 구조 + 세션 핸드오프

**테스트 구조:** Planner 설계 기반으로 테스트 디렉터리, 기본 설정, 실행 스크립트 생성
**세션 핸드오프:** progress.json + feature-status.json (harness-designer v4와 동일 스키마)

### 2-1h. 코드 리뷰 루프 (Ralph Wiggum Loop)

→ `references/review-loop.md` 참조

```
코딩 에이전트가 코드 작성
    │
    ▼
자체 로컬 리뷰 (린트, 테스트)
    │
    ▼
PR 생성
    │
    ▼
리뷰 에이전트(들)에게 리뷰 요청
    │
    ▼
피드백 수신 → 수정 반영
    │
    ▼
리뷰 통과까지 반복
    │
    ▼
[자율성 수준에 따라]
  ├─ 레벨 1: 사람이 최종 승인 후 머지
  ├─ 레벨 2: 에이전트 리뷰 통과 시 자동 머지
  └─ 레벨 3: 완전 자율 + 모니터링 알림
```

**사람 에스컬레이션 기준:**
- 새로운 아키텍처 결정
- 보안 관련 변경
- 제품 방향 판단이 필요한 경우
- 에이전트 간 의견 불일치

### 2-1i. 관찰 가능성 (Observable Runtime)

→ `references/observability.md` 참조

에이전트가 "자기가 만든 것이 실제로 동작하는지" 볼 수 있어야 한다:

| 관찰 수단 | 용도 | 설정 방법 |
|----------|------|----------|
| 브라우저 자동화 | UI 동작 확인 | Playwright/Puppeteer MCP |
| 로그 쿼리 | 에러/경고 확인 | 로컬 로그 파일 또는 LogQL |
| 메트릭 쿼리 | 성능 확인 | PromQL 또는 앱 내장 메트릭 |
| DOM 스냅샷 | UI 상태 확인 | Chrome DevTools Protocol |
| curl/httpie | API 동작 확인 | 직접 호출 |

### 2-1k. bkit 프로젝트 초기화 (Claude Code + bkit 환경일 때)

Discovery Stage 3의 T3에서 "Claude Code"이고 bkit 플러그인이 설치되어 있으면,
Generator가 하네스 구축의 마지막 단계로 bkit 초기화를 실행한다.

**왜 필요한가:**
하네스 스킬이 독자적으로 CLAUDE.md, docs/ 등을 생성하면
bkit의 초기화 경로(/dynamic init 등)를 거치지 않아서
bkit의 자동 트리거(gap-detector 자동 제안, 태스크 분류 등)가 활성화되지 않는다.

**실행 내용:**
```
1. bkit 설치 여부 확인
   → ~/.claude/skills/bkit-rules/SKILL.md 존재 확인 (Glob)
   → 없으면 스킵 (bkit 미설치 환경)

2. 프로젝트 레벨 감지 결과를 CLAUDE.md에 공식 등록
   → "## Project Level: Dynamic" (또는 Starter/Enterprise)
   → bkit-rules가 이 선언을 읽고 레벨별 행동을 자동 적용

3. .bkit-memory.json 생성 (프로젝트 루트)
   {
     "level": "dynamic",
     "initialized": "YYYY-MM-DD",
     "harnessDesigned": true,
     "features": []
   }

4. CLAUDE.md에 bkit 연동 선언 추가 (이미 없는 경우)
   → "bkit PDCA 자동 적용", "에이전트 자동 트리거 활성"
```

**스킵 조건:**
- T3에서 "Claude Code"가 아닌 경우 → 스킵
- bkit-rules SKILL.md가 없는 경우 → 스킵
- .bkit-memory.json이 이미 존재하는 경우 → 스킵

```
[GATE: Generator → Evaluator 강제 전환]
이 절차는 건너뛸 수 없다. Generator 완료 즉시 실행한다.

STEP 1. 산출물 존재 확인
  아래 10종 각각에 대해 Glob으로 존재 + Read로 비어있지 않음을 확인한다:
  □ AGENTS.md (또는 CLAUDE.md 내 동등 섹션)
  □ docs/architecture.md
  □ docs/conventions.md
  □ docs/design/ 내 도메인 설계 문서 1개 이상
  □ docs/testing-strategy.md
  □ docs/quality-grades.md
  □ docs/exec-plans/tech-debt-tracker.md
  □ progress.json
  □ feature-status.json
  □ 강제 규칙 파일 (린터 설정, CI 설계, 또는 구조 테스트 스크립트)
  □ bkit 초기화 (Claude Code + bkit 환경일 때만):
    .bkit-memory.json 존재 + CLAUDE.md에 Level 선언

  → 미존재 파일이 있으면: Generator로 돌아가서 해당 파일만 생성
  → 모두 존재하면: STEP 2로 진행

STEP 2. Evaluator 프로토콜 실행
  → references/evaluator-protocol.md 를 읽고 그 절차를 그대로 실행한다
  → 7대 기둥 × 3항목 = 21항목 채점
  → 가중치 적용 → 총점 산출
  → 결과를 보고 형식으로 사용자에게 출력

STEP 3. 점수별 분기
  → 90점 이상: Layer 2 전환 승인
  → 70~89점: Generator 재작업 (STEP 4)
  → 70점 미만: Planner 재설계 (Phase 1로 복귀)

이 GATE를 통과하지 않으면 Layer 2로 진행할 수 없다.
```

---

## L1 Phase 3: Evaluate — Evaluator 작동

> 이 단계는 GATE에 의해 자동으로 진입한다. 생략할 수 없다.

### 3-1. 검증 실행

→ `references/evaluator-protocol.md` 를 읽고 그대로 실행한다.

요약: 7대 기둥 × 3항목 = 21항목을 PASS/PARTIAL/FAIL로 채점.
가중치 적용 후 100점 만점으로 총점 산출. 결과를 보고 형식으로 출력.

### 3-2. 피드백 루프 (점수별 분기)

| 총점 | 판정 | 구체적 행동 |
|------|------|------------|
| 90점+ | **PASS** | "Layer 1 완료. Layer 2 전환 승인." 사용자에게 Layer 2 설명 제시 |
| 70~89점 | **REWORK** | FAIL/PARTIAL 항목별 피드백 생성 → Generator가 해당 파일만 수정 → Evaluator 재실행 |
| 70점 미만 | **REDESIGN** | 근본 원인 분석 → Planner의 어떤 설계 결정이 문제인지 식별 → Discovery 재시작 |

### 3-3. 재검증 규칙

1. Generator 재작업 후 **Evaluator 전체 재실행** (부분 검증 금지)
2. 최대 **3회 반복**. 초과 시 사용자에게 에스컬레이션
3. 매 반복마다 점수 변화 테이블 보고
4. 3회 연속 점수 개선 없으면 → 즉시 사용자 에스컬레이션 (무한 루프 방지)

### 3-4. REWORK 피드백 형식

각 FAIL/PARTIAL 항목에 대해:

```
❌ [기둥명] 항목 [번호]: [FAIL/PARTIAL]
   문제: [무엇이 부족한지 1줄]
   수정: [구체적으로 어떤 파일에 무엇을 추가/변경할지]
```

이 피드백은 Generator가 그대로 따라 실행할 수 있는 수준이어야 한다.

### 3-5. 하네스 경량화 검토 (PASS 판정 후 실행)

```
[경량화 체크리스트]
- [ ] 이 규칙 중 현재 모델이 자체 준수할 수 있는 것은?
- [ ] CI 게이트 중 과잉인 것은?
- [ ] 에이전트 자율성을 높여도 되는 영역은?
- [ ] 프로젝트 규모에 비해 과도한 구조는?
```

> "모델이 좋아질수록 하네스는 단순해져야 한다." — Anthropic

---

# LAYER 2: 운영 — 완성된 코딩 하네스

## Initializer / Coding Agent 분리

### Initializer (첫 실행 1회만)

```
1. 프로젝트 스캐폴드 생성 (패키지 매니저, 프레임워크 초기화)
2. CI 설정 파일 생성
3. 린터/포매터 설정
4. 테스트 프레임워크 설정
5. progress.json 초기화
6. feature-status.json 생성 (사용자 요구사항 → 200+ 기능 분해)
7. init.sh 작성 (개발 서버 시작, 기본 테스트)
8. 초기 git commit
```

### Coding Agent (매 세션 반복)

```
1. pwd 확인
2. progress.json 읽기 → 현재 상태 파악
3. feature-status.json 확인 → 다음 작업 선택
4. git log --oneline -20 → 최근 변경 이력
5. init.sh 실행 → 기본 동작 테스트
   (깨진 상태면 먼저 수정)
6. 기능 하나 구현:
   a. 코드 작성
   b. 테스트 작성
   c. 린터 통과 확인
   d. 브라우저/API 테스트로 E2E 확인
7. [bkit 연동 검증 루프] — references/layer2-bkit-integration.md 참조
   a. code-analyzer: 코드 품질/보안/아키텍처 검증
      → Critical 이슈 → 즉시 수정 후 재검증
   b. gap-detector: 설계 문서 대비 구현 일치도 검증
      → matchRate < 90% → pdca-iterator: 자동 반복 개선 (최대 5회)
      → matchRate >= 90% → 통과
   (bkit 미설치 환경: 자체 검증 체계로 대체 — layer2-bkit-integration.md 참조)
8. feature-status.json 업데이트 (검증 통과 후에만 passes: true)
9. progress.json 업데이트
10. git commit (설명적 메시지)
```

## 엔트로피 관리 (지속적 품질 유지)

```
[주기적 자동 스캔 — 배경 에이전트 또는 수동 트리거]
    │
    ▼
docs/quality-grades.md 업데이트
    │ (각 도메인/레이어별 A~F 등급)
    │
    ▼
docs/exec-plans/tech-debt-tracker.md 업데이트
    │ (부채 항목 + 우선순위)
    │
    ▼
리팩터링 PR 생성
    │ (소량씩, 매일)
    │
    ▼
"기술 부채는 고이자 대출. 매일 소액 상환이 몰아서 하는 것보다 낫다."
```

---

## 보링 테크놀로지 원칙

에이전트는 다음 조건의 기술로 더 잘 작동한다:
- 학습 데이터가 풍부 (Stack Overflow 답변 다수)
- API가 안정적 (버전 간 호환)
- 구성 가능하고 조합 가능 (composable)
- 불투명한 동작이 적음

최신 프레임워크보다 "지루한" 기술이 에이전트에게는 더 좋은 기반이다.
때로는 외부 라이브러리를 가져오는 것보다
기능의 부분 집합을 직접 구현하는 것이 더 저렴하다.

---

## 참조 파일

| 파일 | 언제 읽는가 |
|------|-----------|
| `references/architecture-patterns.md` | Phase 1에서 아키텍처 설계 시 |
| `references/coding-folder-patterns.md` | Phase 1에서 폴더 구조 선택 시 |
| `references/agents-md-template.md` | Phase 2에서 AGENTS.md 생성 시 |
| `references/docs-structure.md` | Phase 2에서 docs/ 디렉터리 설계 시 |
| `references/enforcement-coding.md` | Phase 2에서 린터/CI 규칙 설계 시 |
| `references/review-loop.md` | Phase 2에서 코드 리뷰 루프 설계 시 |
| `references/observability.md` | Phase 2에서 관찰 가능성 설정 시 |
| `references/evaluator-protocol.md` | **Phase 3 GATE에서 자동 로드** — 7대 기둥 채점 실행 |
| `references/layer2-bkit-integration.md` | Layer 2에서 bkit 에이전트 연동 시 |
