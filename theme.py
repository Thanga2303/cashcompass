"""CashCompass look and feel: page setup, CSS and the 3D compass hero."""
import streamlit as st
import streamlit.components.v1 as components

CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&family=DM+Sans:wght@400;500&display=swap');
.stApp{background:radial-gradient(1100px 600px at 85% -10%,#231B5C 0%,#070B1A 62%);font-family:'DM Sans',sans-serif}
.stApp,.stApp p,.stApp label,.stApp li{color:#EAF0F7}
h1,h2,h3,h4{font-family:'Sora',sans-serif!important;color:#EAF0F7!important;letter-spacing:-0.01em}
header[data-testid="stHeader"]{background:transparent}
[data-testid="stSidebar"]{background:#0E1B33;border-right:1px solid #1E3358}
[data-testid="stCaptionContainer"]{color:#8FA3C0}
[data-testid="stMetric"]{background:rgba(18,27,61,.55);backdrop-filter:blur(8px);border:1px solid rgba(124,140,255,.25);border-left:3px solid #5B8CFF;padding:14px 16px;border-radius:10px}
[data-testid="stMetricValue"]{font-family:'Sora',sans-serif;color:#5B8CFF}
.stTextInput input,.stNumberInput input,[data-testid="stChatInput"] textarea{background:#0E1B33!important;color:#EAF0F7!important;border:1px solid #1E3358!important}
.stButton>button{background:#5B8CFF;color:#fff;border:0;font-weight:600;border-radius:8px;transition:transform .15s,box-shadow .15s}
.stButton>button:hover{background:#7FA4FF;color:#070B1A;transform:translateY(-2px);box-shadow:0 8px 20px rgba(91,140,255,.3)}
[data-testid="stChatMessage"]{background:rgba(18,27,61,.55);backdrop-filter:blur(8px);border-radius:14px;border:1px solid rgba(124,140,255,.25)}
hr{border-color:#1E3358!important}
a{color:#5B8CFF!important}

@keyframes pageIn{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
@keyframes pop{from{opacity:0;transform:scale(.96) translateY(6px)}to{opacity:1;transform:none}}
@keyframes orbA{from{transform:translate(0,0)}to{transform:translate(90px,70px)}}
@keyframes orbB{from{transform:translate(0,0)}to{transform:translate(-80px,-60px)}}
@keyframes edge{0%,100%{box-shadow:-2px 0 0 0 rgba(91,140,255,.25)}50%{box-shadow:-4px 0 14px 0 rgba(91,140,255,.55)}}
.block-container{animation:pageIn .8s ease both}
.stApp::before,.stApp::after{content:"";position:fixed;border-radius:50%;pointer-events:none;z-index:0}
.stApp::before{width:520px;height:520px;top:-140px;left:-120px;background:radial-gradient(circle,rgba(91,140,255,.10),transparent 65%);animation:orbA 18s ease-in-out infinite alternate}
.stApp::after{width:600px;height:600px;bottom:-200px;right:-160px;background:radial-gradient(circle,rgba(91,143,214,.14),transparent 65%);animation:orbB 22s ease-in-out infinite alternate}
[data-testid="stMetric"]{transition:transform .25s ease;transform-style:preserve-3d;animation:edge 4s ease-in-out infinite}
[data-testid="stMetric"]:hover{transform:perspective(700px) rotateX(7deg) rotateY(-8deg) translateZ(10px)}
[data-testid="stChatMessage"]{animation:pop .35s ease both}
[data-testid="stChatInput"]{background:#0E1B33;border:1px solid #1E3358;border-radius:12px}
[data-testid="stChatInput"] textarea{background:transparent!important}
[data-testid="stBottom"]>div{background:transparent}
.stTabs [data-baseweb="tab"]{font-family:'Sora',sans-serif;font-weight:600;color:#8FA3C0}
.stTabs [aria-selected="true"]{color:#5B8CFF}
.stTabs [data-baseweb="tab-highlight"]{background:#5B8CFF}
.stTabs [data-baseweb="tab-border"]{background:#1E3358}
.glass{background:rgba(18,27,61,.55);backdrop-filter:blur(8px);border:1px solid rgba(124,140,255,.25);border-radius:14px;padding:14px 16px;margin-bottom:10px;animation:pageIn .6s ease both;transition:box-shadow .2s,border-color .2s}
.glass:hover{border-color:rgba(124,140,255,.6);box-shadow:0 0 22px rgba(91,140,255,.18)}
.tip{font-size:14px}
.sub{color:#8FA3C0;font-size:12px;margin-top:6px}
.ring{text-align:center}
.arc{animation:ringIn 1.4s ease-out both}
@keyframes ringIn{from{stroke-dashoffset:var(--c)}}
.hm{display:grid;grid-template-columns:repeat(7,1fr);gap:6px;max-width:440px}
.hm-h{text-align:center;font-size:11px;color:#8FA3C0}
.hm-c{aspect-ratio:1;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:11px;transition:transform .15s}
.hm-c:hover{transform:scale(1.15)}
.pers{font-family:'Sora',sans-serif;font-size:20px;font-weight:700;margin-bottom:4px;background:linear-gradient(90deg,#5B8CFF,#B18CFF);-webkit-background-clip:text;background-clip:text;color:transparent}
.fl-bar{display:flex;height:18px;border-radius:9px;overflow:hidden;background:rgba(255,255,255,.06)}
.fl{height:100%;transition:filter .2s}
.fl:hover{filter:brightness(1.3)}
.fl-leg{display:flex;flex-wrap:wrap;gap:6px 14px;margin-top:10px;font-size:12px}
.fl-leg i{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:5px}
.tl{border-left:2px solid rgba(124,140,255,.35);margin-left:8px;padding-left:20px}
.tl-i{position:relative;display:flex;justify-content:space-between;align-items:center;gap:10px;padding:10px 14px;margin-bottom:8px;border-radius:12px;background:rgba(18,27,61,.5);border:1px solid rgba(124,140,255,.15);animation:pageIn .5s ease both;transition:transform .15s}
.tl-i:hover{transform:translateX(4px)}
.dot{position:absolute;left:-28px;width:14px;height:14px;border-radius:50%}
.amt{font-weight:700;color:#8FB0FF;white-space:nowrap}
[data-testid="stFileUploaderDropzone"]{background:rgba(18,27,61,.55)!important;border:1px dashed rgba(124,140,255,.5)!important;border-radius:12px}
[data-testid="stFileUploaderDropzone"] *{color:#C9D5F0!important}
[data-testid="stFileUploaderDropzone"] button{background:rgba(91,140,255,.2)!important;border:1px solid rgba(124,140,255,.5)!important;color:#EAF0F7!important}
[data-baseweb="select"]>div{background:#0E1B33!important;border:1px solid rgba(124,140,255,.35)!important}
[data-baseweb="select"] *{color:#EAF0F7!important}
[data-baseweb="popover"] ul,[data-baseweb="menu"]{background:#0E1B33!important}
[data-baseweb="popover"] li{color:#EAF0F7!important}
[data-baseweb="popover"] li:hover{background:rgba(91,140,255,.25)!important}
[data-baseweb="input"],[data-baseweb="base-input"],[data-baseweb="textarea"]{background:#0E1B33!important;border-color:rgba(124,140,255,.35)!important}
[data-baseweb="input"] input,[data-baseweb="textarea"] textarea{color:#EAF0F7!important;-webkit-text-fill-color:#EAF0F7}
::placeholder{color:#7F8FB0!important;-webkit-text-fill-color:#7F8FB0!important}
[data-testid="stNumberInput"] button{background:#12213D!important;color:#EAF0F7!important;border-color:rgba(124,140,255,.35)!important}
[data-testid="stAlert"]{background:rgba(91,140,255,.12)!important;border:1px solid rgba(124,140,255,.35);border-radius:12px}
[data-testid="stAlert"] *{color:#EAF0F7!important}
[data-testid="stChatInput"],[data-testid="stChatInput"]>div{background:#0E1B33!important;border-color:rgba(124,140,255,.35)!important}
[data-testid="stChatInput"] textarea{color:#EAF0F7!important;-webkit-text-fill-color:#EAF0F7}
[data-testid="stChatInput"] button{background:linear-gradient(135deg,#4F7DFF,#8B5CF6)!important;color:#fff!important}
.stButton>button,[data-testid="stBaseButton-secondary"]{background:linear-gradient(135deg,#4F7DFF,#8B5CF6)!important;color:#fff!important;border:0!important;font-weight:600;border-radius:10px}
.stButton>button:hover,[data-testid="stBaseButton-secondary"]:hover{box-shadow:0 8px 20px rgba(91,140,255,.4);transform:translateY(-2px)}
[data-testid="stCode"],[data-testid="stCode"] pre{background:#0E1B33!important}
.paybtn{display:inline-block;padding:12px 22px;border-radius:12px;background:linear-gradient(135deg,#4F7DFF,#8B5CF6);color:#fff!important;font-weight:700;text-decoration:none!important;box-shadow:0 8px 24px rgba(91,140,255,.35);margin:6px 0}
.mrow{display:grid;grid-template-columns:84px 1fr 80px;align-items:center;gap:10px;margin:8px 0;font-size:13px}
.mrow b{text-align:right;color:#8FB0FF}
.mbar{height:12px;border-radius:6px;background:rgba(255,255,255,.07);overflow:hidden}
.mbar i{display:block;height:100%;border-radius:6px;background:linear-gradient(90deg,#5B8CFF,#8B5CF6);transform-origin:left;animation:grow 1s ease-out both}
@keyframes grow{from{transform:scaleX(0)}}
.stTabs [data-baseweb="tab-list"]{gap:12px;padding:6px 4px 16px;border-bottom:0!important;flex-wrap:wrap}
.stTabs [data-baseweb="tab"]{height:auto;padding:12px 22px;border-radius:14px;background:linear-gradient(180deg,#1B2A5E,#101A3F)!important;border:1px solid rgba(124,140,255,.35);box-shadow:0 6px 0 #0A1030,0 10px 18px rgba(0,0,0,.45),inset 0 1px 0 rgba(255,255,255,.12);color:#C9D5F0!important;font-weight:700;transform:perspective(500px) rotateX(8deg);transition:transform .15s,box-shadow .15s,background .15s}
.stTabs [data-baseweb="tab"]:hover{transform:perspective(500px) rotateX(8deg) translateY(-3px)}
.stTabs [data-baseweb="tab"][aria-selected="true"]{background:linear-gradient(180deg,#6B8FFF,#7C4DFF)!important;color:#fff!important;box-shadow:0 2px 0 #2B2A8F,0 6px 14px rgba(91,140,255,.5),inset 0 1px 0 rgba(255,255,255,.35);transform:perspective(500px) rotateX(8deg) translateY(4px)}
.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"]{display:none!important}
.st-key-navbar button{height:58px;border-radius:16px!important;font-size:16px!important;font-weight:800!important;color:#fff!important;border:1px solid rgba(160,175,255,.45)!important;transform:perspective(600px) rotateX(10deg);transition:transform .15s,box-shadow .15s,background .15s!important}
.st-key-navbar button p{font-weight:800!important;color:#fff!important}
.st-key-navbar button[kind="secondary"],.st-key-navbar [data-testid="stBaseButton-secondary"]{background:linear-gradient(180deg,#2D3F8F,#141E52)!important;box-shadow:0 7px 0 #0A1030,0 14px 22px rgba(0,0,0,.5),inset 0 1px 0 rgba(255,255,255,.22)!important}
.st-key-navbar button[kind="secondary"]:hover,.st-key-navbar [data-testid="stBaseButton-secondary"]:hover{transform:perspective(600px) rotateX(10deg) translateY(-3px)!important;box-shadow:0 10px 0 #0A1030,0 18px 26px rgba(0,0,0,.55),inset 0 1px 0 rgba(255,255,255,.3)!important}
.st-key-navbar button[kind="primary"],.st-key-navbar [data-testid="stBaseButton-primary"]{background:linear-gradient(180deg,#86A6FF,#7C4DFF)!important;box-shadow:0 2px 0 #2B2A8F,0 6px 18px rgba(91,140,255,.6),inset 0 1px 0 rgba(255,255,255,.45)!important;transform:perspective(600px) rotateX(10deg) translateY(5px)!important}
.st-key-navbar button:active{transform:perspective(600px) rotateX(10deg) translateY(7px)!important}
.st-key-navbar{margin-bottom:14px}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
</style>
"""

HERO = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@600;700&family=DM+Sans:wght@400&display=swap');
html,body{margin:0;background:transparent;color:#EAF0F7;font-family:'DM Sans',sans-serif}
.wrap{display:flex;align-items:center;gap:8px;height:300px}
.txt{flex:1 1 55%;padding-left:4px}
h1{font-family:'Sora',sans-serif;font-weight:700;font-size:42px;line-height:1.05;margin:0 0 12px;background:linear-gradient(90deg,#EAF0F7,#8FA8FF,#B18CFF);-webkit-background-clip:text;background-clip:text;color:transparent}
p{margin:0;font-size:16px;line-height:1.5;color:#9DB0CC;max-width:30ch}
#c{flex:1 1 45%;height:100%;min-width:0}
@media(max-width:560px){
  .wrap{flex-direction:column-reverse;height:360px;gap:0;text-align:center}
  .txt{padding:0;flex:0 0 auto}
  p{margin:0 auto}
  h1{font-size:34px}
  #c{flex:1 1 auto;width:100%}
}
</style>
<div class="wrap">
  <div class="txt">
    <h1>CashCompass</h1>
    <p>Ask where your money went. Pay with UPI or Razorpay.</p>
  </div>
  <div id="c"></div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const el=document.getElementById('c');
const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
const scene=new THREE.Scene();
const cam=new THREE.PerspectiveCamera(40,1,0.1,100);cam.position.z=7.8;
const ren=new THREE.WebGLRenderer({antialias:true,alpha:true});
ren.setPixelRatio(Math.min(devicePixelRatio,2));
el.appendChild(ren.domElement);
function size(){const w=el.clientWidth,h=el.clientHeight;ren.setSize(w,h);cam.aspect=w/h;cam.updateProjectionMatrix();}
size();addEventListener('resize',size);

scene.add(new THREE.AmbientLight(0xffffff,0.55));
const l1=new THREE.PointLight(0xffe2a8,1.2);l1.position.set(3,3,5);scene.add(l1);
const l2=new THREE.PointLight(0x5b8fd6,0.9);l2.position.set(-4,-2,3);scene.add(l2);

const brass=new THREE.MeshStandardMaterial({color:0x5B8CFF,metalness:0.9,roughness:0.28});
const navy=new THREE.MeshStandardMaterial({color:0x10213f,metalness:0.3,roughness:0.6});
const g=new THREE.Group();scene.add(g);

g.add(new THREE.Mesh(new THREE.TorusGeometry(1.45,0.09,24,120),brass));
const disc=new THREE.Mesh(new THREE.CylinderGeometry(1.4,1.4,0.1,64),navy);
disc.rotation.x=Math.PI/2;disc.position.z=-0.02;g.add(disc);

for(let i=0;i<12;i++){
  const a=i/12*Math.PI*2, big=i%3===0;
  const t=new THREE.Mesh(new THREE.BoxGeometry(big?0.07:0.035,big?0.26:0.14,0.04),brass);
  t.position.set(Math.sin(a)*1.2,Math.cos(a)*1.2,0.06);t.rotation.z=-a;g.add(t);
}

const needle=new THREE.Group();
const red=new THREE.Mesh(new THREE.ConeGeometry(0.16,1.05,4),new THREE.MeshStandardMaterial({color:0xF26B5B,metalness:0.4,roughness:0.35}));
red.position.y=0.52;
const cream=new THREE.Mesh(new THREE.ConeGeometry(0.16,1.05,4),new THREE.MeshStandardMaterial({color:0xEAF0F7,metalness:0.4,roughness:0.35}));
cream.rotation.z=Math.PI;cream.position.y=-0.52;
needle.add(red,cream);needle.position.z=0.14;g.add(needle);
const cap=new THREE.Mesh(new THREE.SphereGeometry(0.1,24,24),brass);cap.position.z=0.2;g.add(cap);

const badges=[];
[['🍜','#FBBF24'],['🛍️','#F472B6'],['🚌','#A78BFA'],['📚','#34D399'],['🎬','#F87171'],['🧾','#60A5FA']].forEach(b=>{
  const cv=document.createElement('canvas');cv.width=cv.height=128;const x=cv.getContext('2d');
  const gr=x.createRadialGradient(64,64,10,64,64,62);gr.addColorStop(0,b[1]+'cc');gr.addColorStop(1,b[1]+'22');
  x.fillStyle=gr;x.beginPath();x.arc(64,64,60,0,6.283);x.fill();
  x.lineWidth=4;x.strokeStyle=b[1];x.beginPath();x.arc(64,64,58,0,6.283);x.stroke();
  x.font='64px sans-serif';x.textAlign='center';x.textBaseline='middle';x.fillText(b[0],64,70);
  const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:new THREE.CanvasTexture(cv),transparent:true}));
  scene.add(sp);badges.push(sp);});
let mx=0,my=0;
addEventListener('pointermove',e=>{mx=e.clientX/innerWidth*2-1;my=e.clientY/innerHeight*2-1;});
const clock=new THREE.Clock();
function tick(){
  const t=clock.getElapsedTime();
  const k=Math.min(t/2.8,1), ease=1-Math.pow(1-k,3);
  const spin=reduce?0:(1-ease)*Math.PI*6;
  needle.rotation.z=-0.7+spin+(reduce?0:Math.sin(t*1.4)*0.05*ease);
  g.rotation.y+=((mx*0.55)-g.rotation.y)*0.06;
  g.rotation.x+=((-my*0.35)-g.rotation.x)*0.06;
  g.position.y=reduce?0:Math.sin(t*0.9)*0.07;
  badges.forEach((s,i)=>{const a=(reduce?0:t*(0.35+0.05*i))+i*Math.PI*2/6;
    const z=Math.sin(a)*1.6,d=(z/1.6+1)/2;
    s.position.set(Math.cos(a)*1.85,Math.sin(a+i)*0.55+(reduce?0:Math.sin(t*1.5+i)*0.08),z);
    const k=0.5+0.28*d;s.scale.set(k,k,1);s.material.opacity=0.5+0.5*d;});
  ren.render(scene,cam);
  requestAnimationFrame(tick);
}
tick();
</script>
"""


def apply():
    st.set_page_config(page_title="CashCompass", page_icon="🧭", layout="centered")
    st.markdown("<style>" + CSS.replace("<style>", "").replace("</style>", "") + "</style>", unsafe_allow_html=True)
    components.html(HERO, height=380)