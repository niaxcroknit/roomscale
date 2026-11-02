"""Claude 아티팩트 페이지(room-planner.html)를 안드로이드 앱용 www/index.html로 바꿔요.
사용법: python3 tools/make_www.py <room-planner.html 경로>
"""
import os, re, shutil, sys

src = sys.argv[1]
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
www = os.path.join(root, 'www')
os.makedirs(os.path.join(www, 'fonts'), exist_ok=True)
s = open(src, encoding='utf-8').read()

def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)

# 1) 글꼴: 인터넷 없이도 보이게 앱 안에 넣음
rep('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">',
    '<link rel="stylesheet" href="fonts/fonts.css">')
css = []
for pkg, weights in [('ibm-plex-sans-kr', ['400', '600']), ('ibm-plex-mono', ['400', '500'])]:
    base = os.path.join(root, 'node_modules', '@fontsource', pkg)
    for w in weights:
        c = open(os.path.join(base, f'{w}.css'), encoding='utf-8').read()
        for f in set(re.findall(r'\./files/([^)]+\.woff2)', c)):
            shutil.copy(os.path.join(base, 'files', f), os.path.join(www, 'fonts', f))
        c = re.sub(r'url\(\./files/([^)]+\.woff2)\) format\(\'woff2\'\),\s*url\([^)]+\.woff\) format\(\'woff\'\)', r"url(./\1) format('woff2')", c)
        c = c.replace('./files/', './')
        css.append(c)
open(os.path.join(www, 'fonts', 'fonts.css'), 'w', encoding='utf-8').write('\n'.join(css))

# 2) 화면 위·아래 시스템 바 높이 (안드로이드 15+ 화면 끝까지 그리기)
s = re.sub(r'env\(safe-area-inset-(top|bottom|left|right), 0px\)', r'var(--safe-area-inset-\1, env(safe-area-inset-\1, 0px))', s)

# 3) 앱 전용 동작
rep("const T = 1.8; // 선반·칸막이 두께 cm", """const APP = !!(window.Capacitor && Capacitor.isNativePlatform && Capacitor.isNativePlatform()); // 안드로이드 앱 안인지
const T = 1.8; // 선반·칸막이 두께 cm""")
rep("function syncText(long){", """function syncText(long){
  if (APP) return long ? '배치안은 이 폰에 자동으로 저장돼요. 앱을 지우거나 폰을 바꾸면 사라지니, 가끔 "백업 파일 저장"으로 따로 보관해 두세요.' : '이 폰에 저장됨';""")
rep("async function exportBackup(){\n  const data = JSON.stringify({app:'룸 스케일', version:2, exportedAt:new Date().toISOString(), plans:STORE.plans}, null, 1);\n  const d = new Date(), name = `룸스케일_백업_${d.getFullYear()}${String(d.getMonth()+1).padStart(2,'0')}${String(d.getDate()).padStart(2,'0')}.json`;",
    """async function exportBackup(){
  const data = JSON.stringify({app:'룸 스케일', version:2, exportedAt:new Date().toISOString(), plans:STORE.plans}, null, 1);
  const d = new Date(), name = `룸스케일_백업_${d.getFullYear()}${String(d.getMonth()+1).padStart(2,'0')}${String(d.getDate()).padStart(2,'0')}.json`;
  if (APP){ // 앱: 파일을 만든 뒤 공유 창으로 드라이브·카톡·내 파일 등에 보관
    try{
      const P = Capacitor.Plugins, fname = name.replace(/[^\\w.가-힣-]/g, '_');
      await P.Filesystem.writeFile({path:fname, data, directory:'CACHE', encoding:'utf8'});
      const {uri} = await P.Filesystem.getUri({path:fname, directory:'CACHE'});
      await P.Share.share({title:'배치도 백업 파일', text:'룸 스케일 백업', files:[uri], dialogTitle:'백업 파일 보관할 곳 고르기'});
    }catch(e){ if (!/cancel/i.test(String(e && (e.message || e)))) toast('백업 파일을 만들지 못했어요. 다시 눌러 주세요') }
    return;
  }""")

# 4) 뒤로가기: 열린 창 닫기 → 방 배치로 → 앱 닫기
rep("\nrenderAll();\ninitCloud();\n</script>", """
if (APP){
  Capacitor.Plugins.App.addListener('backButton', () => {
    if (mgr.open){ mgr.open = false; renderMgr(); return }
    if (view !== 'room'){ view = 'room'; selBox = null; zoom = 1; renderAll(); return }
    if (selOpen){ selOpen = null; renderAll(); return }
    Capacitor.Plugins.App.minimizeApp ? Capacitor.Plugins.App.minimizeApp() : Capacitor.Plugins.App.exitApp();
  });
}
renderAll();
if (!APP) initCloud();
</script>""")

head = """<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="color-scheme" content="light">
<style>:root{color-scheme:light;box-sizing:border-box;padding-top:var(--safe-area-inset-top, env(safe-area-inset-top,0px));padding-bottom:var(--safe-area-inset-bottom, env(safe-area-inset-bottom,0px))}body{margin:0;padding:0}img{max-width:100%}[hidden]{display:none!important}
html{-webkit-tap-highlight-color:transparent}</style>
</head><body>
"""
# 앱은 밝은 화면으로 고정 (상태바 글자색과 맞춤)
s = re.sub(r'@media \(prefers-color-scheme: dark\)\{:root:not\(\[data-theme="light"\]\)\{.*?\}\}\n', '', s, count=1, flags=re.S)
open(os.path.join(www, 'index.html'), 'w', encoding='utf-8').write(head + s + '\n</body></html>\n')
print('www/index.html', len(s), 'chars;', len(os.listdir(os.path.join(www, 'fonts'))), 'font files')
