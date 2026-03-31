# 관찰 가능성 (Observable Runtime) 참조 v1

> "에이전트에게 앱의 런타임을 직접 볼 수 있게 하는 것에 투자하라." — OpenAI
> "코드만 보고 '끝'이라 선언하는 것이 가장 흔한 실패 패턴이다." — Anthropic

## 핵심 문제

에이전트가 코드를 작성하고 "완료"라 선언하지만,
실제로 돌려보면 동작하지 않는 경우가 빈번하다.

해결: 에이전트가 **자기가 만든 것의 실행 결과를 직접 볼 수 있어야** 한다.

## 관찰 수단 5가지

### 1. 브라우저 자동화 (웹앱 필수)

에이전트가 실제 브라우저에서 앱을 사용해볼 수 있게:

- **Playwright MCP** — E2E 테스트 + 스크린샷
- **Puppeteer MCP** — DOM 스냅샷 + 네비게이션
- **Chrome DevTools Protocol** — DOM 상태, 콘솔 에러, 네트워크

사용 시점:
- 기능 구현 후 "정말 동작하는지" 확인
- UI 버그 재현
- 시각적 결과물 검증

제한: 브라우저 네이티브 모달(alert 등)은 자동화 도구로 보기 어려움.
이런 기능은 버그가 생기기 쉬우므로 수동 테스트 권장.

### 2. 로그 접근

에이전트가 서버 로그를 읽을 수 있게:

```bash
# 간단한 방법: 로그 파일 tail
tail -n 50 logs/app.log

# 구조화된 방법: 로그 쿼리 (LogQL 등)
# 로컬 개발에서는 파일 기반이 실용적
```

### 3. API 직접 호출

```bash
# curl로 API 동작 확인
curl -s http://localhost:3000/api/health | jq .

# 인증 필요한 엔드포인트
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:3000/api/users | jq .
```

에이전트가 구현한 API가 실제로 올바른 응답을 주는지 확인.

### 4. 개발 서버 상태

```bash
# 서버가 살아있는지
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000

# 프로세스 확인
lsof -i :3000
```

### 5. 성능 메트릭 (고급)

대규모 프로젝트에서:
- 응답 시간 측정
- 메모리 사용량 확인
- 동시 접속 테스트

## init.sh에서의 관찰 가능성

Initializer가 만드는 init.sh에 기본 관찰 스크립트 포함:

```bash
#!/bin/bash
# init.sh — 개발 서버 시작 + 기본 헬스 체크

# 서버 시작 (백그라운드)
npm run dev &
SERVER_PID=$!
sleep 3

# 기본 헬스 체크
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ "$HTTP_CODE" = "200" ]; then
  echo "✅ 서버 정상 (PID: $SERVER_PID)"
else
  echo "❌ 서버 비정상 (HTTP $HTTP_CODE)"
  exit 1
fi
```

## Coding Agent 세션 루틴에서의 적용

매 세션 시작 시:
```
1. init.sh 실행 → 서버 시작 + 헬스 체크
2. 브라우저 자동화로 기본 기능 동작 확인
   (로그인, 기본 페이지 로드 등)
3. 깨진 것 있으면 → 먼저 수정
4. 그 다음 새 기능 구현
```

기능 구현 후:
```
1. 유닛 테스트 실행
2. 브라우저/API로 E2E 확인
3. 콘솔 에러 확인
4. 확인 완료 후에만 feature-status.json의 passes를 true로
```

## Generator가 해야 하는 것

1. init.sh 생성 (서버 시작 + 헬스 체크)
2. 관찰 도구 설정 (프로젝트에 맞는 것 선택)
3. docs/testing-strategy.md에 E2E 관찰 방법 명시
4. Coding Agent 세션 루틴에 관찰 단계 포함
