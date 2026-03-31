# 아키텍처 패턴 참조 v1

> "아키텍처적 경직성과 예측 가능한 구조를 갖춤으로써,
>  에이전트가 빠르게 출력하면서도 기반이 무너지지 않게 한다." — OpenAI

## 레이어 구조 원칙

코드는 정해진 방향으로만 의존할 수 있다.
이것은 **제안이 아니라 구조 테스트로 강제**한다.

### 패턴 A: 풀스택 웹앱

```
Types → Config → Repo → Service → Runtime → UI
  ↓       ↓       ↓       ↓         ↓        ↓
 순수    설정    데이터   비즈니스   서버/앱   화면
 타입    값      접근    로직      진입점    렌더링
```

**의존성 규칙:**
- 각 레이어는 **왼쪽 레이어만** import 가능
- UI → Service ✅ / UI → Repo ❌
- 횡단 관심사(auth, telemetry, feature flags)는 Providers 인터페이스로 주입

### 패턴 B: API 서비스

```
Types → Config → Repo → Service → Runtime
```
UI 레이어 없음. Runtime이 HTTP/gRPC 진입점.

### 패턴 C: CLI 도구

```
Types → Config → Core → CLI
```
Core가 비즈니스 로직, CLI가 사용자 인터페이스.

### 패턴 D: 라이브러리

```
Types → Core → Public API
```
Public API만 외부에 노출. Core는 내부 구현.

---

## 모듈 경계 원칙

### 도메인 분리
```
src/
├── domains/
│   ├── auth/          ← 인증·인가
│   │   ├── types.ts
│   │   ├── repo.ts
│   │   └── service.ts
│   ├── billing/       ← 결제
│   └── chat/          ← 채팅
├── shared/            ← 공유 유틸리티 (중앙화)
└── providers/         ← 횡단 관심사 주입
```

### 경계에서 데이터 검증

> "경계에서 데이터 형태를 파싱하라. YOLO 스타일로 데이터를 탐색하지 마라." — OpenAI

- 외부 입력(API 요청, DB 결과, 파일 읽기)은 경계에서 반드시 검증
- 내부 레이어 간 전달은 타입으로 보장
- 검증 방법은 에이전트가 선택 (Zod, io-ts, pydantic 등)

---

## 커스텀 설계 가이드

1. 애플리케이션 유형으로 기본 패턴 선택 (A~D)
2. 도메인 목록 나열 (auth, billing, chat 등)
3. 각 도메인에 레이어 적용
4. 횡단 관심사 식별 → Providers로 분리
5. **의존성 방향을 구조 테스트로 강제**
6. 공유 유틸리티는 shared/에 중앙화 (중복 헬퍼 금지)
