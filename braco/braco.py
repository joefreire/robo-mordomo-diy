"""Peças 05 (braço ESQUERDO, bandeja) e 07 (braço DIREITO, ferramenta) — casca V2.

Um só código: construir(lado). O braço é desenhado no referencial LOCAL do ombro ESQUERDO
(ombro/ombro_manual.py: Z = eixo do ombro para fora, X = trás, Y = cima, braço em 0° para
−Y) e o direito é o ESPELHO em X local, como o ombro. Diferenças por lado: forma do tubo
(esquerdo em L, direito reto), mão (adaptador da bandeja × luva) e o friso do direito.

Peças impressas por braço (PETG):
  A metade interna  (lado do tronco, z < Z_SPLIT) : soquete (laterais), cabeças das torres
  B metade externa  (z > Z_SPLIT)                 : tampa do soquete com 2×M3 da lingueta,
                                                     insertos das torres
  C anel do punho   (grafite)                     : IF-PUNHO (3 insertos M3, chave, Ø10),
                                                     2×M3 no braço
  F friso           (só 07, verde-petróleo)       : faixa encaixada no rebaixo da metade B

Encaixe no ombro: o soquete abraça a lingueta IF-BRAÇO pelos 2 lados tangenciais e pela face
de fora; 2×M3 no sentido do eixo, de fora para dentro, nos insertos que já estão na lingueta.
Montagem: metades A+B fechadas (4 torres M3 + 2 pinos Ø3) -> braço desliza RADIALMENTE na
lingueta até o fundo -> 2×M3×10 por fora -> anel do punho (2×M3×12) -> mão/adaptador (3×M3).

Imprimir: A e B com o PLANO DE DIVISÃO NA MESA (cavidade com teto em gota 52°, ponte
máx. ~12 mm, sem suporte). Anel: costas na mesa (face IF-PUNHO para cima). Friso: deitado.
"""
import math
import sys
from pathlib import Path

import cadquery as cq

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from parameters import globais as G  # noqa: E402
from parameters import bracos as P  # noqa: E402
from ombro import ombro_manual as O  # noqa: E402

NUMERO = {"esquerdo": "05", "direito": "07"}
FOLGA = G.FOLGA_ENCAIXE

# ============================================================
# geometria do eixo (referencial do ombro ESQUERDO, antes do espelho)
# ============================================================
Y_H = -G.BRACO_ESQ_ALTURA                       # −135: eixo do segmento horizontal
RC = G.BRACO_ESQ_RAIO_COTOVELO                   # 30


def fim_metades(lado):
    """Ponto onde terminam as metades (encosta o anel do punho) e direção f do antebraço."""
    if lado == "esquerdo":
        return (-(P.ESQ_PUNHO_X - P.ANEL_ESP), Y_H), (-1.0, 0.0)
    return (0.0, -(G.BRACO_DIR_COMP - P.ANEL_ESP)), (0.0, -1.0)


def caminho(lado, ini=P.TUBO_Y0, recuo_fim=0.0):
    """Linha de centro do tubo em z = Z_TUBO (Workplane com o wire)."""
    wp = cq.Workplane("XY", origin=(0, 0, P.Z_TUBO)).moveTo(0, -ini)
    (xe, ye), (fx, fy) = fim_metades(lado)
    xe, ye = xe - fx * recuo_fim, ye - fy * recuo_fim
    if lado == "esquerdo":
        wp = wp.lineTo(0, Y_H + RC)
        a = math.radians(-45)
        wp = wp.threePointArc((-RC + RC * math.cos(a), Y_H + RC + RC * math.sin(a)), (-RC, Y_H))
        wp = wp.lineTo(xe, ye)
    else:
        wp = wp.lineTo(xe, ye)
    return wp


def ponto(lado, seg, d, s=0.0):
    """Ponto da linha de centro + deslocamento s no plano (s>0 = fora da curva no esquerdo)
    e a direção da tangente. seg 'v' = d abaixo do eixo do ombro; 'h' = d à frente."""
    if seg == "v":
        return (s, -d), (0.0, -1.0), (1.0, 0.0)
    return (-d, Y_H - s), (-1.0, 0.0), (0.0, -1.0)


def _plano_perfil(lado, ini):
    return cq.Plane(origin=(0, -ini, P.Z_TUBO), xDir=(1, 0, 0), normal=(0, -1, 0))


def _perfil_gota(wp):
    """Seção da cavidade: círculo R_CAV com teto e fundo em 'gota' (52° da vertical),
    truncados com parede BRACO_PAREDE. Ponte do topo truncado ~11,7 mm."""
    R = P.R_CAV
    a = math.radians(P.CAV_ANG_TETO)
    ts, tt = R * math.cos(a), R * math.sin(a)
    sf = ts + (tt - R) * math.tan(a)
    return (wp.moveTo(-sf, R).lineTo(sf, R).lineTo(ts, tt).threePointArc((R, 0), (ts, -tt))
            .lineTo(sf, -R).lineTo(-sf, -R).lineTo(-ts, -tt).threePointArc((-R, 0), (-ts, tt)).close())


def ponte_cavidade():
    R = P.R_CAV
    a = math.radians(P.CAV_ANG_TETO)
    return 2 * (R * math.cos(a) + (R * math.sin(a) - R) * math.tan(a))


def _caixa(p, sdir, s0, s1, z0, z1, esp):
    """Caixa no plano do braço: s0..s1 ao longo de sdir, esp ao longo da tangente, z0..z1."""
    pl = cq.Plane(origin=(p[0], p[1], z0), xDir=(sdir[0], sdir[1], 0), normal=(0, 0, 1))
    return cq.Workplane(pl).center((s0 + s1) / 2, 0).rect(s1 - s0, esp).extrude(z1 - z0)


def _cil_z(p, d, z0, z1):
    return cq.Workplane("XY").workplane(offset=z0).center(*p).circle(d / 2).extrude(z1 - z0)


def _cil_eixo(origem, direcao, d, comp):
    return cq.Workplane("XY").add(cq.Solid.makeCylinder(d / 2, comp, cq.Vector(*origem), cq.Vector(*direcao)))


def frame_punho(lado, espelhado=True):
    """Referencial H do IF-PUNHO no LOCAL do lado: origem na face do punho, Z_H = para fora
    do braço, Y_H = 90° do padrão (esquerdo: para cima; direito: para a frente),
    X_H = 0°. Retorna (origem, X_H, Y_H, Z_H)."""
    (xe, ye), (fx, fy) = fim_metades(lado)
    W = (xe + fx * P.ANEL_ESP, ye + fy * P.ANEL_ESP, P.Z_TUBO)
    f = (fx, fy, 0.0)
    u = (0.0, 0.0, 1.0)
    v = (0.0, 1.0, 0.0) if lado == "esquerdo" else (-1.0, 0.0, 0.0)
    if lado == "direito" and espelhado:
        W = (-W[0], W[1], W[2])
        f = (-f[0], f[1], f[2])
        v = (-v[0], v[1], v[2])
        u = (0.0, 0.0, -1.0)          # mantém o referencial destro depois do espelho
    return W, u, v, f


def plano_punho(lado, espelhado=True):
    W, x, _, z = frame_punho(lado, espelhado)
    return cq.Plane(origin=W, xDir=x, normal=z)


def pos_if(ang, r=G.IF_PUNHO_M3_R):
    a = math.radians(ang)
    return (r * math.cos(a), r * math.sin(a))


# ============================================================
# casca (antes do espelho)
# ============================================================
def _tubo(lado):
    ext = cq.Workplane(_plano_perfil(lado, P.TUBO_Y0)).circle(P.R_TUBO).sweep(caminho(lado), transition="round")
    blk = (cq.Workplane("XY").workplane(offset=P.SOQ_Z0).center(0, -(P.SOQ_R0 + P.SOQ_R1) / 2)
           .rect(P.SOQ_LARG, P.SOQ_R1 - P.SOQ_R0).extrude(P.SOQ_Z1 - P.SOQ_Z0))
    blk = blk.edges("|Z").fillet(3.0)
    return ext.union(blk)


def _cavidade(lado):
    ini = G.IF_BRACO_LING_R1 + FOLGA + P.REFORCO_OMBRO
    pl = _plano_perfil(lado, ini)
    return _perfil_gota(cq.Workplane(pl)).sweep(caminho(lado, ini=ini, recuo_fim=P.REFORCO_PUNHO), transition="round")


def torres(lado):
    if lado == "esquerdo":
        return [ponto(lado, seg, d, P.TORRE_S)[0] for seg, d in P.ESQ_TORRES]
    return [ponto(lado, "v", d, P.TORRE_S)[0] for d in P.DIR_TORRES]


def presilhas(lado):
    if lado == "esquerdo":
        return [ponto(lado, seg, d) for seg, d in P.ESQ_PRESILHAS]
    return [ponto(lado, "v", d) for d in P.DIR_PRESILHAS]


def pinos(lado):
    (xe, ye), (fx, fy) = fim_metades(lado)
    q = (xe - fx * P.REFORCO_PUNHO / 2 + fy * 13.0 * (-1), ye - fy * P.REFORCO_PUNHO / 2 + fx * 13.0)
    return [(15.15, -33.0), q]


def casca(lado):
    """Braço inteiro (antes da divisão) no LOCAL do ombro esquerdo."""
    ext = _tubo(lado)
    corpo = ext.cut(_cavidade(lado))
    # torres M3 (unir metades) — cortadas pelo contorno externo
    for p in torres(lado):
        corpo = corpo.union(_cil_z(p, P.TORRE_D, 0, 45).intersect(ext))
    # presilhas de cabo (metade externa): gancho em U preso na parede do lado do canal
    for p, t, sd in presilhas(lado):
        s0 = -(P.R_CAV + 1.0)
        gancho = (_caixa(p, sd, s0, -8.0, P.Z_SPLIT, P.Z_SPLIT + 1.8, 2.4)
                  .union(_caixa(p, sd, -8.0, -6.2, P.Z_SPLIT, P.Z_SPLIT + 7.0, 2.4)))
        corpo = corpo.union(gancho.intersect(ext))
    # ---- soquete da lingueta IF-BRAÇO ----
    larg = G.IF_BRACO_LING_LARG + 2 * FOLGA
    r_fundo = G.IF_BRACO_LING_R1 + FOLGA
    bolso = (cq.Workplane("XY").workplane(offset=-1).center(0, -(P.SOQ_R0 - 2 + r_fundo) / 2)
             .rect(larg, r_fundo - P.SOQ_R0 + 2).extrude(O.Z_B1 + FOLGA + 1))
    corpo = corpo.cut(bolso)
    # o rotor (Ø52) e a tampa (Ø50) do ombro giram dentro do raio SOQ_R0
    corpo = corpo.cut(_cil_z((0, 0), 2 * P.SOQ_R0, -1, 50))
    for r in G.IF_BRACO_M3_R:
        corpo = corpo.cut(_cil_z((0, -r), G.M3_PASSANTE, O.Z_B1, 50))
        corpo = corpo.cut(_cil_z((0, -r), P.SOQ_M3_CBORE_D, P.SOQ_M3_ASSENTO_Z, 50))
    # ---- furos das torres: cabeça por dentro (lado do tronco), inserto na metade externa ----
    for p in torres(lado):
        corpo = corpo.cut(_cil_z(p, P.TORRE_CBORE_D, -5, P.TORRE_ASSENTO_Z))
        corpo = corpo.cut(_cil_z(p, G.M3_PASSANTE, 0, P.Z_SPLIT))
        corpo = corpo.cut(_cil_z(p, G.M3_INSERTO_FURO, P.Z_SPLIT - 0.01, P.Z_SPLIT + G.M3_INSERTO_PROF + 0.5))
        corpo = corpo.cut(_cil_z(p, 3.0, P.Z_SPLIT, P.Z_SPLIT + 10.5))
    # pinos de alinhamento Ø3 (furo nas duas metades)
    for p in pinos(lado):
        corpo = corpo.cut(_cil_z(p, P.PINO_FURO_D, P.Z_SPLIT - P.PINO_PROF, P.Z_SPLIT + P.PINO_PROF))
    # ---- entrada do cabo (V2): rasgo na face interna, lado do canal ----
    (px, py), _, sd = ponto(lado, "v", P.ENTRADA_CABO_R, P.CANAL_S)
    corpo = corpo.cut(_caixa((px, py), sd, -P.ENTRADA_CABO[0] / 2, P.ENTRADA_CABO[0] / 2, -1, P.Z_TUBO, P.ENTRADA_CABO[1]))
    # ---- ponta do punho: furo de cabo Ø10 + 2 insertos do anel ----
    W, u, v, f = frame_punho(lado, espelhado=False)
    (xe, ye), _ = fim_metades(lado)
    fim = (xe, ye, P.Z_TUBO)
    corpo = corpo.cut(_cil_eixo([fim[i] + f[i] * 1 for i in range(3)], [-c for c in f], G.IF_PUNHO_CABO_D, P.REFORCO_PUNHO + 3))
    for ang in P.ANEL_M3_ANG:
        a, b = pos_if(ang)
        o = [fim[i] + a * u[i] + b * v[i] for i in range(3)]
        corpo = corpo.cut(_cil_eixo([o[i] + f[i] * 0.01 for i in range(3)], [-c for c in f], G.M3_INSERTO_FURO, G.M3_INSERTO_PROF + 0.5))
        corpo = corpo.cut(_cil_eixo(o, [-c for c in f], 3.0, P.REFORCO_PUNHO + 1))
    # ---- 07: rebaixo da faixa decorativa ----
    if lado == "direito":
        w, comp, prof = P.FRISO
        corpo = corpo.cut(cq.Workplane("XY").workplane(offset=P.Z_TUBO + P.R_TUBO - prof)
                          .center(0, -(P.FRISO_Y0 + comp / 2)).rect(w, comp).extrude(5))
    return corpo


def _meio_espaco(acima):
    z0 = P.Z_SPLIT if acima else P.Z_SPLIT - 200
    return cq.Workplane("XY").workplane(offset=z0).center(-80, -100).rect(400, 400).extrude(200)


def anel_punho():
    """C: anel do punho (grafite) no referencial H (face IF-PUNHO em z=0, corpo em z<0)."""
    e = P.ANEL_ESP
    p = cq.Workplane("XY").workplane(offset=-e).circle(P.ANEL_D / 2).extrude(e)
    p = p.faces(">Z").edges().chamfer(1.0).faces("<Z").edges().fillet(1.0)
    cw, ch = G.IF_PUNHO_CHAVE
    p = p.union(cq.Workplane("XY").center(0, (P.CHAVE_R0 + 18.0) / 2).rect(cw, 18.0 - P.CHAVE_R0).extrude(ch))
    p = p.cut(cq.Workplane("XY").workplane(offset=-e - 1).circle(G.IF_PUNHO_CABO_D / 2).extrude(e + 5))
    for ang in G.IF_PUNHO_M3_ANG:
        p = p.cut(cq.Workplane("XY").workplane(offset=-G.M3_INSERTO_PROF - 0.5).center(*pos_if(ang))
                  .circle(G.M3_INSERTO_FURO / 2).extrude(G.M3_INSERTO_PROF + 1))
    for ang in P.ANEL_M3_ANG:
        p = p.cut(cq.Workplane("XY").workplane(offset=-e - 1).center(*pos_if(ang)).circle(G.M3_PASSANTE / 2).extrude(e + 2))
        p = p.cut(cq.Workplane("XY").workplane(offset=-P.ANEL_CBORE_P).center(*pos_if(ang))
                  .circle(P.ANEL_CBORE_D / 2).extrude(P.ANEL_CBORE_P + 1))
    return p


def friso():
    """F: faixa verde-petróleo do 07 (impressa deitada), no LOCAL do braço (antes do espelho)."""
    w, comp, prof = P.FRISO
    f = (cq.Workplane("XY").workplane(offset=P.Z_TUBO + P.R_TUBO - prof)
         .center(0, -(P.FRISO_Y0 + comp / 2)).rect(w - 2 * 0.2, comp - 2 * 0.3).extrude(prof + 0.4))
    return f.edges("|Y and >Z").fillet(0.6)


def _local(wp, lado, espelhar):
    return wp.mirror("YZ") if (lado == "direito" and espelhar) else wp


def no_punho(wp_h, lado):
    """Leva uma peça desenhada no referencial H do punho para o LOCAL do lado."""
    shp = wp_h.val() if hasattr(wp_h, "val") else wp_h
    return cq.Workplane("XY").add(shp.moved(cq.Location(plano_punho(lado))))


def construir(lado="esquerdo"):
    """Peças do BRAÇO no LOCAL do lado (ombro em 0°). Direito = esquerdo espelhado."""
    c = casca(lado)
    pecas = {"A_metade_interna": c.intersect(_meio_espaco(False)),
             "B_metade_externa": c.intersect(_meio_espaco(True))}
    if lado == "direito":
        pecas["F_friso"] = friso()
    pecas = {k: _local(v, lado, True) for k, v in pecas.items()}
    pecas["C_anel_punho"] = no_punho(anel_punho(), lado)
    return pecas


# orientação de impressão (peça em pé na mesa, z ≥ 0)
def para_impressao(nome, wp, lado):
    """Leva a peça (no LOCAL do lado ou no H) para a posição de impressão."""
    if nome == "C_anel_punho":
        shp = wp.val().moved(cq.Location(plano_punho(lado)).inverse)
        w = cq.Workplane("XY").add(shp)
    elif nome == "A_metade_interna":
        w = wp.rotate((0, 0, 0), (1, 0, 0), 180)
    else:
        w = wp
    bb = w.val().BoundingBox()
    return w.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))


BOM = {
    "comum": [
        ("Parafuso M3 × 10 (braço -> lingueta do ombro, de fora)", 2),
        ("Parafuso M3 × 16 (torres: metade interna -> externa)", "4 (05) / 3 (07)"),
        ("Inserto térmico M3 (torres, metade externa)", "4 (05) / 3 (07)"),
        ("Pino Ø3 × 10 (aço ou filamento 3 mm) — alinhamento das metades", 2),
        ("Parafuso M3 × 12 (anel do punho -> braço)", 2),
        ("Inserto térmico M3 (ponta do braço, anel do punho)", 2),
        ("Inserto térmico M3 (anel do punho, IF-PUNHO)", 3),
        ("Parafuso M3 × 10 (mão/adaptador -> IF-PUNHO)", 3),
    ],
}


if __name__ == "__main__":
    for lado in ("esquerdo", "direito"):
        for k, s in construir(lado).items():
            v = s.val()
            bb = v.BoundingBox()
            print(f"{NUMERO[lado]}{k:18s} {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:5.1f} valido={v.isValid()} "
                  f"solidos={len(s.solids().vals())} vol={v.Volume()/1000:.1f} cm3")
