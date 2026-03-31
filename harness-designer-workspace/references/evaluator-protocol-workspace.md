# Evaluator 프로토콜 — Workspace v1

> Generator 산출물을 5대 기둥 기반으로 독립 검증하는 절차.
> SKILL.md의 GATE에 의해 자동 호출된다. 이 문서를 읽은 즉시 절차를 실행한다.

## 적용 범위

이 프로토콜은 **Layer 1(메타)** 전용이다.
검증 대상은 "코드"가 아니라 "워크스페이스 구조 파일"이다.

```
Layer 1 Evaluator (이 문서)  → 하네스 환경(문서/프로토콜/프롬프트)이 잘 만들어졌는가?
Layer 2 운영                  → 도메인 에이전트가 실제 업무를 수행
```

---

## STEP 1: 산출물 인벤토리 확인

Generator가 생성해야 하는 파일 목록을 Glob/Read로 확인한다.
각 항목: EXISTS / MISSING

| # | 산출물 | 확인 방법 |
|---|--------|----------|
| 1 | CLAUDE.md (~100줄) | Glob → Read 첫 10줄 |
| 2 | AGENTS.md | Glob |
| 3 | WORKSPACE_TREE.md | Glob |
| 4 | 00-system/prompts/ 내 역할 파일 1개 이상 | Glob `00-system/prompts/*.md` |
| 5 | 00-system/protocols/council-protocol.md | Glob |
| 6 | 00-system/protocols/independence-protocol.md | Glob |
| 7 | 00-system/protocols/maintenance-protocol.md | Glob |
| 8 | .claude/commands/ 내 커맨드 1개 이상 | Glob `.claude/commands/*.md` |
| 9 | README.md | Glob |
| 10 | (장기) progress.json + feature-status.json | Glob (해당 시에만) |

**MISSING이 1개라도 있으면:** Evaluator 중단 → Generator로 돌아가서 해당 파일 생성.
**모두 EXISTS이면:** STEP 2로 진행.

---

## STEP 2: 5대 기둥 채점

### 채점 규칙

- 기둥당 3개 항목, 총 15개 항목
- 각 항목: **PASS**(1점) / **PARTIAL**(0.5점) / **FAIL**(0점)

### 가중치

**가중치는 Discovery Stage 4에서 사용자와 합의하여 결정한다.**
합의된 가중치가 없으면 아래 기본값을 사용한다.

| 기둥 | 기본 가중치 | 근거 |
|------|-----------|------|
| 1. Progressive Disclosure | 20% | 에이전트 진입 품질 — CLAUDE.md 간결성 |
| 2. Mechanical Enforcement | 25% | 워크스페이스 핵심 — 독립성/출처 강제 |
| 3. Feedback Loop | 20% | 자체 개선 — 재작업/에스컬레이션 경로 |
| 4. Session Continuity | 15% | 세션 핸드오프 — 장기 프로젝트 품질 |
| 5. Entropy Management | 20% | 구조 유지 — 문서 신선도, 엔트로피 방지 |

**프로젝트별 가중치 조정 예시:**
- 독립성 중시 → Mechanical Enforcement 30% (나머지 하향)
- 단발 분석 → Session Continuity 5% (나머지 상향)
- 장기 지식 축적 → Session Continuity 20%, Entropy Management 25%

---

### 기둥별 판정 기준

#### 기둥 1: Progressive Disclosure (20%)

| # | 항목 | PASS | PARTIAL | FAIL |
|---|------|------|---------|------|
| 1-1 | CLAUDE.md 길이 | 100줄 이하 | 101~130줄 | 130줄 초과 |
| 1-2 | 참조 라우팅 테이블 | 테이블 존재 + 3개 이상 항목 | 테이블 존재 + 2개 이하 | 없음 |
| 1-3 | protocols/prompts/ 분리 | 모든 상세가 분리됨 | 일부만 분리 | CLAUDE.md에 상세 인라인 |

**확인 방법:**
- 1-1: Read CLAUDE.md → 줄 수 확인
- 1-2: CLAUDE.md 내 `|` 테이블에서 `→` 패턴 검색
- 1-3: CLAUDE.md 내 코드블록 10줄 이상 존재 여부로 역판정

---

#### 기둥 2: Mechanical Enforcement (25%)

| # | 항목 | PASS | PARTIAL | FAIL |
|---|------|------|---------|------|
| 2-1 | 독립성 검증 수단 | 템플릿에 bias_check 필드 또는 동등 수단 | 독립성 문서화만 | 없음 |
| 2-2 | 아웃풋 템플릿 필수 필드 | source 필드 포함 템플릿 존재 | 템플릿 존재하나 필수 필드 미정의 | 없음 |
| 2-3 | 커맨드 정의 | .claude/commands/ 내 파일 존재 | CLAUDE.md에 커맨드 언급만 | 없음 |

**확인 방법:**
- 2-1: Grep `bias_check|독립성.*검증|independence.*check` in protocols/ 또는 prompts/
- 2-2: Grep `source|출처|reference` in prompts/ 또는 templates/
- 2-3: Glob `.claude/commands/*.md`

---

#### 기둥 3: Feedback Loop (20%)

| # | 항목 | PASS | PARTIAL | FAIL |
|---|------|------|---------|------|
| 3-1 | 재작업 경로 | GATE에서 점수별 분기 명시 | "미흡 시 재작업" 수준 | 없음 |
| 3-2 | 에스컬레이션 기준 | 구체적 조건 명시 | 암시적 언급 | 없음 |
| 3-3 | 파일 경로 유효성 | 참조 라우팅의 모든 경로가 실제 파일과 일치 | 90% 이상 일치 | 불일치 존재 |

**확인 방법:**
- 3-1: 이 GATE가 존재하므로 PASS (스킬 자체에 내장)
- 3-2: Grep `에스컬레이션|escalat|사람.*확인` in protocols/ 또는 AGENTS.md
- 3-3: CLAUDE.md의 참조 테이블에서 경로 추출 → Glob으로 존재 확인

---

#### 기둥 4: Session Continuity (15%)

| # | 항목 | PASS | PARTIAL | FAIL |
|---|------|------|---------|------|
| 4-1 | progress.json 구조 | 파일 존재 + last_session, next_todo 필드 | 파일 존재하나 구조 불완전 | 없음 (장기 시 FAIL) |
| 4-2 | Initializer/Operating Agent 분리 | AGENTS.md에 분리 명시 | 암시적 구분 | 구분 없음 |
| 4-3 | 문서 간 일관성 | 에이전트 수가 CLAUDE.md/AGENTS.md/prompts/ 일치 | 1개 불일치 | 2개 이상 불일치 |

**확인 방법:**
- 4-1: Read progress.json → 필드 확인 (단발 프로젝트면 N/A → PASS)
- 4-2: Grep `Initializer|첫.*실행|Operating|반복` in AGENTS.md
- 4-3: CLAUDE.md 에이전트 수 vs AGENTS.md vs prompts/ 파일 수 비교

---

#### 기둥 5: Entropy Management (20%)

| # | 항목 | PASS | PARTIAL | FAIL |
|---|------|------|---------|------|
| 5-1 | maintenance-protocol.md 존재 | 파일 존재 + 문서 신선도 기준 포함 | 파일 존재하나 내용 비어있음 | 없음 |
| 5-2 | 문서 동기화 기준 | CLAUDE.md ↔ WORKSPACE_TREE.md 동기화 주기 명시 | 동기화 언급만 | 없음 |
| 5-3 | 경량화 검토 완료 | 경량화 체크리스트 항목별 판정 기록 | 부분 검토 | 미검토 |

**확인 방법:**
- 5-1: Read maintenance-protocol.md → "신선도|주기|갱신" 패턴 확인
- 5-2: Grep `동기화|sync|주기|갱신` in maintenance-protocol.md
- 5-3: 경량화 검토는 Evaluator PASS 후 실행하므로 첫 채점 시 PARTIAL 허용

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
| 1. Progressive Disclosure | ? | ? | ? | ?% | 20% | ? |
| 2. Mechanical Enforcement | ? | ? | ? | ?% | 25% | ? |
| 3. Feedback Loop | ? | ? | ? | ?% | 20% | ? |
| 4. Session Continuity | ? | ? | ? | ?% | 15% | ? |
| 5. Entropy Management | ? | ? | ? | ?% | 20% | ? |

### 총점: ??.? / 100

### 판정: [PASS / REWORK / REDESIGN]
```

---

## STEP 4: 점수별 분기

| 총점 | 판정 | 행동 |
|------|------|------|
| **90점 이상** | PASS | "Layer 1 완료." → Layer 2 구조 토론 → 사용자 최종 승인 |
| **70~89점** | REWORK | 아래 피드백 생성 → Generator 재작업 → STEP 1부터 재실행 |
| **70점 미만** | REDESIGN | 근본 원인 분석 → Planner 재설계 |

### REWORK 피드백 생성 규칙

각 FAIL/PARTIAL 항목에 대해 반드시 3줄을 출력한다:

```
❌ [기둥명] 항목 [번호]: [판정]
   문제: [무엇이 부족한지 1줄]
   수정: [구체적으로 어떤 파일에 무엇을 추가/변경할지]
```

---

## STEP 5: 재검증 규칙

1. Generator 재작업 후 **STEP 1부터 전체 재실행** (부분 검증 금지)
2. 최대 **3회 반복**. 초과 시 사용자에게 에스컬레이션
3. 매 반복마다 점수 변화 테이블 보고:

```
| 반복 | 총점 | 변화 | FAIL 항목 수 |
|------|------|------|-------------|
| 1차 | 68.0 | -    | 4           |
| 2차 | 82.5 | +14.5| 1           |
| 3차 | 95.0 | +12.5| 0           |
→ PASS. Layer 2 전환 승인.
```

4. 3회 연속 점수 개선 없으면 → 즉시 사용자 에스컬레이션 (무한 루프 방지)
