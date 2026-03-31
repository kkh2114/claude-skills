# 강제 규칙 패턴 참조 v1

> "문서화만으로는 완전히 에이전트가 생성한 코드베이스의 일관성을 유지할 수 없다."
> "불변량(invariants)을 강제하라. 구현을 마이크로매니지하지 말라." — OpenAI

## 핵심 원칙

**문서화 = 안내 / 강제 = 보장**

안내(문서)만으로는:
- 에이전트가 규칙을 "잊거나" 무시할 수 있다
- 시간이 지나면 문서와 실제가 어긋난다 (drift)
- 위반을 사후에야 발견한다

강제(enforcement)는:
- 규칙 위반 시 즉시 피드백
- 기계적으로 검증 가능
- 한 번 인코딩하면 모든 에이전트에 적용

## 이 스킬에서의 적용 범위

이 메타 스킬은 **코딩 에이전트용 CI/린터**를 만드는 것이 아니다.
의사결정·분석·리서치 워크스페이스를 설계하므로,
강제 규칙은 **구조적 강제**와 **템플릿 기반 강제**에 집중한다.

---

## 강제 유형 3가지

### 유형 1: 구조적 강제 (폴더/파일 규칙)

**원칙:** 에이전트가 올바른 위치에 올바른 형태로 산출물을 만들도록 구조로 유도

| 규칙 | 문서만 | 구조적 강제 |
|------|--------|------------|
| 세션 기록 위치 | "sessions/에 저장하세요" | 템플릿이 경로를 포함 |
| 의사결정 기록 | "50-decisions/에 저장" | decision-template.md 파일명 규칙 포함 |
| 지식 축적 | "70-playbook/에 저장" | CARL 형식 템플릿 제공 |

**Generator가 만드는 것:**
- 각 산출물 유형별 template .md 파일 (00-system/templates/)
- 템플릿에 경로, 파일명 규칙, 필수 필드를 포함

### 유형 2: 템플릿 기반 강제 (필수 필드)

**원칙:** 아웃풋 템플릿에 필수 필드를 정의하여 누락을 방지

**예: 세션 기록 템플릿**
```markdown
# [주제] — YYYY-MM-DD

## 필수 메타데이터
- **일시**: (필수)
- **유형**: (필수: Council / 분석 / 상담)
- **대상**: (필수)
- **bias_check**: (필수: 사용자 편향 감지 여부 Y/N)

## 각 에이전트 의견
(각 에이전트별 의견 + **source** 필드 필수)

### [역할A]
- 의견: 
- 근거: 
- source: (필수: 데이터 출처)

## Chairman 종합
- 판정: (필수: Go/Pivot/No-Go)
- 신뢰도: (필수: 높음/중간/낮음)
```

**핵심 필수 필드:**
- `source`: 출처 없는 주장 방지 ("출처 없으면 침묵" 원칙)
- `bias_check`: 독립성 원칙 검증 ("사용자 편향 감지 여부")
- `판정` + `신뢰도`: 결론 누락 방지

### 유형 3: 상태 파일 기반 강제 (JSON)

**원칙:** JSON 파일로 상태를 추적하여 에이전트가 "잊지" 못하게 함

이미 `references/session-handoff.md`에서 다루는 내용:
- progress.json: 세션 간 상태 추적
- feature-status.json: 기능 완료 현황

**추가 강제 규칙:**
- progress.json은 매 세션 종료 시 반드시 업데이트
- feature-status.json의 passes는 실제 검증 후에만 true로 변경

---

## 구조 검증 스크립트 (선택)

Claude Code 환경에서 사용 가능한 검증 스크립트 예시:

```bash
#!/bin/bash
# verify-structure.sh — 워크스페이스 구조 검증

ERRORS=0

# CLAUDE.md 존재 확인
[ ! -f "CLAUDE.md" ] && echo "❌ CLAUDE.md 없음" && ERRORS=$((ERRORS+1))

# CLAUDE.md 100줄 이내 확인
if [ -f "CLAUDE.md" ]; then
  LINES=$(wc -l < CLAUDE.md)
  [ "$LINES" -gt 100 ] && echo "⚠️ CLAUDE.md가 ${LINES}줄 (100줄 초과)" && ERRORS=$((ERRORS+1))
fi

# 필수 프로토콜 존재 확인
for f in independence-protocol.md council-protocol.md maintenance-protocol.md; do
  [ ! -f "00-system/protocols/$f" ] && echo "❌ 00-system/protocols/$f 없음" && ERRORS=$((ERRORS+1))
done

# 에이전트 수 일치 확인 (prompts/ 파일 수)
PROMPT_COUNT=$(ls 00-system/prompts/*.md 2>/dev/null | wc -l)
echo "📊 에이전트 프롬프트 파일: ${PROMPT_COUNT}개"

# 결과
if [ $ERRORS -eq 0 ]; then
  echo "✅ 구조 검증 통과"
else
  echo "❌ ${ERRORS}개 오류 발견"
fi
```

이 스크립트는 **선택 사항**이다.
모든 프로젝트에 필요하지 않으며, 복잡한 워크스페이스에서만 권장.

---

## Generator가 해야 하는 것 요약

1. **필수 필드가 포함된 템플릿** 생성 (00-system/templates/)
2. **JSON 상태 파일** 초기 스키마 생성 (장기 프로젝트)
3. **참조 라우팅 테이블**에 "규칙 위반 시 확인할 파일" 포함
4. (선택) 구조 검증 스크립트 생성
