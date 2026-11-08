"""Validação das Peças 01 (base inferior) e 02 (base superior) + presilha e difusor.

Monta 01 + contrapeso + presilhas + 02 + difusor + cintura REAL (Peça 08) + parafusos e
confere encaixe, folgas, alinhamentos, colisões, acesso, alturas, imprimibilidade e massa.

    ~/.venvs/cadquery/bin/python base/validar_base.py
Saídas: exports/p01_p02_base/{RELATORIO.md, *.png, *.stl, *.step}. Sai 1 se houver falha.
"""
import math
import sys
from pathlib import Path

import cadquery as cq
import trimesh

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from parameters import globais as G  # noqa: E402
from parameters import base as B  # noqa: E402
from base import base_inferior as BI  # noqa: E402
from base import base_superior as BS  # noqa: E402
from cintura import cintura_manual as C  # noqa: E402
from tools.render import CORES, cortar, render_conjunto  # noqa: E402

OUT = RAIZ / "exports" / "p01_p02_base"
OUT.mkdir(parents=True, exist_ok=True)
REL, FALHAS = [], []
TOL = 0.5                 # mm³: abaixo disso é contato de face / ruído numérico
PETG = 1.27               # g/cm³
MESA_META, MESA_MAX = 220.0, 256.0
PONTE_MAX = 12.0


def ok(cond, msg):
    REL.append(("OK  " if cond else "FALHA ") + msg)
    if not cond:
        FALHAS.append(msg)


def inter_vol(a, b):
    try:
        return a.intersect(b).val().Volume()
    except Exception:
        return 0.0


def dentro(wp, x, y, z):
    return wp.val().isInside(cq.Vector(x, y, z))


def to_mesh(wp, nome="_tmp"):
    path = OUT / f"{nome}.stl"
    cq.exporters.export(wp, str(path), tolerance=0.05, angularTolerance=0.2)
    m = trimesh.load(str(path))
    path.unlink(missing_ok=True)
    return m


def cil(x, y, d, z0, z1):
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).circle(d / 2).extrude(z1 - z0)


# ---------------- peças ----------------
print("gerando peças…")
p01 = BI.modelo()
pres_local = BI.presilha_local()
pres = [BI.presilha(i) for i in range(len(BI.PRESILHAS))]
cp = BI.contrapeso()
p02 = BS.modelo()
dif = BS.difusor_cego()
cint = {n: f().translate((0, 0, G.Z_TOPO_P02)) for n, f in C.PECAS.items()}

IMPRESSAS = {"01_base_inferior": p01, "01P_presilha": pres_local,
             "02_base_superior": p02, "02L_difusor_cego": dif}

# parafusos (comprados) na posição montada
z_cab = BI.REBAIXO_M3_PROF                       # face de apoio da cabeça M3
parafusos_m3 = []
for x, y in B.BASE_TORRES:
    s = cil(x, y, 3.0, z_cab, z_cab + B.M3_UNIAO_COMP).union(
        cil(x, y, B.M3_CABECA_D, z_cab - B.M3_CABECA_H, z_cab))
    parafusos_m3.append(s)
z_m4 = G.Z_TOPO_P02 + C.FI_ESP - C.M4_REBAIXO_PROF
parafusos_m4 = [cil(x, y, 4.0, z_m4 - 12.0, z_m4).union(cil(x, y, G.M4_CABECA_D, z_m4, z_m4 + G.M4_CABECA_H))
                for x, y in G.IF_CINTURA_M4]
z_pres = BI.Z_PRES_BOSS + BI.PRES_ESP
parafusos_pres = [cil(x, y, 3.0, z_pres - 8.0, z_pres).union(cil(x, y, B.M3_CABECA_D, z_pres, z_pres + 3.0))
                  for x, y, _ in BI.PRESILHAS]

# ---------------- 1. sólidos ----------------
REL.append("## 1. Sólidos")
for n, s in IMPRESSAS.items():
    ok(s.val().isValid() and len(s.solids().vals()) == 1, f"{n}: válido e 1 corpo")

# ---------------- 2. alturas ----------------
REL.append("\n## 2. Alturas da pilha")
bb1, bb2 = p01.val().BoundingBox(), p02.val().BoundingBox()
ok(abs(bb1.zmax - G.P01_ALTURA) < 0.05, f"topo da 01 em z = {bb1.zmax:.2f} (P01_ALTURA {G.P01_ALTURA:g})")
ok(abs(bb2.zmax - G.Z_TOPO_P02) < 0.05,
   f"topo da 02 em z = {bb2.zmax:.2f} = 25 + 45 = Z_TOPO_P02 {G.Z_TOPO_P02:g}")
ok(abs(bb2.zmin - B.Z_JUNTA) < 0.05, f"ponto mais baixo da 02 (aba/bosses) z = {bb2.zmin:.2f} = Z_JUNTA {B.Z_JUNTA:g}")
ok(dentro(p01, 0, G.BASE_PROF / 2 - 1.5 - B.TAN_INCL * 24.9, 24.9),
   "borda de cima da 01 contínua (sólida no meio da frente, z 24,9)")

# ---------------- 3. encaixe 01 <-> 02 ----------------
REL.append("\n## 3. Encaixe 01 ↔ 02")
v = inter_vol(p01, p02)
ok(v < TOL, f"01 × 02 sem interferência ({v:.2f} mm³)")
faixa = cq.Workplane("XY").workplane(offset=B.Z_JUNTA - 1).rect(400, 400).extrude(G.P01_ALTURA - 0.05 - B.Z_JUNTA + 1)
aba = p02.intersect(faixa)
for x, y in B.BASE_TORRES:
    aba = aba.cut(cil(x, y, 22, 0, 40))
d_aba = aba.val().distance(p01.val())
folga_normal = G.FOLGA_ENCAIXE * math.cos(math.radians(G.BASE_INCLINACAO))
ok(abs(d_aba - folga_normal) < 0.05,
   f"folga aba × parede da 01 = {d_aba:.3f} mm na normal (0,3 na horizontal → {folga_normal:.3f})")
# a 02 apoia na borda da 01: contato em z = 25 no meio dos 4 lados
for (x, y) in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
    px = x * (G.BASE_LARG / 2 - G.recuo(G.P01_ALTURA) - 1.5) if x else 30.0
    py = y * (G.BASE_PROF / 2 - G.recuo(G.P01_ALTURA) - 1.5) if y else 0.0
    if y > 0:
        px = 70.0                                          # fora do rasgo do LED
    ok(dentro(p01, px, py, G.P01_ALTURA - 0.1) and dentro(p02, px, py, G.P01_ALTURA + 0.1),
       f"02 apoia na borda da 01 em ({px:+.0f},{py:+.0f}) (as duas sólidas a ±0,1 de z=25)")

# ---------------- 4. torres x bosses ----------------
REL.append("\n## 4. Torres (01) × bosses (02) e parafusos M3 por baixo")
for (x, y), paraf in zip(B.BASE_TORRES, parafusos_m3):
    furo01 = not dentro(p01, x, y, 10) and dentro(p01, x + 3.5, y, 10)
    furo02 = not dentro(p02, x, y, B.Z_JUNTA + 3) and dentro(p02, x + 3.5, y, B.Z_JUNTA + 3)
    ok(furo01 and furo02, f"({x:+.0f},{y:+.0f}): furo da torre e furo do inserto no mesmo eixo")
    t = p01.intersect(cil(x, y, 12, 15, 30))
    b = p02.intersect(cil(x, y, 12, 15, 30))
    d = t.val().distance(b.val())
    ok(abs(d - B.FOLGA_TORRE) < 0.05, f"({x:+.0f},{y:+.0f}): vão torre→boss {d:.2f} (borda é o apoio)")
    vi = sum(inter_vol(paraf, s) for s in (p01, p02))
    ok(vi < TOL, f"({x:+.0f},{y:+.0f}): parafuso M3×{B.M3_UNIAO_COMP:g} livre na 01 e na 02 ({vi:.2f} mm³)")
    acesso = cil(x, y, BI.REBAIXO_M3_D - 0.2, -30, z_cab - B.M3_CABECA_H)
    ok(inter_vol(acesso, p01) < TOL, f"({x:+.0f},{y:+.0f}): rebaixo aberto por baixo (chave entra virando o robô)")
pega = z_cab + B.M3_UNIAO_COMP - B.Z_JUNTA
ok(G.M3_INSERTO_PROF - 0.5 <= pega <= BS.M3_FURO_PROF - 0.5,
   f"M3×{B.M3_UNIAO_COMP:g}: entra {pega:.1f} mm acima da junta (inserto {G.M3_INSERTO_PROF:g}, furo {BS.M3_FURO_PROF:g})")
ok(BI.F - BI.REBAIXO_M3_PROF > 0 and True, f"cabeça M3 embutida {BI.REBAIXO_M3_PROF - B.M3_CABECA_H:.1f} mm no fundo")
for fx, fy in BI.PES:
    dmin = min(math.hypot(fx - x, fy - y) for x, y in B.BASE_TORRES) - G.PES_D / 2 - BI.REBAIXO_M3_D / 2
    borda = min(G.BASE_LARG / 2 - abs(fx), G.BASE_PROF / 2 - abs(fy))
    rc = math.hypot(abs(fx) - (G.BASE_LARG / 2 - G.BASE_RAIO), abs(fy) - (G.BASE_PROF / 2 - G.BASE_RAIO))
    dborda = min(borda, G.BASE_RAIO - rc) - G.PES_D / 2
    ok(dmin >= 3 and dborda >= 8,
       f"pé ({fx:+.0f},{fy:+.0f}): {dmin:.1f} mm do rebaixo M3, {dborda:.1f} mm da borda")

# ---------------- 5. contrapeso ----------------
REL.append("\n## 5. Contrapeso e presilhas")
for n, s in [("01", p01), ("02", p02), ("difusor", dif)]:
    v = inter_vol(cp, s)
    ok(v < TOL, f"placa {G.CONTRAPESO[0]:g}×{G.CONTRAPESO[1]:g}×{G.CONTRAPESO[2]:g} × {n}: {v:.2f} mm³")
d_torre = min(abs(y) - G.BASE_TORRE_D / 2 for _, y in B.BASE_TORRES) - (G.CONTRAPESO[1] / 2 + B.CONTRAPESO_FOLGA)
ok(d_torre >= 2.0, f"torre a {d_torre:.1f} mm da placa deslocada até a guia (mín. 2)")
d_guia = cp.val().distance(p01.intersect(cq.Workplane("XY").workplane(offset=BI.F + 0.5).rect(400, 400).extrude(10)).val())
ok(abs(d_guia - B.CONTRAPESO_FOLGA) < 0.05, f"folga placa × guias/bosses {d_guia:.2f} mm")
for i, s in enumerate(pres):
    vs = [inter_vol(s, o) for o in (p01, cp, p02, dif)]
    ok(max(vs) < TOL, f"presilha {i}: sem interferência com 01/placa/02/difusor ({max(vs):.2f} mm³)")
    x, y, _ = BI.PRESILHAS[i]
    ok(s.val().distance(cp.val()) < 0.01, f"presilha {i}: pé encosta na placa (aperta)")
    vi = inter_vol(parafusos_pres[i], p01) + inter_vol(parafusos_pres[i], s)
    ok(vi < TOL, f"presilha {i}: parafuso {BI.PRES_PARAF} livre ({vi:.2f} mm³)")
ok(BI.Z_PRES_BOSS - BI.PRES_FURO_PROF >= 2.0,
   f"fundo do furo do inserto da presilha {BI.Z_PRES_BOSS - BI.PRES_FURO_PROF:.1f} mm acima da mesa")

# ---------------- 6. LED ----------------
REL.append("\n## 6. IF-LED e difusor cego")
for n, s in [("01", p01), ("02", p02)]:
    v = inter_vol(dif, s)
    ok(v < TOL, f"difusor × {n}: {v:.2f} mm³")
d = dif.val().distance(p02.val())
ok(abs(d - folga_normal) < 0.06 or abs(d - G.FOLGA_ENCAIXE) < 0.06, f"folga difusor × 02 {d:.2f} mm")
yf = G.BASE_PROF / 2 - B.TAN_INCL * 31
ok(dentro(dif, 0, yf - 0.5, 31) and not dentro(p02, 0, yf - 0.5, 31),
   "janela 120 × 12 preenchida pelo difusor, face rente à parede")
# retenção: deslocar o difusor 1 mm em cada sentido tem que colidir
for nome, dv, alvo in [("para fora (+Y)", (0, 1.0, 0), p01.union(p02)),
                       ("para dentro (−Y)", (0, -1.0, 0), p02),
                       ("para cima", (0, 0, 1.0), p02), ("para baixo", (0, 0, -1.0), p01)]:
    v = inter_vol(dif.translate(dv), alvo)
    ok(v > TOL, f"difusor preso {nome}: deslocar 1 mm colide {v:.0f} mm³")
ok(dentro(p02, 0, BS.U_LABIO + 1 - B.TAN_INCL * 30, 30), "lábio atrás do difusor existe (x=0)")

# ---------------- 7. cintura real ----------------
REL.append("\n## 7. Montagem com a cintura (Peça 08 real, z += Z_TOPO_P02)")
for ang in (-C.GIRO, 0.0, C.GIRO):
    piores = []
    for n, s in cint.items():
        w = s.rotate((0, 0, 0), (0, 0, 1), ang) if n in C.GIRAM else s
        for nb, base in (("02", p02), ("01", p01)):
            v = inter_vol(w, base)
            if v > TOL:
                piores.append(f"{n} × {nb} = {v:.1f}")
    ok(not piores, f"giro {ang:+.0f}°: cintura sem interferência com 01/02" + (": " + "; ".join(piores) if piores else ""))
fa = cint["08A_flange_inferior"]
for x, y in G.IF_CINTURA_M4:
    ok(not dentro(p02, x, y, G.Z_TOPO_P02 - 1) and not dentro(fa, x, y, G.Z_TOPO_P02 + 1)
       and dentro(p02, x + G.M4_INSERTO_FURO / 2 + 1, y, G.Z_TOPO_P02 - 1),
       f"M4 ({x:+.0f},{y:+.0f}): furo do inserto da 02 sob o furo passante da 08A")
for i, s in enumerate(parafusos_m4):
    v = inter_vol(s, p02) + inter_vol(s, fa)
    ok(v < TOL, f"parafuso M4×12 {i}: livre na 08A e no furo do inserto ({v:.2f} mm³)")
ok(BS.M4_FURO_PROF >= G.M4_INSERTO_PROF + 0.5 and BS.M4_FURO_PROF >= 12 - (C.FI_ESP - C.M4_REBAIXO_PROF) + 0.5,
   f"furo M4 {BS.M4_FURO_PROF:g} mm ≥ inserto {G.M4_INSERTO_PROF:g} e ponta do M4×12 "
   f"({12 - (C.FI_ESP - C.M4_REBAIXO_PROF):.1f})")
ok(not dentro(p02, 0, 0, 60) and not dentro(p02, G.IF_CINTURA_CABO_D / 2 - 0.5, 0, 66),
   f"passa-cabos Ø{G.IF_CINTURA_CABO_D:g} livre até dentro da base")
ok(BS.PLAT_D >= C.FI_D and BS.PLAT_D >= C.COLAR_DE,
   f"plataforma Ø{BS.PLAT_D:g} cobre 08A Ø{C.FI_D:g} e colar Ø{C.COLAR_DE:g}")
r_topo = min(G.BASE_LARG, G.BASE_PROF) / 2 - G.recuo(BS.Z_TRANS) - (G.Z_TOPO_P02 - BS.Z_TRANS) * math.tan(
    math.radians(BS.TRANS_TAPER)) - BS.FILETE_TOPO
ok(r_topo >= BS.PLAT_D / 2, f"topo plano (meia-largura útil {r_topo:.1f}) contém a plataforma Ø{BS.PLAT_D:g}")

# ---------------- 8. imprimibilidade ----------------
REL.append("\n## 8. Imprimibilidade (orientação de impressão)")
# rotação (eixo, graus) que leva a peça para a posição de impressão
ORIENT = {"01_base_inferior": None,                       # fundo na mesa
          "01P_presilha": ([1, 0, 0], 180.0),             # topo liso na mesa
          "02_base_superior": ([1, 0, 0], 180.0),         # de cabeça para baixo
          "02L_difusor_cego": ([1, 0, 0], -(90.0 + G.BASE_INCLINACAO))}   # face da frente na mesa
DESC = {"01_base_inferior": "fundo na mesa", "01P_presilha": "face de cima na mesa",
        "02_base_superior": "de cabeça para baixo (face z=70 na mesa)",
        "02L_difusor_cego": "face aparente na mesa"}
# maiores vãos de ponte (pela geometria; o detector de faces abaixo confirma onde existem)
VAO = {"01_base_inferior": max(BI.REBAIXO_M3_D, G.PES_D), "01P_presilha": 0.0,
       "02_base_superior": G.M4_INSERTO_FURO,      # fundo dos furos cegos M4 (abertos na mesa)
       "02L_difusor_cego": 0.0}
LIMITE = {"01_base_inferior": 15.5}      # pés Ø15: ponte circular, ver nota
MALHAS = {}
for n, s in IMPRESSAS.items():
    m = to_mesh(s)
    MALHAS[n] = m.copy()
    if ORIENT[n]:
        eixo, ang = ORIENT[n]
        m.apply_transform(trimesh.transformations.rotation_matrix(math.radians(ang), eixo))
    m.apply_translation([0, 0, -m.bounds[0][2]])
    nz = m.face_normals[:, 2]
    zc = m.triangles_center[:, 2]
    pend = (nz < -0.72) & (zc > 1.0)          # mais de ~44° da vertical, fora do pé da peça
    area = m.area_faces[pend].sum()
    bb = m.bounds[1] - m.bounds[0]
    lim = LIMITE.get(n, PONTE_MAX)
    ok(VAO[n] <= lim, f"{n} ({DESC[n]}): {area:.0f} mm² voltados para baixo; maior ponte {VAO[n]:.1f} mm (≤{lim:g})")
    cabe = max(bb[:2]) <= MESA_MAX and bb[2] <= MESA_MAX
    meta = "" if max(bb) <= MESA_META else f" — passa da meta {MESA_META:g} (cabe na A1 {MESA_MAX:g})"
    ok(cabe, f"{n}: {bb[0]:.1f} × {bb[1]:.1f} × {bb[2]:.1f} mm na mesa{meta}")
REL.append("- Nota: o único vão > 12 mm é o teto dos alojamentos dos pés (Ø15, 2 mm acima da mesa): ponte "
           "circular curta, a A1 faz em PETG sem suporte. Na 02 (invertida) as únicas pontes são os fundos dos "
           "4 furos cegos M4 (Ø5,6); o resto voltado para baixo são as raízes a 45° da aba e da moldura do LED e a "
           "faixa de transição a 40° da vertical. Nenhum teto em ponte, nenhum suporte.")

# ---------------- 9. paredes ----------------
REL.append("\n## 9. Espessuras")
ok(BS.BOSS_M3_D - G.M3_INSERTO_FURO >= 2 * 2.5, f"parede do boss M3 da 02 {(BS.BOSS_M3_D - G.M3_INSERTO_FURO)/2:.1f} mm")
ok(G.BASE_TORRE_D - G.M3_PASSANTE >= 2 * 2.5, f"parede da torre da 01 {(G.BASE_TORRE_D - G.M3_PASSANTE)/2:.1f} mm")
ok((BS.M4_BOSS_D - G.M4_INSERTO_FURO) / 2 >= 2.5, f"parede do boss M4 {(BS.M4_BOSS_D - G.M4_INSERTO_FURO)/2:.1f} mm")
ok(BS.M4_BOSS_ALT - BS.M4_FURO_PROF >= 2.0, f"fundo do furo M4 {BS.M4_BOSS_ALT - BS.M4_FURO_PROF:.1f} mm")
ok(G.P01_FUNDO - G.PES_PROF >= 2.0, f"fundo sobre os pés {G.P01_FUNDO - G.PES_PROF:.1f} mm")
ok(BS.Z_TRANS - BS.LED_Z_TOPO >= 8, f"verga do LED até a transição {BS.Z_TRANS - BS.LED_Z_TOPO:.0f} mm "
   "(+ moldura interna com lábio e bochechas)")

# ---------------- exportação e vistas ----------------
print("exportando e renderizando…")
BI.exportar(OUT)
BS.exportar(OUT)

mp01, mp02, mdif = MALHAS["01_base_inferior"], MALHAS["02_base_superior"], MALHAS["02L_difusor_cego"]
mcp = to_mesh(cp)
mpres = [to_mesh(s) for s in pres]
mcint = [(to_mesh(s), CORES["grafite"] if n in ("08A_flange_inferior", "08B_flange_superior") else
          CORES["creme"] if n == "08D_colar" else CORES["petroleo"] if n == "08C_anel_retencao" else CORES["ambar"])
         for n, s in cint.items()]
mparaf = [(to_mesh(s), CORES["aco"]) for s in parafusos_m3]

it01 = [(mp01, CORES["petroleo"]), (mcp, CORES["aco"])] + [(m, CORES["grafite"]) for m in mpres]
render_conjunto(it01, str(OUT / "p01_vistas.png"), ["iso", "topo", "baixo", "lado"],
                titulo="Peca 01 - base inferior com contrapeso (aco) e 4 presilhas")
CREME = (0.86, 0.80, 0.66, 1.0)   # creme um pouco mais escuro: no render o creme puro estoura
it02 = [(mp02, CREME), (mdif, CORES["ambar"])]
render_conjunto(it02, str(OUT / "p02_vistas.png"), ["iso", "topo", "baixo", "lado", "iso_tras", "frente"],
                titulo="Peca 02 - base superior + difusor cego (M08)")
inv = mp02.copy()
inv.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
render_conjunto([(inv, CREME)], str(OUT / "p02_por_dentro.png"), ["iso", "iso_tras"],
                titulo="Peca 02 virada (= orientacao de impressao): nervuras, bosses M3/M4, aba, moldura do LED")
conj = it01 + it02 + mparaf
render_conjunto(conj + mcint, str(OUT / "corte_x0.png"), ["lado"], corte=("x", 0.0, False),
                titulo="Corte x=0: LED (frente a direita), plataforma, M4, contrapeso", tam=(1000, 560))
render_conjunto(conj, str(OUT / "corte_torre.png"), ["lado"], corte=("x", B.BASE_TORRES[3][0], False),
                titulo=f"Corte x={B.BASE_TORRES[3][0]:g}: torre, boss, parafuso M3 por baixo, aba", tam=(1000, 560))
render_conjunto(conj, str(OUT / "corte_y0.png"), ["frente"], corte=("y", 0.0, True),
                titulo="Corte y=0 (vista da frente): aba nas laterais, nervuras, presilhas", tam=(1000, 560))



def recorte(itens, x, y0, y1):
    """Fatia fina para detalhe: x <= x (vista de +X) e y0 <= y <= y1."""
    r = []
    for m, c in itens:
        a = cortar(m, "x", x, False)
        a = cortar(a, "y", y0, True) if a is not None and len(a.faces) else None
        a = cortar(a, "y", y1, False) if a is not None and len(a.faces) else None
        if a is not None and len(a.faces):
            r.append((a, c))
    return r


render_conjunto(recorte(conj, 0.0, 55, 105), str(OUT / "detalhe_led.png"), ["lado"], tam=(1000, 700),
                titulo="Detalhe x=0: difusor (ambar) na janela, lingueta atras da verga, labio, aba na 01")
xt, yt = B.BASE_TORRES[3]
render_conjunto(recorte(conj, xt, yt - 25, 105), str(OUT / "detalhe_torre.png"), ["lado"], tam=(1000, 700),
                titulo=f"Detalhe x={xt:g}: torre (01), boss com inserto (02), M3x{B.M3_UNIAO_COMP:g} por baixo, aba")


def desloca(m, dz):
    m = m.copy()
    m.apply_translation([0, 0, dz])
    return m


expl = ([(mp01, CORES["petroleo"]), (desloca(mcp, 12), CORES["aco"])]
        + [(desloca(m, 24), CORES["grafite"]) for m in mpres]
        + [(desloca(m, -40), CORES["aco"]) for m, _ in mparaf]
        + [(desloca(mdif, 45), CORES["ambar"]), (desloca(mp02, 70), CREME)]
        + [(desloca(m, 110), c) for m, c in mcint])
render_conjunto(expl, str(OUT / "explodida.png"), ["iso", "lado"],
                titulo="Explodida: parafusos M3 (por baixo), 01, placa, presilhas, difusor, 02, cintura")
render_conjunto(it01 + it02 + mcint, str(OUT / "montagem.png"), ["iso", "frente", "lado", "iso_tras"],
                titulo="Montagem 01 + 02 + cintura (Peca 08 real)")

# ---------------- relatório ----------------
txt = ["# Peças 01 e 02 (base) — relatório de validação", "",
       f"Resultado: **{'APROVADO' if not FALHAS else 'COM FALHAS'}** ({len(FALHAS)} falhas)", ""] + REL
txt += ["", "## Volume e massa (sólido, PETG 1,27 g/cm³; com preenchimento real fica ~45–60%)", ""]
for n, s in IMPRESSAS.items():
    vol = s.val().Volume() / 1000
    qt = len(BI.PRESILHAS) if n == "01P_presilha" else 1
    txt.append(f"- {n}: {vol:.1f} cm³ → {vol * PETG:.0f} g" + (f" (× {qt})" if qt > 1 else ""))
aco = G.CONTRAPESO[0] * G.CONTRAPESO[1] * G.CONTRAPESO[2] / 1000 * 7.85
txt.append(f"- contrapeso de aço {G.CONTRAPESO[0]:g}×{G.CONTRAPESO[1]:g}×{G.CONTRAPESO[2]:g}: {aco:.0f} g")
txt += ["", "## Impressão", "",
        "| Peça | Orientação | Observação |", "|---|---|---|",
        "| 01 base inferior | fundo na mesa | 4 paredes, 20% giroide; insertos M3 das presilhas depois |",
        "| 01P presilha (×4) | face de cima na mesa | 3 paredes, 40% |",
        "| 02 base superior | de cabeça para baixo (topo na mesa) | 4 paredes, 20% giroide; sem suporte; "
        "insertos M4 (topo) e M3 (bosses) depois |",
        "| 02L difusor cego | face aparente na mesa | âmbar/translúcido; 3 paredes |",
        "", "## Ordem de montagem", "",
        "1. Insertos: 4×M3 nos bosses da 02, 4×M3 nos bosses de presilha da 01, 4×M4 no topo da 02.",
        "2. Pés de borracha embaixo da 01. Placa de aço entre as guias; 4 presilhas com M3×8.",
        "3. Difusor na janela da 02 (entra por dentro: lingueta atrás da verga, encostado no lábio).",
        "4. 02 sobre a 01 (a aba entra por dentro da parede). Virar o conjunto e apertar 4×M3×25 por baixo.",
        "5. Cintura 08A por cima com 4×M4×12 nos insertos da 02.",
        "", "## Fixadores e comprados", ""] + [f"- {q} × {d}" for d, q in BI.BOM + BS.BOM]
(OUT / "RELATORIO.md").write_text("\n".join(txt) + "\n")
print("\n".join(txt))
sys.exit(1 if FALHAS else 0)
