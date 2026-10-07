#!/usr/bin/env python3
"""Descarga recursos CC0 de Poly Haven (texturas PBR, muebles glTF y HDRI) y los optimiza
para embeberlos en el HTML: texturas a 512/1024 px JPG y modelos empaquetados como GLB con
texturas reducidas. Licencia de todos los recursos: CC0 (https://polyhaven.com/license).

Uso: python3 tools/fetch_assets.py   (requiere Pillow)
"""
import io
import json
import os
import struct
import urllib.request

from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'assets')
UA = {'User-Agent': 'Mozilla/5.0 casa-bariloche-asset-fetch'}

# textura -> (tamaño final, mapas)
TEXTURES = {
    'corrugated_iron_02': (512, ['nor_gl', 'Rough']),
    'oak_wood_planks': (1024, ['Diffuse', 'nor_gl', 'Rough']),
    'brushed_concrete': (512, ['Diffuse', 'nor_gl', 'Rough']),
    'japanese_cedar_planks': (512, ['Diffuse', 'nor_gl', 'Rough']),
    'leafy_grass': (512, ['Diffuse', 'nor_gl']),
    'gravel': (512, ['Diffuse', 'nor_gl']),
    'rough_linen': (512, ['Diffuse', 'nor_gl']),
    'painted_plaster_wall': (512, ['nor_gl']),
    'wood_floor_deck': (512, ['Diffuse', 'nor_gl', 'Rough']),
    'fine_grained_wood': (512, ['Diffuse', 'nor_gl']),
}
MODELS = {
    'Sofa_01': 512,
    'dining_chair_02': 512,
    'wooden_table_02': 512,
    'side_table_01': 512,
    'modern_ceiling_lamp_01': 256,
    'potted_plant_04': 512,
    'ceramic_vase_01': 256,
    'hanging_picture_frame_01': 256,
}
HDRI = 'alps_field'


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
        return r.read()


def files(asset):
    return json.loads(get(f'https://api.polyhaven.com/files/{asset}'))


def jpg(data, size):
    im = Image.open(io.BytesIO(data))
    if im.mode not in ('RGB', 'L'):
        im = im.convert('RGB')
    if max(im.size) > size:
        im = im.resize((size, int(size * im.size[1] / im.size[0])), Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, 'JPEG', quality=82, optimize=True)
    return b.getvalue()


def fetch_textures():
    os.makedirs(os.path.join(OUT, 'tex'), exist_ok=True)
    for name, (size, maps) in TEXTURES.items():
        f = files(name)
        for m in maps:
            url = f[m]['1k']['jpg']['url'] if size <= 1024 else f[m]['2k']['jpg']['url']
            out = os.path.join(OUT, 'tex', f'{name}_{m.lower()}.jpg')
            if not os.path.exists(out):
                open(out, 'wb').write(jpg(get(url), size))
            print('tex', os.path.basename(out), os.path.getsize(out) // 1024, 'KB')


def pack_glb(gltf, resources, tex_size):
    """Convierte glTF (json + .bin + imágenes) en un GLB autocontenido, reduciendo texturas."""
    bin_chunks = []
    offset = 0

    def push(data):
        nonlocal offset
        pad = (4 - (len(data) % 4)) % 4
        bin_chunks.append(data + b'\x00' * pad)
        start = offset
        offset += len(data) + pad
        return start

    # buffers -> un solo buffer
    buf_offsets = []
    for b in gltf['buffers']:
        buf_offsets.append(push(resources[b['uri']]))
    for bv in gltf['bufferViews']:
        bv['byteOffset'] = bv.get('byteOffset', 0) + buf_offsets[bv['buffer']]
        bv['buffer'] = 0
    for img in gltf.get('images', []):
        data = jpg(resources[img['uri']], tex_size)
        start = push(data)
        gltf['bufferViews'].append({'buffer': 0, 'byteOffset': start, 'byteLength': len(data)})
        img['bufferView'] = len(gltf['bufferViews']) - 1
        img['mimeType'] = 'image/jpeg'
        del img['uri']
    blob = b''.join(bin_chunks)
    gltf['buffers'] = [{'byteLength': len(blob)}]
    js = json.dumps(gltf, separators=(',', ':')).encode()
    js += b' ' * ((4 - len(js) % 4) % 4)
    total = 12 + 8 + len(js) + 8 + len(blob)
    return (struct.pack('<4sII', b'glTF', 2, total) + struct.pack('<I4s', len(js), b'JSON') + js
            + struct.pack('<I4s', len(blob), b'BIN\x00') + blob)


def fetch_models():
    os.makedirs(os.path.join(OUT, 'models'), exist_ok=True)
    for name, tex_size in MODELS.items():
        out = os.path.join(OUT, 'models', f'{name}.glb')
        if not os.path.exists(out):
            g = files(name)['gltf']['1k']['gltf']
            gltf = json.loads(get(g['url']))
            res = {k: get(v['url']) for k, v in g['include'].items()}
            open(out, 'wb').write(pack_glb(gltf, res, tex_size))
        print('glb', name, os.path.getsize(out) // 1024, 'KB')


def fetch_hdri():
    os.makedirs(os.path.join(OUT, 'hdri'), exist_ok=True)
    f = files(HDRI)
    hdr = os.path.join(OUT, 'hdri', f'{HDRI}_1k.hdr')
    if not os.path.exists(hdr):
        open(hdr, 'wb').write(get(f['hdri']['1k']['hdr']['url']))
    bg = os.path.join(OUT, 'hdri', f'{HDRI}_bg.jpg')
    if not os.path.exists(bg):
        open(bg, 'wb').write(jpg(get(f['tonemapped']['url']), 2048))
    print('hdri', os.path.getsize(hdr) // 1024, 'KB +', os.path.getsize(bg) // 1024, 'KB')


if __name__ == '__main__':
    fetch_textures()
    fetch_models()
    fetch_hdri()
    open(os.path.join(OUT, 'LICENCIA.md'), 'w').write(
        '# Recursos de terceros\n\nTexturas, modelos y HDRI de [Poly Haven](https://polyhaven.com), licencia CC0 '
        '(dominio público). Descargados y optimizados con `tools/fetch_assets.py`.\n\n'
        + '\n'.join(f'- {k}' for k in [*TEXTURES, *MODELS, HDRI]) + '\n')
