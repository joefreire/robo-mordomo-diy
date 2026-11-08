"""Validação das Peças 05 (braço esquerdo + adaptador V1), 06 (bandeja) e 07 (braço direito
+ mão-luva) com as peças REAIS do ombro (ombro/ombro_manual.py).

    ~/.venvs/cadquery/bin/python braco/validar_bracos.py
Saídas: exports/p05_p06_p07_bracos/ (RELATORIO.md, PNGs, STL+STEP na orientação de impressão).
Sai com código 1 se houver FALHA.

Convenção de giro = a do validar_ombro.py (gira(): rotação −ang em torno do Z local), que é
a que os furos de indexação e o batente REAIS do rotor permitem.
"""
import math
import sys
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely.ops import polylabel, unary_union

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from parameters import globais as G  # noqa: E402
from parameters import bracos as P  # noqa: E402
from ombro import ombro_manual as O  # noqa: E402
from braco import braco as B  # noqa: E402
from braco import maos as M  # noqa: E402
from braco import bandeja as T  # noqa: E402
from tools.render import CORES, render_conjunto  # noqa: E402
from ombro.validar_ombro import HIP  # noqa: E402

OUT = RAIZ / "exports" / "p05_p06_p07_bracos"
OUT.mkdir(parents=True, exist_ok=True)
TMP = OUT / "_tmp.stl"
TOL = 0.5                 # mm³
G_ACEL = 9.81
TRAVA_NM = 2.6            # capacidade estimada do pino de indexação (validar_ombro.py)
CARGA_KG = 0.300
INSERTO_ARRANQUE_N = 400.0   # arrancamento conservador de inserto M3 em PETG (catálogo 500–900 N)
PARAF_M3_N = 2900.0          # carga de prova M3 8.8 (≈ 0,58 × 800 MPa × 5,03 mm²... arredondado)

rel, falhas, avisos = [], [], []


def ok(c, m):
    rel.append(("OK  " if c else "FALHA ") + m)
    if not c:
        falhas.append(m)


def aviso(m):
    rel.append("AVISO " + m)
    avisos.append(m)


def vol(a, b):
    ba, bb = a.val().BoundingBox(), b.val().BoundingBox()
    if (ba.xmax < bb.xmin or bb.xmax < ba.xmin or ba.ymax < bb.ymin or bb.ymax < ba.ymin
            or ba.zmax < bb.zmin or bb.zmax < ba.zmin):
        return 0.0
    try:
        return a.intersect(b).val().Volume()
    except Exception:
        return 0.0


def gira(wp, ang, lado="esquerdo"):
    return O.girar(wp, ang, lado)   # convenção única (ombro_manual.girar)


def to_mesh(wp, tol=0.05):
    cq.exporters.export(wp, str(TMP), tolerance=tol, angularTolerance=0.2)
    return trimesh.load(str(TMP))


def caixa(dx, dy, dz, z0):
    return cq.Workplane("XY").box(dx, dy, dz).translate((0, 0, z0 + dz / 2))


TRONCO = caixa(G.TRONCO_LARG, G.TRONCO_PROF, G.TRONCO_ALT, G.Z_PISO_TRONCO)
BASE = caixa(G.BASE_LARG, G.BASE_PROF, 70.0, 0.0)
MESA = caixa(800, 800, 20, -20.0)


def base_real():
    """Contorno real da base (Peças 01+02) pelos globais: retângulo 225×200 R35 na mesa,
    laterais fechando 6° até z = 70. Só informativo (o critério é a caixa)."""
    h = G.Z_TOPO_P02
    r = G.recuo(h)
    s0 = cq.Workplane("XY").rect(G.BASE_LARG, G.BASE_PROF).val()
    w0 = cq.Workplane("XY").sketch().rect(G.BASE_LARG, G.BASE_PROF).vertices().fillet(G.BASE_RAIO).finalize()
    w1 = (cq.Workplane("XY").workplane(offset=h).sketch().rect(G.BASE_LARG - 2 * r, G.BASE_PROF - 2 * r)
          .vertices().fillet(G.BASE_RAIO - r).finalize())
    return cq.Workplane("XY").add(cq.Solid.makeLoft([w0._getFaces()[0].outerWire(), w1._getFaces()[0].outerWire()]))


BASE_REAL = base_real()


# ============================================================
# conjuntos (LOCAL do ombro do lado, ombro em 0°)
# ============================================================
def conjunto(lado):
    """{nome: (wp_local, cor, grupo, impressão)}; grupo: braco | mao | bandeja."""
    num = B.NUMERO[lado]
    d = {}
    cores = {"A_metade_interna": "creme", "B_metade_externa": "creme", "C_anel_punho": "grafite", "F_friso": "petroleo"}
    for k, s in B.construir(lado).items():
        d[num + k] = (s, cores[k], "braco")
    if lado == "esquerdo":
        d["05D_adaptador_v1"] = (B.no_punho(M.adaptador_v1(), lado), "creme", "mao")
        d["06B_cubo"] = (B.no_punho(T.no_adaptador(T.cubo()), lado), "grafite", "bandeja")
        d["06A_bandeja"] = (B.no_punho(T.no_adaptador(T.bandeja()), lado), "grafite", "bandeja")
        d["06C_anel_decorativo"] = (B.no_punho(T.no_adaptador(T.anel_decorativo()), lado), "petroleo", "bandeja")
    else:
        d["07E_mao_luva"] = (B.no_punho(M.luva(), lado), "grafite", "mao")
    return d


def canonico(nome):
    """Peça no referencial em que é desenhada + transformação para impressão."""
    k = nome[2:]
    if k in ("A_metade_interna", "B_metade_externa", "F_friso", "C_anel_punho"):
        return None
    f = {"D_adaptador_v1": M.adaptador_v1, "E_mao_luva": M.luva, "A_bandeja": T.bandeja,
         "B_cubo": T.cubo, "C_anel_decorativo": T.anel_decorativo}[k]
    return f()


def impressao(nome, wp_local, lado):
    k = nome[2:]
    if k in ("A_metade_interna", "B_metade_externa", "F_friso", "C_anel_punho"):
        return B.para_impressao(k, wp_local, lado)
    w = canonico(nome)
    if k == "D_adaptador_v1":
        w = w.rotate((0, 0, 0), (1, 0, 0), 90)          # Y_H (cima) -> Z: em pé
    elif k == "B_cubo":
        w = w.rotate((0, 0, 0), (1, 0, 0), 180)         # face da bandeja na mesa
    bb = w.val().BoundingBox()
    return w.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))


ORIENT = {
    "A_metade_interna": "plano de divisão na mesa (face do tronco para cima)",
    "B_metade_externa": "plano de divisão na mesa",
    "C_anel_punho": "costas na mesa, face IF-PUNHO para cima",
    "F_friso": "deitado",
    "D_adaptador_v1": "em pé: fundo plano na mesa, face IF-BANDEJA para cima",
    "E_mao_luva": "face do punho na mesa",
    "A_bandeja": "fundo na mesa (superfície útil para cima)",
    "B_cubo": "face da bandeja na mesa (rasgo da chave para cima)",
    "C_anel_decorativo": "deitado",
}
PAREDES = {"E_mao_luva": "3 paredes, 15%", "D_adaptador_v1": "4 paredes, 25% (insertos)",
           "B_cubo": "4 paredes, 40% (insertos)", "C_anel_punho": "4 paredes, 40% (insertos)"}


# ============================================================
# imprimibilidade (malha na orientação de impressão)
# ============================================================
def analisar_impressao(m):
    """Vão máximo sem apoio: faces voltadas para baixo com mais de 60° da vertical (inclui as
    horizontais = pontes), acima de 0,3 mm da mesa, agrupadas por vizinhança; vão = 2 × raio
    inscrito da projeção do grupo na mesa (ponte de 10 mm ou balanço de 5 mm dão 10).
    O teto de furo horizontal dá vão pequeno (faixa estreita), como deve."""
    n = m.face_normals
    c = m.triangles_center
    sel = np.where((n[:, 2] < -0.866) & (c[:, 2] > 0.3) & (m.area_faces > 1e-7))[0]
    if len(sel) == 0:
        return 0.0, 0.0
    sset = set(sel.tolist())
    adj = [(a, b) for a, b in m.face_adjacency if a in sset and b in sset]
    grupos = trimesh.graph.connected_components(adj, nodes=sel, min_len=1)
    maior, area = 0.0, 0.0
    for g in grupos:
        polys = [Polygon(m.triangles[i][:, :2]).buffer(0.02) for i in g]
        u = unary_union([p for p in polys if p.area > 0])
        for gg in getattr(u, "geoms", [u]):
            if gg.area < 0.3:
                continue
            pt = polylabel(gg, tolerance=0.05)
            vao = 2 * gg.boundary.distance(pt)
            if vao > maior:
                maior, area = vao, gg.area
    return maior, area


# ============================================================
# massa
# ============================================================
def massa_g(wp):
    s = wp.val()
    V, A = s.Volume(), s.Area()
    casca = min(V, A * P.PAREDES_MM)
    return P.PETG_DENS * (casca + P.PREENCH * max(0.0, V - casca)) / 1000, P.PETG_DENS * V / 1000


# ============================================================
def validar():
    conj = {l: conjunto(l) for l in ("esquerdo", "direito")}
    ombro = {l: O.construir(l) for l in ("esquerdo", "direito")}

    # ---------------- 1. sólidos e tamanhos ----------------
    rel.append("## 1. Sólidos, tamanho e orientação de impressão")
    impressos = {}
    for lado, d in conj.items():
        for nome, (s, _, _) in d.items():
            if nome in impressos:
                continue
            ok(s.val().isValid() and len(s.solids().vals()) == 1, f"{nome}: válido e 1 corpo")
            w = impressao(nome, s, lado)
            impressos[nome] = w
            bb = w.val().BoundingBox()
            ok(max(bb.xlen, bb.ylen, bb.zlen) <= 220, f"{nome}: {bb.xlen:.0f}×{bb.ylen:.0f}×{bb.zlen:.0f} mm "
               f"(≤ 220) — {ORIENT[nome[2:]]}")

    # ---------------- 2. encaixe na lingueta REAL ----------------
    rel.append("\n## 2. Encaixe braço ↔ lingueta IF-BRAÇO (rotor real 09B/10B)")
    for lado in ("esquerdo", "direito"):
        num = B.NUMERO[lado]
        rotor = ombro[lado]["B_rotor_braco"]
        braco = conj[lado][num + "A_metade_interna"][0].union(conj[lado][num + "B_metade_externa"][0])
        v0 = vol(braco, rotor)
        ok(v0 < TOL, f"{num}: soquete sem interferência com o rotor ({v0:.2f} mm³)")
        for desc, dv in (("+tangencial", (0.45, 0, 0)), ("−tangencial", (-0.45, 0, 0)), ("face de fora", (0, 0, 0.45))):
            perto = vol(braco, rotor.translate(dv))
            longe = vol(braco, rotor.translate(tuple(c * 0.2 / 0.45 for c in dv)))
            ok(perto > TOL and longe < TOL, f"{num}: lado {desc}: folga entre 0,2 e 0,45 mm (encosta só com 0,45)")
        dfundo = vol(braco, rotor.translate((0, -0.45, 0)))
        ok(dfundo > TOL, f"{num}: fundo do soquete encosta no topo da lingueta (r={G.IF_BRACO_LING_R1:g}) com 0,45 mm")
        for r in G.IF_BRACO_M3_R:
            haste = cq.Workplane("XY").workplane(offset=O.Z_B1 - 5).center(0, -r).circle(1.45).extrude(P.SOQ_Z1 - O.Z_B1 + 6)
            if lado == "direito":
                haste = haste.mirror("YZ")
            livre = vol(haste, rotor) + vol(haste, braco)
            desl = vol(haste.translate((0.7, 0, 0)), braco)
            ok(livre < TOL and desl > TOL, f"{num}: M3 r={r:g}: furo do braço coaxial ao inserto da lingueta "
               f"(haste Ø2,9 livre: {livre:.2f} mm³; deslocada 0,7 mm bate)")

    # ---------------- 3. curso ----------------
    rel.append("\n## 3. Curso do ombro a cada 15°: colisões (peças do ombro, tronco 185×105×190, base 225×200×70, mesa)")
    rel.append("Convenção do validar_ombro.py (furos/batente reais). Bandeja avaliada à parte.")
    curso_bandeja = []
    for lado in ("esquerdo", "direito"):
        num = B.NUMERO[lado]
        gmin, gmax = O.CURSO[lado]
        fixos = {k: O.posicionar(v, lado) for k, v in ombro[lado].items() if k not in O.GIRAM}
        dmin_global = 1e9
        ang = gmin
        while ang <= gmax + 1e-6:
            rot = O.posicionar(gira(ombro[lado]["B_rotor_braco"], ang, lado), lado)
            ruins, ruins_b = [], []
            for nome, (s, _, grupo) in conj[lado].items():
                sp = O.posicionar(gira(s, ang, lado), lado)
                obst = dict(fixos)
                obst["rotor"] = rot
                obst["tronco"], obst["base"], obst["mesa"] = TRONCO, BASE, MESA
                for on, ow in obst.items():
                    v = vol(sp, ow)
                    if v > TOL:
                        (ruins_b if grupo == "bandeja" else ruins).append(f"{nome[3:]}×{on}={v:.0f}")
                if nome.endswith("B_metade_externa"):
                    for on in ("C_tampa_pressao", "D_manipulo"):
                        dmin_global = min(dmin_global, sp.val().distance(fixos[on].val()))
            real = ""
            if any("×base=" in r for r in ruins):
                vr = sum(vol(O.posicionar(gira(s, ang, lado), lado), BASE_REAL) for s, _, g in conj[lado].values() if g != "bandeja")
                real = f" [base REAL inclinada: {'livre' if vr < TOL else f'{vr:.0f} mm³'}]"
                if vr < TOL:
                    # 07/11: a caixa 225×200×70 é conservadora (a base real é inclinada e tem
                    # topo de 110). Vale a geometria real; a caixa vira só observação.
                    rel.append(f"- obs. {num} {ang:+.0f}°: toca a CAIXA da base, mas a base real está livre")
                    ruins = [r for r in ruins if "×base=" not in r]
                    real = ""
            ok(not ruins, f"{num} {ang:+5.0f}°: braço + mão livres" + ("" if not ruins else " — " + "; ".join(ruins) + real))
            if lado == "esquerdo":
                curso_bandeja.append((ang, ruins_b))
            ang += O.PASSO_INDEX
        ok(dmin_global >= 0.5, f"{num}: folga mínima braço ↔ tampa/manípulo do ombro no curso: {dmin_global:.1f} mm (≥ 0,5)")
    livres = [a for a, r in curso_bandeja if not r]
    rel.append(f"- 05 com bandeja: livre em {', '.join(f'{a:+.0f}°' for a in livres) or 'nenhuma posição'}")
    for a, r in curso_bandeja:
        if r:
            aviso(f"05 {a:+.0f}° COM bandeja: {'; '.join(r)} -> tirar a bandeja antes de levar o braço a essa posição")
    ok(0.0 in livres, "05 em 0° (serviço) com bandeja: livre")

    # ---------------- 4. IF-PUNHO igual ----------------
    rel.append("\n## 4. IF-PUNHO igual nos dois braços (sondas no referencial H do punho)")
    assin = {}
    for lado in ("esquerdo", "direito"):
        num = B.NUMERO[lado]
        pl = B.plano_punho(lado)
        anel = conj[lado][num + "C_anel_punho"][0]
        braco = conj[lado][num + "A_metade_interna"][0].union(conj[lado][num + "B_metade_externa"][0])
        mao = [v[0] for k, v in conj[lado].items() if v[2] == "mao"][0]

        def sonda(xy, z0, z1, d=2.9):
            s = cq.Workplane("XY").workplane(offset=z0).center(*xy).circle(d / 2).extrude(z1 - z0)
            return cq.Workplane("XY").add(s.val().moved(cq.Location(pl)))

        res = []
        for a in G.IF_PUNHO_M3_ANG:            # insertos do anel (IF) + furo passante da mão
            xy = B.pos_if(a)
            res.append(vol(sonda(xy, -G.M3_INSERTO_PROF, 5.5, 3.6), anel) < TOL)
            res.append(vol(sonda(xy, 0.2, 5.5), mao) < TOL)
            res.append(vol(sonda((xy[0] + 1.3, xy[1]), -G.M3_INSERTO_PROF, -0.5, 3.6), anel) > TOL)
        for a in P.ANEL_M3_ANG:                # anel -> braço
            xy = B.pos_if(a)
            res.append(vol(sonda(xy, -P.ANEL_ESP - 5.5, -P.ANEL_ESP - 0.3, 3.6), braco) < TOL)
            res.append(vol(sonda(xy, -P.ANEL_ESP, 0.0), anel) < TOL)
        cw, ch = G.IF_PUNHO_CHAVE
        chave = cq.Workplane("XY").add(cq.Solid.makeBox(cw - 0.4, 2.5, ch - 0.2, cq.Vector(-(cw - 0.4) / 2, P.CHAVE_R0 + 0.2, 0.1)))
        chave = cq.Workplane("XY").add(chave.val().moved(cq.Location(pl)))
        res.append(vol(chave, anel) > 10)
        res.append(vol(anel, mao) < TOL)
        res.append(vol(sonda((0, 0), -P.ANEL_ESP - 3, 0.5, 9.5), anel.union(braco)) < TOL)
        assin[lado] = res
        ok(all(res), f"{num}: 3 insertos a {G.IF_PUNHO_M3_ANG} r={G.IF_PUNHO_M3_R:g}, chave a 90°, cabo Ø{G.IF_PUNHO_CABO_D:g}, "
           f"2 M3 do anel e furos da {'mão' if lado == 'direito' else 'adaptador'} alinhados ({sum(res)}/{len(res)})")
    ok(assin["esquerdo"] == assin["direito"], "mesma assinatura nos dois punhos (mão, adaptador e garra futura servem nos dois)")
    rotacionada = [vol(cq.Workplane("XY").add(cq.Solid.makeCylinder(1.45, 6, cq.Vector(*B.pos_if(a + 20), -0.5))),
                       B.anel_punho()) < TOL
                   for a in G.IF_PUNHO_M3_ANG]
    ok(not all(rotacionada), "padrão assimétrico: a mão girada 20° não encontra os 3 insertos")

    # ---------------- 5. bandeja na pose de serviço ----------------
    rel.append("\n## 5. Bandeja (Peça 06) na pose de serviço (ombro esquerdo 0°)")
    band = O.posicionar(conj["esquerdo"]["06A_bandeja"][0], "esquerdo")
    faces = sorted(band.faces().vals(), key=lambda f: -f.Area())
    nrm = faces[0].normalAt()
    incl = math.degrees(math.acos(min(1.0, abs(nrm.z))))
    ok(incl < 0.1, f"fundo da bandeja horizontal: inclinação {incl:.3f}°")
    cen = band.val().BoundingBox().center
    alc = abs(cen.y - G.IF_OMBRO_Y)
    ok(abs(alc - G.BRACO_ESQ_ALCANCE) < 0.5, f"alcance horizontal (plano do ombro -> centro da bandeja): {alc:.1f} mm "
       f"(alvo {G.BRACO_ESQ_ALCANCE:g})")
    ok(abs(cen.x - (-(G.IF_OMBRO_X + P.Z_TUBO))) < 0.5, f"bandeja centrada sobre o braço (x = {cen.x:.1f})")
    zb = band.val().BoundingBox().zmin
    rel.append(f"- fundo da bandeja a z = {zb:.0f} mm; segmento horizontal a z = {G.IF_OMBRO_Z - G.BRACO_ESQ_ALTURA:g} "
               f"(altura {G.BRACO_ESQ_ALTURA:g} abaixo do eixo do ombro)")
    if band.val().BoundingBox().ymin <= G.TRONCO_PROF / 2:
        aviso("borda de trás da bandeja dentro da profundidade do tronco")
    else:
        rel.append(f"- borda de trás da bandeja a {band.val().BoundingBox().ymin - G.TRONCO_PROF / 2:.0f} mm da frente do tronco")
    # troca do adaptador sem mexer na bandeja (cubo continua na bandeja)
    pl = B.plano_punho("esquerdo")
    adapt = conj["esquerdo"]["05D_adaptador_v1"][0]
    fixos = [conj["esquerdo"][k][0] for k in ("06A_bandeja", "06B_cubo", "05C_anel_punho", "05A_metade_interna", "05B_metade_externa")]

    def mov(w, dh):
        v = pl.toWorldCoords(dh) - pl.toWorldCoords((0, 0, 0))
        return w.translate((v.x, v.y, v.z))

    caminho = [(0, -1.0, 0), (0, -3.5, 0), (0, -3.5, 3.0), (0, -3.5, 15.0), (0, -20.0, 15.0)]
    bate = [max(vol(mov(adapt, d), f) for f in fixos) for d in caminho]
    ok(max(bate) < TOL, "adaptador sai sem desmontar a bandeja: tirar 2×M3 (cubo) + 3×M3 (punho), descer 3,5, "
       f"afastar 15 do punho (máx. interferência {max(bate):.2f} mm³); cubo fica preso à bandeja")
    ok(vol(adapt, conj["esquerdo"]["06B_cubo"][0]) < TOL and vol(mov(adapt, (0, 0.4, 0)), conj["esquerdo"]["06B_cubo"][0]) > TOL,
       "língua do adaptador entra no rasgo assimétrico do cubo e a face IF-BANDEJA apoia o cubo")
    cubo_t = T.cubo()
    girado = vol(cq.Workplane("XY").add(M.adaptador_v1().val().moved(cq.Location(T.plano_bandeja()).inverse))
                 .rotate((0, 0, 0), (0, 0, 1), 180), cubo_t)
    ok(girado > TOL, f"cubo girado 180° não monta (chave fora de centro: {girado:.0f} mm³ de interferência)")

    # ---------------- 6. massas e momento ----------------
    rel.append("\n## 6. Massa real (PETG 1,27 g/cm³; casca 4 paredes + 15%; entre parênteses = sólido, limite superior)")
    massas, cms = {}, {}
    for lado in ("esquerdo", "direito"):
        for nome, (s, _, g) in conj[lado].items():
            me, ms = massa_g(s)
            massas[nome] = (me, ms)
            cms[nome] = s.val().Center()
            rel.append(f"- {nome}: {me:.0f} g ({ms:.0f} g)")
    FIX_G = 12.0   # parafusos/insertos/pinos por braço
    rel.append(f"- fixadores por braço (estimativa): {FIX_G:.0f} g")
    rel.append("\n### Momento no eixo do ombro (máximo no curso, passo 1°)")
    rel.append("| Lado | Itens | Massa (g) | M real (N·m) | M hipótese HIP (N·m) | Trava ~2,6 N·m |")
    rel.append("|---|---|---|---|---|---|")
    hip = {}
    for lado in ("esquerdo", "direito"):
        gmin, gmax = O.CURSO[lado]
        ang_crit = 90.0 if gmax >= 90 else max(abs(gmin), abs(gmax))
        hip[lado] = sum(m * G_ACEL * dd for _, m, dd in HIP[lado]) * math.sin(math.radians(ang_crit))

    def momento(itens, lado):
        """itens: [(kg, Vector local)]; devolve máximo |M| no curso e o ângulo."""
        gmin, gmax = O.CURSO[lado]
        melhor = (0.0, 0.0)
        for a in np.arange(gmin, gmax + 0.01, 1.0):
            t = math.radians(-a)
            m = 0.0
            for kg, c in itens:
                x = c.x * math.cos(t) - c.y * math.sin(t)
                y_rob = (-x if lado == "esquerdo" else x)      # X local: trás (esq.) / frente (dir.)
                m += kg * G_ACEL * y_rob / 1000
            if abs(m) > abs(melhor[0]):
                melhor = (m, a)
        return melhor

    def itens_de(lado, grupos):
        it = [(massas[n][0] / 1000, cms[n]) for n, v in conj[lado].items() if v[2] in grupos]
        cb = [cms[n] for n, v in conj[lado].items() if n.endswith("B_metade_externa")][0]
        it.append((FIX_G / 1000, cb))
        return it

    W, u, v, f = B.frame_punho("esquerdo")
    tc = conj["esquerdo"]["06A_bandeja"][0].val().Center()
    carga = cq.Vector(tc.x, tc.y + 25, tc.z)          # copo: CG 25 mm acima do fundo
    casos = {
        "esquerdo": [("braço + adaptador + bandeja (vazia)", itens_de("esquerdo", ("braco", "mao", "bandeja"))),
                     ("… + 300 g na bandeja", itens_de("esquerdo", ("braco", "mao", "bandeja")) + [(CARGA_KG, carga)])],
        "direito": [("braço + mão-luva", itens_de("direito", ("braco", "mao")))],
    }
    Wd, ud, vd, fd = B.frame_punho("direito")
    garra = [(0.12, cq.Vector(Wd[0] + fd[0] * 40, Wd[1] + fd[1] * 40, Wd[2])), (0.10, cq.Vector(Wd[0] + fd[0] * 70, Wd[1] + fd[1] * 70, Wd[2]))]
    casos["direito"].append(("braço + garra V2 120 g + objeto 100 g (hipóteses HIP)", itens_de("direito", ("braco",)) + garra))
    mreal = {}
    for lado, lst in casos.items():
        for desc, it in lst:
            mm, aa = momento(it, lado)
            kg = sum(k for k, _ in it)
            mreal[(lado, desc)] = abs(mm)
            rel.append(f"| {B.NUMERO[lado]} | {desc} | {kg*1000:.0f} | {abs(mm):.2f} (a {aa:+.0f}°) | {hip[lado]:.2f} | "
                       f"{'OK' if abs(mm) * 1.5 <= TRAVA_NM else ('margem < 1,5' if abs(mm) <= TRAVA_NM else 'PASSA')} |")
            ok(abs(mm) <= TRAVA_NM, f"{B.NUMERO[lado]} {desc}: momento real {abs(mm):.2f} N·m ≤ trava {TRAVA_NM} N·m")
    m_brac_esq = sum(massas[n][0] for n, v in conj["esquerdo"].items() if v[2] == "braco") + FIX_G
    m_brac_dir = sum(massas[n][0] for n, v in conj["direito"].items() if v[2] == "braco") + FIX_G
    rel.append(f"- braço (casca + anel + fixadores): 05 = {m_brac_esq:.0f} g, 07 = {m_brac_dir:.0f} g (HIP: 180 g)")

    # ---------------- 7. esforços nos M3 ----------------
    rel.append("\n## 7. Esforços nos M3 com 300 g (estático, × 2 para choque)")
    # punho (05): momento na face do punho = peso de adaptador + cubo + bandeja + carga × braço de alavanca ao longo de f
    pesos = [(massas[n][0] / 1000, cms[n]) for n in ("05D_adaptador_v1", "06B_cubo", "06A_bandeja", "06C_anel_decorativo")]
    pesos.append((CARGA_KG, carga))
    Mw = sum(kg * G_ACEL * ((c.x - W[0]) * f[0] + (c.y - W[1]) * f[1]) / 1000 for kg, c in pesos)
    Fpeso = sum(kg for kg, _ in pesos) * G_ACEL
    pivo = -G.IF_PUNHO_D / 2
    ds = [B.pos_if(a)[1] - pivo for a in G.IF_PUNHO_M3_ANG]
    Fmax = Mw * 1000 * max(ds) / sum(x * x for x in ds) * 2
    ok(Fmax * 2 <= INSERTO_ARRANQUE_N, f"IF-PUNHO (05): momento {Mw:.2f} N·m na face; tração no M3 de cima ≈ {Fmax:.0f} N "
       f"(com choque ×2); cisalhamento {Fpeso * 2 / 3:.1f} N/parafuso; inserto ~{INSERTO_ARRANQUE_N:.0f} N -> FS {INSERTO_ARRANQUE_N / Fmax:.1f}")
    # IF-BANDEJA: 300 g na borda, tombando sobre a aresta do adaptador
    r_borda = G.BANDEJA_D / 2 - P.BANDEJA_PAREDE
    casos_b = []
    meia = P.ADAPT_LARG / 2      # aresta lateral do topo do adaptador
    d_long = 12.0 + meia
    casos_b.append(CARGA_KG * G_ACEL * (r_borda - meia) * d_long / (d_long ** 2 + (meia - 12.0) ** 2))
    frente = P.ADAPT_Z_FIM - P.ADAPT_L
    casos_b.append(CARGA_KG * G_ACEL * (r_borda - frente) / (2 * (frente)))
    Fb = max(casos_b) * 2
    ok(Fb <= INSERTO_ARRANQUE_N, f"IF-BANDEJA: 300 g na borda (r={r_borda:.0f}) tomba sobre o adaptador: tração máx. ≈ {Fb:.0f} N "
       f"por M3 (choque ×2) -> FS {INSERTO_ARRANQUE_N / Fb:.1f}; peso apoiado na face, não nos parafusos")
    Mluva = massas["07E_mao_luva"][0] / 1000 * G_ACEL * (cms["07E_mao_luva"] - cq.Vector(*Wd)).Length / 1000
    rel.append(f"- IF-PUNHO (07, luva): momento máx. {Mluva:.3f} N·m (desprezível)")

    # ---------------- 8. canal de cabo ----------------
    rel.append("\n## 8. Canal de cabos contínuo (feixe de teste Ø6 da entrada no ombro até a face do punho)")
    for lado in ("esquerdo", "direito"):
        num = B.NUMERO[lado]
        zc = P.Z_TUBO + 3.5
        s = P.CANAL_S
        pts = []
        (x0, y0), _, _ = B.ponto(lado, "v", P.ENTRADA_CABO_R, s)
        pts += [(x0, y0, -3.0), (x0, y0, zc)]
        (xe, ye), (fx, fy) = B.fim_metades(lado)
        fim_cav = (xe - fx * (P.REFORCO_PUNHO + 4), ye - fy * (P.REFORCO_PUNHO + 4))
        if lado == "esquerdo":
            rc = G.BRACO_ESQ_RAIO_COTOVELO + s
            cx, cy = -G.BRACO_ESQ_RAIO_COTOVELO, -G.BRACO_ESQ_ALTURA + G.BRACO_ESQ_RAIO_COTOVELO
            for k in range(0, 91, 15):
                a = math.radians(-k)
                pts.append((cx + rc * math.cos(a), cy + rc * math.sin(a), zc))
            pts.append((fim_cav[0], -G.BRACO_ESQ_ALTURA - s, zc))
        else:
            pts.append((s, fim_cav[1], zc))
        pts.append((fim_cav[0], fim_cav[1], P.Z_TUBO))
        W0 = (xe + fx * (P.ANEL_ESP + 1), ye + fy * (P.ANEL_ESP + 1), P.Z_TUBO)
        pts.append(W0)
        tubo = None
        for a, b in zip(pts[:-1], pts[1:]):
            va, vb = cq.Vector(*a), cq.Vector(*b)
            dd = vb - va
            seg = cq.Solid.makeCylinder(P.CABO_TESTE_D / 2, dd.Length, va, dd.normalized())
            sph = cq.Solid.makeSphere(P.CABO_TESTE_D / 2, cq.Vector(*b))
            seg = cq.Workplane("XY").add(seg).union(cq.Workplane("XY").add(sph))
            tubo = seg if tubo is None else tubo.union(seg)
        if lado == "direito":
            tubo = tubo.mirror("YZ")
        pecas = [conj[lado][num + k][0] for k in ("A_metade_interna", "B_metade_externa", "C_anel_punho")]
        bate = sum(vol(tubo, p) for p in pecas)
        ok(bate < TOL, f"{num}: feixe Ø{P.CABO_TESTE_D:g} passa da entrada (r={P.ENTRADA_CABO_R:g}) pelas presilhas até a face do punho "
           f"sem tocar torres/paredes ({bate:.2f} mm³)")
        if lado == "direito":
            cl, ca, cc = P.CONECTOR_ENVELOPE
            env = (cq.Workplane("XY").box(cl, cc, ca)
                   .translate((0, fim_cav[1] + cc / 2 - 2, P.Z_TUBO)))
            env = env.mirror("YZ")
            bate = sum(vol(env, p) for p in pecas[:2])
            ok(bate < TOL, f"07: espaço livre {cl:g}×{ca:g}×{cc:g} mm para conector removível antes da parede do punho ({bate:.2f} mm³)")

    # ---------------- 9. imprimibilidade ----------------
    rel.append("\n## 9. Imprimibilidade (vão sem apoio = 2 × raio inscrito das regiões voltadas para baixo > 60°; limite ~12 mm)")
    for nome, w in impressos.items():
        m = to_mesh(w, 0.03)
        vao, area = analisar_impressao(m)
        ok(vao <= 12.5, f"{nome}: maior vão sem apoio {vao:.1f} mm (ponte/balanço > 60°, área {area:.0f} mm²), sem suporte — {ORIENT[nome[2:]]}"
           + (f"; {PAREDES[nome[2:]]}" if nome[2:] in PAREDES else ""))
        cq.exporters.export(w, str(OUT / f"{nome}.stl"), tolerance=0.01, angularTolerance=0.1)
        cq.exporters.export(w, str(OUT / f"{nome}.step"))
    rel.append(f"- teto da cavidade em gota ({P.CAV_ANG_TETO:g}° da vertical): ponte {B.ponte_cavidade():.1f} mm")

    return conj, ombro


# ============================================================
# vistas
# ============================================================
def vistas(conj, ombro):
    cache = {}

    def mesh(key, w):
        if key not in cache:
            cache[key] = to_mesh(w, 0.08)
        return cache[key]

    def itens_lado(lado, ang=0.0, expl=0.0, ombro_on=True, fantasma=False):
        lst = []
        H = B.frame_punho(lado)
        for nome, (s, cor, grupo) in conj[lado].items():
            w = s
            if expl:
                k = nome[2:]
                dz = {"A_metade_interna": -1.0, "B_metade_externa": 1.0, "F_friso": 2.0}.get(k, 0.0)
                w = w.translate((0, 0, dz * expl))
                if grupo != "braco" or k == "C_anel_punho":
                    fac = {"C_anel_punho": 0.3, "D_adaptador_v1": 1.0, "E_mao_luva": 1.0}.get(k, 1.0)
                    up = 1.8 if grupo == "bandeja" else 0.0
                    if k == "C_anel_decorativo":
                        up = 2.4
                    vv = [H[3][i] * fac * expl + H[2][i] * up * expl for i in range(3)]
                    w = w.translate(tuple(vv))
            w = O.posicionar(gira(w, ang, lado), lado)
            lst.append((mesh((nome, ang, expl), w), CORES["fantasma"] if fantasma else CORES[cor]))
        if ombro_on:
            for k, s in ombro[lado].items():
                w = O.posicionar(gira(s, ang, lado) if k in O.GIRAM else s, lado)
                lst.append((mesh(("ombro", lado, k, ang), w), CORES["aco"]))
        return lst

    tronco = (to_mesh(TRONCO, 0.5), CORES["fantasma"])
    base = (to_mesh(BASE, 0.5), CORES["fantasma"])
    tudo = itens_lado("esquerdo") + itens_lado("direito")
    render_conjunto(tudo + [tronco, base], str(OUT / "vistas.png"), ["iso", "frente", "lado"],
                    titulo="Pecas 05/06/07 - bracos V2 na pose 0 graus (tronco e base = caixas de verificacao)")
    render_conjunto(itens_lado("esquerdo") + itens_lado("direito"), str(OUT / "iso_detalhe.png"), ["iso", "iso_tras"],
                    titulo="Bracos + ombros reais (05 esquerdo com bandeja, 07 direito com luva)")
    xe = -(G.IF_OMBRO_X + P.Z_TUBO)
    render_conjunto(itens_lado("esquerdo", ombro_on=True), str(OUT / "corte.png"), ["lado"], corte=("x", xe, False),
                    titulo="Corte no plano do braco esquerdo (x = eixo do tubo): cavidade, torres, soquete, punho")
    render_conjunto(itens_lado("direito", ombro_on=True), str(OUT / "corte_07.png"), ["lado"], corte=("x", -xe + 0.01, False),
                    titulo="Corte no plano do braco direito: canal, espaco do conector, anel do punho")
    for lado in ("esquerdo", "direito"):
        render_conjunto(itens_lado(lado, expl=25, ombro_on=False), str(OUT / f"explodida_{B.NUMERO[lado]}.png"), ["iso", "frente"],
                        titulo=f"Peca {B.NUMERO[lado]} explodida: metades, anel do punho, " + ("adaptador, cubo, bandeja, anel" if lado == "esquerdo" else "luva, friso"))
    for lado in ("esquerdo", "direito"):
        gmin, gmax = O.CURSO[lado]
        lst = []
        for a in (gmin, 0.0, gmax):
            lst += itens_lado(lado, ang=a, ombro_on=(a == 0.0), fantasma=(a != 0.0))
        render_conjunto(lst + [tronco, base], str(OUT / f"curso_{B.NUMERO[lado]}.png"), ["lado"],
                        titulo=f"Peca {B.NUMERO[lado]} no curso do ombro: {gmin:+.0f} / 0 / {gmax:+.0f} graus (convencao do validar_ombro)")
    lst = []
    for lado, dx in (("esquerdo", 150), ("direito", -150)):
        for m, c in itens_lado(lado, ombro_on=True):
            mm = m.copy()
            mm.apply_translation([dx, 0, 0])
            lst.append((mm, c))
    render_conjunto(lst, str(OUT / "comparacao.png"), ["lado", "iso"],
                    titulo="Comparacao: 07 direito (esq. da imagem no 'lado') x 05 esquerdo, mesma escala, IF-PUNHO igual")


if __name__ == "__main__":
    conj, ombro = validar()
    vistas(conj, ombro)
    TMP.unlink(missing_ok=True)
    txt = ["# Peças 05 / 06 / 07 — braços V2, bandeja e mãos: relatório", "",
           f"Resultado: **{'APROVADO' if not falhas else 'COM FALHAS'}** ({len(falhas)} falhas, {len(avisos)} avisos)", ""] + rel
    txt += ["", "## Fixadores (por braço)", ""] + [f"- {q if q else 'conforme torres'} × {d}" for d, q in B.BOM["comum"]]
    txt += [f"- 06: {q} × {d}" for d, q in T.BOM]
    (OUT / "RELATORIO.md").write_text("\n".join(txt) + "\n")
    print("\n".join(txt))
    sys.exit(1 if falhas else 0)
