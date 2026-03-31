# Evaluator 프로토콜 v1

> Generator 산출물을 7대 기둥 기반으로 독립 검증하는 절차.
> SKILL.md의 GATE에 의해 자동 호출된다. 이 문서를 읽은 즉시 절차를 실행한다.

## 적용 범위

이 프로토콜은 **Layer 1(메타)** 전용이다.
검증 대상은 "코드"가 아니라 "하네스 구조 파일"이다.

```
Layer 1 Evaluator (이 문서)  → 하네스 환경이 잘 만들어졌는가?
Layer 2 bkit 검증             → 하네스 안에서 만든 코드가 좋은가?
```

---

## STEP 1: 산출물 인벤토리 확인

Generator가 생성해야 하는 파일 목록을 Glob/Read로 확인한다.
각 항목: EXISTS(파일 존재 + 비어있지 않음) / MISSING(미존재 또는 비어있음)

| # | 산출물 | 확인 방법 |
|---|--------|----------|
| 1 | AGENTS.md (또는 CLAUDE.md 내 동등 섹션) | Glob → Read 첫 10줄 |
| 2 | docs/architecture.md | Glob |
| 3 | docs/conventions.md | Glob |
| 4 | docs/design/ 내 도메인 설계 문서 1개 이상 | Glob `docs/design/*.md` |
| 5 | docs/testing-strategy.md | Glob |
| 6 | docs/quality-grades.md | Glob |
| 7 | docs/exec-plans/tech-debt-tracker.md | Glob |
| 8 | progress.json | Glob |
| 9 | feature-status.json | Glob |
| 10 | 강제 규칙 파일 (.eslintrc, lint 스크립트, 또는 CI 설계 문서) | Glob 패턴 다수 시도 |

**MISSING이 1개라도 있으면:** Evaluator 중단 → Generator로 돌아가서 해당 파일 생성.
**모두 EXISTS이면:** STEP 2로 진행.

---

## STEP 2: 7대 기둥 채점

### 채점 규칙

- 기둥당 3개 항목, 총 21개 항목
- 각 항목: **PASS**(1점) / **PARTIAL**(0.5점) / **FAIL**(0점)
- 판정은 아래 기준표의 **객관적 조건**으로 결정한다 (주관 판단 최소화)

### 가중치

**가중치는 Discovery Stage 4에서 사용자와 합의하여 결정한다.**
합의된 가중치가 없으면 아래 기본값을 사용한다.

| 기둥 | 기본 가중치 | 근거 |
|------|-----------|------|
| 1. Progressive Disclosure | 15% | 에이전트 진입 품질 — 과잉 정보는 혼란 유발 |
| 2. Mechanical Enforcement | 20% | 코딩 하네스의 핵심 차별점 — 문서가 아닌 기계적 강제 |
| 3. Feedback Loop | 15% | 자체 수정 능력 — 에러 시 즉시 복구 가능성 |
| 4. Session Continuity | 10% | 세션 간 핸드오프 — 멀티세션 작업 품질 |
| 5. Entropy Management | 10% | 장기 품질 유지 — 시간에 따른 구조 부패 방지 |
| 6. Architectural Rigidity | 20% | 코딩 전용 핵심 — 모듈 경계와 의존성 방향 |
| 7. Observable Runtime | 10% | 코딩 전용 — 실행 결과 확인 가능성 |

**프로젝트별 가중치 조정 예시:**
- 보안 중시 → Mechanical Enforcement 25%, Architectural Rigidity 25% (나머지 하향)
- 빠른 출시 → Entropy Management 5%, Observable Runtime 15% (빌드 확인 우선)
- 장기 유지보수 → Session Continuity 15%, Entropy Management 15% (지속성 강화)

### 기둥별 판정 기준

---

#### 기둥 1: Progressive Disclosure (15%)

| # | 항목 | PASS | PARTIAL | FAIL |
|---|------|------|---------|------|
| 1-1 | AGENTS.md 길이 | 120줄 이하 | 121~150줄 | 150줄 초과 |
| 1-2 | 참조 라우팅 테이블 | 테이블 존재 + 3개 이상 항목 | 테이블 존재 + 2개 이하 | 없음 |
| 1-3 | docs/ 분리 | 모든 상세가 docs/에 분리 | 일부만 분리 | AGENTS.md에 상세 내용 인라인 |

**확인 방법:**
- 1-1: `wc -l AGENTS.md` 또는 Read 후 줄 수 확인
- 1-2: AGENTS.md 내 `|` 구분 테이블에서 `→ docs/` 또는 `→ ` 패턴 검색
- 1-3: AGENTS.md 내 코드블록 10줄 이상 존재 여부로 역판정 (있으면 FAIL)

---

#### 기둥 2: Mechanical Enforcement (20%)

| # | 항목 | PASS | PARTIAL | FAIL |
|---|------|------|---------|------|
| 2-1 | 린터/포매터 설정 | 설정 파일 존재 (.eslintrc*, prettier*, biome* 등) | package.json에 lint 스크립트만 존재 | 없음 |
| 2-2 | 구조 테스트 또는 import 규칙 | scripts/ 내 검증 스크립트 또는 린터 커스텀 룰 존재 | docs/에 규칙 문서화만 | 없음 |
| 2-3 | CI 게이트 설계 | CI 설정 파일 또는 CI 설계 문서 존재 | docs/에 CI 언급만 | 없음 |

**확인 방법:**
- 2-1: Glob `.eslintrc*`, `prettier*`, `biome*`, `.editorconfig`
- 2-2: Glob `scripts/*lint*`, `scripts/*check*` 또는 Grep `no-restricted-imports`
- 2-3: Glob `.github/workflows/*`, `ci.yml` 또는 Grep `CI` in docs/

---

#### 기둥 3: Feedback Loop (15%)

| # | 항목 | PASS | PARTIAL | FAIL |
|---|------|------|---------|------|
| 3-1 | 에러 메시지에 수정 가이드 포함 | 에러 출력에 "Fix:" 또는 "See docs/" 패턴 포함 | 에러 메시지는 있으나 가이드 없음 | 커스텀 에러 메시지 없음 |
| 3-2 | 코드 리뷰 루프 정의 | docs/review-protocol.md 또는 동등 문서 존재 | AGENTS.md에 리뷰 언급만 | 없음 |
| 3-3 | 에스컬레이션 기준 | 리뷰 문서 내 "에스컬레이션" 또는 "사람 리뷰" 기준 명시 | 암시적 언급 | 없음 |

**확인 방법:**
- 3-1: scripts/ 내 파일에서 "Fix", "See", "참조" Grep
- 3-2: Glob `docs/*review*`, `docs/*protocol*`
- 3-3: Grep "에스컬레이션|escalat|사람.*리뷰|human.*review" in docs/

---

#### 기둥 4: Session Continuity (10%)

| # | 항목 | PASS | PARTIAL | FAIL |
|---|------|------|---------|------|
| 4-1 | progress.json 구조 | 파일 존재 + currentPhase, completedTasks 필드 포함 | 파일 존재하나 구조 불완전 | 없음 |
| 4-2 | feature-status.json 구조 | 파일 존재 + features 배열 + 각 항목에 status 필드 | 파일 존재하나 구조 불완전 | 없음 |
| 4-3 | Initializer/Agent 분리 | AGENTS.md 또는 docs/에 첫 실행과 반복 실행 구분 명시 | 암시적 구분 | 구분 없음 |

**확인 방법:**
- 4-1: Read progress.json → JSON 파싱 → 필드 확인
- 4-2: Read feature-status.json → JSON 파싱 → 구조 확인
- 4-3: Grep "Initializer|첫.*실행|init|초기화" in AGENTS.md 또는 docs/

---

#### 기둥 5: Entropy Management (10%)

| # | 항목 | PASS | PARTIAL | FAIL |
|---|------|------|---------|------|
| 5-1 | quality-grades.md 존재 | 파일 존재 + 등급 기준 정의 | 파일 존재하나 내용 비어있음 | 없음 |
| 5-2 | tech-debt-tracker.md 존재 | 파일 존재 + 추적 테이블 구조 | 파일 존재하나 구조 없음 | 없음 |
| 5-3 | 자동 스캔/정리 전략 | docs/ 내 스캔 주기 또는 트리거 명시 | 품질 관리 언급만 | 없음 |

**확인 방법:**
- 5-1: Read quality-grades.md → 등급(A~F) 또는 기준 테이블 존재 확인
- 5-2: Read tech-debt-tracker.md → 테이블 헤더 존재 확인
- 5-3: Grep "주기|periodic|scan|스캔|cron|trigger" in docs/

---

#### 기둥 6: Architectural Rigidity (20%)

| # | 항목 | PASS | PARTIAL | FAIL |
|---|------|------|---------|------|
| 6-1 | 레이어 구조 정의 | docs/architecture.md에 레이어 + 의존성 방향 명시 | 레이어 나열만 | 없음 |
| 6-2 | 모듈 경계 규칙 | import 규칙 또는 도메인 간 접근 규칙 명시 | 권고 수준 | 없음 |
| 6-3 | 의존성 방향 검증 수단 | 린터 규칙/스크립트로 역방향 import 차단 | 문서에 규칙만 기술 | 없음 |

**확인 방법:**
- 6-1: Read docs/architecture.md → "→" 또는 "방향" 또는 "layer" 패턴 확인
- 6-2: Grep "import.*금지|restrict|경계|boundary" in docs/
- 6-3: Grep "no-restricted-imports|lint-layers|layer.*check" in 프로젝트 전체

---

#### 기둥 7: Observable Runtime (10%)

| # | 항목 | PASS | PARTIAL | FAIL |
|---|------|------|---------|------|
| 7-1 | 관찰 도구/방법 명시 | docs/에 테스트 또는 관찰 방법 구체적 기술 | "테스트 예정" 수준 | 없음 |
| 7-2 | E2E 또는 API 테스트 수단 | 테스트 프레임워크 설정 또는 curl 스크립트 존재 | 문서에 계획만 | 없음 |
| 7-3 | 헬스체크/시작 스크립트 | init.sh 또는 package.json scripts에 dev/start + 검증 | dev 스크립트만 | 없음 |

**확인 방법:**
- 7-1: Read docs/testing-strategy.md → 구체적 도구명/커맨드 존재 확인
- 7-2: Glob `tests/**`, `e2e/**`, `scripts/*test*` 또는 package.json 내 test 스크립트
- 7-3: Glob `init.sh` 또는 Grep "dev.*&&|start.*&&|health" in package.json

---

## STEP 3: 점수 계산

### 계산 공식

```
기둥별 점수 = (항목1 + 항목2 + 항목3) / 3.0 × 100
가중 기여점수 = 기둥별 점수 × 가중치
총점 = Σ 가중 기여점수
```

### 보고 형식 (반드시 이 형식으로 출력)

```
## Evaluator 검증 결과 — [프로젝트명]

### 기둥별 점수

| 기둥 | 항목1 | 항목2 | 항목3 | 기둥점수 | 가중치 | 기여점수 |
|------|-------|-------|-------|---------|--------|---------|
| 1. Progressive Disclosure | ? | ? | ? | ?% | 15% | ? |
| 2. Mechanical Enforcement | ? | ? | ? | ?% | 20% | ? |
| 3. Feedback Loop | ? | ? | ? | ?% | 15% | ? |
| 4. Session Continuity | ? | ? | ? | ?% | 10% | ? |
| 5. Entropy Management | ? | ? | ? | ?% | 10% | ? |
| 6. Architectural Rigidity | ? | ? | ? | ?% | 20% | ? |
| 7. Observable Runtime | ? | ? | ? | ?% | 10% | ? |

### 총점: ??.? / 100

### 판정: [PASS / REWORK / REDESIGN]
```

---

## STEP 4: 점수별 분기

| 총점 | 판정 | 행동 |
|------|------|------|
| **90점 이상** | PASS | "Layer 1 완료. Layer 2 전환 승인." → 사용자에게 Layer 2 설명 제시 |
| **70~89점** | REWORK | 아래 피드백 생성 → Generator가 해당 파일만 수정 → STEP 1부터 재실행 |
| **70점 미만** | REDESIGN | 근본 원인 분석 → Planner의 어떤 결정이 문제인지 식별 → Discovery 재시작 가능 |

### REWORK 피드백 생성 규칙

각 FAIL/PARTIAL 항목에 대해 반드시 3줄을 출력한다:

```
❌ [기둥명] 항목 [번호]: [판정]
   문제: [무엇이 부족한지 1줄]
   수정: [구체적으로 어떤 파일에 무엇을 추가/변경할지]
```

이 피드백은 Generator가 그대로 따라 실행할 수 있는 수준이어야 한다.

---

## STEP 5: 재검증 규칙

1. Generator 재작업 후 **STEP 1부터 전체 재실행** (부분 검증 금지)
2. 최대 **3회 반복**. 초과 시 사용자에게 에스컬레이션
3. 매 반복마다 점수 변화 테이블 보고:

```
| 반복 | 총점 | 변화 | FAIL 항목 수 |
|------|------|------|-------------|
| 1차 | 72.5 | - | 5 |
| 2차 | 85.0 | +12.5 | 2 |
| 3차 | 92.0 | +7.0 | 0 |
→ PASS. Layer 2 전환 승인.
```

4. 3회 연속 점수 개선 없으면 → 즉시 사용자 에스컬레이션 (무한 루프 방지)
