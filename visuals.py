"""Dashboard visuals: Money Universe, budget ring, heatmap, flow, personality, timeline, insights."""
import html
import json
import math

import pandas as pd

from fin_core import *  # noqa: F401,F403


# ---------------- Visual components ----------------
def category_stats(df, period):
    cur, prev = month_df(df, period), month_df(df, period - 1)
    total = float(cur["amount"].sum())
    out = {}
    for cat, g in cur.groupby("category"):
        t = float(g["amount"].sum())
        recent = g.sort_values("date", ascending=False).head(5)
        out[cat] = {"total": t, "count": int(len(g)), "pct": t / total * 100 if total else 0,
                    "prev": float(prev[prev["category"] == cat]["amount"].sum()),
                    "recent": [html.escape(f"{r.date:%d %b} · {r.description} · {inr(r.amount)}")
                               for r in recent.itertuples()]}
    return out, total


UNIVERSE = r"""
<style>
html,body{margin:0;background:transparent;overflow:hidden;font-family:'DM Sans',sans-serif;color:#EAF0F7}
#wrap{position:relative;width:100%;height:460px;border-radius:16px;overflow:hidden;background:radial-gradient(900px 500px at 50% 40%,#1a1650 0%,#070B1A 70%);border:1px solid rgba(124,140,255,.25)}
#c{position:absolute;inset:0}
#panel{position:absolute;right:12px;bottom:12px;width:min(300px,calc(100% - 24px));max-height:70%;overflow:auto;box-sizing:border-box;padding:14px 16px;border-radius:14px;background:rgba(14,20,50,.75);backdrop-filter:blur(10px);border:1px solid rgba(124,140,255,.35);display:none;font-size:13px;line-height:1.45}
#panel h3{margin:0 0 4px;font-size:17px}
#panel .big{font-size:22px;font-weight:700;color:#8FB0FF}
#panel ul{margin:6px 0 0;padding-left:16px;color:#B8C4E0}
#hint{position:absolute;left:14px;top:12px;font-size:12px;color:#8FA3C0}
</style>
<div id="wrap"><div id="c"></div><div id="hint">Hover a planet, click for details</div><div id="panel"></div></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const D=__DATA__;
const names=Object.keys(D.cats),n=names.length;
const vals=names.map(k=>D.cats[k].total);
const max=Math.max.apply(null,vals.concat([1]));
const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
const box=document.getElementById('c'),panel=document.getElementById('panel');
if(!n)document.getElementById('hint').textContent='No spending recorded for '+D.label;
const inr=v=>'\u20b9'+Math.round(v).toLocaleString('en-IN');
const scene=new THREE.Scene();
const cam=new THREE.PerspectiveCamera(42,1,0.1,300);
const ren=new THREE.WebGLRenderer({antialias:true,alpha:true});
ren.setPixelRatio(Math.min(devicePixelRatio,2));box.appendChild(ren.domElement);
const gap=1.0,R0=2.6,R=R0+Math.max(n-1,0)*gap+1.0;
function size(){const w=box.clientWidth,h=box.clientHeight;ren.setSize(w,h);cam.aspect=w/h;
  const t=0.384,d=Math.max((R+0.8)/(t*cam.aspect),(0.5*R+1.8)/t);
  cam.position.set(0,d*0.5,d*0.87);cam.lookAt(0,0,0);cam.updateProjectionMatrix();}
size();addEventListener('resize',size);
scene.add(new THREE.AmbientLight(0x8899ff,0.5));
scene.add(new THREE.PointLight(0x7aa2ff,2.2,60));
const sp=[];for(let i=0;i<500;i++){const r=40+Math.random()*60,a=Math.random()*6.283,b=Math.acos(2*Math.random()-1);
  sp.push(r*Math.sin(b)*Math.cos(a),r*Math.cos(b),r*Math.sin(b)*Math.sin(a));}
const sg=new THREE.BufferGeometry();sg.setAttribute('position',new THREE.Float32BufferAttribute(sp,3));
const stars=new THREE.Points(sg,new THREE.PointsMaterial({color:0xaabbff,size:0.25,transparent:true,opacity:0.8}));scene.add(stars);
const g=new THREE.Group();scene.add(g);
function label(a,b){const c=document.createElement('canvas');c.width=384;c.height=128;const x=c.getContext('2d');
  x.textAlign='center';x.fillStyle='#EAF0F7';x.font='bold 44px sans-serif';x.fillText(a,192,52);
  x.fillStyle='#8FB0FF';x.font='40px sans-serif';x.fillText(b,192,100);
  const s=new THREE.Sprite(new THREE.SpriteMaterial({map:new THREE.CanvasTexture(c),transparent:true,depthTest:false}));
  s.scale.set(2.7,0.9,1);return s;}
const core=new THREE.Mesh(new THREE.SphereGeometry(1.0,48,48),new THREE.MeshStandardMaterial({color:0x4f7dff,emissive:0x5b8cff,emissiveIntensity:1.0,metalness:0.2,roughness:0.3}));
const halo1=new THREE.Mesh(new THREE.SphereGeometry(1.35,32,32),new THREE.MeshBasicMaterial({color:0x7c5cff,transparent:true,opacity:0.14}));
const halo2=new THREE.Mesh(new THREE.SphereGeometry(1.8,32,32),new THREE.MeshBasicMaterial({color:0x5b8cff,transparent:true,opacity:0.07}));
g.add(core,halo1,halo2);
const cl=label(D.label,inr(D.total));cl.position.set(0,1.9,0);g.add(cl);
const planets=[];
names.forEach((nm,i)=>{
  const c=D.cats[nm],col=new THREE.Color(c.color),r=R0+i*gap,rad=0.28+0.62*Math.sqrt(c.total/max);
  const ring=new THREE.Mesh(new THREE.TorusGeometry(r,0.01,8,160),new THREE.MeshBasicMaterial({color:0x3a4a8a,transparent:true,opacity:0.5}));
  ring.rotation.x=Math.PI/2;g.add(ring);
  const pl=new THREE.Mesh(new THREE.SphereGeometry(rad,32,32),new THREE.MeshStandardMaterial({color:col,emissive:col,emissiveIntensity:0.25,metalness:0.2,roughness:0.5}));
  pl.userData={i:i};g.add(pl);
  const lg=new THREE.BufferGeometry();lg.setAttribute('position',new THREE.BufferAttribute(new Float32Array(6),3));
  const ln=new THREE.Line(lg,new THREE.LineBasicMaterial({color:col,transparent:true,opacity:0.5}));ln.frustumCulled=false;g.add(ln);
  const pu=new THREE.Mesh(new THREE.SphereGeometry(0.07,12,12),new THREE.MeshBasicMaterial({color:0xffffff}));g.add(pu);
  const lb=label(nm,inr(c.total));g.add(lb);
  planets.push({pl:pl,ln:ln,pu:pu,lb:lb,r:r,rad:rad,speed:0.28/(1+i*0.5),phase:i*2.1,off:i*0.17});
});
function showPanel(i){const nm=names[i],c=D.cats[nm];let cmp='No spending recorded in '+D.prev;
  if(c.prev>0){const ch=(c.total-c.prev)/c.prev*100;cmp=(ch>=0?'Up ':'Down ')+Math.abs(ch).toFixed(0)+'% vs '+D.prev+' ('+inr(c.prev)+')';}
  panel.innerHTML='<h3 style="color:'+c.color+'">'+nm+'</h3><div class="big">'+inr(c.total)+'</div><div>'+c.count+' transactions, '+c.pct.toFixed(0)+'% of '+D.label+'</div><div style="margin-top:4px">'+cmp+'</div><ul>'+c.recent.map(x=>'<li>'+x+'</li>').join('')+'</ul>';
  panel.style.display='block';}
const ray=new THREE.Raycaster(),mouse=new THREE.Vector2(9,9);let hover=-1,sel=-1,mx=0;
function setMouse(e){const b=ren.domElement.getBoundingClientRect();mouse.x=((e.clientX-b.left)/b.width)*2-1;mouse.y=-((e.clientY-b.top)/b.height)*2+1;mx=mouse.x;}
ren.domElement.addEventListener('pointermove',setMouse);
ren.domElement.addEventListener('pointerleave',()=>{mouse.set(9,9);});
ren.domElement.addEventListener('click',e=>{setMouse(e);ray.setFromCamera(mouse,cam);
  const h=ray.intersectObjects(planets.map(p=>p.pl));
  if(h.length){sel=h[0].object.userData.i;showPanel(sel);}else{sel=-1;panel.style.display='none';}});
const clock=new THREE.Clock();
function tick(){
  const t=clock.getElapsedTime();
  core.scale.setScalar(1+Math.sin(t*2)*0.04);halo1.scale.setScalar(1+Math.sin(t*1.4)*0.08);halo2.scale.setScalar(1+Math.sin(t*1.1+1)*0.1);
  ray.setFromCamera(mouse,cam);const h=ray.intersectObjects(planets.map(p=>p.pl));
  hover=h.length?h[0].object.userData.i:-1;ren.domElement.style.cursor=hover>=0?'pointer':'default';
  planets.forEach((o,i)=>{
    const a=o.phase+(reduce?0:t*o.speed);
    const p=reduce?1:Math.min(Math.max((t-0.18*i)/0.9,0),1),e=1-Math.pow(1-p,3);
    const on=(i===hover||i===sel),target=on?1.18:1;
    o.s=(o.s===undefined?target:o.s+(target-o.s)*0.15);
    o.pl.scale.setScalar(Math.max(e*o.s,0.001));
    o.pl.position.set(Math.cos(a)*o.r,0,Math.sin(a)*o.r);o.pl.rotation.y=t*0.6;
    o.pl.material.emissiveIntensity=on?0.7:0.25;
    const pos=o.ln.geometry.attributes.position;pos.setXYZ(0,0,0,0);pos.setXYZ(1,o.pl.position.x,0,o.pl.position.z);pos.needsUpdate=true;
    o.ln.material.opacity=on?0.95:0.5;o.ln.visible=p>0.1;
    const u=reduce?0.5:((t*0.35+o.off)%1);o.pu.position.set(o.pl.position.x*u,0,o.pl.position.z*u);o.pu.visible=p>0.5;
    o.lb.position.set(o.pl.position.x,o.rad*e*o.s+0.75,o.pl.position.z);o.lb.visible=p>0.3;
  });
  g.rotation.y+=((mx*0.4)-g.rotation.y)*0.04;stars.rotation.y=t*0.01;
  ren.render(scene,cam);requestAnimationFrame(tick);
}
tick();
</script>
"""


def universe_html(df, period):
    stats, total = category_stats(df, period)
    cats = {k: {**v, "color": COLORS.get(k, "#94A3B8")}
            for k, v in sorted(stats.items(), key=lambda kv: -kv[1]["total"])}
    data = {"total": total, "label": period.strftime("%B %Y"), "prev": (period - 1).strftime("%B %Y"), "cats": cats}
    return UNIVERSE.replace("__DATA__", json.dumps(data).replace("</", "<\\/"))


def budget_ring_html(spent, budget):
    if budget <= 0:
        return "<div class='glass'>Set a monthly budget in the sidebar to see your budget health.</div>"
    used = spent / budget
    color = "#34D399" if used < 0.75 else "#FBBF24" if used < 1 else "#F87171"
    c = 2 * math.pi * 54
    off = c * (1 - min(used, 1.0))
    return ("<div class='glass ring'><svg viewBox='0 0 140 140' width='150' height='150'>"
            "<circle cx='70' cy='70' r='54' fill='none' stroke='rgba(255,255,255,.08)' stroke-width='12'/>"
            f"<circle class='arc' cx='70' cy='70' r='54' fill='none' stroke='{color}' stroke-width='12' stroke-linecap='round' "
            f"stroke-dasharray='{c:.1f}' style='--c:{c:.1f};stroke-dashoffset:{off:.1f}' transform='rotate(-90 70 70)'/>"
            f"<text x='70' y='68' text-anchor='middle' fill='#EAF0F7' font-size='26' font-weight='700'>{used:.0%}</text>"
            "<text x='70' y='88' text-anchor='middle' fill='#8FA3C0' font-size='11'>of budget used</text></svg>"
            f"<div class='sub'>{inr(spent)} of {inr(budget)}</div></div>")


def heatmap_html(df, period):
    cur = month_df(df, period)
    daily = cur.groupby(cur["date"].dt.day)["amount"].sum()
    mx = float(daily.max()) if len(daily) else 0.0
    cells = [f"<div class='hm-h'>{d}</div>" for d in "MTWTFSS"] + ["<div></div>"] * period.to_timestamp().weekday()
    for d in range(1, period.days_in_month + 1):
        v = float(daily.get(d, 0))
        if v and mx:
            t = v / mx
            rgb = f"{91 + 48 * t:.0f},{140 - 48 * t:.0f},{255 - 9 * t:.0f}"
            style = f"background:rgba({rgb},{0.25 + 0.75 * t:.2f})"
        else:
            style = "background:rgba(255,255,255,.04)"
        tip = f"{d} {period.strftime('%b')}: {inr(v)}"
        cells.append(f"<div class='hm-c' style='{style}' title='{tip}'>{d}</div>")
    return f"<div class='glass'><div class='hm'>{''.join(cells)}</div><div class='sub'>Darker and more purple means a higher-spend day. Hover a day for the amount.</div></div>"


def flow_html(df, period, income):
    cur = month_df(df, period)
    spent = float(cur["amount"].sum())
    if income <= 0:
        return "<div class='glass'>Set your monthly income in the sidebar to see how it splits into expenses and what is left.</div>"
    by = cur.groupby("category")["amount"].sum().sort_values(ascending=False)
    left = max(income - spent, 0.0)
    base = max(income, spent)
    segs = [(k, float(v), COLORS.get(k, "#94A3B8")) for k, v in by.items()]
    if left > 0:
        segs.append(("Left over", left, "#34D399"))
    bar = "".join(f"<div class='fl' style='width:{v / base * 100:.2f}%;background:{c}' title='{k}: {inr(v)}'></div>"
                  for k, v, c in segs)
    legend = "".join(f"<span><i style='background:{c}'></i>{k} {inr(v)}</span>" for k, v, c in segs)
    status = (f"You are spending {inr(spent - income)} more than your income." if spent > income
              else f"{inr(left)} of your {inr(income)} income is left ({left / income:.0%}).")
    return f"<div class='glass'><div class='fl-bar'>{bar}</div><div class='fl-leg'>{legend}</div><div class='sub'>{status}</div></div>"


def personality(df, period):
    cur = month_df(df, period)
    if len(cur) < 5:
        return None
    total = float(cur["amount"].sum())
    by = cur.groupby("category")["amount"].sum().sort_values(ascending=False)
    wants = float(cur[~cur["category"].isin(NEEDS)]["amount"].sum()) / total * 100
    top, share = by.index[0], by.iloc[0] / total * 100
    weekend = float(cur[cur["date"].dt.weekday >= 5]["amount"].sum()) / total * 100
    if wants >= 40:
        t, e, why = "The Impulse Explorer", "⚡", f"Wants like shopping and entertainment make up {wants:.0f}% of your spending."
    elif top == "Food" and share >= 35:
        t, e, why = "The Foodie", "🍜", f"Food is {share:.0f}% of your spending."
    elif top == "Education" and share >= 30:
        t, e, why = "The Scholar", "📚", f"Education is {share:.0f}% of your spending."
    elif top == "Transport" and share >= 30:
        t, e, why = "The Commuter", "🚌", f"Transport is {share:.0f}% of your spending."
    elif wants <= 25:
        t, e, why = "The Steady Planner", "🧭", f"Wants are only {wants:.0f}% of your spending."
    else:
        t, e, why = "The Balanced Spender", "⚖️", f"Your top category, {top}, is {share:.0f}% and wants are {wants:.0f}%."
    return {"title": t, "emoji": e, "why": why,
            "detail": f"{len(cur)} transactions, average {inr(total / len(cur))}; weekends account for {weekend:.0f}% of spend."}


def personality_html(df, period):
    p = personality(df, period)
    if not p:
        return "<div class='glass'>Not enough transactions this month (need at least 5) to work out a spending personality.</div>"
    return (f"<div class='glass'><div class='pers'>{p['emoji']} {p['title']}</div><div>{p['why']}</div>"
            f"<div class='sub'>{p['detail']} Based on a simple rule set applied to your real transactions.</div></div>")


def timeline_html(df, period, limit=12):
    cur = month_df(df, period).sort_values("date", ascending=False).head(limit)
    if cur.empty:
        return "<div class='glass'>No transactions recorded for this month.</div>"
    items = []
    for i, r in enumerate(cur.itertuples()):
        c = COLORS.get(r.category, "#94A3B8")
        items.append(f"<div class='tl-i' style='animation-delay:{i * 60}ms'><span class='dot' style='background:{c};box-shadow:0 0 10px {c}'></span>"
                     f"<div><b>{html.escape(str(r.description))}</b><div class='sub'>{r.date:%d %b} · {r.category}</div></div>"
                     f"<div class='amt'>{inr(r.amount)}</div></div>")
    return f"<div class='tl'>{''.join(items)}</div>"


def insights(df, period, budget, income):
    cur = month_df(df, period)
    if cur.empty:
        return ["No transactions are recorded for this month yet."]
    total = float(cur["amount"].sum())
    by = cur.groupby("category")["amount"].sum().sort_values(ascending=False)
    out = [f"{by.index[0]} accounts for the largest share of your spending: {inr(by.iloc[0])} ({by.iloc[0] / total:.0%})."]
    prev_total = float(month_df(df, period - 1)["amount"].sum())
    if prev_total > 0:
        ch = (total - prev_total) / prev_total * 100
        out.append(f"Your spending is {abs(ch):.0f}% {'higher' if ch >= 0 else 'lower'} than {(period - 1).strftime('%B')} ({inr(total)} vs {inr(prev_total)}).")
    last = cur["date"].max()
    this_w = float(spend(cur, cat="Food", start=last - pd.Timedelta(days=6))["amount"].sum())
    prev_w = float(spend(df, cat="Food", start=last - pd.Timedelta(days=13), end=last - pd.Timedelta(days=7))["amount"].sum())
    if this_w or prev_w:
        out.append(f"You spent {inr(this_w)} on food in the last 7 days of records vs {inr(prev_w)} the 7 days before.")
    if budget > 0:
        used = total / budget
        out.append(f"You have crossed your budget by {inr(total - budget)}." if used >= 1
                   else f"You are approaching your budget: {used:.0%} used, {inr(budget - total)} left." if used >= 0.8
                   else f"You are within budget: {used:.0%} used, {inr(budget - total)} left.")
    wants = cur[~cur["category"].isin(NEEDS)].groupby("category")["amount"].sum().sort_values(ascending=False)
    if len(wants) and wants.sum() / total > 0.3:
        out.append(f"Wants are {wants.sum() / total:.0%} of spending. Trimming {wants.index[0]} by 15% would save about {inr(wants.iloc[0] * 0.15)}.")
    if income > 0 and total > income:
        out.append("You are spending more than your monthly income.")
    return out[:5]


def monthly_html(monthly):
    if len(monthly) == 0:
        return "<div class='glass'>No months recorded yet.</div>"
    mx = float(monthly.max()) or 1.0
    rows = "".join(f"<div class='mrow'><span>{m.strftime('%b %Y')}</span><div class='mbar'><i style='width:{v / mx * 100:.1f}%'></i></div><b>{inr(v)}</b></div>"
                   for m, v in monthly.iloc[::-1].items())
    return f"<div class='glass'>{rows}</div>"