# 폴더 구조 패턴 참조 v3

## 번호 체계 원칙

```
00-09: 시스템 (에이전트 프롬프트, 프로토콜, 템플릿)
10-29: 인풋 원자료 (필요 시)
30-49: 작업 공간 (분석, 세션, 비교, 지식인덱스)
50-69: 산출물 (결정, 보고서)
70-89: 축적 (플레이북, 교훈)
90-99: 아카이브
```

번호 간격 10씩 → 나중에 중간 폴더 추가 가능.
**knowledge-index는 40번대** (자주 참조되는 작업 공간이므로).

---

## 표준 구조 (패턴 A: 분석·의사결정형)

부동산·투자·연구 등 반복적 판단이 필요한 프로젝트:

```
project-root/
├── .claude/
│   ├── commands/              ← 슬래시 커맨드 (.md 파일)
│   └── skills/                ← 도메인 전용 스킬
│
├── 00-system/
│   ├── prompts/               ← 에이전트 역할 파일
│   ├── protocols/
│   │   ├── council-protocol.md
│   │   ├── analysis-protocol.md
│   │   ├── independence-protocol.md
│   │   ├── data-pipeline-architecture.md
│   │   └── maintenance-protocol.md    ← v4 필수
│   └── templates/
│       ├── session-template.md
│       ├── analysis-template.md
│       ├── decision-template.md
│       └── comparison-template.md
│
├── RESEARCH/                  ← /deep-research 전용 세션 루트
│
├── 30-analysis/
│   ├── sessions/              ← YYYY-MM-DD-케이스명.md
│   ├── research/              ← 수동 리서치 산출물
│   └── comparisons/           ← 비교 분석 문서
│
├── 40-knowledge-index/
│   ├── KNOWLEDGE_INDEX.md
│   └── knowledge-base/
│
├── 50-decisions/
│   └── YYYY-MM-DD-[결정].md
│
├── 70-playbook/
│   ├── patterns/              ← 성공 패턴
│   ├── anti-patterns/         ← CARL 형식 실패 교훈
│   └── insights/              ← 시장 관찰 메모
│
├── 90-archive/
│
├── CLAUDE.md                  ← 목차 (100줄 이내)
├── AGENTS.md                  ← 에이전트 운영 규칙
├── README.md                  ← 사용자 가이드
├── WORKSPACE_TREE.md
├── progress.json              ← 세션 핸드오프 (장기 프로젝트)
└── feature-status.json        ← 기능 완료 현황 (장기 프로젝트)
```

**RESEARCH/ vs 30-analysis/research/ 구분:**
- `RESEARCH/`: `/deep-research` 커맨드가 자동 생성. 원본 리서치 세션 보관.
- `30-analysis/research/`: 수동으로 저장하는 요약형 리서치 산출물.

---

## 패턴 B: 건설·프로젝트 관리형

```
project-root/
├── .claude/
│   ├── commands/
│   └── skills/
├── 00-system/
│   ├── prompts/
│   ├── protocols/             ← maintenance-protocol.md 포함
│   └── templates/
├── 10-specs/                  ← 설계도, 시방서, 계약서
├── 20-planning/               ← 공정계획, 물량내역
├── 30-execution/
│   ├── daily-reports/
│   ├── issues/
│   └── changes/
├── 40-knowledge-index/
├── 50-cost/                   ← 원가 분석, 정산
├── 70-lessons/
│   ├── patterns/
│   ├── anti-patterns/         ← CARL 형식
│   └── insights/
├── 90-archive/
├── CLAUDE.md
├── AGENTS.md
├── README.md
└── WORKSPACE_TREE.md
```

---

## 패턴 C: 리서치·콘텐츠형

```
project-root/
├── .claude/
│   ├── commands/
│   └── skills/
├── 00-system/
│   ├── prompts/
│   ├── protocols/
│   └── templates/
├── RESEARCH/
├── 30-analysis/
│   ├── drafts/
│   └── reviews/
├── 40-knowledge-index/
├── 50-published/              ← 최종 산출물
├── 70-playbook/
│   ├── patterns/
│   ├── anti-patterns/
│   └── insights/
├── 90-archive/
├── CLAUDE.md
├── AGENTS.md
├── README.md
└── WORKSPACE_TREE.md
```

---

## 패턴 D: 장기 에이전트형 (v4 신규)

멀티 세션 자율 코딩, 장기 자동화 빌드 등:

```
project-root/
├── .claude/
│   ├── commands/
│   └── skills/
├── 00-system/
│   ├── prompts/
│   ├── protocols/
│   └── templates/
├── 30-workspace/              ← 작업 산출물
│   ├── sessions/
│   └── artifacts/
├── 40-knowledge-index/
├── 50-output/                 ← 최종 결과물
├── 70-playbook/
├── 90-archive/
│
├── CLAUDE.md
├── AGENTS.md
├── README.md
├── WORKSPACE_TREE.md
├── init.sh                    ← Initializer 생성 (환경 설정 스크립트)
├── progress.json              ← 세션 핸드오프 (필수)
└── feature-status.json        ← 기능 완료 현황 (필수)
```

**패턴 D의 특징:**
- progress.json / feature-status.json이 **필수**
- init.sh로 환경 초기화 자동화
- Initializer / Operating Agent 분리 적용

---

## 맞춤 설계 가이드

1. 핵심 흐름 동사 나열 (입력→분석→결정→기록)
2. 동사 → 폴더 변환 (30-analysis, 50-decisions, 70-playbook)
3. 시스템(00)과 아카이브(90)는 항상 포함
4. knowledge-index는 반드시 40번대 배치
5. .claude/commands/와 .claude/skills/ 항상 포함
6. RESEARCH/는 deep-research 기능 사용 시 포함
7. 총 최상위 폴더 수 8개 이내 권장
8. **장기 프로젝트라면 progress.json + feature-status.json 포함**
9. **maintenance-protocol.md는 모든 패턴에서 필수**
