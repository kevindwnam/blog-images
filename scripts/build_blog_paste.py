# usage: python3 build_blog_paste.py src.txt imgdir "제목" out.html
# src markup: "## 소제목", "> 리드줄", "![](파일)", "---"(구분선), "REF 참고자료줄", "LINK url"(가운데), "#TAGS ...", 그 외=본문 문단
import sys,re,html,base64,io
from PIL import Image
src,imgdir,title,out=sys.argv[1:5]
def datauri(fn):
    im=Image.open(f'{imgdir}/{fn}').convert('RGB')
    if im.width>1400: im=im.resize((1400,round(im.height*1400/im.width)),Image.LANCZOS)
    b=io.BytesIO(); im.save(b,'JPEG',quality=88); return 'data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode()
E=html.escape
P='<p style="font-style:normal;margin:0;font-size:16px;line-height:1.9;color:#222;">{}</p>'
BLANK='<p style="font-style:normal;margin:0;font-size:16px;line-height:1.9;">&nbsp;</p>'
def sentences(t): return [x for x in re.split(r'(?<=[.?!])\s+(?=\S)',t.strip()) if x]
blocks=[];cur=[]
def flush():
    global cur
    while cur and cur[-1]==BLANK: cur.pop()
    if cur: blocks.append(('text','\n'.join(cur)))
    cur=[]
for line in open(src).read().split('\n'):
    line=line.rstrip()
    if not line: continue
    if line.startswith('![]('):
        flush(); blocks.append(('img',(datauri(line[4:-1]),line[4:-1])))
    elif line=='---': cur.append('<hr style="border:0;border-top:1px solid #ddd;margin:40px 0;">')
    elif line.startswith('## '): cur.append(f'<p style="font-style:normal;margin:0 0 6px;font-size:21px;font-weight:bold;color:#111;">{E(line[3:])}</p>')
    elif line.startswith('> '): cur.append(f'<p style="font-style:normal;margin:0;font-size:14px;color:#888;">{E(line[2:])}</p>'); cur.append(BLANK)
    elif line.startswith('REF '): cur.append(f'<p style="font-style:normal;margin:0;font-size:14px;line-height:1.7;color:#444;">{E(line[4:])}</p>')
    elif line.startswith('LINK '): cur.append(f'<p style="font-style:normal;margin:0;text-align:center;font-size:14px;"><a href="{E(line[5:])}">{E(line[5:])}</a></p>')
    elif line.startswith('#TAGS '): cur.append(f'<p style="font-style:normal;margin:0;font-size:14px;line-height:1.8;color:#2a6bd4;">{E(line[6:])}</p>')
    else:
        for s in sentences(line): cur.append(P.format(E(s)))
        cur.append(BLANK)
flush()
parts=[];steps=['title']
for i,(k,v) in enumerate(blocks):
    sid=f'b{i}';steps.append(sid);n=len(steps)
    if k=='text':
        parts.append(f'<div class="blk"><button class="cb" onclick="go({n-1})">{n}. 글 복사</button><div id="{sid}" class="txt">{v}</div></div>')
    else:
        parts.append(f'<div class="blk"><button class="cb img" onclick="go({n-1})">{n}. 이미지 복사</button><p style="text-align:center;margin:0"><img id="{sid}" data-file="{v[1]}" src="{v[0]}" style="max-width:100%"></p></div>')
page=f'''<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><title>블로그 붙여넣기용 — {E(title)}</title>
<style>body{{font-family:'Malgun Gothic',sans-serif;background:#f4f5f7;margin:0}}.bar{{position:sticky;top:0;background:#111;color:#fff;padding:12px 20px;display:flex;gap:12px;align-items:center;z-index:9}}.bar button{{font-size:16px;padding:10px 18px;border:0;border-radius:6px;cursor:pointer;background:#03c75a;color:#fff;font-weight:bold}}.bar span{{font-size:13px;color:#ccc}}.wrap{{max-width:760px;margin:24px auto;background:#fff;padding:40px 48px;border-radius:8px}}.t{{font-size:22px;font-weight:bold;padding-bottom:16px;border-bottom:1px solid #eee}}.blk{{position:relative;border-left:3px solid transparent;padding:14px 0 14px 14px;margin-left:-17px}}.blk.on{{border-left-color:#03c75a;background:#f3fbf6}}.cb{{position:absolute;right:-150px;top:14px;width:130px;font-size:13px;padding:7px;border:1px solid #03c75a;background:#fff;color:#03a24a;border-radius:5px;cursor:pointer}}.cb.img{{border-color:#2a6bd4;color:#2a6bd4}}.done{{opacity:.45}}</style></head><body>
<div class="bar"><button id="nx" onclick="go(cur)">1. 제목 복사</button><span id="msg">버튼 → 네이버 블로그에 Ctrl+V → 다시 버튼. 위에서부터 순서대로 {len(steps)}단계</span></div>
<div class="wrap"><div class="blk" style="margin-left:-17px"><div class="t" id="title">{E(title)}</div></div>
{''.join(parts)}</div>
<script>
const steps={steps};let cur=0;
const pngs={{}};function mk(el){{return new Promise(r=>{{const f=()=>{{const c=document.createElement('canvas');c.width=el.naturalWidth;c.height=el.naturalHeight;c.getContext('2d').drawImage(el,0,0);c.toBlob(r,'image/png');}};el.complete?f():el.onload=f;}});}}
window.addEventListener('load',()=>document.querySelectorAll('img[id]').forEach(el=>pngs[el.id]=mk(el)));
async function go(i){{const id=steps[i],el=document.getElementById(id);let what;
 try{{if(id==='title'){{await navigator.clipboard.writeText(el.innerText.trim());what='제목';}}
 else if(el.tagName==='IMG'){{await navigator.clipboard.write([new ClipboardItem({{'image/png':pngs[id]||mk(el)}})]);what='이미지';}}
 else{{await navigator.clipboard.write([new ClipboardItem({{'text/html':new Blob([el.innerHTML],{{type:'text/html'}}),'text/plain':new Blob([el.innerText],{{type:'text/plain'}})}})]);what='글';}}
 document.querySelectorAll('.blk').forEach(b=>b.classList.remove('on'));const bl=el.closest('.blk');bl.classList.add('on');bl.classList.add('done');
 cur=Math.min(i+1,steps.length-1);const nid=steps[cur],ne=document.getElementById(nid);
 document.getElementById('nx').textContent=(i+1>=steps.length?'완료':(cur+1)+'. '+(nid==='title'?'제목':ne.tagName==='IMG'?'이미지':'글')+' 복사');
 document.getElementById('msg').textContent=(i+1)+'단계 '+what+' 복사됨 — 네이버에 Ctrl+V 후 다음 버튼';}}
 catch(e){{
  if(el.tagName==='IMG'){{document.querySelectorAll('.blk').forEach(b=>b.classList.remove('on'));el.closest('.blk').classList.add('on');el.scrollIntoView({{block:'center'}});
   document.getElementById('msg').textContent='이미지 자동 복사가 막혔어요('+e.name+') → 이 파일과 같은 폴더의 ['+el.dataset.file+'] 파일을 네이버 글쓰기 화면에 끌어다 놓은 뒤 다음 버튼';
   cur=Math.min(i+1,steps.length-1);document.getElementById('nx').textContent=(cur+1)+'. 다음 복사';return;}}
  const r=document.createRange();r.selectNodeContents(el);const sel=getSelection();sel.removeAllRanges();sel.addRange(r);const ok=document.execCommand('copy');sel.removeAllRanges();
  if(ok){{document.querySelectorAll('.blk').forEach(b=>b.classList.remove('on'));el.closest('.blk').classList.add('on','done');cur=Math.min(i+1,steps.length-1);const ne=document.getElementById(steps[cur]);
   document.getElementById('nx').textContent=(cur+1)+'. '+(ne.tagName==='IMG'?'이미지':'글')+' 복사';document.getElementById('msg').textContent=(i+1)+'단계 복사됨 — 네이버에 Ctrl+V 후 다음 버튼';}}
  else document.getElementById('msg').textContent='복사 실패('+e.name+'): 이 파일을 다운로드 폴더에서 더블클릭해 크롬으로 열어 주세요';}}}}
</script></body></html>'''
open(out,'w').write(page);print(len(steps),'steps',len(page))
