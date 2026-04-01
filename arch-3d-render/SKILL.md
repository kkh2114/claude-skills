---
name: arch-3d-render
description: "건축 3D 렌더링 스킬 (Blender + Gemini 이미지 생성). DXF 도면을 분석하여 Blender로 3D 모델을 자동 생성하고, 나노바나나(Gemini) API로 감성적 건축 렌더링 이미지를 생성한다. 사용 시점: (1) DXF 도면에서 3D 모델 생성, (2) 건축 3D 렌더링 이미지 생성, (3) 인테리어 시각화, (4) 고객 프레젠테이션용 이미지 제작, (5) 공간 디자인 시각화. NOT for: 애니메이션, 동영상 렌더링, 실시간 VR."
---

# 건축 3D 렌더링 스킬

DXF 도면 → Blender 3D 모델 → 렌더링 이미지 파이프라인.

## 환경

- Blender 4.1.0 (헤드리스): `/home/sudesign/.local/bin/blender`
- Python 3.12+, ezdxf 1.4.3+
- 나노바나나 API: Gemini 이미지 생성 (유료 플랜 필요)

## 2가지 렌더링 경로

### 경로 A: Blender 3D (정확한 구조 렌더링)
```
DXF 도면 → ezdxf로 파싱 → Blender Python으로 3D 생성 → EEVEE/Cycles 렌더링 → PNG
```
- 용도: 시공 검증, 구조 확인, 정확한 치수 반영
- 스크립트: `scripts/dxf_to_blender.py`

### 경로 B: 나노바나나 AI (감성적 렌더링)
```
DXF 도면 → 공간 분석 → 프롬프트 생성 → Gemini API → 렌더링 이미지
```
- 용도: 고객 프레젠테이션, 분위기 시각화, 제안서
- 스크립트: `scripts/ai_render.py`

## 경로 A: Blender 3D 워크플로우

### 기본 실행
```bash
blender -b -P scripts/dxf_to_blender.py -- input.dxf output.png
```

### DXF → 3D 변환 핵심 로직

```python
import bpy
import ezdxf

# 1. DXF 파싱 → 벽체 좌표 추출
doc = ezdxf.readfile("floorplan.dxf")
msp = doc.modelspace()

# 2. 벽체를 3D로 압출 (높이 2700mm)
for entity in msp.query("LWPOLYLINE[layer=='WALL']"):
    points = list(entity.get_points(format="xy"))
    # 폴리라인 → 메시 → 압출
    
# 3. 재질 적용
wall_mat = bpy.data.materials.new("Wall")
wall_mat.diffuse_color = (0.95, 0.93, 0.88, 1)  # 밝은 베이지

# 4. 조명 + 카메라 자동 설정
# 5. 렌더링 → PNG 출력
bpy.ops.render.render(write_still=True)
```

### Blender 벽체 높이 기준

| 공간 | 높이(mm) |
|------|---------|
| 일반 주거 | 2,400 ~ 2,700 |
| 상업 공간 | 3,000 ~ 4,000 |
| 복층 | 5,000+ |

### 카메라 프리셋

| 뷰 | 설명 |
|----|------|
| 탑뷰 | 위에서 내려다보기 (평면도 확인) |
| 아이레벨 | 사람 눈높이 (1500mm) 투시도 |
| 코너뷰 | 대각선 45° (공간감 극대화) |
| 버드아이 | 30° 각도 조감도 |

## 경로 B: 나노바나나 AI 워크플로우

### 지원 모델 (우선순위)

| 모델 | 용도 | 비용/장 |
|------|------|---------|
| `gemini-2.5-flash-image` | 빠른 생성 | ~$0.04 |
| `nano-banana-pro-preview` | 고품질 | ~$0.13 |
| `gemini-3.1-flash-image-preview` | 4K 지원 | ~$0.07~0.15 |
| `imagen-4.0-fast-generate-001` | 저렴한 대량 | ~$0.02 |

### 기본 실행
```bash
python3 scripts/ai_render.py --dxf input.dxf --style modern --view living-room
```

### 프롬프트 생성 전략

DXF에서 추출한 정보로 상세 프롬프트 자동 구성:

```
[공간 정보] 30평 아파트, 거실 5m x 4m, 남향
[스타일] 모던 미니멀, 화이트+우드톤
[가구] 3인 소파, 월넛 TV장, 라운드 커피테이블
[조명] 자연광 남향, 간접 조명
[뷰] 아이레벨, 입구에서 거실 방향
→ "Interior design photo, modern minimalist living room, 5m x 4m, 
   south-facing natural light, white walls, wood flooring, 
   3-seater gray sofa, walnut TV console, round coffee table,
   eye-level perspective from entrance, warm ambient lighting,
   architectural photography, 4K resolution"
```

### 스타일 프리셋

| 스타일 | 키워드 |
|--------|--------|
| 모던 미니멀 | clean lines, white, minimal furniture, natural light |
| 내추럴 우드 | warm wood tones, plants, organic textures, cozy |
| 인더스트리얼 | exposed brick, concrete, metal, loft style |
| 스칸디나비안 | hygge, light wood, soft textiles, muted colors |
| 럭셔리 | marble, gold accents, chandelier, premium materials |
| 한국 모던 | 온돌, 한옥 요소, 자연 소재, 한지 조명 |

## API 설정

나노바나나 API 키는 환경변수로 관리:
```bash
export GEMINI_IMAGE_API_KEY="your-api-key"
```

또는 OpenClaw 설정에서:
```json
{
  "skills": {
    "entries": {
      "arch-3d-render": {
        "apiKey": "your-gemini-api-key"
      }
    }
  }
}
```

## 상세 참조

- **Blender 변환 스크립트**: `scripts/dxf_to_blender.py` — DXF→3D 완전 자동화
- **AI 렌더링 스크립트**: `scripts/ai_render.py` — 나노바나나 API 연동
- **재질 라이브러리**: `references/materials.md` — Blender 재질 프리셋
