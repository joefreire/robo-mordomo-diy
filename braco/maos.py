"""Ferramentas do IF-PUNHO: mão-luva (07, V1, grafite) e adaptador fixo V1 da bandeja (05).

Todas desenhadas no referencial H do punho (braco.frame_punho): face IF-PUNHO em z = 0,
peça em z > 0; Y_H = 90° do padrão (chave), X_H = 0°. Prendem com 3×M3×10 nos insertos do
anel do punho (90°, 200°, 340°, r 12,5); a chave do anel entra no rasgo da peça.

  Mão-luva (07E)  : maciça, imprime com a face do punho na MESA. Canais Ø6,5 até a ponta para
                    a chave Allen (as cabeças ficam no fundo dos canais).
  Adaptador (05D) : IF-PUNHO de um lado, IF-BANDEJA em cima (face horizontal na pose de
                    serviço). As cabeças dos 3×M3 do punho ficam no vão do pescoço (chave Allen
                    de ponta esférica pelo lado). 2×M3×12 por baixo prendem o cubo da bandeja.
                    Imprime EM PÉ (fundo plano na mesa, face da bandeja para cima). Na V2 é a
                    única peça trocada (nivelador).
"""
import math
import sys
from pathlib import Path

import cadquery as cq

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from parameters import globais as G  # noqa: E402
from parameters import bracos as P  # noqa: E402
from braco.braco import pos_if  # noqa: E402

FOLGA = G.FOLGA_ENCAIXE


def _furos_if(p, prof_passante, canal_ate=None):
    """3×M3 passantes do IF-PUNHO (+ canal de acesso Ø6,5), rasgo da chave e Ø10 do cabo."""
    for ang in G.IF_PUNHO_M3_ANG:
        xy = pos_if(ang)
        p = p.cut(cq.Workplane("XY").workplane(offset=-1).center(*xy).circle(G.M3_PASSANTE / 2).extrude(prof_passante + 2))
        if canal_ate:
            p = p.cut(cq.Workplane("XY").workplane(offset=prof_passante).center(*xy).circle(P.ACESSO_D / 2)
                      .extrude(canal_ate - prof_passante))
    cw, ch = G.IF_PUNHO_CHAVE
    r0 = P.CHAVE_R0 - FOLGA
    p = p.cut(cq.Workplane("XY").workplane(offset=-1).center(0, (r0 + 25) / 2).rect(cw + 2 * FOLGA, 25 - r0).extrude(ch + FOLGA + 1))
    return p


def luva():
    """07E: mão-luva (mitene) maciça, grafite."""
    d = G.IF_PUNHO_D
    p = cq.Workplane("XY").circle(d / 2).extrude(P.LUVA_PUNHO_L + 4)
    sx, sy, sz = P.LUVA_SEMI

    def elip(c, s):
        e = cq.Solid.makeSphere(1.0, angleDegrees1=-90, angleDegrees2=90)
        e = e.transformGeometry(cq.Matrix([[s[0], 0, 0, 0], [0, s[1], 0, 0], [0, 0, s[2], 0]]))
        return cq.Workplane("XY").add(e.moved(cq.Location(cq.Vector(*c))))

    p = p.union(elip((0, 0, P.LUVA_Z), (sx, sy, sz)))
    c, s = P.LUVA_POLEGAR
    p = p.union(elip(c, s))
    p = p.faces("<Z").edges().chamfer(0.6)
    p = _furos_if(p, 6.0, canal_ate=P.LUVA_Z + sz + 5)
    p = p.cut(cq.Workplane("XY").workplane(offset=-1).circle(G.IF_PUNHO_CABO_D / 2).extrude(15))
    return p


def adaptador_v1():
    """05D: adaptador fixo IF-PUNHO -> IF-BANDEJA (V1), PETG creme/grafite."""
    e = P.ADAPT_FLANGE_ESP
    yb, yt = P.ADAPT_Y_BASE, P.ADAPT_Y_TOPO
    fl = cq.Workplane("XY").circle(G.BRACO_D / 2).extrude(e)
    pesc = cq.Workplane("XY").workplane(offset=e - 0.5).circle(P.ADAPT_PESCOCO_D / 2).extrude(P.ADAPT_PESCOCO_L + 1)
    z0 = e + P.ADAPT_PESCOCO_L
    corpo = (cq.Workplane("XY").workplane(offset=z0).center(0, (yb + yt) / 2)
             .rect(P.ADAPT_LARG, yt - yb).extrude(P.ADAPT_Z_FIM - z0))
    corpo = corpo.edges("|Z").fillet(6.0).faces(">Z").edges().fillet(3.0)
    p = fl.union(pesc).union(corpo)
    # fundo plano comum (imprime em pé)
    p = p.cut(cq.Workplane("XY").workplane(offset=-5).center(0, yb - 25).rect(100, 50).extrude(200))
    p = _furos_if(p, e)
    p = p.cut(cq.Workplane("XY").workplane(offset=-1).circle(G.IF_PUNHO_CABO_D / 2).extrude(e + P.ADAPT_PESCOCO_L - 2))
    # IF-BANDEJA no topo (referencial T: x_T = −X_H, y_T = Z_H, centro em z_H = ADAPT_L)
    zc = P.ADAPT_L
    for (xt, yt_) in G.IF_BANDEJA_M3:
        x, z = -xt, zc + yt_
        p = p.cut(cq.Workplane("XY").add(cq.Solid.makeCylinder(G.M3_PASSANTE / 2, 30, cq.Vector(x, P.ADAPT_M3_ASSENTO - 1, z), cq.Vector(0, 1, 0))))
        p = p.cut(cq.Workplane("XY").add(cq.Solid.makeCylinder(P.ADAPT_M3_CBORE_D / 2, P.ADAPT_M3_ASSENTO - yb + 5, cq.Vector(x, yb - 5, z), cq.Vector(0, 1, 0))))
    L, A, h = G.IF_BANDEJA_CHAVE
    ox, oy = G.IF_BANDEJA_CHAVE_OFF
    lingua = cq.Workplane("XY").add(cq.Solid.makeBox(L - 2 * FOLGA, h - FOLGA + 0.01, A - 2 * FOLGA,
                                                     cq.Vector(-ox - (L - 2 * FOLGA) / 2, yt - 0.01, zc + oy - (A - 2 * FOLGA) / 2)))
    return p.union(lingua)


if __name__ == "__main__":
    for nome, f in (("07E_mao_luva", luva), ("05D_adaptador_v1", adaptador_v1)):
        s = f()
        bb = s.val().BoundingBox()
        print(f"{nome:18s} {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:5.1f} valido={s.val().isValid()} "
              f"solidos={len(s.solids().vals())} vol={s.val().Volume()/1000:.1f} cm3")
