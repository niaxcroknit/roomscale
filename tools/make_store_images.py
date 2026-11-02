"""스토어 등록 이미지: 휴대폰 스크린샷 1080×1920 5장, 그래픽 이미지 1024×500. 사용법: python3 tools/make_store_images.py"""
import os, base64
from playwright.sync_api import sync_playwright
from PIL import Image

def show(page, html):
    tmp = os.path.join(root, 'www', '_compose.html'); open(tmp, 'w', encoding='utf-8').write(html); page.goto('file://' + tmp); os.remove(tmp)

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
store = os.path.join(root, 'store'); shots = os.path.join(store, 'screenshots'); os.makedirs(shots, exist_ok=True)
url = 'file://' + os.path.join(root, 'www', 'index.html')
fontcss = 'file://' + os.path.join(root, 'www', 'fonts', 'fonts.css')

SCENES = [
    ('01-room', '실측 그대로', '방 크기와 가구 치수를 넣으면<br>비율 그대로 배치해 봐요',
     "()=>{ S.example=false; sel=S.furniture.find(f=>f.name==='침대 (슈퍼싱글)').id; renderAll() }", 0),
    ('02-inner', '가구 속까지', '옷장 칸을 나누고 리빙박스가<br>들어가는지 미리 넣어 봐요',
     "()=>{ S.example=false; const w=S.furniture.find(f=>f.name==='옷장'); sel=w.id; view='inner'; selBox=w.boxes.find(b=>b.name==='속옷 바구니').id; renderAll() }", 0),
    ('03-fit', '몇 개 들어갈까', '수납함 크기를 넣으면<br>칸마다 몇 개 들어가는지 알려줘요',
     "()=>{ S.example=false; const w=S.furniture.find(f=>f.name==='3단 수납장'); sel=w.id; view='inner'; selBox=null; selCell=null; renderAll(); document.getElementById('nb-name').value='리빙박스 S'; }", 'calc'),
    ('04-compare', 'A안 B안 비교', '배치안을 여러 개 만들고<br>나란히 놓고 골라요',
     "()=>{ S.example=false; S.name='A안'; const q=clone(S); q.id=uid(); q.name='B안 (침대 창가)'; const F=n=>q.furniture.find(f=>f.name===n); Object.assign(F('침대 (슈퍼싱글)'),{x:230,y:90,rot:0}); Object.assign(F('ㄱ자 책상'),{x:0,y:0,rot:0,flip:false,w:150,d:130}); Object.assign(F('코너렉'),{x:300,y:0,rot:90}); Object.assign(F('옷장'),{x:0,y:232,rot:180}); Object.assign(F('3단 수납장'),{x:160,y:0,rot:0}); STORE.plans.push(q); const st=document.createElement('style'); st.textContent='.compare{grid-template-columns:1fr 1fr!important;gap:8px!important}.cmpcol select{font-size:12px!important;padding:6px!important}'; document.head.appendChild(st); view='compare'; cmpIds=[S.id,q.id]; renderAll() }", 0),
    ('05-door', '문도 창문도', '문이 열리는 자리와 통로 폭까지<br>한눈에 확인해요',
     "()=>{ S.example=false; selOpen=S.room.openings[0].id; sel=S.furniture.find(f=>f.name==='옷장').id; renderAll() }", 0),
]

def b64(path):
    return 'data:image/png;base64,' + base64.b64encode(open(path, 'rb').read()).decode()

with sync_playwright() as p:
    b = p.chromium.launch()
    for name, title, sub, js, scroll in SCENES:
        pg = b.new_page(viewport={'width': 360, 'height': 560}, device_scale_factor=3)
        pg.goto(url); pg.wait_for_timeout(400)
        pg.evaluate("()=>{ try{ localStorage.clear() }catch(e){} }"); pg.reload(); pg.wait_for_timeout(400)
        pg.evaluate(js); pg.wait_for_timeout(200)
        if scroll == 'calc':
            pg.evaluate("()=>{ const s=document.querySelector('#nb-name').closest('section'); renderCalc(); window.scrollTo(0, s.getBoundingClientRect().top + scrollY - 10) }")
        else:
            pg.evaluate("()=>window.scrollTo(0,0)")
        pg.wait_for_timeout(200)
        raw = os.path.join(shots, f'_{name}.png'); pg.screenshot(path=raw); pg.close()
        # 위에 큰 글씨 설명 + 아래 앱 화면 (폰 테두리 느낌)
        comp = b.new_page(viewport={'width': 1080, 'height': 1920})
        show(comp, f'''<html><head><link rel="stylesheet" href="{fontcss}"><style>
          body{{margin:0;width:1080px;height:1920px;background:#e4e8eb;font-family:"IBM Plex Sans KR",sans-serif;overflow:hidden}}
          .cap{{height:330px;display:flex;flex-direction:column;justify-content:center;padding:0 90px;gap:18px}}
          h1{{margin:0;font-size:84px;font-weight:600;color:#2f373d;letter-spacing:-2px}}
          p{{margin:0;font-size:44px;line-height:1.4;color:#5b656c;letter-spacing:-1px}}
          .ph{{margin:0 auto;width:960px;height:1500px;border-radius:56px 56px 0 0;background:#3d464d;padding:22px 22px 0;box-sizing:border-box}}
          .ph img{{width:916px;height:1478px;object-fit:cover;object-position:top;border-radius:38px 38px 0 0;display:block}}
          </style></head><body><div class="cap"><h1>{title}</h1><p>{sub}</p></div><div class="ph"><img src="{b64(raw)}"></div></body></html>''')
        comp.wait_for_timeout(500)
        out = os.path.join(shots, f'{name}.png'); comp.screenshot(path=out); comp.close(); os.remove(raw)
        Image.open(out).convert('RGB').save(out)

    # 그래픽 이미지 1024×500 (알파 없음)
    pg = b.new_page(viewport={'width': 760, 'height': 640}, device_scale_factor=2)
    pg.goto(url); pg.wait_for_timeout(300); pg.evaluate("()=>{ try{ localStorage.clear() }catch(e){} }"); pg.reload(); pg.wait_for_timeout(300)
    pg.evaluate("()=>{ S.example=false; sel=null; renderAll() }"); pg.wait_for_timeout(200)
    plan_png = os.path.join(store, '_plan.png'); pg.locator('#cv').screenshot(path=plan_png); pg.close()
    icon = b64(os.path.join(store, 'icon-512.png'))
    fg = b.new_page(viewport={'width': 1024, 'height': 500})
    show(fg, f'''<html><head><link rel="stylesheet" href="{fontcss}"><style>
      body{{margin:0;width:1024px;height:500px;background:#e4e8eb;font-family:"IBM Plex Sans KR",sans-serif;overflow:hidden;display:flex;align-items:center}}
      .l{{width:470px;padding-left:64px;display:flex;flex-direction:column;gap:18px}}
      .l img{{width:96px;height:96px;border-radius:22px}}
      h1{{margin:0;font-size:52px;font-weight:600;color:#2f373d;letter-spacing:-1.5px;line-height:1.15}}
      p{{margin:0;font-size:25px;color:#5b656c;line-height:1.45}}
      .r{{flex:1;min-width:0;padding-right:40px;height:100%;display:flex;align-items:center;justify-content:center}}
      .card{{background:#fbfbfc;border-radius:22px;padding:14px;box-shadow:0 10px 40px rgb(0 0 0 / .08)}}
      .card img{{max-height:400px;max-width:470px;display:block}}
      </style></head><body><div class="l"><img src="{icon}"><h1>룸 스케일</h1><p>잰 치수 그대로 가구를 놓아 보고<br>가구 속 수납까지 미리 맞춰 봐요</p></div>
      <div class="r"><div class="card"><img src="{b64(plan_png)}"></div></div></body></html>''')
    fg.wait_for_timeout(500)
    out = os.path.join(store, 'feature-graphic-1024x500.png'); fg.screenshot(path=out); os.remove(plan_png)
    Image.open(out).convert('RGB').save(out)
    b.close()
print('done')
