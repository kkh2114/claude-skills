# AGENTS.md 작성 가이드 (코딩 프로젝트용) v1

## 핵심 원칙

> "지도를 줘라, 1000페이지 매뉴얼 말고."

AGENTS.md (또는 CLAUDE.md)는 **~100줄 목차**다.
에이전트의 첫 진입점이며, docs/로 가는 포인터를 제공한다.

### 왜 100줄인가

OpenAI의 실험 결과:
- 모놀리식 instruction file은 컨텍스트를 밀어내 작업 코드 공간이 줄어든다
- 모든 것이 "중요"하면 에이전트는 의도적 탐색 대신 로컬 패턴 매칭에 빠진다
- 거대한 단일 파일은 즉시 낡고, 기계적 검증도 불가능하다

### 필수 섹션

```markdown
# [프로젝트명]

> [한 줄 설명]

## 아키텍처 개요
[레이어 구조 3줄 요약 — Types→Config→...→UI]
→ 상세: docs/architecture.md

## 참조 라우팅
| 상황 | 읽을 파일 |
|------|----------|
| 아키텍처 규칙·레이어 | → docs/architecture.md |
| 코딩 컨벤션·네이밍 | → docs/conventions.md |
| 도메인 설계 | → docs/design/[domain].md |
| 테스트 전략 | → docs/testing-strategy.md |
| 코드 리뷰 규칙 | → docs/review-protocol.md |
| 품질 현황 | → docs/quality-grades.md |
| 기술 부채 | → docs/exec-plans/tech-debt-tracker.md |
| 세션 상태 | → progress.json |
| 기능 현황 | → feature-status.json |
| 환경 시작 | → init.sh |

## 핵심 불변 규칙
1. [규칙 — 예: 레이어 역방향 의존 금지]
2. [규칙 — 예: 경계에서 데이터 검증 필수]
3. [규칙 — 예: 공유 유틸은 shared/에만]
(5개 이내. 에이전트가 항상 기억해야 하는 것만.)

## 테스트
→ docs/testing-strategy.md

## 커맨드
| 커맨드 | 기능 |
|--------|------|
| /implement [기능] | 기능 구현 |
| /test | 테스트 실행 |
| /review | 코드 리뷰 |
| /refactor [대상] | 리팩터링 |
| /scan | 품질 스캔 + 부채 업데이트 |

## 최종 업데이트: YYYY-MM-DD
```

### 하지 말아야 할 것

- 코딩 컨벤션 전체를 AGENTS.md에 쓰기 (→ docs/conventions.md로)
- 모든 API 엔드포인트 목록 넣기 (→ docs/design/에 도메인별로)
- 설치 가이드 넣기 (→ README.md로)
- 테스트 작성법 상세 (→ docs/testing-strategy.md로)
