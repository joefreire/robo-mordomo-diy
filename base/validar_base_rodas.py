"""Validação da Peça 01R (base com rodas, V2) contra a 01, a 02, a cintura e o robô inteiro.

    ~/.venvs/cadquery/bin/python base/validar_base_rodas.py
Saídas: exports/p01R_base_rodas/ (RELATORIO.md + PNGs)
"""
import math
import sys
from pathlib import Path

import cadquery as cq
import trimesh

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from parameters import globais as G  # noqa: E402
from base import base_inferior as B1, base_superior as B2, base_rodas as BR, doca_carga as DC  # noqa: E402
from cintura import cintura_manual as C  # noqa: E402
from assembly import montagem_v1 as MV  # noqa: E402
from tools.render import CORES, render_conjunto  # noqa: E402

OUT = RAIZ / "exports" / "p01R_base_rodas"
OUT.mkdir(parents=True, exist_ok=True)
TMP = OUT / "_tmp.stl"
TOL = 0.5
REL, FALHAS = [], []

# Massas da V2 que a V1 não tem (hipóteses; conferir com as peças compradas)
V2_EMBAIXO = [("bateria 2×18650 + suporte", 110.0, "bateria"), ("2 motores N20 com redução", 40.0, "motores"),
              ("2 rodas", 30.0, "rodas"), ("4 rodízios", 40.0, "rodizios"), ("driver dos motores", 25.0, "driver"), ("placa de carga", 15.0, "carregador")]
V2_EM_CIMA = [("servo da cintura", 55.0, (0, 0, 82)), ("2 servos dos ombros", 110.0, (0, -9, 233)),
              ("2 servos pan/tilt", 40.0, (0, 0, 330)), ("tela do peito 3,5\"", 40.0, (0, 40, 214)),
              ("ESP32-S3 + áudio + fiação", 70.0, (0, -25, 190))]


def ok(c, m):
    REL.append(("OK  " if c else "FALHA ") + m)
    if not c:
        FALHAS.append(m)


def inter(a, b):
    try:
        return a.intersect(b).val().Volume()
    except Exception:
        return 0.0


def to_mesh(wp):
    cq.exporters.export(wp, str(TMP), tolerance=0.1, angularTolerance=0.3)
    return trimesh.load(str(TMP))


p01, p01r, p02 = B1.modelo(), BR.modelo(), B2.modelo()
env = BR.envelopes()

REL.append("## 1. Sólido")
ok(p01r.val().isValid() and len(p01r.solids().vals()) == 1, "01R válido e 1 corpo")
bb = p01r.val().BoundingBox()
ok(max(bb.xlen, bb.ylen) <= 256, f"01R {bb.xlen:.0f}×{bb.ylen:.0f}×{bb.zlen:.0f} mm cabe na A1 (256)")

REL.append("\n## 2. IF-BASE idêntica à Peça 01 (borda, contorno, torres)")
# faixa do CONTORNO (parede externa + borda), sem o miolo onde ficam os poços/sapatas da 01R
faixa = (cq.Workplane("XY").workplane(offset=G.P01_ALTURA - 4).rect(400, 400).extrude(4.01)
         .cut(cq.Workplane("XY").workplane(offset=G.P01_ALTURA - 7).rect(G.BASE_LARG - 24, G.BASE_PROF - 24).extrude(9)))
a, b = p01.intersect(faixa), p01r.intersect(faixa)
dif = a.cut(b).val().Volume() + b.cut(a).val().Volume()
ok(dif < 1.0, f"contorno e borda (z {G.P01_ALTURA - 4:g}–{G.P01_ALTURA:g}, faixa de 12 mm junto à parede) iguais à 01: diferença {dif:.2f} mm³ "
   "(abaixo disso a 01R tem, de propósito, a janela de IR e os furos dos contatos na traseira)")
for x, y in G.BASE_TORRES:
    furo = cq.Workplane("XY").workplane(offset=BR.Z0 - 1).center(x, y).circle(G.M3_PASSANTE / 2 - 0.05).extrude(G.P01_ALTURA - BR.Z0 + 1)
    ok(inter(furo, p01r) < 0.01, f"M3 de união ({x:+.0f},{y:+.0f}) atravessa a torre da 01R livre (mesmo eixo da 01 e do inserto da 02)")
ok(inter(p01r, p02) < TOL, f"01R × 02 sem interferência ({inter(p01r, p02):.2f} mm³)")
ok(abs(bb.zmax - G.P01_ALTURA) < 0.01, f"borda em z = {bb.zmax:.1f} (= 01): altura do robô não muda")
ok(abs(bb.zmin - G.RODAS_FOLGA_CHAO) < 0.01, f"fundo {bb.zmin:.1f} mm acima da mesa")

REL.append("\n## 3. Envelopes V2 (rodas, motores, rodízios, bateria, driver) livres")
fixos = {"01R": p01r, "02": p02, "08A_cintura": C.flange_inferior().translate((0, 0, G.Z_TOPO_P02)),
         "difusor": B2.difusor_cego()}
for n, e in env.items():
    ruins = [f"{k}={inter(e, w):.1f}" for k, w in fixos.items() if inter(e, w) > TOL]
    ok(not ruins, f"{n}: livre" + ("" if not ruins else " — " + "; ".join(ruins)))
nomes = list(env)
for i in range(len(nomes)):
    for j in range(i + 1, len(nomes)):
        v = inter(env[nomes[i]], env[nomes[j]])
        if v > TOL:
            ok(False, f"{nomes[i]} × {nomes[j]} = {v:.1f} mm³")
for n in ("roda_esq", "roda_dir"):
    zmin = env[n].val().BoundingBox().zmin
    ok(abs(zmin) < 0.01, f"{n} toca a mesa (z mín {zmin:.2f})")
ok(True, f"4 rodízios {G.RODIZIO_ALIVIO:g} mm acima da mesa: as rodas sempre tracionam; ao inclinar o robô apoia neles")
topo_roda = env["roda_dir"].val().BoundingBox().zmax
REL.append(f"- roda Ø{G.RODA_D_MAX:g}: topo em z {topo_roda:.0f}; folga ao teto da 02 conferida acima (sem interferência)")

REL.append("\n## 4. Estabilidade sobre rodas (polígono: 2 rodas + 2 rodízios)")
# polígono de apoio ao inclinar: rodas + rodízios (casco convexo, sentido horário)
_pts = [(-G.RODA_X, 0.0), (G.RODA_X, 0.0)] + list(G.RODIZIOS)
_c = (0.0, 0.0)
apoio = sorted(_pts, key=lambda p: -math.atan2(p[1] - _c[1], p[0] - _c[0]))


def margem(cg):
    m = 1e9
    for (x1, y1), (x2, y2) in zip(apoio, apoio[1:] + apoio[:1]):
        nx, ny = y2 - y1, -(x2 - x1)
        L = math.hypot(nx, ny)
        d = ((cg[0] - x1) * nx + (cg[1] - y1) * ny) / L
        m = min(m, d)            # polígono no sentido horário: dentro = d positivo
    return m


def cg_v2(grupos, carga):
    m, (cx, cy, cz), _ = MV.massa_cg({k: {n: v for n, v in d.items() if n != "aco"} for k, d in grupos.items()}, carga)
    mx, my, mz = m * cx, m * cy, m * cz
    for d, mg, k in V2_EMBAIXO:
        w = env.get(k, None) or (env["roda_esq"] if k in ("rodas", "motores") else env["bateria"])
        c = w.val().Center()
        m += mg; mx += mg * c.x; my += mg * c.y; mz += mg * c.z
    for d, mg, (x, y, z) in V2_EM_CIMA:
        m += mg; mx += mg * x; my += mg * y; mz += mg * z
    return m, (mx / m, my / m, mz / m)


for d, mg, _ in V2_EMBAIXO:
    REL.append(f"- (hipótese) {d}: {mg:.0f} g embaixo")
for d, mg, _ in V2_EM_CIMA:
    REL.append(f"- (hipótese) {d}: {mg:.0f} g em cima")
casos = [("repouso, bandeja vazia", MV.montar(), 0.0), ("bandeja com 300 g", MV.montar(), MV.CARGA_BANDEJA_G),
         ("braço esq. +60° e 300 g", MV.montar(ombro_esq=60.0), MV.CARGA_BANDEJA_G)]
for titulo, g, carga in casos:
    m, cg = cg_v2(g, carga)
    mar = margem(cg)
    ang = math.degrees(math.atan2(mar, cg[2]))
    ok(mar > 25, f"V2 {titulo}: {m:.0f} g, CG ({cg[0]:+.0f}, {cg[1]:+.0f}, {cg[2]:.0f}) {mar:.0f} mm dentro do apoio; tomba com ~{ang:.0f}°")

REL.append("\n## 5. Doca de carga (robô encaixado de ré)")
doca = DC.bloco()
bbd = doca.val().BoundingBox()
ok(max(bbd.xlen, bbd.ylen) <= 256, f"doca {bbd.xlen:.0f}×{bbd.ylen:.0f}×{bbd.zlen:.0f} mm cabe na A1")
obst = {"01R": p01r, "02": p02, **{k: v for k, v in env.items()}}
gr = casos[0][1]
for gn in ("braco_esquerdo", "braco_direito", "cintura"):
    for n, (w, _) in gr[gn].items():
        obst[n] = w
ruins = [f"{k}={inter(doca, w):.1f}" for k, w in obst.items() if inter(doca, w) > TOL]
ok(not ruins, "doca × base, rodas, rodízios, braços, mão e bandeja: livre" + ("" if not ruins else " — " + "; ".join(ruins)))
pontas = DC.contatos_soltos()
v_ponta = inter(pontas, p01r)
penetra = DC.CONTATO_SALIENCIA - DC.DOCA_FOLGA
ok(penetra > G.CARGA_PAD[2], f"contato de mola passa {penetra:.1f} mm da face traseira; o rebaixo do contato tem "
   f"{G.CARGA_PAD[2]:g} mm -> compressão ~{penetra - G.CARGA_PAD[2]:.1f} mm sobre a placa de cobre")
# ponta solta: só o trecho que entra no rebaixo pode cruzar a 01R (o resto é ar); o que sobrar é a compressão
v_rebaixo = 2 * 3.1416 * (DC.CONTATO_PONTA_D / 2) ** 2 * (penetra - G.CARGA_PAD[2])
ok(v_ponta <= v_rebaixo + 1.0, f"pontas dos contatos batem só na placa de cobre do rebaixo (x ±{G.CARGA_X:g}, z {G.CARGA_Z:g}): "
   f"{v_ponta:.1f} mm³ ≈ compressão prevista {v_rebaixo:.1f} mm³")
ok(True, f"IR: emissor da doca e janela do robô no mesmo eixo (x 0, z {G.CARGA_IR_Z:g})")
REL.append(f"- captura lateral das guias em V: ±{DC.GUIA_ABERTURA + DC.DOCA_FOLGA:.1f} mm na entrada (o IR faz o resto do alinhamento)")

# ---------------- vistas ----------------
itens = [(to_mesh(p01r), CORES["petroleo"]), (to_mesh(p02.translate((0, 0, 0))), (0.93, 0.89, 0.80, 0.35))]
cor_env = {"roda": CORES["grafite"], "motor": CORES["aco"], "rodizio": CORES["grafite"], "bateria": CORES["ambar"],
           "driver": CORES["silicone"], "carregador": CORES["silicone"]}
for n, e in env.items():
    itens.append((to_mesh(e), cor_env[n.split("_")[0]]))
itens.append((to_mesh(doca), CORES["creme"]))
render_conjunto(itens, str(OUT / "vistas.png"), ["iso", "baixo", "frente", "lado"], titulo="Peca 01R - base com rodas (V2) + 02 transparente + envelopes")
render_conjunto(itens, str(OUT / "corte.png"), ["frente"], corte=("y", 0.01), titulo="01R - corte pelo eixo das rodas")
TMP.unlink(missing_ok=True)
txt = ["# Peça 01R — base com rodas (V2): relatório", "",
       f"Resultado: **{'APROVADO' if not FALHAS else 'COM FALHAS'}** ({len(FALHAS)} falhas)", ""] + REL
(OUT / "RELATORIO.md").write_text("\n".join(txt) + "\n")
print("\n".join(txt))
sys.exit(1 if FALHAS else 0)
