#!/usr/bin/env python3
"""
DXF → Blender 3D 변환 및 렌더링 스크립트

사용법:
  blender -b -P dxf_to_blender.py -- input.dxf output.png [--height 2700] [--view eye|top|corner|bird]

Blender 헤드리스 모드로 실행. DXF 파일의 벽체/문/창을 3D로 변환하고 렌더링.
"""

import sys
import os
import math

# Blender 내부 실행 확인
try:
    import bpy
    import bmesh
    from mathutils import Vector
    IN_BLENDER = True
except ImportError:
    IN_BLENDER = False
    print("이 스크립트는 Blender 내부에서 실행해야 합니다:")
    print("  blender -b -P dxf_to_blender.py -- input.dxf output.png")
    sys.exit(1)

import ezdxf


def parse_args():
    """Blender -- 이후의 인자 파싱"""
    argv = sys.argv
    if "--" in argv:
        args = argv[argv.index("--") + 1:]
    else:
        args = []

    input_dxf = args[0] if len(args) > 0 else "floorplan.dxf"
    output_png = args[1] if len(args) > 1 else "render_output.png"

    wall_height = 2700  # mm
    view_type = "corner"

    for i, a in enumerate(args):
        if a == "--height" and i + 1 < len(args):
            wall_height = float(args[i + 1])
        elif a == "--view" and i + 1 < len(args):
            view_type = args[i + 1]

    return input_dxf, output_png, wall_height, view_type


def clear_scene():
    """기존 오브젝트 모두 삭제"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    for collection in bpy.data.collections:
        bpy.data.collections.remove(collection)


def create_materials():
    """건축 재질 생성"""
    materials = {}

    # 벽 재질
    mat = bpy.data.materials.new("Wall")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.95, 0.93, 0.88, 1)
    bsdf.inputs["Roughness"].default_value = 0.8
    materials["WALL"] = mat

    # 내벽
    mat = bpy.data.materials.new("InnerWall")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.92, 0.90, 0.85, 1)
    bsdf.inputs["Roughness"].default_value = 0.8
    materials["WALL_INNER"] = mat

    # 바닥 (나무 느낌)
    mat = bpy.data.materials.new("Floor")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.65, 0.45, 0.25, 1)
    bsdf.inputs["Roughness"].default_value = 0.4
    materials["FLOOR"] = mat

    # 천장
    mat = bpy.data.materials.new("Ceiling")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1)
    materials["CEILING"] = mat

    # 창문 (유리)
    mat = bpy.data.materials.new("Glass")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.8, 0.9, 1.0, 0.3)
    bsdf.inputs["Roughness"].default_value = 0.0
    bsdf.inputs["Alpha"].default_value = 0.3
    mat.blend_method = 'BLEND' if hasattr(mat, 'blend_method') else None
    materials["WINDOW"] = mat

    return materials


def polyline_to_wall(msp, layer, height, thickness, materials):
    """LWPOLYLINE 엔티티를 3D 벽체로 변환"""
    objects = []
    entities = list(msp.query(f"LWPOLYLINE[layer=='{layer}']"))

    for idx, entity in enumerate(entities):
        points = list(entity.get_points(format="xy"))
        if len(points) < 2:
            continue

        # mm → m 변환 (Blender 단위)
        scale = 0.001
        h = height * scale
        t = thickness * scale

        mesh = bpy.data.meshes.new(f"{layer}_{idx}")
        obj = bpy.data.objects.new(f"{layer}_{idx}", mesh)
        bpy.context.collection.objects.link(obj)

        bm = bmesh.new()

        for i in range(len(points) - 1):
            x1, y1 = points[i][0] * scale, points[i][1] * scale
            x2, y2 = points[i + 1][0] * scale, points[i + 1][1] * scale

            # 벽 방향 벡터
            dx = x2 - x1
            dy = y2 - y1
            length = math.sqrt(dx * dx + dy * dy)
            if length < 0.001:
                continue

            # 법선 벡터 (두께 방향)
            nx = -dy / length * t
            ny = dx / length * t

            # 4개의 바닥 꼭짓점
            v1 = bm.verts.new((x1, y1, 0))
            v2 = bm.verts.new((x2, y2, 0))
            v3 = bm.verts.new((x2 + nx, y2 + ny, 0))
            v4 = bm.verts.new((x1 + nx, y1 + ny, 0))

            # 4개의 천장 꼭짓점
            v5 = bm.verts.new((x1, y1, h))
            v6 = bm.verts.new((x2, y2, h))
            v7 = bm.verts.new((x2 + nx, y2 + ny, h))
            v8 = bm.verts.new((x1 + nx, y1 + ny, h))

            # 면 생성
            try:
                bm.faces.new([v1, v2, v6, v5])  # 앞면
                bm.faces.new([v3, v4, v8, v7])  # 뒷면
                bm.faces.new([v1, v4, v8, v5])  # 왼쪽
                bm.faces.new([v2, v3, v7, v6])  # 오른쪽
                bm.faces.new([v5, v6, v7, v8])  # 윗면
                bm.faces.new([v1, v2, v3, v4])  # 아랫면
            except ValueError:
                pass

        bm.to_mesh(mesh)
        bm.free()

        # 재질 적용
        mat_key = "WALL" if "WALL" in layer.upper() else layer.upper()
        if mat_key in materials:
            obj.data.materials.append(materials[mat_key])

        objects.append(obj)

    return objects


def create_floor(msp, materials):
    """바닥 생성 (외벽 기준)"""
    for entity in msp.query("LWPOLYLINE[layer=='WALL']"):
        points = list(entity.get_points(format="xy"))
        if len(points) < 3:
            continue

        scale = 0.001
        mesh = bpy.data.meshes.new("Floor")
        obj = bpy.data.objects.new("Floor", mesh)
        bpy.context.collection.objects.link(obj)

        bm = bmesh.new()
        verts = []
        for p in points:
            v = bm.verts.new((p[0] * scale, p[1] * scale, 0))
            verts.append(v)

        if len(verts) >= 3:
            # 중복 제거 (닫힌 폴리라인)
            if verts[0].co == verts[-1].co:
                verts = verts[:-1]
            try:
                bm.faces.new(verts)
            except ValueError:
                pass

        bm.to_mesh(mesh)
        bm.free()

        if "FLOOR" in materials:
            obj.data.materials.append(materials["FLOOR"])

        return obj
    return None


def setup_lighting():
    """건축 렌더링용 조명 설정"""
    # 태양광
    sun_data = bpy.data.lights.new("Sun", type='SUN')
    sun_data.energy = 3.0
    sun_data.color = (1.0, 0.98, 0.95)
    sun_obj = bpy.data.objects.new("Sun", sun_data)
    bpy.context.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = (math.radians(45), math.radians(15), math.radians(135))

    # 환경 조명 (HDRI 대체)
    world = bpy.data.worlds.get("World")
    if world is None:
        world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.7, 0.8, 1.0, 1)
        bg.inputs["Strength"].default_value = 0.5


def setup_camera(view_type, bounds):
    """카메라 설정"""
    cam_data = bpy.data.cameras.new("Camera")
    cam_obj = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # 바운딩 박스 중심
    cx = (bounds["min_x"] + bounds["max_x"]) / 2
    cy = (bounds["min_y"] + bounds["max_y"]) / 2
    width = bounds["max_x"] - bounds["min_x"]
    height = bounds["max_y"] - bounds["min_y"]
    max_dim = max(width, height)

    if view_type == "top":
        cam_obj.location = (cx, cy, max_dim * 1.5)
        cam_obj.rotation_euler = (0, 0, 0)
        cam_data.type = 'ORTHO'
        cam_data.ortho_scale = max_dim * 1.2

    elif view_type == "eye":
        # 아이레벨 (1.5m 높이)
        cam_obj.location = (bounds["min_x"] - 1, cy, 1.5)
        look_at = Vector((cx, cy, 1.5))
        direction = look_at - cam_obj.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam_obj.rotation_euler = rot_quat.to_euler()
        cam_data.lens = 24  # 광각

    elif view_type == "bird":
        # 조감도 (30도)
        dist = max_dim * 1.2
        cam_obj.location = (cx - dist * 0.5, cy - dist * 0.7, dist * 0.6)
        look_at = Vector((cx, cy, 1.0))
        direction = look_at - cam_obj.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam_obj.rotation_euler = rot_quat.to_euler()
        cam_data.lens = 35

    else:  # corner (기본)
        dist = max_dim * 1.0
        cam_obj.location = (bounds["min_x"] - dist * 0.3, bounds["min_y"] - dist * 0.3, max_dim * 0.8)
        look_at = Vector((cx, cy, 1.2))
        direction = look_at - cam_obj.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam_obj.rotation_euler = rot_quat.to_euler()
        cam_data.lens = 28

    return cam_obj


def setup_render(output_path):
    """렌더링 설정"""
    scene = bpy.context.scene
    # Blender 4.2+: BLENDER_EEVEE_NEXT, 4.0~4.1: BLENDER_EEVEE
    if bpy.app.version >= (4, 2, 0):
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
    else:
        scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.filepath = output_path
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = False


def get_bounds(doc):
    """DXF 바운딩 박스 계산 (m 단위)"""
    scale = 0.001
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')

    msp = doc.modelspace()
    for entity in msp.query("LWPOLYLINE"):
        for p in entity.get_points(format="xy"):
            x, y = p[0] * scale, p[1] * scale
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)

    return {"min_x": min_x, "min_y": min_y, "max_x": max_x, "max_y": max_y}


def main():
    input_dxf, output_png, wall_height, view_type = parse_args()

    print(f"=== DXF → 3D 렌더링 ===")
    print(f"  입력: {input_dxf}")
    print(f"  출력: {output_png}")
    print(f"  벽 높이: {wall_height}mm")
    print(f"  카메라: {view_type}")

    # 1. 씬 초기화
    clear_scene()

    # 2. DXF 로드
    doc = ezdxf.readfile(input_dxf)
    msp = doc.modelspace()

    # 3. 재질 생성
    materials = create_materials()

    # 4. 벽체 변환
    wall_thickness = {"WALL": 200, "WALL_INNER": 150}
    for layer, thickness in wall_thickness.items():
        objs = polyline_to_wall(msp, layer, wall_height, thickness, materials)
        print(f"  {layer}: {len(objs)}개 오브젝트 생성")

    # 5. 바닥 생성
    floor = create_floor(msp, materials)
    if floor:
        print(f"  바닥 생성 완료")

    # 6. 조명
    setup_lighting()

    # 7. 카메라
    bounds = get_bounds(doc)
    setup_camera(view_type, bounds)

    # 8. 렌더링 설정 및 실행
    output_path = os.path.abspath(output_png)
    setup_render(output_path)

    print(f"  렌더링 시작...")
    bpy.ops.render.render(write_still=True)
    print(f"  렌더링 완료: {output_path}")


if __name__ == "__main__":
    main()
