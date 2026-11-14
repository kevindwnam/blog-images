# 강조 표기: **볼드** __밑줄__ ==파란 볼드== ^^크게(19px 볼드)^^ !!노란 형광!!
# 세 번 복사 버전(① 제목 ② 대표이미지=첫 이미지, 업로드되어 대표 지정 가능 ③ 본문). 대표이미지는 imgdir에서 읽음. 인자: src 제목 기본URL out [imgdir]: python3 build_blog_paste2.py src.txt "제목" 이미지기본URL out.html
# src 표기는 build_blog_paste.py와 같음. ![](파일)은 기본URL/파일 로 연결(공개 주소여야 네이버가 받아감)
import sys,re,html,base64,io
from PIL import Image
src,title,base,out=sys.argv[1:5];imgdir=sys.argv[5] if len(sys.argv)>5 else '.';E=html.escape
rep=None
def datauri(fn):
    im=Image.open(f'{imgdir}/{fn}').convert('RGB')
    W=345
    im=im.resize((W,round(im.height*W/im.width)),Image.LANCZOS)
    b=io.BytesIO(); im.save(b,'JPEG',quality=92); return 'data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode()
P='<p style="font-style:normal;margin:0;font-size:16px;line-height:1.9;color:#222;">{}</p>';BLANK='<p style="font-style:normal;margin:0;font-size:16px;line-height:1.9;">&nbsp;</p>'
sent=lambda t:[x for x in re.split(r'(?<=[.?!])\s+(?=\S)',t.strip()) if x]
def fx(t):
    t=E(t)
    t=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',t)
    t=re.sub(r'__(.+?)__',r'<u>\1</u>',t)
    t=re.sub(r'==(.+?)==',r'<span style="color:#1f5fd6;font-weight:bold;">\1</span>',t)
    t=re.sub(r'\^\^(.+?)\^\^',r'<span style="font-size:19px;font-weight:bold;">\1</span>',t)
    t=re.sub(r'!!(.+?)!!',r'<span style="background-color:#fff1a8;">\1</span>',t)
    return t
o=[]
for line in open(src).read().split('\n'):
    line=line.rstrip()
    if not line: continue
    if line.startswith('![](') and rep is None: rep=datauri(line[4:-1]); continue
    if line.startswith('![]('): o+= [f'<p style="text-align:center;margin:0;"><img src="{base.rstrip("/")}/{line[4:-1]}" style="max-width:100%;"></p>',BLANK]
    elif line=='---': o.append('<hr style="border:0;border-top:1px solid #ddd;margin:40px 0;">')
    elif line.startswith('## '): o.append(f'<p style="font-style:normal;margin:0 0 6px;font-size:21px;font-weight:bold;color:#111;">{E(line[3:])}</p>')
    elif line.startswith('> '): o+=[f'<p style="font-style:normal;margin:0;font-size:14px;color:#888;">{E(line[2:])}</p>',BLANK]
    elif line.startswith('REF '): o.append(f'<p style="font-style:normal;margin:0;font-size:14px;line-height:1.7;color:#444;">{E(line[4:])}</p>')
    elif line.startswith('LINK '): o.append(f'<p style="font-style:normal;margin:0;text-align:center;font-size:14px;"><a href="{E(line[5:])}">{E(line[5:])}</a></p>')
    elif line.startswith('#TAGS '): o.append(f'<p style="font-style:normal;margin:0;font-size:14px;line-height:1.8;color:#2a6bd4;">{E(line[6:])}</p>')
    else: o+=[P.format(fx(s)) for s in sent(line)]+[BLANK]
body='\n'.join(o)
page=f'''<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><title>블로그 붙여넣기용 — {E(title)}</title>
<style>body{{font-family:'Malgun Gothic',sans-serif;background:#f4f5f7;margin:0}}.bar{{position:sticky;top:0;background:#111;color:#fff;padding:12px 20px;display:flex;gap:10px;align-items:center;z-index:9}}.bar button{{font-size:16px;padding:10px 18px;border:0;border-radius:6px;cursor:pointer;background:#03c75a;color:#fff;font-weight:bold}}.bar span{{font-size:13px;color:#ccc}}.wrap{{max-width:760px;margin:24px auto;background:#fff;padding:40px 48px;border-radius:8px}}.t{{font-size:22px;font-weight:bold;margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid #eee}}</style></head><body>
<div class="bar"><button onclick="cp('title')">① 제목 복사</button><button onclick="cp('rep')">② 대표이미지 복사</button><button onclick="cp('post')">③ 본문 복사</button><span id="msg">① 제목칸 Ctrl+V → ② 본문 맨 위 Ctrl+V → ③ 이미지 아래 Ctrl+V</span></div>
<div class="wrap"><div class="t" id="title">{E(title)}</div><p style="text-align:center"><img id="rep" src="{rep}" style="max-width:100%"></p><div id="post">
{body}
</div></div>
<script>let png=null;window.addEventListener('load',()=>{{const el=document.getElementById('rep');png=new Promise(r=>{{const c=document.createElement('canvas');c.width=el.naturalWidth;c.height=el.naturalHeight;c.getContext('2d').drawImage(el,0,0);c.toBlob(r,'image/png');}});}});
async function cp(id){{const el=document.getElementById(id),m=document.getElementById('msg');try{{if(id==='rep'){{await navigator.clipboard.write([new ClipboardItem({{'image/png':png}})]);m.textContent='대표이미지 복사됨 — 본문 맨 위에 Ctrl+V';return;}}if(id==='title')await navigator.clipboard.writeText(el.innerText.trim());else await navigator.clipboard.write([new ClipboardItem({{'text/html':new Blob([el.innerHTML],{{type:'text/html'}}),'text/plain':new Blob([el.innerText],{{type:'text/plain'}})}})]);}}catch(e){{if(id==='rep'){{m.textContent='이미지 복사가 막혔어요('+e.name+') — 이 파일을 크롬으로 열어 주세요';return;}}const r=document.createRange();r.selectNodeContents(el);const s=getSelection();s.removeAllRanges();s.addRange(r);document.execCommand('copy');s.removeAllRanges();}}m.textContent=(id==='title'?'제목':'본문')+' 복사됨 — 네이버에 Ctrl+V';}}</script></body></html>'''
open(out,'w').write(page);print(out,len(page))
