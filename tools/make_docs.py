"""GitHub Pages(docs/)용 웹 버전을 만들어요: 첫 화면 = 앱, privacy-policy.html = 개인정보처리방침.
사용법: python3 tools/make_docs.py   (make_www.py를 먼저 돌린 뒤)
"""
import os, shutil

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
s = s.replace('<meta name="color-scheme" content="light">', '<meta name="color-scheme" content="light">\n<meta name="description" content="룸 스케일 - 잰 치수 그대로 방에 가구를 놓아 보고, 옷장 속 수납까지 미리 맞춰 보는 배치도">', 1)
s = s.replace('\n</body></html>', '\n<p style="text-align:center;font:12px/1.6 sans-serif;color:#7a848a;margin:0 0 24px"><a href="privacy-policy.html" style="color:inherit">개인정보처리방침</a></p>\n</body></html>', 1)
open(os.path.join(docs, 'index.html'), 'w', encoding='utf-8').write(s)
shutil.copy(os.path.join(root, 'store', 'privacy-policy.html'), os.path.join(docs, 'privacy-policy.html'))
open(os.path.join(docs, '.nojekyll'), 'w').close()
print('docs/ ready')
