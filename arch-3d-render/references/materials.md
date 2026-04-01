# Blender 건축 재질 프리셋

## 목차
1. [벽면](#벽면)
2. [바닥재](#바닥재)
3. [천장](#천장)
4. [목재](#목재)
5. [석재/타일](#석재타일)
6. [금속](#금속)
7. [유리](#유리)
8. [패브릭](#패브릭)

---

## 벽면

### 화이트 벽지
```python
mat = bpy.data.materials.new("WhiteWall")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.95, 0.93, 0.88, 1)
bsdf.inputs["Roughness"].default_value = 0.8
bsdf.inputs["Specular IOR Level"].default_value = 0.1
```

### 콘크리트
```python
bsdf.inputs["Base Color"].default_value = (0.55, 0.53, 0.50, 1)
bsdf.inputs["Roughness"].default_value = 0.95
```

### 벽돌 (인더스트리얼)
```python
bsdf.inputs["Base Color"].default_value = (0.6, 0.3, 0.2, 1)
bsdf.inputs["Roughness"].default_value = 0.9
```

---

## 바닥재

### 원목 마루
```python
bsdf.inputs["Base Color"].default_value = (0.65, 0.45, 0.25, 1)
bsdf.inputs["Roughness"].default_value = 0.35
bsdf.inputs["Specular IOR Level"].default_value = 0.3
```

### 라이트 오크
```python
bsdf.inputs["Base Color"].default_value = (0.78, 0.65, 0.45, 1)
bsdf.inputs["Roughness"].default_value = 0.4
```

### 다크 월넛
```python
bsdf.inputs["Base Color"].default_value = (0.35, 0.22, 0.12, 1)
bsdf.inputs["Roughness"].default_value = 0.3
```

### 타일 (화이트)
```python
bsdf.inputs["Base Color"].default_value = (0.9, 0.9, 0.9, 1)
bsdf.inputs["Roughness"].default_value = 0.15
bsdf.inputs["Specular IOR Level"].default_value = 0.5
```

### 대리석
```python
bsdf.inputs["Base Color"].default_value = (0.92, 0.90, 0.88, 1)
bsdf.inputs["Roughness"].default_value = 0.1
bsdf.inputs["Specular IOR Level"].default_value = 0.5
```

---

## 천장

### 화이트 무광
```python
bsdf.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1)
bsdf.inputs["Roughness"].default_value = 0.95
bsdf.inputs["Specular IOR Level"].default_value = 0.02
```

---

## 목재

### 소나무 (밝은)
```python
bsdf.inputs["Base Color"].default_value = (0.82, 0.70, 0.48, 1)
bsdf.inputs["Roughness"].default_value = 0.5
```

### 체리목
```python
bsdf.inputs["Base Color"].default_value = (0.55, 0.28, 0.15, 1)
bsdf.inputs["Roughness"].default_value = 0.25
```

---

## 석재/타일

### 그레이 타일
```python
bsdf.inputs["Base Color"].default_value = (0.5, 0.5, 0.5, 1)
bsdf.inputs["Roughness"].default_value = 0.2
```

### 테라조
```python
bsdf.inputs["Base Color"].default_value = (0.85, 0.82, 0.78, 1)
bsdf.inputs["Roughness"].default_value = 0.15
```

---

## 금속

### 스테인리스
```python
bsdf.inputs["Base Color"].default_value = (0.8, 0.8, 0.8, 1)
bsdf.inputs["Metallic"].default_value = 1.0
bsdf.inputs["Roughness"].default_value = 0.15
```

### 블랙 메탈
```python
bsdf.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
bsdf.inputs["Metallic"].default_value = 1.0
bsdf.inputs["Roughness"].default_value = 0.3
```

### 골드
```python
bsdf.inputs["Base Color"].default_value = (1.0, 0.77, 0.34, 1)
bsdf.inputs["Metallic"].default_value = 1.0
bsdf.inputs["Roughness"].default_value = 0.2
```

---

## 유리

### 투명 유리
```python
mat.blend_method = 'BLEND'
bsdf.inputs["Base Color"].default_value = (0.9, 0.95, 1.0, 1)
bsdf.inputs["Roughness"].default_value = 0.0
bsdf.inputs["Alpha"].default_value = 0.1
bsdf.inputs["IOR"].default_value = 1.45
```

### 반투명 유리 (욕실)
```python
bsdf.inputs["Base Color"].default_value = (0.85, 0.9, 0.95, 1)
bsdf.inputs["Roughness"].default_value = 0.5
bsdf.inputs["Alpha"].default_value = 0.4
```

---

## 패브릭

### 소파 (그레이)
```python
bsdf.inputs["Base Color"].default_value = (0.4, 0.4, 0.42, 1)
bsdf.inputs["Roughness"].default_value = 0.9
bsdf.inputs["Sheen Weight"].default_value = 0.3
```

### 커튼 (화이트)
```python
bsdf.inputs["Base Color"].default_value = (0.95, 0.93, 0.90, 1)
bsdf.inputs["Roughness"].default_value = 0.85
bsdf.inputs["Alpha"].default_value = 0.7
```
