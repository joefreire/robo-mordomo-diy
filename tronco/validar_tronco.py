"""Validação das Peças 03 (traseira) e 04 (frontal) + peças soltas, montadas com as peças REAIS
da cintura (08), dos ombros (09/10) e do pescoço (11).

    ~/.venvs/cadquery/bin/python tronco/validar_tronco.py
Saídas: exports/p03_p04_tronco/RELATORIO.md + PNGs. Sai com 1 se houver falha.
"""
import math
import sys
from functools import reduce
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from parameters import globais as G  # noqa: E402
from parameters import tronco as T  # noqa: E402
from tronco import forma as F  # noqa: E402
from tronco import tronco_traseiro as TR  # noqa: E402
from tronco import tronco_frontal as TF  # noqa: E402
from cintura import cintura_manual as C  # noqa: E402
from ombro import ombro_manual as O  # noqa: E402
from ombro import validar_ombro as VO  # noqa: E402  (só funções; o script dele roda no __main__)
from pescoco import pescoco_manual as P  # noqa: E402
from tools.render import CORES, render_conjunto  # noqa: E402

OUT = RAIZ / "exports" / "p03_p04_tronco"
OUT.mkdir(parents=True, exist_ok=True)
TMP = OUT / "_tmp.stl"
TOL = 0.5          # mm³: abaixo disso é contato de face / ruído numérico
REL, FALHAS = [], []


def ok(c, m):
    REL.append(("OK  " if c else "FALHA ") + m)
    if not c:
        FALHAS.append(m)


def sec(t):
    REL.append(f"\n## {t}")


def inter_vol(a, b):
    try:
        r = a.intersect(b)
        return sum(s.Volume() for s in r.solids().vals())
    except Exception:
        return 0.0


def _comp(wp):
    return cq.Compound.makeCompound(wp.solids().vals())


def dist(a, b):
    try:
        return _comp(a).distance(_comp(b))
    except Exception:
        return float("nan")


def to_mesh(wp, tol=0.05):
    cq.exporters.export(wp, str(TMP), tolerance=tol, angularTolerance=0.2)
    return trimesh.load(str(TMP))


def uniao(lst):
    return reduce(lambda a, b: a.union(b), lst)


def mover(wp, dz):
    return wp.translate((0, 0, dz))


# ============================================================
print("gerando peças do tronco ...")
pecas = {n: f() for n, f in {**TR.PECAS, **TF.PECAS}.items()}            # como impressas (com anéis)
tras = TR.traseira(sacrificio=False)                                       # montagem: anéis cortados
frente = TF.frontal(sacrificio=False)
moldura, bandeja, tampa_f, painel_t, m06 = (pecas["04B_moldura_tela"], pecas["04C_bandeja_tela"],
                                            pecas["04D_tampa_manutencao"], pecas["03B_painel_traseiro"],
                                            pecas["04E_painel_decorativo_M06"])

sec("1. Sólidos")
for n, s in pecas.items():
    ok(F.valido(s), f"{n}: válido e 1 corpo")

# ============================================================
sec("2. Forma e interfaces da traseira (esqueleto)")
bb = tras.val().BoundingBox()
ok(abs(bb.ymin - G.TRONCO_Y_FUNDO) < 0.05 and abs(bb.ymax - G.TRONCO_Y_DIVISAO) < 0.05,
   f"traseira de y={bb.ymin:+.1f} a {bb.ymax:+.1f} (divisão {G.TRONCO_Y_DIVISAO:+.1f})")
ok(abs(bb.zmin - G.Z_PISO_TRONCO) < 0.05 and abs(bb.zmax - G.Z_TOPO_TRONCO) < 0.05,
   f"z {bb.zmin:.1f}..{bb.zmax:.1f} (piso {G.Z_PISO_TRONCO:g}, topo {G.Z_TOPO_TRONCO:g}, altura {G.TRONCO_ALT:g})")
ok(abs(bb.xlen - G.TRONCO_LARG) < 0.1, f"largura {bb.xlen:.1f} (ombros {G.TRONCO_LARG:g}); base {2 * T.meia_largura(G.Z_PISO_TRONCO):.0f} "
   f"(TRONCO_LARG_BASE {G.TRONCO_LARG_BASE:g})")
# IF-CINTURA: piso plano e apoiado
piso = F.cil_z(0, 0, 2 * 45.0, G.Z_PISO_TRONCO, G.Z_PISO_TRONCO + 0.3).intersect(F.lado_y(-60, G.TRONCO_Y_DIVISAO))
furos = uniao([F.cil_z(x, y, G.M4_PASSANTE, 90, 100) for x, y in G.IF_CINTURA_M4] +
              [F.cil_z(0, 0, G.IF_CINTURA_ABERTURA_TRONCO_D, 90, 100)])
v_piso = piso.cut(furos).val().Volume()
ok(abs(inter_vol(tras, piso) - v_piso) < 1.0, f"IF-CINTURA: piso plano em z={G.Z_PISO_TRONCO:g} cheio sobre a 08B (Ø90), "
   f"{v_piso / 0.3:.0f} mm² de apoio")
# IF-OMBRO: face plana ⟂ X, nada além de x = ±92,5
for sx, lado in ((-1, "esquerda"), (1, "direita")):
    xf = sx * G.IF_OMBRO_X
    disco = F.cil_x(G.IF_OMBRO_Y, G.IF_OMBRO_Z, G.IF_OMBRO_FACE_D, *TR._faixa(sx, G.IF_OMBRO_X - 0.3, G.IF_OMBRO_X))
    furos_o = uniao([F.cil_x(y, z, F.INS_FURO, *TR._faixa(sx, 80, 95)) for y, z in TR.furos_ombro(sx)] +
                    [F.gota_x(G.IF_OMBRO_Y, G.IF_OMBRO_Z, G.IF_OMBRO_FURO_D, *TR._faixa(sx, 80, 95), ponta="+y")])
    v_d = disco.cut(furos_o).val().Volume()
    ok(abs(inter_vol(tras, disco) - v_d) < 0.5, f"IF-OMBRO {lado}: face Ø{G.IF_OMBRO_FACE_D:g} plana e cheia em x={xf:+.1f}")
    fora = F.caixa(*TR._faixa(sx, G.IF_OMBRO_X + 0.01, 150), -100, 100, 0, 400)
    ok(inter_vol(tras, fora) < 0.01, f"IF-OMBRO {lado}: nada passa de x={xf:+.1f} (face ⟂ X)")
# IF-PESCOÇO: prateleira plana
disco = F.cil_z(0, 0, G.IF_PESCOCO_FACE_D, G.Z_TOPO_TRONCO - 0.3, G.Z_TOPO_TRONCO).intersect(F.lado_y(-60, G.TRONCO_Y_DIVISAO))
furos_p = uniao([F.cil_z(x, y, F.INS_FURO, 270, 290) for x, y in G.IF_PESCOCO_M3] +
                [F.gota_z(0, 0, G.IF_PESCOCO_CABO_D, 270, 290)])
v_d = disco.cut(furos_p).val().Volume()
ok(abs(inter_vol(tras, disco) - v_d) < 0.5, f"IF-PESCOÇO: prateleira Ø{G.IF_PESCOCO_FACE_D:g} plana em z={G.Z_TOPO_TRONCO:g} "
   f"(parte em y>{G.TRONCO_Y_DIVISAO:+.1f} é a frontal, rebaixada 0,3)")
ok(inter_vol(frente, F.cil_z(0, 0, G.IF_PESCOCO_FACE_D, G.Z_TOPO_TRONCO - 0.29, G.Z_TOPO_TRONCO + 1)) < 0.01,
   "frontal não encosta na flange do pescoço (alívio 0,3): a carga vai só para a traseira")
ok(inter_vol(frente, F.cil_z(0, 0, 90.0, G.Z_PISO_TRONCO, G.Z_PISO_TRONCO + 0.29)) < 0.01,
   "frontal não apoia na 08B (alívio 0,3 no piso): a carga vai só para a traseira")

# ============================================================
sec("3. Traseira × frontal: fechamento, folgas, união acessível")
v = inter_vol(tras, frente)
ok(v < TOL, f"03 × 04 sem interferência ({v:.2f} mm³)")
casca = F.casca()
for nome, peca, y0, y1 in (("traseira", tras, G.TRONCO_Y_DIVISAO - 0.3, G.TRONCO_Y_DIVISAO),
                           ("frontal", frente, G.TRONCO_Y_DIVISAO, G.TRONCO_Y_DIVISAO + 0.3)):
    faixa = casca.intersect(F.lado_y(y0, y1)).cut(                      # menos os recortes de projeto
        F.cil_z(0, 0, G.IF_CINTURA_ABERTURA_TRONCO_D, 90, 100)).cut(
        F.cil_z(0, 0, 96.0, 90, G.Z_PISO_TRONCO + 0.3)).cut(F.cil_z(0, 0, G.IF_PESCOCO_FACE_D + 1, G.Z_TOPO_TRONCO - 0.3, 290))
    falta = faixa.val().Volume() - inter_vol(faixa, peca)
    ok(falta < 0.5, f"{nome}: borda de união com a casca inteira em y={G.TRONCO_Y_DIVISAO:+.1f} (sem degrau; falta {falta:.2f} mm³)")
ok(T.PINO_FURO_D - T.PINO_D >= 2 * G.FOLGA_ENCAIXE - 1e-9 and T.PINO_FURO_PROF > T.PINO_L,
   f"pinos Ø{T.PINO_D:g}×{T.PINO_L:g} em furos Ø{T.PINO_FURO_D:g}×{T.PINO_FURO_PROF:g} (folga {G.FOLGA_ENCAIXE:g}/lado, fundo livre 1 mm)")
for x, z in T.UNIAO_M3:
    chave = F.cil_y(x, z, 6.0, G.TRONCO_Y_FUNDO - 80, T.UNIAO_ASSENTO_Y - 0.05)
    haste = F.cil_y(x, z, 3.0, T.UNIAO_ASSENTO_Y, G.TRONCO_Y_DIVISAO + 6.0)
    em_volta = F.cil_y(x, z, T.UNIAO_TUBO_D, G.TRONCO_Y_DIVISAO, G.TRONCO_Y_DIVISAO + F.INS_PROF).cut(
        F.cil_y(x, z, F.INS_FURO, 0, 60))
    livre = inter_vol(chave, tras) + inter_vol(chave, frente) + inter_vol(haste, tras) + inter_vol(haste, frente)
    cheio = inter_vol(em_volta, frente) / em_volta.val().Volume()
    ok(livre < 0.01 and cheio > 0.97,
       f"união M3 ({x:+.0f}, {z:.0f}): chave Ø6 entra reto pelas costas até o assento (y={T.UNIAO_ASSENTO_Y:+g}), "
       f"haste alinhada com o inserto da 04 ({cheio * 100:.0f}% de material em volta)")
aperto = G.TRONCO_Y_DIVISAO - T.UNIAO_ASSENTO_Y
ok(16 - aperto >= 4.5, f"{T.UNIAO_PARAFUSO}: aperta {aperto:.1f} mm de traseira e rosca {16 - aperto:.1f} mm no inserto")

# ============================================================
sec("4. Montagem com a cintura REAL (Peça 08), giro −60° / 0° / +60°")
cint = {n: mover(f(), G.Z_TOPO_P02) for n, f in C.PECAS.items()}
for ang in (-C.GIRO, 0.0, C.GIRO):
    g = lambda w: w.rotate((0, 0, 0), (0, 0, 1), ang)  # noqa: E731
    ruins = []
    for n, s in cint.items():
        s2 = g(s) if n in C.GIRAM else s
        for nt, t in (("03", g(tras)), ("04", g(frente))):
            vv = inter_vol(s2, t)
            if vv > TOL:
                ruins.append(f"{n}×{nt}={vv:.1f}")
    ok(not ruins, f"giro {ang:+.0f}°: tronco × cintura sem colisão" + ("" if not ruins else ": " + "; ".join(ruins)))
d = dist(tras, cint["08B_flange_superior"])
ok(d < 0.01, f"piso da traseira apoiado na 08B (distância {d:.3f} mm)")
for x, y in G.IF_CINTURA_M4:
    paraf = F.cil_z(x, y, 4.0, G.Z_PISO_TRONCO - 9.0, G.Z_PISO_TRONCO + T.PISO_ESP)
    cabeca = F.cil_z(x, y, G.M4_CABECA_D, G.Z_PISO_TRONCO + T.PISO_ESP, G.Z_PISO_TRONCO + T.PISO_ESP + G.M4_CABECA_H)
    chave = F.cil_z(x, y, 10.0, G.Z_PISO_TRONCO + T.PISO_ESP + G.M4_CABECA_H, 165.0)
    vv = inter_vol(paraf, tras) + inter_vol(paraf, cint["08B_flange_superior"])
    ok(vv < 0.01, f"M4 ({x:+.0f},{y:+.0f}): furo do piso alinhado com o inserto da 08B")
    ok(inter_vol(cabeca, tras) < 0.01 and inter_vol(chave, tras) < 0.01,
       f"M4 ({x:+.0f},{y:+.0f}): cabeça Ø7 assenta e chave/soquete Ø10 desce na vertical (livre até z=165)")
ok(C.ANEL_PARAF_R + 3 < G.IF_CINTURA_ABERTURA_TRONCO_D / 2, "parafusos do anel 08C alcançáveis pela abertura Ø56 do piso")

# ============================================================
sec("5. Montagem com os ombros REAIS (Peças 09 e 10) + gabarito do braço, curso completo")
for lado, sx in (("esquerdo", -1), ("direito", 1)):
    num = O.NUMERO[lado]
    loc = O.construir(lado)
    braco = VO.gab_braco().mirror("YZ") if lado == "direito" else VO.gab_braco()
    reg = F.caixa(*TR._faixa(sx, 30, 120), -60, 60, 180, 290)
    t_loc, f_loc = tras.intersect(reg), frente.intersect(reg)
    ruins = []
    for k, s in loc.items():
        if k in O.GIRAM:
            continue
        for nt, t in (("03", t_loc), ("04", f_loc)):
            vv = inter_vol(O.posicionar(s, lado), t)
            if vv > TOL:
                ruins.append(f"{num}{k}×{nt}={vv:.1f}")
    ok(not ruins, f"ombro {lado}: flange/tampa/manípulo sem colisão com o tronco" + ("" if not ruins else ": " + "; ".join(ruins)))
    d = dist(O.posicionar(loc["A_flange_tronco"], lado), t_loc)
    ok(d < 0.01, f"ombro {lado}: flange {num}A apoiada na face plana (distância {d:.3f} mm)")
    for y, z in TR.furos_ombro(sx):
        paraf = F.cil_x(y, z, 3.0, *TR._faixa(sx, G.IF_OMBRO_X - 6.0, G.IF_OMBRO_X + O.A_ESP))
        vv = inter_vol(paraf, t_loc) + inter_vol(paraf, O.posicionar(loc["A_flange_tronco"], lado))
        ok(vv < 0.01, f"ombro {lado}: M3 (y={y:+.1f}, z={z:.1f}) — furo da {num}A alinhado com o inserto do tronco")
    gmin, gmax = O.CURSO[lado]
    ang, ruins, dmin = gmin, [], 1e9
    while ang <= gmax + 1e-6:
        rot = O.posicionar(O.girar(loc["B_rotor_braco"], ang, lado), lado)
        br = O.posicionar(O.girar(braco, ang, lado), lado)
        for nome, s in (("rotor", rot), ("braço", br)):
            for nt, t in (("03", t_loc), ("04", f_loc)):
                vv = inter_vol(s, t)
                if vv > TOL:
                    ruins.append(f"{ang:+.0f}° {nome}×{nt}={vv:.1f}")
        dmin = min(dmin, dist(br, t_loc), dist(br, f_loc))
        ang += O.PASSO_INDEX
    ok(not ruins, f"ombro {lado}: curso {gmin:+.0f}°..{gmax:+.0f}° (a cada 15°) sem bater no tronco; "
       f"menor folga braço–tronco {dmin:.1f} mm" + ("" if not ruins else ": " + "; ".join(ruins)))
    x0, x1, y0, y1, z0, z1 = TR.ENV_OMBRO
    env = F.caixa(*TR._faixa(sx, x0, x1), y0, y1, z0, z1)
    vv = inter_vol(env, tras) + inter_vol(env, frente)
    ok(inter_vol(env, F.casca()) < 0.01, f"ombro {lado}: envelope do servo inteiro dentro da cavidade (a casca não precisa ser cortada)")
    ok(vv < 0.01, f"envelope do servo V2 ({G.IF_OMBRO_ENVELOPE_INTERNO[0]:g}×{G.IF_OMBRO_ENVELOPE_INTERNO[1]:g}×"
       f"{G.IF_OMBRO_ENVELOPE_INTERNO[2]:g}, x de ±{x0:g} a ±{x1:g}; a placa e os bosses ocupam o resto) livre: {vv:.2f} mm³")

# ============================================================
sec("6. Montagem com o pescoço REAL (Peça 11), pan ±90° × tilt ±30°")


def pose(n, s, pan, tilt):
    if n in P.TILT_GIRAM:
        s = s.rotate((0, 0, P.Z_TILT), (1, 0, P.Z_TILT), tilt)
    if n in P.PAN_GIRAM:
        s = s.rotate((0, 0, 0), (0, 0, 1), pan)
    return mover(s, G.Z_TOPO_TRONCO)


pesc = {n: f() for n, f in P.PECAS.items()}
cab = (cq.Workplane("XY").workplane(offset=G.PESCOCO_ALTURA + 3.01).rect(*G.CABECA[:2]).extrude(G.CABECA[2])
       .edges("|Y").fillet(G.CABECA_RAIO))
reg = F.caixa(-100, 100, -60, 60, 250, 300)
t_top, f_top = tras.intersect(reg), frente.intersect(reg)
ruins, dcab = [], 1e9
for pan in (-P.PAN_GIRO, 0, P.PAN_GIRO):
    for tilt in (-P.TILT_GIRO, 0, P.TILT_GIRO):
        for n, s in pesc.items():
            if n == "11A_flange_tronco" and (pan or tilt):
                continue
            for nt, t in (("03", t_top), ("04", f_top)):
                vv = inter_vol(pose(n, s, pan, tilt), t)
                if vv > TOL:
                    ruins.append(f"pan {pan:+.0f} tilt {tilt:+.0f}: {n}×{nt}={vv:.1f}")
        c = pose("11E_placa_cabeca", cab, pan, tilt)
        dcab = min(dcab, dist(c, t_top), dist(c, f_top))
ok(not ruins, "pescoço em todas as 9 combinações sem bater no tronco" + ("" if not ruins else ": " + "; ".join(ruins)))
ok(dcab > 10, f"cabeça (caixa {G.CABECA[0]:g}×{G.CABECA[1]:g}×{G.CABECA[2]:g}) fica a ≥ {dcab:.0f} mm do tronco em todas as poses")
d = dist(pose("11A_flange_tronco", pesc["11A_flange_tronco"], 0, 0), t_top)
ok(d < 0.01, f"flange 11A apoiada na prateleira da traseira (distância {d:.3f} mm)")
for x, y in G.IF_PESCOCO_M3:
    paraf = F.cil_z(x, y, 3.0, G.Z_TOPO_TRONCO - 6.0, G.Z_TOPO_TRONCO + P.A_ESP)
    vv = inter_vol(paraf, t_top) + inter_vol(paraf, pose("11A_flange_tronco", pesc["11A_flange_tronco"], 0, 0))
    ok(vv < 0.01, f"pescoço M3 ({x:+.0f},{y:+.0f}): furo da 11A alinhado com o inserto do tronco")

# ============================================================
sec("7. Frontal: tela do peito, moldura, bandeja, tampa, gravata")
ew, eh, ep = G.IF_TELA_PEITO_ENVELOPE
env_tela = F.caixa(-ew / 2, ew / 2, T.TELA_Y_FUNDO, T.TELA_Y_VIDRO, G.IF_TELA_PEITO_Z - eh / 2, G.IF_TELA_PEITO_Z + eh / 2)
vv = sum(inter_vol(env_tela, s) for s in (frente, tras, bandeja, moldura))
ok(vv < 0.01, f"envelope da tela {ew:g}×{eh:g}×{ep:g} cabe (y {T.TELA_Y_FUNDO:+.1f}..{T.TELA_Y_VIDRO:+.1f}, centro z={G.IF_TELA_PEITO_Z:g}): {vv:.2f} mm³")
passa = F.caixa(-ew / 2, ew / 2, T.TELA_Y_FUNDO, 70, G.IF_TELA_PEITO_Z - eh / 2, G.IF_TELA_PEITO_Z + eh / 2)
ok(inter_vol(passa, frente) < 0.01, "a tela sai pela frente com a moldura tirada (troca sem abrir o tronco)")
for nome, s in (("moldura 04B", moldura), ("painel M06", m06), ("bandeja 04C", bandeja), ("tampa 04D", tampa_f),
                ("painel 03B", painel_t)):
    vv = inter_vol(s, frente) + inter_vol(s, tras)
    ok(vv < TOL, f"{nome} encaixa sem interferência ({vv:.2f} mm³)")
for nome, pts, y0, y1, pecas_f in (
        ("moldura/M06", T.MOLDURA_M3, TF.Y_REB_TELA - 6.0, TF.Y_REB_TELA + T.MOLDURA_ESP, (moldura, m06)),
        ("bandeja", T.MOLDURA_M3, G.TRONCO_Y_DIVISAO, T.TELA_Y_FUNDO + 5.0, (bandeja,)),
        ("tampa", T.TAMPA_M3, TF.Y_REB_TAMPA - 5.0, G.TRONCO_PROF / 2, (tampa_f,)),
        ("gravata", T.GRAVATA_M3, G.TRONCO_PROF / 2 - 6.0, G.TRONCO_PROF / 2 + 3, ())):
    vv = 0.0
    for x, z in pts:
        paraf = F.cil_y(x, z, 3.0, y0, y1)
        vv += inter_vol(paraf, frente) + sum(inter_vol(paraf, s) for s in pecas_f)
    ok(vv < 0.01, f"{nome}: {len(pts)}×M3 alinhados com os insertos da frontal")
for x, z in T.PAINEL_M3:
    paraf = F.cil_y(x, z, 3.0, G.TRONCO_Y_FUNDO, G.TRONCO_Y_FUNDO + T.PAINEL_REBAIXO + 5.0)
    ok(inter_vol(paraf, tras) + inter_vol(paraf, painel_t) < 0.01, f"painel 03B: M3 ({x:+.0f},{z:.0f}) alinhado com o inserto")
z_tela_inf = G.IF_TELA_PEITO_Z - TF.REB_TELA[1] / 2
z_tampa_sup = T.TAMPA_Z + TF.REB_TAMPA[1] / 2
ok(z_tela_inf - z_tampa_sup >= 10, f"material entre os rebaixos da tela e da tampa: {z_tela_inf - z_tampa_sup:.1f} mm "
   f"(entre as aberturas: {G.IF_TELA_PEITO_Z - T.TELA_ABERTURA[1] / 2 - T.TAMPA_Z - T.TAMPA_ABERTURA[1] / 2:.1f} mm)")
ok(T.TAMPA_Z - TF.REB_TAMPA[1] / 2 - G.Z_PISO_TRONCO >= 9.5,
   f"material abaixo da tampa: {T.TAMPA_Z - TF.REB_TAMPA[1] / 2 - G.Z_PISO_TRONCO:.1f} mm")
zg = min(z for _, z in T.GRAVATA_M3)
folga_g = zg - F.INS_FURO / 2 - (G.IF_TELA_PEITO_Z + TF.REB_TELA[1] / 2)
ok(folga_g >= 4, f"gravata: insertos em z={zg:g}, {G.Z_TOPO_TRONCO - zg:g} mm abaixo do topo; "
   f"{folga_g:.1f} mm de material entre o furo e o rebaixo da moldura")
ok(TF.REB_TELA[0] / 2 + TF.ESP_ANEL < T.meia_largura(z_tela_inf) - 17.6,
   "moldura inteira na região plana da frente (impressão de frente na mesa)")

# ============================================================
sec("8. Bandeja do ESP32, alto-falante, trilhos")
x0, x1, z0, z1, y0, y1 = T.ESP32_ZONA
zona = F.caixa(x0, x1, y0, y1, z0, z1)
ok(inter_vol(zona, tras) + inter_vol(zona, frente) < 0.01,
   f"zona da bandeja do ESP32 livre ({x1 - x0:g}×{z1 - z0:g}×{y1 - y0:g}, presa nos trilhos; abertura do painel atrás = USB-C)")
fx, fz = T.FALANTE_CENTRO
zf = F.cil_y(fx, fz, T.FALANTE_ZONA_D, TR.Y_INT, TR.Y_INT + 20)
ok(inter_vol(zf, tras) < 0.01, f"superfície do alto-falante Ø{T.FALANTE_ZONA_D:g} × 20 livre por dentro (grade Ø{T.FALANTE_GRADE_D:g})")
ok(len(T.TRILHO_FUROS_Z) >= 8 and all(abs(b - a - T.TRILHO_PASSO) < 1e-6 for a, b in zip(T.TRILHO_FUROS_Z, T.TRILHO_FUROS_Z[1:])),
   f"2 trilhos × {len(T.TRILHO_FUROS_Z)} insertos M3, passo {T.TRILHO_PASSO:g} (z {T.TRILHO_FUROS_Z[0]:g}..{T.TRILHO_FUROS_Z[-1]:g})")

# ============================================================
sec("9. Espessuras (do CAD e dos parâmetros)")
ext_m = to_mesh(F.corpo_externo(), 0.05)
x0, x1, y0, y1, z0, z1 = TR.ENV_OMBRO
pts = np.array([[x1, y, z] for y in (y0, y1) for z in np.linspace(z0, z1, 13)] +
               [[x1, y, z] for z in (z0, z1) for y in np.linspace(y0, y1, 11)])
_, dd, _ = trimesh.proximity.closest_point(ext_m, pts)
ok(dd.min() >= 2.9, f"parede mínima entre o envelope do servo e a superfície externa: {dd.min():.2f} mm (bordas do envelope em x = ±{x1:g})")
ok(F.PAREDE >= 3.0, f"parede geral {F.PAREDE:g} mm")
ok(T.PAINEL_REBAIXO + 1.5 >= F.PAREDE, f"moldura do painel traseiro: rebaixo {T.PAINEL_REBAIXO:g} por fora + {1.5:g} por dentro = parede de 3")
ok(TF.ESP_ANEL + F.PAREDE - T.MOLDURA_REBAIXO >= 3.0,
   f"fundo do rebaixo da moldura {TF.ESP_ANEL + F.PAREDE - T.MOLDURA_REBAIXO + 1:.0f} mm; da tampa {TF.ESP_ANEL + F.PAREDE - T.TAMPA_REBAIXO:.1f} mm")
ok(T.OMBRO_PLACA_ESP + T.OMBRO_BOSS_ALT >= F.INS_PROF + 2, f"IF-OMBRO: placa {T.OMBRO_PLACA_ESP:g} + boss {T.OMBRO_BOSS_ALT:g} para inserto de {F.INS_PROF:.1f}")
ok(T.PESCOCO_NERVURA_ALT >= F.INS_PROF + 3, f"IF-PESCOÇO: {T.PESCOCO_NERVURA_ALT:g} mm sob a prateleira (inserto {F.INS_PROF:.1f})")
ok((T.OMBRO_BOSS_D - F.INS_FURO) / 2 >= 2.0 and (T.UNIAO_TUBO_D - T.UNIAO_ROSCA_FURO) / 2 >= 2.0,
   f"paredes em volta dos insertos ≥ 2 mm (boss {(T.OMBRO_BOSS_D - F.INS_FURO) / 2:.1f}; tubo da união {(T.UNIAO_TUBO_D - T.UNIAO_ROSCA_FURO) / 2:.2f})")
ok(T.PISO_ESP >= 5, f"piso {T.PISO_ESP:g} mm + {len(T.PISO_NERVURAS_X)} nervuras de {T.PISO_NERVURA_ESP:g}×{T.PISO_NERVURA_ALT:g}")

# ============================================================
sec("10. Imprimibilidade (orientação de impressão, balanços > 44°, maior vão por região)")
ORIENT = {  # rotação em X para pôr a face de apoio na mesa
    "03A_tronco_traseiro": (90, "de costas na mesa"), "03B_painel_traseiro": (90, "face externa na mesa"),
    "04A_tronco_frontal": (-90, "de frente na mesa"), "04B_moldura_tela": (90, "costas na mesa"),
    "04C_bandeja_tela": (90, "deitada"), "04D_tampa_manutencao": (-90, "face externa na mesa"),
    "04E_painel_decorativo_M06": (90, "costas na mesa"),
}


def vao_regiao(m, faces):
    tri = m.triangles[faces][:, :, :2]
    pol = unary_union([Polygon(t).buffer(0.01) for t in tri if Polygon(t).area > 1e-6])
    if pol.is_empty:
        return 0.0
    lo, hi = 0.0, 60.0
    for _ in range(14):
        mid = (lo + hi) / 2
        if pol.buffer(-mid).is_empty:
            hi = mid
        else:
            lo = mid
    return 2 * lo


for n, s in pecas.items():
    m = to_mesh(s, 0.08)
    ang, desc = ORIENT[n]
    m.apply_transform(trimesh.transformations.rotation_matrix(math.radians(ang), [1, 0, 0]))
    m.apply_translation(-m.bounds[0])
    nz = m.face_normals[:, 2]
    zc = m.triangles_center[:, 2]
    pend = np.where((nz < -0.72) & (zc > 0.3))[0]
    vmax, area = 0.0, m.area_faces[pend].sum()
    if len(pend):
        adj = m.face_adjacency
        mask = np.isin(adj, pend).all(axis=1)
        comps = trimesh.graph.connected_components(adj[mask], nodes=pend, min_len=1)
        vaos = sorted(((vao_regiao(m, c), float(m.triangles_center[c][:, 2].mean())) for c in comps), reverse=True)
        vmax = vaos[0][0]
        top = ", ".join(f"{v:.1f} (z {z:.0f})" for v, z in vaos[:3])
    else:
        top = "—"
    dims = m.bounds[1] - m.bounds[0]
    ok(vmax <= 12.0, f"{n} ({desc}): {area:.0f} mm² voltados para baixo; maiores vãos {top} mm (≤ 12 sem suporte)")
    ok(max(dims) <= 220, f"{n}: {dims[0]:.0f} × {dims[1]:.0f} × {dims[2]:.0f} mm na mesa (≤ 220; A1 256)")
for n, com, sem in (("03A_tronco_traseiro", pecas["03A_tronco_traseiro"], tras), ("04A_tronco_frontal", pecas["04A_tronco_frontal"], frente)):
    dv = com.val().Volume() - sem.val().Volume()
    ok(dv > 1.0, f"{n}: anéis de sacrifício presentes no arquivo de impressão ({dv:.0f} mm³) -> as faixas dos rebaixos viram ponte")
REL.append(f"- Anéis de sacrifício ({T.SACRIFICIO_ESP:g} mm) nas bordas das aberturas do painel 03B, da moldura e da tampa: "
           "cortar com estilete depois de imprimir (sem eles a faixa do rebaixo seria um balanço solto).")

# ============================================================
sec("11. Volume e massa (PETG 1,27 g/cm³, peça maciça = limite superior)")
tot = 0.0
for n, s in pecas.items():
    vcm = s.val().Volume() / 1000
    tot += vcm * T.PETG_DENS
    REL.append(f"- {n}: {vcm:.1f} cm³ → {vcm * T.PETG_DENS:.0f} g")
REL.append(f"- **total {tot:.0f} g** (com 3 mm de parede, 4 paredes + 20 % giroide fica perto disso: a casca é quase toda perímetro)")

# ============================================================
print("renderizando ...")
cor_c2 = (0.88, 0.84, 0.74, 1.0)
mt, mf = to_mesh(tras), to_mesh(frente)
render_conjunto([(to_mesh(pecas["03A_tronco_traseiro"]), CORES["creme"]), (to_mesh(painel_t), CORES["petroleo"])],
                str(OUT / "p03_vistas.png"), ["tras", "frente", "lado", "iso_tras", "iso"],
                titulo="Peca 03 - tronco traseiro (esqueleto): traseira, interna (frente aberta), lateral, iso")
render_conjunto([(to_mesh(pecas["04A_tronco_frontal"]), CORES["creme"]), (to_mesh(moldura), CORES["petroleo"]),
                 (to_mesh(tampa_f), cor_c2)],
                str(OUT / "p04_vistas.png"), ["frente", "tras", "lado", "iso"],
                titulo="Peca 04 - tronco frontal (capa) com moldura 04B e tampa 04D")
render_conjunto([(to_mesh(s), CORES["petroleo"] if "M06" in n or "moldura" in n or "painel" in n else CORES["creme"])
                 for n, s in pecas.items() if n[2] in "BCDE"], str(OUT / "pecas_soltas.png"), ["frente", "iso"],
                titulo="03B painel, 04B moldura, 04C bandeja, 04D tampa, 04E painel M06")

itens = [(mt, CORES["creme"]), (mf, cor_c2), (to_mesh(moldura), CORES["petroleo"]), (to_mesh(tampa_f), cor_c2),
         (to_mesh(painel_t), CORES["petroleo"]), (to_mesh(bandeja), CORES["grafite"])]
for n, s in cint.items():
    itens.append((to_mesh(s), CORES["creme"] if n == "08D_colar" else CORES["grafite"]))
for lado in ("esquerdo", "direito"):
    for k, s in O.construir(lado).items():
        itens.append((to_mesh(O.posicionar(s, lado)), CORES["creme"] if k == "B_rotor_braco" else CORES["grafite"]))
    br = VO.gab_braco().mirror("YZ") if lado == "direito" else VO.gab_braco()
    itens.append((to_mesh(O.posicionar(br, lado)), CORES["fantasma"]))
for n, s in pesc.items():
    itens.append((to_mesh(pose(n, s, 0, 0)), CORES["petroleo"] if n in ("11C_anel_retencao", "11E_placa_cabeca") else CORES["creme"]))
tela = (to_mesh(env_tela), CORES["fantasma"])
render_conjunto(itens, str(OUT / "montagem.png"), ["iso", "frente", "lado", "iso_tras"],
                titulo="Montagem: tronco 03+04 + cintura 08 + ombros 09/10 (braco = gabarito) + pescoco 11")
render_conjunto(itens + [tela], str(OUT / "corte_x0.png"), ["lado"], corte=("x", 0.01, False),
                titulo="Corte x=0: cintura, piso, tela (envelope), pescoco, uniao 03|04 em y=+22,5")
render_conjunto(itens + [tela], str(OUT / "corte_z239.png"), ["topo"], corte=("z", G.IF_OMBRO_Z, False),
                titulo="Corte z=239 (eixo dos ombros): placa plana, bosses, envelope livre, tela")
x0, x1, y0, y1, z0, z1 = TR.ENV_OMBRO
envs = [(to_mesh(F.caixa(*TR._faixa(sx, x0, x1), y0, y1, z0, z1)), CORES["ambar"]) for sx in (-1, 1)]
zesp = (to_mesh(F.caixa(T.ESP32_ZONA[0], T.ESP32_ZONA[1], T.ESP32_ZONA[4], T.ESP32_ZONA[5], T.ESP32_ZONA[2], T.ESP32_ZONA[3])),
        CORES["silicone"])
render_conjunto([(mt, CORES["creme"])] + envs + [zesp, tela], str(OUT / "envelopes.png"), ["frente", "iso", "topo"],
                titulo="Envelopes: servo do ombro V2 (ambar), bandeja ESP32 (vermelho), tela do peito (azul)")
pos = []
for lado in ("esquerdo", "direito"):
    gmin, gmax = O.CURSO[lado]
    loc = O.construir(lado)
    br = VO.gab_braco().mirror("YZ") if lado == "direito" else VO.gab_braco()
    for a in (gmin, gmax):
        pos.append((to_mesh(O.posicionar(O.girar(br, a, lado), lado)), CORES["fantasma"]))
        pos.append((to_mesh(O.posicionar(O.girar(loc["B_rotor_braco"], a, lado), lado)), CORES["creme"]))
for pan, tilt in ((90, 30), (-90, -30)):
    pos.append((to_mesh(pose("11E_placa_cabeca", cab, pan, tilt)), CORES["fantasma"]))
    for n in P.PAN_GIRAM:
        pos.append((to_mesh(pose(n, pesc[n], pan, tilt)), CORES["creme"]))
render_conjunto([(mt, CORES["creme"]), (mf, cor_c2)] + pos, str(OUT / "cursos.png"), ["lado", "frente", "iso"],
                titulo="Cursos extremos: ombros (esq -60/+60, dir -30/+120) e pescoco (pan +-90 / tilt +-30) com cabeca fantasma")
imp = []
for n, desl in (("03A_tronco_traseiro", -110), ("04A_tronco_frontal", 110)):
    m = to_mesh(pecas[n], 0.08)
    m.apply_transform(trimesh.transformations.rotation_matrix(math.radians(ORIENT[n][0]), [1, 0, 0]))
    m.apply_translation(-m.bounds[0] + [desl - 92.5, 0, 0])
    imp.append((m, CORES["creme"]))
render_conjunto(imp, str(OUT / "impressao.png"), ["iso", "lado"],
                titulo="Orientacao de impressao: 03 de costas na mesa (esq.), 04 de frente na mesa (dir.)")
TMP.unlink(missing_ok=True)

# ============================================================
txt = ["# Peças 03 + 04 — tronco traseiro e frontal: relatório", "",
       f"Resultado: **{'APROVADO' if not FALHAS else 'COM FALHAS'}** ({len(FALHAS)} falhas)", ""] + REL
txt += ["", "## Fixadores e comprados", ""] + [f"- {q} × {d}" for d, q in TR.BOM + TF.BOM]
(OUT / "RELATORIO.md").write_text("\n".join(txt) + "\n")
print("\n".join(txt))
sys.exit(1 if FALHAS else 0)
