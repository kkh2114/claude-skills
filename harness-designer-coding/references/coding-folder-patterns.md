# 코딩 프로젝트 폴더 패턴 참조 v1

## 표준 구조: 풀스택 웹앱

```
project-root/
├── AGENTS.md                  ← 목차 (~100줄)
├── README.md                  ← 개발자 가이드
├── progress.json              ← 세션 핸드오프
├── feature-status.json        ← 기능 완료 현황
├── init.sh                    ← 환경 초기화 스크립트
│
├── docs/                      ← System of Record
│   ├── architecture.md        ← 레이어 구조, 의존성 규칙
│   ├── conventions.md         ← 코딩 컨벤션
│   ├── quality-grades.md      ← 도메인별 품질 등급
│   ├── testing-strategy.md    ← 테스트 전략
│   ├── review-protocol.md     ← 코드 리뷰 규칙
│   ├── design/                ← 도메인별 설계 문서
│   │   ├── auth.md
│   │   └── billing.md
│   └── exec-plans/            ← 실행 계획
│       ├── tech-debt-tracker.md
│       └── current-sprint.md
│
├── src/                       ← 소스 코드
│   ├── types/                 ← 순수 타입 정의
│   ├── config/                ← 설정
│   ├── domains/               ← 도메인별 로직
│   │   └── [domain]/
│   │       ├── repo.ts
│   │       ├── service.ts
│   │       └── __tests__/
│   ├── shared/                ← 공유 유틸리티
│   ├── providers/             ← 횡단 관심사
│   └── runtime/               ← 앱 진입점
│       └── ui/ (또는 api/)
│
├── tests/                     ← 통합/E2E 테스트
│   ├── integration/
│   └── e2e/
│
├── scripts/                   ← 도구 스크립트
│   ├── lint-layers.sh         ← 레이어 의존성 검증
│   └── check-structure.sh     ← 구조 테스트
│
├── .github/workflows/         ← CI/CD (또는 해당 CI 시스템)
│   └── ci.yml
│
├── .claude/ (또는 .codex/)    ← 에이전트 설정
│   ├── commands/
│   └── skills/
│
└── package.json / pyproject.toml / etc.
```

## API 서비스 변형

```
project-root/
├── AGENTS.md
├── docs/
├── src/
│   ├── types/
│   ├── config/
│   ├── domains/
│   ├── shared/
│   ├── providers/
│   └── runtime/           ← HTTP/gRPC 서버
├── tests/
├── scripts/
└── progress.json
```

## CLI 도구 변형

```
project-root/
├── AGENTS.md
├── docs/
├── src/
│   ├── types/
│   ├── config/
│   ├── core/              ← 비즈니스 로직
│   └── cli/               ← CLI 인터페이스
├── tests/
└── progress.json
```

## 핵심 원칙

1. docs/가 유일한 진실의 원천 (Google Docs나 Slack에 지식 두지 않기)
2. 테스트는 소스 옆(__tests__/)과 통합 테스트(tests/) 분리
3. scripts/에 검증 스크립트 (린터 + 구조 테스트)
4. 에이전트 설정(.claude/ 등)은 프로젝트 루트에
5. progress.json과 feature-status.json은 프로젝트 루트에
