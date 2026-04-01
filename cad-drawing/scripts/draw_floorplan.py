#!/usr/bin/env python3
"""
CAD Floor Plan Generator - ezdxf 기반 DXF 평면도 생성 스크립트

사용법:
  python3 draw_floorplan.py <json_spec_file> <output.dxf>
  
JSON 스펙 예시는 references/spec-format.md 참조
"""

import sys
import json
import math
import ezdxf
from ezdxf import units
from ezdxf.enums import TextEntityAlignment


# ── Layer 정의 ──────────────────────────────────────────
LAYERS = {
    "WALL":       {"color": 7, "lineweight": 50},   # 흰색, 굵은선
    "WALL-INT":   {"color": 7, "lineweight": 30},   # 내벽
    "DOOR":       {"color": 3, "lineweight": 18},    # 녹색
    "WINDOW":     {"color": 5, "lineweight": 18},    # 파랑
    "DIM":        {"color": 1, "lineweight": 13},    # 빨강
    "TEXT":       {"color": 7, "lineweight": 13},    # 텍스트
    "FURNITURE":  {"color": 8, "lineweight": 13},    # 회색
    "HATCH":      {"color": 253, "lineweight": 13},  # 옅은 회색
    "GRID":       {"color": 9, "lineweight": 13},    # 그리드
    "TITLEBLOCK": {"color": 7, "lineweight": 25},    # 도면틀
}


def setup_doc():
    """DXF 문서 초기화 + 레이어 설정"""
    doc = ezdxf.new("R2013")
    doc.units = units.MM
    
    for name, props in LAYERS.items():
        doc.layers.add(name, color=props["color"], lineweight=props["lineweight"])
    
    # 치수 스타일
    doc.dimstyles.new("ARCH", dxfattribs={
        "dimtxt": 150,      # 텍스트 높이
        "dimasz": 100,      # 화살표 크기
        "dimexo": 50,       # 보조선 오프셋
        "dimexe": 100,      # 보조선 연장
        "dimgap": 50,       # 텍스트 갭
    })
    
    return doc


def draw_wall(msp, x1, y1, x2, y2, thickness=200, layer="WALL"):
    """벽체 그리기 (두께 있는 사각형)"""
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx*dx + dy*dy)
    if length == 0:
        return
    
    # 법선 벡터 (벽 두께 방향)
    nx = -dy / length * thickness / 2
    ny = dx / length * thickness / 2
    
    points = [
        (x1 + nx, y1 + ny),
        (x2 + nx, y2 + ny),
        (x2 - nx, y2 - ny),
        (x1 - nx, y1 - ny),
    ]
    msp.add_lwpolyline(points, close=True, dxfattribs={"layer": layer})


def draw_door(msp, x, y, width=900, angle=0, swing="left"):
    """문 심볼 (스윙 아크 포함)"""
    import math as m
    rad = m.radians(angle)
    cos_a, sin_a = m.cos(rad), m.sin(rad)
    
    def rotate(px, py):
        return (x + px * cos_a - py * sin_a, y + px * sin_a + py * cos_a)
    
    # 문 개구부 (벽 끊기 라인)
    p1 = rotate(0, 0)
    p2 = rotate(width, 0)
    msp.add_line(p1, p2, dxfattribs={"layer": "DOOR"})
    
    # 스윙 아크
    if swing == "left":
        center = p1
        start_angle = angle
        end_angle = angle + 90
    else:
        center = p2
        start_angle = angle + 90
        end_angle = angle + 180
    
    msp.add_arc(center, radius=width, start_angle=start_angle, end_angle=end_angle,
                dxfattribs={"layer": "DOOR"})


def draw_window(msp, x1, y1, x2, y2, layer="WINDOW"):
    """창문 심볼 (이중선)"""
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx*dx + dy*dy)
    if length == 0:
        return
    
    nx = -dy / length * 60
    ny = dx / length * 60
    
    # 외부선
    msp.add_line((x1 + nx, y1 + ny), (x2 + nx, y2 + ny), dxfattribs={"layer": layer})
    msp.add_line((x1 - nx, y1 - ny), (x2 - nx, y2 - ny), dxfattribs={"layer": layer})
    # 중심선 (유리)
    msp.add_line((x1, y1), (x2, y2), dxfattribs={"layer": layer})


def draw_room_label(msp, x, y, name, area_sqm=None):
    """방 이름 + 면적 라벨"""
    msp.add_text(name, height=200, dxfattribs={"layer": "TEXT"}).set_placement(
        (x, y), align=TextEntityAlignment.MIDDLE_CENTER
    )
    if area_sqm:
        area_text = f"{area_sqm:.1f}㎡"
        msp.add_text(area_text, height=150, dxfattribs={"layer": "TEXT"}).set_placement(
            (x, y - 300), align=TextEntityAlignment.MIDDLE_CENTER
        )


def draw_dimension(msp, p1, p2, offset=500):
    """치수선"""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = math.sqrt(dx*dx + dy*dy)
    if length == 0:
        return
    
    # 치수선 위치 (오프셋)
    nx = -dy / length * offset
    ny = dx / length * offset
    
    dim_point = ((p1[0] + p2[0]) / 2 + nx, (p1[1] + p2[1]) / 2 + ny)
    
    dim = msp.add_linear_dim(
        base=dim_point,
        p1=p1,
        p2=p2,
        dimstyle="ARCH",
        override={"dimtxt": 150},
        dxfattribs={"layer": "DIM"}
    )
    dim.render()


def draw_title_block(msp, width=42000, height=29700, project="", title="평면도", scale="1:100", date=""):
    """A3 도면틀"""
    layer = "TITLEBLOCK"
    # 외곽선
    msp.add_lwpolyline(
        [(0, 0), (width, 0), (width, height), (0, height)],
        close=True, dxfattribs={"layer": layer}
    )
    
    # 타이틀 블록 (우측 하단)
    tb_w, tb_h = 8000, 4000
    tb_x = width - tb_w - 500
    tb_y = 500
    
    msp.add_lwpolyline(
        [(tb_x, tb_y), (tb_x + tb_w, tb_y), (tb_x + tb_w, tb_y + tb_h), (tb_x, tb_y + tb_h)],
        close=True, dxfattribs={"layer": layer}
    )
    
    # 구분선
    for i, ratio in enumerate([0.25, 0.5, 0.75]):
        y = tb_y + tb_h * ratio
        msp.add_line((tb_x, y), (tb_x + tb_w, y), dxfattribs={"layer": layer})
    
    # 텍스트
    cx = tb_x + tb_w / 2
    texts = [
        (project or "프로젝트명", tb_y + tb_h * 0.875),
        (title, tb_y + tb_h * 0.625),
        (f"축척: {scale}", tb_y + tb_h * 0.375),
        (date or "날짜", tb_y + tb_h * 0.125),
    ]
    for text, ty in texts:
        msp.add_text(text, height=150, dxfattribs={"layer": layer}).set_placement(
            (cx, ty), align=TextEntityAlignment.MIDDLE_CENTER
        )


def build_from_spec(spec, output_path):
    """JSON 스펙에서 DXF 생성"""
    doc = setup_doc()
    msp = doc.modelspace()
    
    # 도면틀
    tb = spec.get("title_block", {})
    if tb.get("enabled", True):
        draw_title_block(msp, 
            project=tb.get("project", ""),
            title=tb.get("title", "평면도"),
            scale=tb.get("scale", "1:100"),
            date=tb.get("date", ""))
    
    # 벽체
    for wall in spec.get("walls", []):
        draw_wall(msp, wall["x1"], wall["y1"], wall["x2"], wall["y2"],
                  thickness=wall.get("thickness", 200),
                  layer=wall.get("layer", "WALL"))
    
    # 문
    for door in spec.get("doors", []):
        draw_door(msp, door["x"], door["y"],
                  width=door.get("width", 900),
                  angle=door.get("angle", 0),
                  swing=door.get("swing", "left"))
    
    # 창문
    for win in spec.get("windows", []):
        draw_window(msp, win["x1"], win["y1"], win["x2"], win["y2"])
    
    # 방 라벨
    for room in spec.get("rooms", []):
        draw_room_label(msp, room["x"], room["y"], room["name"],
                       area_sqm=room.get("area"))
    
    # 치수선
    for dim in spec.get("dimensions", []):
        draw_dimension(msp, (dim["x1"], dim["y1"]), (dim["x2"], dim["y2"]),
                      offset=dim.get("offset", 500))
    
    # 가구 (사각형)
    for furn in spec.get("furniture", []):
        x, y = furn["x"], furn["y"]
        w, h = furn["width"], furn["height"]
        msp.add_lwpolyline(
            [(x, y), (x+w, y), (x+w, y+h), (x, y+h)],
            close=True, dxfattribs={"layer": "FURNITURE"}
        )
        if "name" in furn:
            msp.add_text(furn["name"], height=100, dxfattribs={"layer": "FURNITURE"}).set_placement(
                (x + w/2, y + h/2), align=TextEntityAlignment.MIDDLE_CENTER
            )
    
    doc.saveas(output_path)
    print(f"✅ DXF 저장 완료: {output_path}")
    return output_path


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 draw_floorplan.py <spec.json> <output.dxf>")
        sys.exit(1)
    
    with open(sys.argv[1], 'r') as f:
        spec = json.load(f)
    
    build_from_spec(spec, sys.argv[2])


if __name__ == "__main__":
    main()
