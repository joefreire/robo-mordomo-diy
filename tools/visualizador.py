"""Gera exports/visualizador_robo.html: robô montado interativo, arquivo único (abre com 2 cliques).

Hierarquia de juntas igual à real (cintura -> tronco -> ombros/pescoço -> pan -> tilt -> cabeça),
com os limites de curso de cada módulo. Explodida, corte, grupos, transparência e lista de peças
(medidas, volume, massa estimada, relatório). Three.js vem de CDN (precisa de internet na 1ª vez).

    ~/.venvs/cadquery/bin/python tools/visualizador.py
"""
import base64
import io
import json
import sys
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from parameters import globais as G  # noqa: E402
from assembly import montagem_v1 as MV  # noqa: E402
from cintura import cintura_manual as C  # noqa: E402
from ombro import ombro_manual as O  # noqa: E402
from pescoco import pescoco_manual as P  # noqa: E402
from tools.render import CORES  # noqa: E402

OUT = RAIZ / "exports"
TMP = OUT / "_vis.stl"
TOL, ANG = 0.25, 0.4            # tesselação (leve o bastante para o navegador)

RELATORIO = {"base": "p01_p02_base/RELATORIO.md", "cintura": "p08_cintura/RELATORIO.md",
             "tronco": "p03_p04_tronco/RELATORIO.md", "braco_esquerdo": "p05_p06_p07_bracos/RELATORIO.md",
             "braco_direito": "p05_p06_p07_bracos/RELATORIO.md", "pescoco": "p11_pescoco/RELATORIO.md",
             "cabeca": "p_cabeca/RELATORIO.md"}
EXPLODE = {"base": (0, 0, -1.0), "cintura": (0, 0, -0.4), "tronco": (0, 0, 0.2), "braco_esquerdo": (-1.2, 0, 0.3),
           "braco_direito": (1.2, 0, 0.3), "pescoco": (0, 0, 0.9), "cabeca": (0, 0, 1.8)}

Z_TILT = G.Z_TOPO_TRONCO + P.Z_TILT
# juntas: nome -> (pai, pivô no referencial do robô)
JUNTAS = {"raiz": (None, (0, 0, 0)), "cintura": ("raiz", (0, 0, 0)),
          "ombro_esq": ("cintura", (-G.IF_OMBRO_X, G.IF_OMBRO_Y, G.IF_OMBRO_Z)),
          "ombro_dir": ("cintura", (G.IF_OMBRO_X, G.IF_OMBRO_Y, G.IF_OMBRO_Z)),
          "pan": ("cintura", (0, 0, 0)), "tilt": ("pan", (0, 0, Z_TILT))}
LIMITES = {"cintura": (-G.IF_CINTURA_GIRO, G.IF_CINTURA_GIRO, "z"), "ombro_esq": (*O.CURSO["esquerdo"], "x"),
           "ombro_dir": (*O.CURSO["direito"], "x"), "pan": (-P.PAN_GIRO, P.PAN_GIRO, "z"),
           "tilt": (-P.TILT_GIRO, P.TILT_GIRO, "x")}


def junta_de(grupo, nome):
    if grupo == "base":
        return "raiz"
    if grupo == "cintura":
        return "cintura" if nome in C.GIRAM else "raiz"
    if grupo == "tronco":
        return "cintura"
    if grupo in ("braco_esquerdo", "braco_direito"):
        j = "ombro_esq" if grupo.endswith("esquerdo") else "ombro_dir"
        movel = nome[2:] == "B_rotor_braco" or not nome[:2] in ("09", "10")
        return j if movel else "cintura"
    if grupo == "pescoco":
        if nome in P.TILT_GIRAM:
            return "tilt"
        return "pan" if nome in P.PAN_GIRAM else "cintura"
    return "tilt"            # cabeça


def mesh_de(wp):
    cq.exporters.export(wp, str(TMP), tolerance=TOL, angularTolerance=ANG)
    return trimesh.load(str(TMP))


def main():
    g = MV.montar()
    cena = trimesh.Scene()
    cena.graph.update(frame_from=cena.graph.base_frame, frame_to="raiz", matrix=np.eye(4))
    for j, (pai, piv) in JUNTAS.items():
        if pai is None:
            continue
        ppai = np.array(JUNTAS[pai][1], float)
        T = trimesh.transformations.translation_matrix(np.array(piv, float) - ppai)
        cena.graph.update(frame_from=pai, frame_to=j, matrix=T)
    pecas = []
    for grupo, d in g.items():
        for nome, (wp, cor) in d.items():
            j = junta_de(grupo, nome)
            piv = np.array(JUNTAS[j][1], float)
            m = mesh_de(wp)
            m.apply_translation(-piv)
            rgba = CORES[cor]
            m.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
                baseColorFactor=[int(255 * c) for c in rgba], metallicFactor=0.05, roughnessFactor=0.7, doubleSided=True))
            cena.add_geometry(m, node_name=nome, geom_name=nome, parent_node_name=j)
            bb = wp.val().BoundingBox()
            v = MV.vol(wp)
            massa = MV.ACO_G if nome == "aco" else v * MV.RHO_PETG * MV.FATOR_IMPRESSO
            pecas.append({"nome": nome, "grupo": grupo, "junta": j, "dim": [round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)],
                          "vol": round(v / 1000, 1), "massa": round(massa), "cor": cor, "rel": RELATORIO[grupo]})
    TMP.unlink(missing_ok=True)
    buf = io.BytesIO()
    buf.write(cena.export(file_type="glb"))
    glb64 = base64.b64encode(buf.getvalue()).decode()
    html = HTML.replace("__GLB__", glb64).replace("__PECAS__", json.dumps(pecas, ensure_ascii=False)) \
        .replace("__JUNTAS__", json.dumps({k: list(v) for k, v in LIMITES.items()})) \
        .replace("__EXPLODE__", json.dumps(EXPLODE)) \
        .replace("__RESUMO__", json.dumps({"altura": 550, "pes": MV.PES}))
    saida = OUT / "visualizador_robo.html"
    saida.write_text(html, encoding="utf-8")
    print(f"{saida}  ({saida.stat().st_size / 1e6:.1f} MB, {len(pecas)} peças)")


HTML = r"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Robô Mordomo V1</title>
<style>
:root{--bg:#f3f4f6;--painel:#ffffff;--tx:#1f2933;--mut:#6b7280;--ac:#0f6b6b;--bd:#e5e7eb}
@media (prefers-color-scheme: dark){:root{--bg:#111418;--painel:#1b1f24;--tx:#e5e7eb;--mut:#9ca3af;--ac:#3fb8b8;--bd:#2d333b}}
*{box-sizing:border-box}body{margin:0;font:13px system-ui,Segoe UI,sans-serif;background:var(--bg);color:var(--tx);display:flex;height:100vh;overflow:hidden}
#lado{width:330px;min-width:330px;background:var(--painel);border-right:1px solid var(--bd);overflow:auto;padding:12px 14px}
#vista{flex:1;position:relative}canvas{display:block}
h1{font-size:16px;margin:0 0 4px}h2{font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:var(--mut);margin:16px 0 6px}
.lin{display:flex;align-items:center;gap:8px;margin:4px 0}.lin label{width:96px}.lin input[type=range]{flex:1}.val{width:44px;text-align:right;font-variant-numeric:tabular-nums}
button{background:var(--bg);color:var(--tx);border:1px solid var(--bd);border-radius:6px;padding:4px 8px;cursor:pointer;margin:2px 2px 2px 0}button:hover{border-color:var(--ac)}
#pecas div{padding:3px 6px;border-radius:4px;cursor:pointer;display:flex;justify-content:space-between}#pecas div:hover{background:var(--bg)}#pecas div.sel{background:var(--ac);color:#fff}
#info{position:absolute;right:12px;top:12px;background:var(--painel);border:1px solid var(--bd);border-radius:8px;padding:10px 12px;min-width:240px;display:none}
#dica{position:absolute;left:12px;bottom:10px;color:var(--mut);font-size:12px}
.mut{color:var(--mut)}a{color:var(--ac)}
@media (max-width:760px){body{flex-direction:column}#lado{width:100%;min-width:0;height:45vh}#vista{height:55vh}}
</style></head><body>
<div id="lado">
<h1>Robô Mordomo — V1</h1><div class="mut">550 mm · CAD validado · gire, explode, corte e clique nas peças</div>
<h2>Juntas (limites reais)</h2><div id="juntas"></div>
<div><button data-p="repouso">Repouso</button><button data-p="servico">Serviço</button><button data-p="aceno">Aceno</button><button data-p="limites">Extremos</button></div>
<h2>Vista</h2>
<div class="lin"><label>Explodir</label><input id="exp" type="range" min="0" max="120" value="0"><span class="val" id="expv">0</span></div>
<div class="lin"><label>Corte</label><select id="corteEixo"><option value="">sem corte</option><option value="x">X (lado)</option><option value="y">Y (frente)</option><option value="z">Z (altura)</option></select></div>
<div class="lin"><label></label><input id="corte" type="range" min="-130" max="560" value="0"><span class="val" id="cortev">0</span></div>
<div class="lin"><label>Transparente</label><input id="transp" type="checkbox"></div>
<div><button data-v="frente">Frente</button><button data-v="lado">Lado</button><button data-v="tras">Trás</button><button data-v="topo">Topo</button><button data-v="iso">Iso</button></div>
<h2>Grupos</h2><div id="grupos"></div>
<h2>Peças (<span id="npecas"></span>)</h2><div id="pecas"></div>
</div>
<div id="vista"><div id="info"></div><div id="dica">arrastar: girar · roda: zoom · botão direito: mover · clique: peça</div></div>
<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/"}}</script>
<script type="module">
import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
const PECAS=__PECAS__, LIM=__JUNTAS__, EXP=__EXPLODE__;
const NOMEJ={cintura:'Cintura',ombro_esq:'Ombro esq.',ombro_dir:'Ombro dir.',pan:'Pescoço pan',tilt:'Pescoço tilt'};
const vista=document.getElementById('vista');
const r=new THREE.WebGLRenderer({antialias:true});r.setPixelRatio(devicePixelRatio);r.localClippingEnabled=true;vista.appendChild(r.domElement);
const cena=new THREE.Scene();
const escuro=matchMedia('(prefers-color-scheme: dark)').matches;cena.background=new THREE.Color(escuro?0x111418:0xf3f4f6);
cena.add(new THREE.HemisphereLight(0xffffff,0x667788,1.6));const dl=new THREE.DirectionalLight(0xffffff,2.2);dl.position.set(300,-500,800);cena.add(dl);
const cam=new THREE.PerspectiveCamera(35,1,5,8000);cam.up.set(0,0,1);
const ctl=new OrbitControls(cam,r.domElement);ctl.target.set(0,0,275);
const chao=new THREE.GridHelper(600,24,0x888888,0xbbbbbb);chao.rotation.x=Math.PI/2;cena.add(chao);
function tam(){const w=vista.clientWidth,h=vista.clientHeight;r.setSize(w,h);cam.aspect=w/h;cam.updateProjectionMatrix();}
addEventListener('resize',tam);tam();
function ver(v){const t=ctl.target,d=1100;const p={frente:[0,d,275],lado:[-d,0,275],tras:[0,-d,275],topo:[0,1,d+275],iso:[-650,800,650]}[v];cam.position.set(p[0],p[1],p[2]);t.set(0,0,275);ctl.update();}
ver('iso');
const plano=new THREE.Plane(new THREE.Vector3(1,0,0),0);
const bin=Uint8Array.from(atob('__GLB__'),c=>c.charCodeAt(0)).buffer;
const nos={},malhas={},base={},grupoDe={};
new GLTFLoader().parse(bin,'',g=>{
  const raiz=g.scene;raiz.traverse(o=>{nos[o.name]=o;if(o.isMesh){o.material=o.material.clone();o.material.clippingPlanes=[];malhas[o.name]=o;}});
  // glTF não guarda o nome da malha no nó pai: o nó com o nome da peça é o pai da malha
  raiz.traverse(o=>{if(o.isMesh&&o.parent&&PECAS.find(p=>p.nome===o.parent.name)){malhas[o.parent.name]=o;}});
  PECAS.forEach(p=>{const o=nos[p.nome];if(o){base[p.nome]=o.position.clone();grupoDe[p.nome]=p.grupo;}});
  cena.add(raiz);montarUI();aplicar();
});
const ang={cintura:0,ombro_esq:0,ombro_dir:0,pan:0,tilt:0};
function aplicar(){for(const j in ang){const o=nos[j];if(!o)continue;const a=THREE.MathUtils.degToRad(ang[j]);o.rotation.set(0,0,0);o.rotation[LIM[j][2]]=a;}
  const e=+document.getElementById('exp').value;
  PECAS.forEach(p=>{const o=nos[p.nome];if(!o)return;const v=EXP[p.grupo]||[0,0,0];o.position.copy(base[p.nome]).add(new THREE.Vector3(v[0]*e,v[1]*e,v[2]*e));});}
function montarUI(){
  const J=document.getElementById('juntas');
  for(const j in LIM){const [a,b]=LIM[j];const d=document.createElement('div');d.className='lin';
    d.innerHTML=`<label>${NOMEJ[j]}</label><input type=range min=${a} max=${b} step=1 value=0 id=j_${j}><span class=val id=v_${j}>0°</span>`;J.appendChild(d);
    d.querySelector('input').oninput=ev=>{ang[j]=+ev.target.value;document.getElementById('v_'+j).textContent=ang[j]+'°';aplicar();};}
  const PRE={repouso:{cintura:0,ombro_esq:0,ombro_dir:0,pan:0,tilt:0},servico:{cintura:20,ombro_esq:30,ombro_dir:15,pan:-20,tilt:-10},
    aceno:{cintura:-15,ombro_esq:0,ombro_dir:110,pan:25,tilt:5},limites:Object.fromEntries(Object.keys(LIM).map(j=>[j,LIM[j][1]]))};
  document.querySelectorAll('[data-p]').forEach(b=>b.onclick=()=>{const p=PRE[b.dataset.p];for(const j in p){ang[j]=p[j];document.getElementById('j_'+j).value=p[j];document.getElementById('v_'+j).textContent=p[j]+'°';}aplicar();});
  document.querySelectorAll('[data-v]').forEach(b=>b.onclick=()=>ver(b.dataset.v));
  document.getElementById('exp').oninput=e=>{document.getElementById('expv').textContent=e.target.value;aplicar();};
  const ce=document.getElementById('corteEixo'),cs=document.getElementById('corte');
  function corte(){const ax=ce.value;document.getElementById('cortev').textContent=cs.value;
    for(const n in malhas){malhas[n].material.clippingPlanes=ax?[plano]:[];malhas[n].material.needsUpdate=true;}
    if(ax){plano.normal.set(ax==='x'?-1:0,ax==='y'?-1:0,ax==='z'?-1:0);plano.constant=+cs.value;}}
  ce.onchange=()=>{cs.value=ce.value==='z'?275:0;corte();};cs.oninput=corte;
  document.getElementById('transp').onchange=e=>{for(const n in malhas){const m=malhas[n].material;m.transparent=e.target.checked;m.opacity=e.target.checked?0.35:1;m.depthWrite=!e.target.checked;}};
  const grupos=[...new Set(PECAS.map(p=>p.grupo))];const GD=document.getElementById('grupos');
  grupos.forEach(gr=>{const d=document.createElement('div');d.className='lin';d.innerHTML=`<input type=checkbox checked id=g_${gr}><label for=g_${gr} style="width:auto">${gr.replace('_',' ')} <span class=mut>(${PECAS.filter(p=>p.grupo===gr).reduce((s,p)=>s+p.massa,0)} g)</span></label>`;GD.appendChild(d);
    d.querySelector('input').onchange=e=>PECAS.filter(p=>p.grupo===gr).forEach(p=>{if(nos[p.nome])nos[p.nome].visible=e.target.checked;});});
  const L=document.getElementById('pecas');document.getElementById('npecas').textContent=PECAS.length;
  PECAS.forEach(p=>{const d=document.createElement('div');d.dataset.n=p.nome;d.innerHTML=`<span>${p.nome}</span><span class=mut>${p.massa} g</span>`;d.onclick=()=>sel(p.nome);L.appendChild(d);});
}
let selAtual=null;const info=document.getElementById('info');
function sel(n){if(selAtual&&malhas[selAtual])malhas[selAtual].material.emissive.setHex(0x000000);
  document.querySelectorAll('#pecas div').forEach(d=>d.classList.toggle('sel',d.dataset.n===n));selAtual=n;
  const p=PECAS.find(x=>x.nome===n);if(!p){info.style.display='none';return;}
  if(malhas[n])malhas[n].material.emissive.setHex(0x664400);
  info.style.display='block';info.innerHTML=`<b>${p.nome}</b><br><span class=mut>grupo</span> ${p.grupo} · <span class=mut>junta</span> ${p.junta}<br>
  <span class=mut>medidas</span> ${p.dim[0]} × ${p.dim[1]} × ${p.dim[2]} mm<br><span class=mut>volume</span> ${p.vol} cm³ · <span class=mut>massa est.</span> ${p.massa} g<br>
  <a href="${p.rel}" target=_blank>relatório do grupo</a> · <a href="#" id=isolar>isolar</a> · <a href="#" id=todas>mostrar todas</a>`;
  document.getElementById('isolar').onclick=e=>{e.preventDefault();PECAS.forEach(q=>{if(nos[q.nome])nos[q.nome].visible=q.nome===n;});};
  document.getElementById('todas').onclick=e=>{e.preventDefault();PECAS.forEach(q=>{if(nos[q.nome])nos[q.nome].visible=true;});};}
const ray=new THREE.Raycaster(),mouse=new THREE.Vector2();let down=null;
r.domElement.addEventListener('pointerdown',e=>down=[e.clientX,e.clientY]);
r.domElement.addEventListener('pointerup',e=>{if(!down||Math.hypot(e.clientX-down[0],e.clientY-down[1])>4)return;
  const b=r.domElement.getBoundingClientRect();mouse.set((e.clientX-b.left)/b.width*2-1,-(e.clientY-b.top)/b.height*2+1);ray.setFromCamera(mouse,cam);
  const hit=ray.intersectObjects(Object.values(malhas).filter(m=>{let o=m;while(o){if(!o.visible)return false;o=o.parent;}return true;}),false)[0];
  if(hit){let o=hit.object;while(o&&!PECAS.find(p=>p.nome===o.name))o=o.parent;sel(o?o.name:null);}else sel(null);});
(function anim(){requestAnimationFrame(anim);ctl.update();r.render(cena,cam);})();
</script></body></html>"""

if __name__ == "__main__":
    main()
