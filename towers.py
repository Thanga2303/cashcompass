"""Month-by-month coin towers: each month is a 3D stack of coins (three.js)."""
import json

import pandas as pd

from fin_core import inr

TOWERS = r"""
<style>
html,body{margin:0;background:transparent;overflow:hidden;font-family:'DM Sans',sans-serif;color:#EAF0F7}
#wrap{position:relative;width:100%;height:420px;border-radius:16px;overflow:hidden;background:radial-gradient(900px 480px at 50% 30%,#1a1650 0%,#070B1A 72%);border:1px solid rgba(124,140,255,.25)}
#c{position:absolute;inset:0}
#panel{position:absolute;right:12px;bottom:12px;width:min(280px,calc(100% - 24px));box-sizing:border-box;padding:14px 16px;border-radius:14px;background:rgba(14,20,50,.78);backdrop-filter:blur(10px);border:1px solid rgba(124,140,255,.35);display:none;font-size:13px;line-height:1.5}
#panel h3{margin:0 0 2px;font-size:17px}
#panel .big{font-size:22px;font-weight:700;color:#8FB0FF}
#hint{position:absolute;left:14px;top:12px;font-size:12px;color:#8FA3C0}
</style>
<div id="wrap"><div id="c"></div><div id="hint"></div><div id="panel"></div></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const D=__DATA__;
const M=D.months,n=M.length;
const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
const box=document.getElementById('c'),panel=document.getElementById('panel');
const inr=v=>'\u20b9'+Math.round(v).toLocaleString('en-IN');
const mx=Math.max.apply(null,M.map(m=>m.total).concat([1]));
const units=[10,25,50,100,250,500,1000,2500,5000,10000,25000,50000,100000];
const unit=units.find(u=>mx/u<=22)||units[units.length-1];
document.getElementById('hint').textContent=n?('1 coin = '+inr(unit)+'. Hover a tower, click for details.'):'No months recorded yet.';
const scene=new THREE.Scene();
const cam=new THREE.PerspectiveCamera(42,1,0.1,200);
const ren=new THREE.WebGLRenderer({antialias:true,alpha:true});
ren.setPixelRatio(Math.min(devicePixelRatio,2));box.appendChild(ren.domElement);
const gapX=1.5,coinH=0.16,R=0.52,span=Math.max(n,2)*gapX+1.2;
function size(){const w=box.clientWidth,h=box.clientHeight;ren.setSize(w,h);cam.aspect=w/h;
  const d=Math.max(span/(2*0.384*cam.aspect)+1,9.5);
  cam.position.set(0,d*0.38,d*0.92);cam.lookAt(0,1.7,0);cam.updateProjectionMatrix();}
size();addEventListener('resize',size);
scene.add(new THREE.AmbientLight(0x8899ff,0.55));
const key=new THREE.DirectionalLight(0xffffff,1.0);key.position.set(4,9,7);scene.add(key);
const rim=new THREE.PointLight(0x8b5cf6,1.2,40);rim.position.set(-6,4,3);scene.add(rim);
const g=new THREE.Group();scene.add(g);
const plat=new THREE.Mesh(new THREE.BoxGeometry(span,0.2,2.2),new THREE.MeshStandardMaterial({color:0x10213f,metalness:0.4,roughness:0.5}));
plat.position.y=-0.1;g.add(plat);
const edge=new THREE.LineSegments(new THREE.EdgesGeometry(plat.geometry),new THREE.LineBasicMaterial({color:0x5b8cff}));
edge.position.y=-0.1;g.add(edge);
function label(a,b){const c=document.createElement('canvas');c.width=384;c.height=128;const x=c.getContext('2d');
  x.textAlign='center';x.fillStyle='#EAF0F7';x.font='bold 44px sans-serif';x.fillText(a,192,52);
  x.fillStyle='#8FB0FF';x.font='40px sans-serif';x.fillText(b,192,100);
  const s=new THREE.Sprite(new THREE.SpriteMaterial({map:new THREE.CanvasTexture(c),transparent:true,depthTest:false}));
  s.scale.set(2.4,0.8,1);return s;}
const towers=[],all=[];
M.forEach((m,i)=>{
  const k=Math.max(1,Math.ceil(m.total/unit)),t=n>1?i/(n-1):0;
  const col=m.current?new THREE.Color(0xFBBF24):new THREE.Color().setHSL(0.62+0.12*t,0.85,0.62);
  const x=(i-(n-1)/2)*gapX,coins=[];
  for(let j=0;j<k;j++){
    const c=new THREE.Mesh(new THREE.CylinderGeometry(R,R,coinH*0.88,36),new THREE.MeshStandardMaterial({color:col,metalness:0.65,roughness:0.3,emissive:col,emissiveIntensity:0.08}));
    c.userData={i:i};c.position.set(x,9,0);g.add(c);coins.push(c);all.push(c);
  }
  const lb=label(m.label,inr(m.total));g.add(lb);
  towers.push({coins:coins,x:x,k:k,lb:lb});
});
function show(i){const m=M[i];let cmp='No earlier month to compare';
  if(m.prev!==null&&m.prev>0){const ch=(m.total-m.prev)/m.prev*100;cmp=(ch>=0?'Up ':'Down ')+Math.abs(ch).toFixed(0)+'% vs the month before ('+inr(m.prev)+')';}
  panel.innerHTML='<h3>'+m.full+'</h3><div class="big">'+inr(m.total)+'</div><div>'+m.count+' transactions</div><div>Top category: '+m.top+' ('+inr(m.topv)+')</div><div style="margin-top:4px">'+cmp+'</div>';
  panel.style.display='block';}
const ray=new THREE.Raycaster(),mouse=new THREE.Vector2(9,9);let hover=-1,sel=-1,mxp=0;
function setMouse(e){const b=ren.domElement.getBoundingClientRect();mouse.x=((e.clientX-b.left)/b.width)*2-1;mouse.y=-((e.clientY-b.top)/b.height)*2+1;mxp=mouse.x;}
ren.domElement.addEventListener('pointermove',setMouse);
ren.domElement.addEventListener('pointerleave',()=>{mouse.set(9,9);});
ren.domElement.addEventListener('click',e=>{setMouse(e);ray.setFromCamera(mouse,cam);const h=ray.intersectObjects(all);
  if(h.length){sel=h[0].object.userData.i;show(sel);}else{sel=-1;panel.style.display='none';}});
const clock=new THREE.Clock();
function tick(){
  const t=clock.getElapsedTime();
  ray.setFromCamera(mouse,cam);const h=ray.intersectObjects(all);
  hover=h.length?h[0].object.userData.i:-1;ren.domElement.style.cursor=hover>=0?'pointer':'default';
  towers.forEach((o,i)=>{
    const on=(i===hover||i===sel);
    o.coins.forEach((c,j)=>{
      const target=coinH*(j+0.5),delay=i*0.22+j*0.045;
      const p=reduce?1:Math.min(Math.max((t-delay)/0.55,0),1),e=1-Math.pow(1-p,3);
      c.position.y=9+(target-9)*e;
      c.rotation.y=j*0.4+(on&&!reduce?t*2:0);
      c.material.emissiveIntensity=on?0.5:0.08;
    });
    const landed=reduce||(t-(i*0.22+(o.k-1)*0.045))>0.45;
    o.lb.visible=landed;o.lb.position.set(o.x,coinH*o.k+0.85,0);o.lb.scale.set(on?2.8:2.4,on?0.93:0.8,1);
  });
  g.rotation.y+=((mxp*0.35)-g.rotation.y)*0.05;
  ren.render(scene,cam);requestAnimationFrame(tick);
}
tick();
</script>
"""


def towers_html(df, current=None, last=12):
    if df.empty:
        data = {"months": []}
    else:
        per = df["date"].dt.to_period("M")
        tot = df.groupby(per)["amount"].sum().sort_index()
        months = []
        for p in tot.index[-last:]:
            g = df[per == p]
            top = g.groupby("category")["amount"].sum().sort_values(ascending=False)
            months.append({"label": p.strftime("%b %Y"), "full": p.strftime("%B %Y"), "total": float(tot[p]),
                           "count": int(len(g)), "top": str(top.index[0]), "topv": float(top.iloc[0]),
                           "prev": float(tot[p - 1]) if (p - 1) in tot.index else None,
                           "current": bool(current is not None and p == current)})
        data = {"months": months}
    return TOWERS.replace("__DATA__", json.dumps(data).replace("</", "<\\/"))