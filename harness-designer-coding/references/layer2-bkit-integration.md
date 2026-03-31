# Layer 2 bkit 에이전트 연동 가이드 v1

> Layer 2(운영)에서 코딩 에이전트가 bkit 에이전트를 활용하는 방법.
> Generator가 하네스 구축 시 이 문서를 참조하여 Layer 2 구조에 bkit 연동 지점을 포함시킨다.

## 적용 범위

```
Layer 1 (메타)  → evaluator-protocol.md  → 하네스 구조 검증 (이 문서의 범위 아님)
Layer 2 (운영)  → 이 문서                → 생산된 코드 검증
```

Layer 2의 Coding Agent가 기능을 구현한 후, 그 코드가 설계와 일치하고 품질 기준을 충족하는지 검증하는 단계에서 bkit 에이전트를 활용한다.

---

## bkit 에이전트 역할 매핑

| bkit 에이전트 | Layer 2 역할 | 검증 대상 | 출력 |
|--------------|-------------|----------|------|
| **gap-detector** | 설계-구현 일치도 검증 | docs/design/ vs src/ | matchRate % + gap 목록 |
| **code-analyzer** | 코드 품질/보안/아키텍처 | src/ 전체 | Quality Score + issue 목록 |
| **pdca-iterator** | 자동 반복 개선 | 위 두 에이전트의 결과 | 최대 5회 반복 후 최종 점수 |

---

## 호출 시점

### Coding Agent 워크플로우 내 위치

```
1. progress.json 읽기
2. feature-status.json → 다음 작업 선택
3. 기능 구현 (코드 + 테스트)
4. 자체 로컬 검증 (린트, 유닛 테스트)
5. ──────────────────────────────────
   │ [bkit 검증 루프 시작]           │
   │                                │
   │ 5a. code-analyzer 호출          │
   │     → Critical 이슈 → 즉시 수정 │
   │     → Warning만 → 판단 후 진행  │
   │                                │
   │ 5b. gap-detector 호출           │
   │     → matchRate >= 90% → 통과  │
   │     → matchRate < 90%          │
   │       → pdca-iterator 호출     │
   │       → 자동 반복 (최대 5회)    │
   │                                │
   │ [bkit 검증 루프 종료]           │
   ──────────────────────────────────
6. feature-status.json 업데이트
7. progress.json 업데이트
8. git commit
```

### 호출하지 않는 경우

- Quick Fix (< 50자 변경) — 린트 통과만 확인
- 문서만 수정 — 코드 검증 불필요
- 스캐폴드/보일러플레이트 생성 — 아직 로직 없음

---

## Generator가 하네스에 포함할 연동 설정

### 방법 1: AGENTS.md 커맨드 테이블

Generator가 AGENTS.md를 생성할 때 아래 커맨드를 포함한다:

```markdown
## 커맨드

| 커맨드 | 기능 | bkit 에이전트 |
|--------|------|--------------|
| /implement [기능] | 기능 구현 | - |
| /review | 코드 리뷰 실행 | code-analyzer |
| /check [기능] | 설계-구현 비교 | gap-detector |
| /iterate [기능] | 자동 반복 개선 | pdca-iterator |
| /test | 테스트 실행 | - |
| /refactor [대상] | 리팩터링 | code-analyzer (사후 검증) |
```

### 방법 2: docs/review-protocol.md

Generator가 코드 리뷰 프로토콜을 생성할 때 bkit 검증 단계를 포함한다:

```markdown
## 코드 리뷰 절차

1. 코딩 에이전트: 코드 작성 + 테스트 작성
2. 자체 검증: 린트 + 유닛 테스트 통과
3. [bkit] code-analyzer: 품질/보안/아키텍처 검증
   - Critical → 머지 차단, 즉시 수정
   - Warning → 판단 후 진행
4. [bkit] gap-detector: 설계 대비 구현 일치도
   - < 90% → pdca-iterator로 자동 개선
   - >= 90% → 리뷰 통과
5. PR 생성 또는 커밋
```

### 방법 3: CI 파이프라인 (선택)

에이전트 자율성 레벨 2~3에서 CI에 bkit 검증을 포함할 수 있다:

```
Gate 4: 에이전트 코드 리뷰
  ├─ code-analyzer 자동 실행
  ├─ gap-detector 자동 실행
  └─ 둘 다 통과 시 머지 승인
```

---

## bkit 미설치 환경 대응

bkit은 **권장**이지 **필수**가 아니다.
Planner Phase 1의 Q5(코딩 에이전트 도구) 답변에 따라 연동 수준을 결정한다.

| 환경 | 연동 수준 | 대체 검증 |
|------|----------|----------|
| Claude Code + bkit | 전체 연동 | gap-detector + code-analyzer + pdca-iterator |
| Claude Code, bkit 미설치 | 자체 검증 | 린터 + 테스트 + 구조 테스트 스크립트 |
| Cursor / Codex / 기타 | 도구별 대응 | 해당 도구의 검증 체계 사용 |

### 자체 검증 체계 (bkit 미설치 시)

Generator가 대체 검증 수단을 구축한다:

```
scripts/
├── lint-layers.sh      ← 레이어 의존성 방향 검증 (기둥 6 대응)
├── check-conventions.sh ← 네이밍/import 컨벤션 검증 (기둥 2 대응)
└── health-check.sh     ← 앱 시작 + 기본 동작 확인 (기둥 7 대응)
```

이 스크립트들은 bkit 에이전트가 하는 것의 축소판이지만,
하네스가 독립적으로 동작할 수 있게 한다.

---

## bkit 에이전트 입출력 요약

### gap-detector

```
입력:
  - 설계 문서: docs/design/*.md (API spec, data model, feature design)
  - 구현 코드: src/ 전체

출력:
  - docs/03-analysis/{feature}-gap.md (또는 프로젝트 관례에 따른 경로)
  - matchRate: N% (90% 이상이면 PASS)
  - gaps: { missing: N, added: N, changed: N }
```

### code-analyzer

```
입력:
  - 구현 코드: src/ 전체
  - 기준: 보안(OWASP), 성능, 아키텍처, DRY, 네이밍

출력:
  - Quality Score (100점 만점)
  - Issues: Critical / Warning / Info 분류
```

### pdca-iterator

```
입력:
  - gap-detector 또는 code-analyzer의 결과
  - 통과 기준: matchRate >= 90%

출력:
  - 반복 횟수 + 최종 점수
  - 성공(PASS) / 실패(FAILURE, 5회 초과) / 부분(PARTIAL)
```
