# 세션 핸드오프 참조 v1

> 원안: Anthropic "Effective harnesses for long-running agents" (2025.11)
> 원칙: "각 새 세션은 이전에 무슨 일이 있었는지 기억 없이 시작된다."

## 핵심 문제

장기 프로젝트에서 에이전트는 반복적으로 새 세션을 시작한다.
각 세션은 이전 맥락을 모른다. 이로 인해:
1. **One-shotting**: 한 번에 전부 하려다 컨텍스트 소진, 반쯤 만든 채 방치
2. **Premature completion**: 진행된 걸 보고 "끝났다" 선언
3. **State corruption**: 이전 세션이 남긴 불완전한 상태 위에 작업

## 해결: Initializer + Operating Agent 분리

같은 에이전트 시스템에서 **프롬프트만 다르게** 한다.

### Initializer Agent (첫 실행 1회만)

목적: 모든 후속 세션이 효과적으로 작업할 수 있는 환경을 설정

**생성하는 산출물:**

1. **init.sh** (해당 시) — 개발 서버 시작, 기본 테스트 실행 스크립트
2. **progress.json** — 세션 간 상태 추적
3. **feature-status.json** — 기능 목록 + 완료 상태
4. **초기 git commit** — 기준점 설정

### Operating Agent (매 세션 반복)

목적: 점진적으로 하나의 기능만 진행하고 clean state로 마무리

**세션 시작 루틴:**
```
1. pwd 확인 (작업 디렉터리)
2. progress.json 읽기 → 최근 작업 파악
3. feature-status.json 읽기 → 다음 작업 선택
4. git log 확인 → 최근 변경 이력
5. (해당 시) init.sh 실행 → 기본 동작 테스트
6. 기존 버그 있으면 먼저 수정
7. 그 다음에 새 기능 하나 작업
```

**세션 종료 루틴:**
```
1. 작업 결과 검증 (테스트, 수동 확인)
2. feature-status.json 업데이트 (passes: true/false만 변경)
3. progress.json 업데이트
4. git commit (설명적 메시지)
5. 세션 기록 저장 (30-analysis/sessions/)
```

---

## progress.json 스키마

```json
{
  "last_session": "ISO 8601 타임스탬프",
  "last_completed": "마지막으로 완료한 작업 설명",
  "next_todo": "다음에 해야 할 작업",
  "open_issues": [
    "해결되지 않은 이슈 1",
    "해결되지 않은 이슈 2"
  ],
  "session_count": 0,
  "notes": "특이사항"
}
```

**규칙:**
- 매 세션 시작 시 읽기, 종료 시 업데이트
- 전체 덮어쓰기 (append 아님)
- 간결하게 유지 (각 필드 1~2문장)

---

## feature-status.json 스키마

```json
[
  {
    "id": "F001",
    "category": "core",
    "description": "Council 5인 독립 토론 실행",
    "steps": [
      "5개 에이전트 프롬프트 로드",
      "각 에이전트 독립 실행",
      "Chairman 종합 실행",
      "결과 세션 파일로 저장"
    ],
    "passes": false
  },
  {
    "id": "F002",
    "category": "analysis",
    "description": "비교 분석 자동 저장",
    "passes": false
  }
]
```

**규칙:**
- **JSON을 사용한다** (Markdown 아님). 에이전트가 JSON을 부적절하게 편집할 가능성이 낮다.
- `passes` 필드만 변경한다. description이나 steps는 수정 금지.
  "기능을 삭제하거나 수정하는 것은 허용되지 않는다 — 누락되거나 버그 있는 기능을 초래할 수 있다."
- Initializer가 최초 생성, Operating Agent는 상태만 변경

---

## 적용 기준

| 프로젝트 유형 | 적용 여부 | 이유 |
|-------------|----------|------|
| 단발 분석/토론 | 불필요 | 한 세션에 완결 |
| 반복 분석 (매주 시장 체크) | 선택적 | progress.json만 사용 |
| 장기 코딩/빌드 | 필수 | feature-status.json + progress.json |
| 멀티 세션 리서치 | 권장 | progress.json + git history |

---

## Council 모드 적용 예시

부동산 토론 워크스페이스처럼 Council 패턴을 사용하는 경우:

```json
// feature-status.json 예시
[
  {"id": "C001", "description": "5인 Council 병렬 토론", "passes": true},
  {"id": "C002", "description": "지역 분석 자동 데이터 수집", "passes": true},
  {"id": "C003", "description": "비교 분석 템플릿 적용", "passes": false},
  {"id": "C004", "description": "의사결정 기록 자동 생성", "passes": false},
  {"id": "C005", "description": "CARL 교훈 축적", "passes": false}
]
```

```json
// progress.json 예시
{
  "last_session": "2026-03-29T14:00:00",
  "last_completed": "동탄 vs 광교 비교 분석",
  "next_todo": "비교 분석 결과 자동 저장 기능 구현 (C003)",
  "open_issues": ["비교 템플릿 형식 미확정"],
  "session_count": 12,
  "notes": "사용자가 비교 시 가격 그래프 포함 요청"
}
```
