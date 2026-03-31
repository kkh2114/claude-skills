# 코딩 강제 규칙 패턴 참조 v1

> "불변량(invariants)을 강제하라, 구현을 마이크로매니지하지 말라." — OpenAI
> "한 번 인코딩하면, 모든 코드 라인에 적용된다."

## 3종 강제 수단

### 1. 구조 테스트 (Structural Tests)

아키텍처 규칙을 코드로 검증. CI에서 실행.

**레이어 의존성 검증 예시 (bash):**
```bash
#!/bin/bash
# scripts/lint-layers.sh
# UI 레이어가 Repo 레이어를 직접 import 하면 실패

VIOLATIONS=$(grep -rn "from.*repo" src/runtime/ui/ 2>/dev/null || true)
if [ -n "$VIOLATIONS" ]; then
  echo "❌ Layer violation: UI layer imports from Repo layer"
  echo "$VIOLATIONS"
  echo ""
  echo "FIX: Move this logic to a Service layer function."
  echo "     UI → Service → Repo (정방향만 허용)"
  echo "     See docs/architecture.md#layer-rules"
  exit 1
fi
echo "✅ Layer dependencies OK"
```

**모듈 경계 검증 예시:**
```bash
#!/bin/bash
# 도메인 간 직접 import 검사
for domain in src/domains/*/; do
  DOMAIN_NAME=$(basename "$domain")
  CROSS_IMPORTS=$(grep -rn "from.*domains/" "$domain" | grep -v "$DOMAIN_NAME" || true)
  if [ -n "$CROSS_IMPORTS" ]; then
    echo "❌ Cross-domain import in $DOMAIN_NAME:"
    echo "$CROSS_IMPORTS"
    echo "FIX: Use shared/ or providers/ for cross-domain communication."
    exit 1
  fi
done
echo "✅ Module boundaries OK"
```

### 2. 린터 규칙 (Custom Linters)

코딩 컨벤션을 기계적으로 강제. ESLint, Ruff, 커스텀 스크립트.

**핵심 규칙 예시:**
- 중복 유틸리티 감지: shared/에 이미 있는 기능 재구현 시 경고
- 경계 검증 누락: 외부 입력 처리 시 검증 코드 없으면 경고
- 금지 패턴: 직접 DB 쿼리 in UI, 하드코딩된 설정값

**에러 메시지 원칙:**
모든 에러는 에이전트가 **즉시 수정할 수 있도록** 작성:

```
❌ 나쁜: "Import violation"
✅ 좋은: "Import violation in src/runtime/ui/Dashboard.tsx:15
   'import { getUserById } from ../../domains/auth/repo'
   UI layer cannot import from Repo layer.
   → Create a Service function: src/domains/auth/service.ts
   → Import from Service: import { getUserById } from ../../domains/auth/service
   → Reference: docs/architecture.md#layer-rules"
```

### 3. CI 게이트 (Pipeline Gates)

PR이 머지되기 위해 통과해야 하는 검증 단계:

```yaml
# .github/workflows/ci.yml 골격
name: CI
on: [pull_request]
jobs:
  gate-1-lint:
    steps:
      - run: npm run lint          # 코드 스타일
      - run: npm run typecheck     # 타입 검사
      - run: bash scripts/lint-layers.sh  # 레이어 규칙
      - run: bash scripts/check-structure.sh  # 구조 검증

  gate-2-unit-test:
    needs: gate-1-lint
    steps:
      - run: npm test -- --coverage
      - run: bash scripts/check-coverage.sh  # 커버리지 기준

  gate-3-integration:
    needs: gate-2-unit-test
    steps:
      - run: npm run test:integration
      - run: npm run test:e2e  # (해당 시)
```

## "취향 불변량" (Taste Invariants)

정량적 규칙 외에, 코드 품질에 대한 "취향"도 인코딩 가능:

```markdown
# docs/conventions.md 에 포함

## 취향 규칙
- 공유 유틸 패키지를 선호, 도메인별 헬퍼 남발 금지
- 데이터 검증은 스키마 기반 (Zod, pydantic), 수동 if 문 금지
- 에러 메시지는 사용자 친화적 (내부 스택트레이스 노출 금지)
```

이런 규칙은 린터로 완벽히 강제하기 어렵지만,
코드 리뷰 루프에서 리뷰 에이전트가 체크한다.

## Generator가 해야 하는 것

1. docs/architecture.md에 레이어 규칙 정의
2. scripts/에 구조 테스트 스크립트 생성
3. 린터 설정 파일 생성 (.eslintrc / pyproject.toml 등)
4. CI 파이프라인 설정 생성
5. 모든 에러 메시지에 **수정 방법 + 참조 문서 경로** 포함
