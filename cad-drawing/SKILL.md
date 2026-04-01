---
name: cad-drawing
description: Generate CAD floor plans and architectural drawings as DXF files using ezdxf (Python). Use when asked to draw, create, or generate floor plans (평면도), section views (단면도), elevation views (입면도), or any CAD/DXF drawings. Triggers on requests like "평면도 그려줘", "도면 만들어", "DXF 생성", "CAD drawing", "floor plan". Supports walls, doors, windows, dimensions, room labels, furniture, and title blocks. Output is AutoCAD-compatible .dxf file.
---

# CAD Drawing Skill

ezdxf 기반 DXF 도면 생성 스킬. AutoCAD/나노캐드 호환 .dxf 파일을 코드로 생성.

## 워크플로우

1. 고객 요구사항 파악 (평수, 방 수, 구성)
2. JSON 스펙 작성 (좌표 mm 단위)
3. `scripts/draw_floorplan.py` 실행하여 DXF 생성
4. 결과 파일 전달

## 스펙 작성 가이드

모든 좌표는 **mm 단위**. 좌하단 원점 기준.
스펙 포맷 상세: [references/spec-format.md](references/spec-format.md)
평면 템플릿 예시: [references/templates.md](references/templates.md)

## 실행 방법

```bash
# JSON 스펙 파일로 실행
python3 scripts/draw_floorplan.py spec.json output.dxf
```

또는 Python에서 직접:

```python
import json, sys
sys.path.insert(0, "<skill_dir>/scripts")
from draw_floorplan import build_from_spec

spec = { ... }  # JSON 스펙 딕셔너리
build_from_spec(spec, "output.dxf")
```

## 레이어 구조

- `WALL` — 외벽 (두께 200mm)
- `WALL-INT` — 내벽 (두께 100~150mm)
- `DOOR` — 문 (스윙 아크 포함)
- `WINDOW` — 창문 (이중선)
- `DIM` — 치수선
- `TEXT` — 방 이름, 면적 라벨
- `FURNITURE` — 가구 (사각형)
- `TITLEBLOCK` — 도면틀

## 평면도 설계 순서

1. 외벽 먼저 배치 (사각형 또는 ㄱ자)
2. 내벽으로 방 구획
3. 문/창문 배치 (벽 위 위치)
4. 방 라벨 + 면적 표기
5. 치수선 추가
6. 가구 배치 (선택)
7. 도면틀 설정

## 주의사항

- 벽 좌표는 중심선 기준 (두께는 양쪽으로 분배)
- 문은 벽에 개구부를 만들지 않음 → 벽을 문 위치에서 끊어서 그려야 함
- 1평 = 3.3㎡, 좌표 환산 시 참고
- 한국 건축 기준 치수는 references/spec-format.md 참조
