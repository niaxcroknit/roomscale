"""GitHub Pages(docs/)용 웹 버전을 만들어요: 첫 화면 = 앱, privacy-policy.html = 개인정보처리방침.
사용법: python3 tools/make_docs.py   (make_www.py를 먼저 돌린 뒤)
"""
import os, shutil, json
from PIL import Image, ImageDraw

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
www, docs = os.path.join(root, 'www'), os.path.join(root, 'docs')
shutil.rmtree(docs, ignore_errors=True)
shutil.copytree(os.path.join(www, 'fonts'), os.path.join(docs, 'fonts'))
s = open(os.path.join(www, 'index.html'), encoding='utf-8').read()

# 일반 웹에서는 백업 파일을 바로 내려받게 (Claude·앱이 아닐 때)
old = "  try{ await navigator.clipboard.writeText(data);"
assert s.count(old) == 1
s = s.replace(old, """  if (!window.claude){ const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([data], {type:'application/json'})); a.download = name;
    document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 5000); toast('백업 파일을 저장했어요'); return }
""" + old)
# 공유 미리보기·검색용 설명, 개인정보처리방침 링크
SITE = 'https://niaxcroknit.github.io/roomscale/'
DESC = '잰 치수 그대로 방에 가구를 놓아 보고, 옷장 속 수납까지 미리 맞춰 보는 배치도'
HEAD = f'''<meta name="color-scheme" content="light">
<meta name="description" content="{DESC}">
<meta name="theme-color" content="#f0f1f2">
<link rel="icon" href="favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="icons/favicon-32.png">
<link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<link rel="manifest" href="manifest.webmanifest">
<meta name="apple-mobile-web-app-title" content="룸 스케일">
<meta name="mobile-web-app-capable" content="yes">
<meta property="og:type" content="website">
<meta property="og:site_name" content="룸 스케일">
<meta property="og:title" content="룸 스케일 - 실측 가구 배치·수납 정리">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="{SITE}">
<meta property="og:image" content="{SITE}icons/og-image.png">
<meta property="og:image:width" content="1024">
<meta property="og:image:height" content="500">
<meta name="twitter:card" content="summary_large_image">'''
assert s.count('<meta name="color-scheme" content="light">') == 1
s = s.replace('<meta name="color-scheme" content="light">', HEAD, 1)
s = s.replace('\n</body></html>', '\n<p style="text-align:center;font:12px/1.6 sans-serif;color:#7a848a;margin:0 0 24px"><a href="privacy-policy.html" style="color:inherit">개인정보처리방침</a></p>\n</body></html>', 1)
open(os.path.join(docs, 'index.html'), 'w', encoding='utf-8').write(s)
pp = open(os.path.join(root, 'store', 'privacy-policy.html'), encoding='utf-8').read()
pp = pp.replace('<title>', '<link rel="icon" href="favicon.ico" sizes="any"><link rel="apple-touch-icon" href="icons/apple-touch-icon.png">\n<title>', 1)
open(os.path.join(docs, 'privacy-policy.html'), 'w', encoding='utf-8').write(pp)
open(os.path.join(docs, '.nojekyll'), 'w').close()

# ---------- 아이콘: 브라우저 탭, 홈 화면에 추가, 링크 미리보기 ----------
icons = os.path.join(docs, 'icons'); os.makedirs(icons, exist_ok=True)
sq = Image.open(os.path.join(root, 'store', 'icon-512.png')).convert('RGBA')  # 꽉 찬 정사각형 아이콘
def rounded(img, size, r=0.22):
    im = img.resize((size, size), Image.LANCZOS); m = Image.new('L', (size * 4, size * 4), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size * 4 - 1, size * 4 - 1], radius=int(size * 4 * r), fill=255)
    out = Image.new('RGBA', (size, size), (0, 0, 0, 0)); out.paste(im, (0, 0), m.resize((size, size), Image.LANCZOS)); return out
for n in (16, 32, 48): rounded(sq, n).save(os.path.join(icons, f'favicon-{n}.png'))
rounded(sq, 48).save(os.path.join(docs, 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)])
sq.convert('RGB').resize((180, 180), Image.LANCZOS).save(os.path.join(icons, 'apple-touch-icon.png'))  # 아이폰은 모서리를 알아서 둥글게
for n in (192, 512):
    rounded(sq, n).save(os.path.join(icons, f'icon-{n}.png'))
    sq.convert('RGB').resize((n, n), Image.LANCZOS).save(os.path.join(icons, f'maskable-{n}.png'))
Image.open(os.path.join(root, 'store', 'feature-graphic-1024x500.png')).convert('RGB').save(os.path.join(icons, 'og-image.png'))
json.dump({'name': '룸 스케일', 'short_name': '룸 스케일', 'lang': 'ko', 'start_url': './', 'scope': './', 'display': 'standalone',
           'background_color': '#f0f1f2', 'theme_color': '#f0f1f2',
           'description': '잰 치수 그대로 방에 가구를 놓아 보고, 옷장 속 수납까지 미리 맞춰 보는 배치도',
           'icons': [{'src': 'icons/icon-192.png', 'sizes': '192x192', 'type': 'image/png'}, {'src': 'icons/icon-512.png', 'sizes': '512x512', 'type': 'image/png'},
                     {'src': 'icons/maskable-192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'maskable'}, {'src': 'icons/maskable-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'}]},
          open(os.path.join(docs, 'manifest.webmanifest'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('docs/ ready')
