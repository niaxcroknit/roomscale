"""앱 아이콘(안드로이드 런처, 스플래시)과 스토어 아이콘(512)을 그려요. 사용법: python3 tools/make_icons.py"""
import os
from playwright.sync_api import sync_playwright

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
res = os.path.join(root, 'android', 'app', 'src', 'main', 'res')
store = os.path.join(root, 'store')
os.makedirs(store, exist_ok=True)

BG = '#e4e8eb'      # 아이콘 바탕 (연한 회색)
WALL = '#3d464d'    # 벽
LINE = '#5b656c'    # 가구·문 선
FUR = '#c9d0d5'     # 가구
FLOOR = '#fbfbfc'   # 바닥
DIM = '#7d878d'     # 치수선

def plan(mono=False):
    """108×108 캔버스 안, 가운데 66 안전 영역에 들어가는 평면도 그림"""
    w = '#fff' if mono else WALL; l = '#fff' if mono else LINE; d = '#fff' if mono else DIM
    floor = '' if mono else f'<rect x="28" y="31" width="52" height="47" fill="{FLOOR}"/>'
    fur = 'none' if mono else FUR
    return f'''{floor}
  <rect x="31.5" y="46.5" width="17" height="28" rx="1.2" fill="{fur}" stroke="{l}" stroke-width="1.8"/>
  <line x1="31.5" y1="51" x2="48.5" y2="51" stroke="{l}" stroke-width="1.4"/>
  <rect x="53" y="34.5" width="23.5" height="10" rx="1" fill="{fur}" stroke="{l}" stroke-width="1.8"/>
  <path d="M56 78 L56 62.5 M56 62.5 A15.5 15.5 0 0 1 71.5 78" fill="none" stroke="{l}" stroke-width="1.8" stroke-linecap="round"/>
  <path d="M56 78 H28 V31 H80 V78 H71.5" fill="none" stroke="{w}" stroke-width="4.2" stroke-linejoin="miter" stroke-linecap="square"/>
  <path d="M28 24.5 H80 M28 21.8 V27.2 M80 21.8 V27.2" stroke="{d}" stroke-width="1.6" fill="none"/>'''

def svg(content, vb='0 0 108 108', bg=None, shape=None):
    clip = ''
    if shape == 'round':
        clip = '<clipPath id="c"><circle cx="54" cy="54" r="40"/></clipPath>'
    elif shape == 'square':
        clip = '<clipPath id="c"><rect x="14" y="14" width="80" height="80" rx="14"/></clipPath>'
    g_open = '<g clip-path="url(#c)">' if clip else '<g>'
    back = f'<rect x="-20" y="-20" width="160" height="160" fill="{bg}"/>' if bg else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"><defs>{clip}</defs>{g_open}{back}{content}</g></svg>'

jobs = []
dens = {'mdpi': 1, 'hdpi': 1.5, 'xhdpi': 2, 'xxhdpi': 3, 'xxxhdpi': 4}
for d, k in dens.items():
    jobs.append((svg(plan()), int(108 * k), f'{res}/mipmap-{d}/ic_launcher_foreground.png'))
    jobs.append((svg(plan(True)), int(108 * k), f'{res}/mipmap-{d}/ic_launcher_monochrome.png'))
    jobs.append((svg(plan(), '14 14 80 80', BG, 'square'), int(48 * k), f'{res}/mipmap-{d}/ic_launcher.png'))
    jobs.append((svg(plan(), '14 14 80 80', BG, 'round'), int(48 * k), f'{res}/mipmap-{d}/ic_launcher_round.png'))
# 스토어 아이콘: 512×512, 꽉 찬 정사각형 (모서리는 구글 플레이가 둥글게 깎음)
jobs.append((svg(plan(), '16 16 76 76', BG), 512, f'{store}/icon-512.png'))
# 예전 폰(안드로이드 11 이하) 시작 화면
for d, k in dens.items():
    for o, (W, H) in {'port': (320, 480), 'land': (480, 320)}.items():
        side = min(W, H) * 0.42
        x, y = (W - side) / 2, (H - side) / 2
        s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="#f0f1f2"/><svg x="{x}" y="{y}" width="{side}" height="{side}" viewBox="14 14 80 80">{plan()}</svg></svg>'
        jobs.append((s, (int(W * k), int(H * k)), f'{res}/drawable-{o}-{d}/splash.png'))
jobs.append((f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 320"><rect width="480" height="320" fill="#f0f1f2"/><svg x="173" y="93" width="134" height="134" viewBox="14 14 80 80">{plan()}</svg></svg>', (480, 320), f'{res}/drawable/splash.png'))

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    for s, size, out in jobs:
        W, H = size if isinstance(size, tuple) else (size, size)
        pg.set_viewport_size({'width': W, 'height': H})
        pg.set_content(f'<html><body style="margin:0;background:transparent">{s.replace("<svg ", f"<svg width={W} height={H} ", 1)}</body></html>')
        os.makedirs(os.path.dirname(out), exist_ok=True)
        pg.screenshot(path=out, omit_background=True)
    b.close()
print(len(jobs), 'images')
