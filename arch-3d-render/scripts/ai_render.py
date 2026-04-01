#!/usr/bin/env python3
"""
AI 건축 렌더링 이미지 생성 스크립트 (나노바나나 / Gemini API)

사용법:
  python3 ai_render.py --dxf input.dxf --style modern --view living-room --output render.png
  python3 ai_render.py --prompt "30평 아파트 거실, 모던 미니멀" --output render.png
  python3 ai_render.py --dxf input.dxf --model imagen-4.0-fast-generate-001 --output render.png

환경변수:
  GEMINI_IMAGE_API_KEY — Gemini API 키 (필수)
"""

import sys
import os
import json
import base64
import argparse
import urllib.request
import urllib.error

# ezdxf는 DXF 분석 시에만 필요
try:
    import ezdxf
    HAS_EZDXF = True
except ImportError:
    HAS_EZDXF = False


STYLE_PRESETS = {
    "modern": "modern minimalist interior, clean lines, white walls, natural light, contemporary furniture, architectural photography",
    "natural": "warm natural wood interior, indoor plants, organic textures, cozy atmosphere, soft lighting, hygge style",
    "industrial": "industrial loft style, exposed brick walls, concrete floor, metal fixtures, Edison bulbs, urban chic",
    "scandinavian": "Scandinavian interior design, light wood, soft textiles, muted pastel colors, simple functional furniture",
    "luxury": "luxury interior, marble surfaces, gold accents, crystal chandelier, premium materials, elegant",
    "korean": "Korean modern interior, ondol floor, natural materials, hanji lighting, warm minimal, hanok elements",
}

GEMINI_IMAGE_MODELS = [
    "gemini-2.5-flash-image",
    "nano-banana-pro-preview",
    "gemini-3.1-flash-image-preview",
    "gemini-3-pro-image-preview",
]

IMAGEN_MODELS = [
    "imagen-4.0-fast-generate-001",
    "imagen-4.0-generate-001",
    "imagen-4.0-ultra-generate-001",
]


def analyze_dxf(dxf_path):
    """DXF 파일에서 공간 정보 추출"""
    if not HAS_EZDXF:
        return None

    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()

    # 전체 바운딩 박스 계산
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')

    layers_found = set()
    room_labels = []

    for entity in msp:
        layers_found.add(entity.dxf.layer)

        if entity.dxftype() == "LWPOLYLINE":
            for p in entity.get_points(format="xy"):
                min_x = min(min_x, p[0])
                min_y = min(min_y, p[1])
                max_x = max(max_x, p[0])
                max_y = max(max_y, p[1])

        elif entity.dxftype() == "TEXT" or entity.dxftype() == "MTEXT":
            text = entity.dxf.text if entity.dxftype() == "TEXT" else entity.text
            room_labels.append(text)

    width_m = (max_x - min_x) / 1000
    height_m = (max_y - min_y) / 1000
    area_m2 = width_m * height_m
    area_pyeong = area_m2 / 3.3058

    info = {
        "width_m": round(width_m, 1),
        "height_m": round(height_m, 1),
        "area_m2": round(area_m2, 1),
        "area_pyeong": round(area_pyeong, 1),
        "layers": sorted(layers_found),
        "rooms": room_labels,
        "has_furniture": "FURNITURE" in layers_found,
        "has_windows": "WINDOW" in layers_found,
    }

    return info


def build_prompt(dxf_info, style, view, custom_prompt=""):
    """공간 분석 결과를 기반으로 이미지 생성 프롬프트 구성"""
    parts = []

    # 기본 품질 지시
    parts.append("Professional architectural interior photograph, high quality, 4K resolution")

    # 스타일
    style_text = STYLE_PRESETS.get(style, STYLE_PRESETS["modern"])
    parts.append(style_text)

    # DXF 분석 정보 반영
    if dxf_info:
        parts.append(f"{dxf_info['area_pyeong']:.0f}평 ({dxf_info['area_m2']:.0f}㎡) apartment")
        parts.append(f"room dimensions approximately {dxf_info['width_m']}m x {dxf_info['height_m']}m")

        if dxf_info["rooms"]:
            rooms = [r.split("\n")[0] for r in dxf_info["rooms"] if r.strip()]
            if rooms:
                parts.append(f"rooms: {', '.join(rooms[:5])}")

        if dxf_info["has_windows"]:
            parts.append("large windows with natural daylight")

    # 뷰 지정
    if view:
        parts.append(f"viewed from {view}, interior perspective")

    # 사용자 커스텀 프롬프트
    if custom_prompt:
        parts.append(custom_prompt)

    return ", ".join(parts)


def generate_gemini(api_key, model, prompt, output_path):
    """Gemini 계열 모델로 이미지 생성 (generateContent API)"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"]
        }
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    print(f"  모델: {model}")
    print(f"  프롬프트: {prompt[:100]}...")

    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read())

    candidates = result.get("candidates", [])
    for c in candidates:
        parts = c.get("content", {}).get("parts", [])
        for p in parts:
            if "inlineData" in p:
                img_bytes = base64.b64decode(p["inlineData"]["data"])
                with open(output_path, "wb") as f:
                    f.write(img_bytes)
                print(f"  ✅ 이미지 저장: {output_path} ({len(img_bytes):,} bytes)")
                return True
            elif "text" in p:
                print(f"  텍스트 응답: {p['text'][:200]}")

    print("  ❌ 이미지가 생성되지 않았습니다")
    return False


def generate_imagen(api_key, model, prompt, output_path):
    """Imagen 모델로 이미지 생성 (predict API)"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:predict?key={api_key}"

    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {"sampleCount": 1}
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    print(f"  모델: {model}")
    print(f"  프롬프트: {prompt[:100]}...")

    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read())

    predictions = result.get("predictions", [])
    for pred in predictions:
        if "bytesBase64Encoded" in pred:
            img_bytes = base64.b64decode(pred["bytesBase64Encoded"])
            with open(output_path, "wb") as f:
                f.write(img_bytes)
            print(f"  ✅ 이미지 저장: {output_path} ({len(img_bytes):,} bytes)")
            return True

    print("  ❌ 이미지가 생성되지 않았습니다")
    return False


def main():
    parser = argparse.ArgumentParser(description="AI 건축 렌더링 이미지 생성")
    parser.add_argument("--dxf", help="입력 DXF 파일 경로")
    parser.add_argument("--prompt", help="직접 프롬프트 입력 (DXF 없이)")
    parser.add_argument("--style", default="modern",
                        choices=list(STYLE_PRESETS.keys()),
                        help="인테리어 스타일")
    parser.add_argument("--view", default="living room entrance",
                        help="카메라 뷰 위치")
    parser.add_argument("--model", default="gemini-2.5-flash-image",
                        help="사용할 모델")
    parser.add_argument("--output", default="ai_render.png",
                        help="출력 이미지 경로")
    parser.add_argument("--api-key", help="API 키 (환경변수 대체)")

    args = parser.parse_args()

    # API 키
    api_key = args.api_key or os.environ.get("GEMINI_IMAGE_API_KEY", "")
    if not api_key:
        print("❌ API 키가 필요합니다. --api-key 또는 GEMINI_IMAGE_API_KEY 환경변수를 설정하세요.")
        sys.exit(1)

    # DXF 분석
    dxf_info = None
    if args.dxf:
        print(f"DXF 분석 중: {args.dxf}")
        dxf_info = analyze_dxf(args.dxf)
        if dxf_info:
            print(f"  크기: {dxf_info['width_m']}m x {dxf_info['height_m']}m ({dxf_info['area_pyeong']:.0f}평)")
            print(f"  방: {', '.join(dxf_info['rooms'][:5])}")

    # 프롬프트 생성
    if args.prompt:
        prompt = args.prompt
    else:
        prompt = build_prompt(dxf_info, args.style, args.view)

    print(f"\n생성 프롬프트:\n  {prompt}\n")

    # 모델 선택 후 생성
    try:
        if args.model in IMAGEN_MODELS:
            success = generate_imagen(api_key, args.model, prompt, args.output)
        else:
            success = generate_gemini(api_key, args.model, prompt, args.output)

        if success:
            print(f"\n✅ 렌더링 완료: {os.path.abspath(args.output)}")
        else:
            print(f"\n❌ 렌더링 실패")
            sys.exit(1)

    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"\n❌ API 오류 (HTTP {e.code}):")
        try:
            err = json.loads(body)
            print(f"  {err.get('error', {}).get('message', body[:300])}")
        except json.JSONDecodeError:
            print(f"  {body[:300]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
