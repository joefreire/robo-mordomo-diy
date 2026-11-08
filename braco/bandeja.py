"""Peça 06 — bandeja Ø120 (grafite) + cubo IF-BANDEJA aparafusado + anel decorativo opcional.

Referencial T da bandeja: z para cima, origem no centro da FACE DE BAIXO do fundo. O cubo
fica embaixo (z < 0). Interface com o adaptador (IF-BANDEJA, globais.py): 2 insertos M3 em
(±12, 0) na face de baixo do cubo + rasgo de chave 14×8×3 deslocado (0, +6) — só monta de
um jeito. A bandeja não muda entre V1 (adaptador fixo) e V2 (nivelador).

  06A bandeja      : fundo 3, borda 10 (acima do fundo), cantos internos R3, canal raso do
                     anel decorativo. Fundo LISO embaixo -> imprime com o fundo na mesa, sem
                     suporte. 3×M3 escareados de cima prendem o cubo.
  06B cubo         : Ø50 × 10, imprime de cabeça para baixo (face da bandeja na mesa).
  06C anel decor.  : opcional, verde-petróleo, encaixa no canal.
"""
import math
import sys
from pathlib import Path

import cadquery as cq

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from parameters import globais as G  # noqa: E402
from parameters import bracos as P  # noqa: E402

FOLGA = G.FOLGA_ENCAIXE
ALT = G.BANDEJA_FUNDO + G.BANDEJA_BORDA


def _pol(r, a):
    a = math.radians(a)
    return (r * math.cos(a), r * math.sin(a))


def bandeja():
    R = G.BANDEJA_D / 2
    f = G.BANDEJA_FUNDO
    p = cq.Workplane("XY").circle(R).extrude(ALT)
    p = p.cut(cq.Workplane("XY").workplane(offset=f).circle(R - P.BANDEJA_PAREDE).extrude(ALT))
    p = p.faces(">Z").edges().fillet(1.2)
    p = p.edges(cq.selectors.BoxSelector((-R, -R, f - 0.1), (R, R, f + 0.1))).fillet(P.BANDEJA_RAIO_INT)
    p = p.faces("<Z").edges().chamfer(0.6)
    r0, r1, prof, _ = P.ANEL_DECOR
    p = p.cut(cq.Workplane("XY").workplane(offset=f - prof).circle(r1).circle(r0).extrude(prof + 1))
    for a in P.BOSS_M3_ANG:
        xy = _pol(P.BOSS_M3_R, a)
        p = p.cut(cq.Workplane("XY").workplane(offset=-1).center(*xy).circle(G.M3_PASSANTE / 2).extrude(f + 2))
        # escareado 90° (cabeça chata M3 Ø6)
        p = p.cut(cq.Workplane("XY").add(cq.Solid.makeCone(1.7, 3.25 + 0.3, 1.55 + 0.3, cq.Vector(xy[0], xy[1], f - 1.55))))
    return p


def cubo():
    h = P.BOSS_H
    p = cq.Workplane("XY").workplane(offset=-h).circle(P.BOSS_D / 2).extrude(h)
    p = p.faces("<Z").edges().fillet(1.0)
    for xy in G.IF_BANDEJA_M3:
        p = p.cut(cq.Workplane("XY").workplane(offset=-h - 0.01).center(*xy).circle(G.M3_INSERTO_FURO / 2).extrude(G.M3_INSERTO_PROF + 0.5))
    L, A, prof = G.IF_BANDEJA_CHAVE
    p = p.cut(cq.Workplane("XY").workplane(offset=-h - 1).center(*G.IF_BANDEJA_CHAVE_OFF).rect(L, A).extrude(prof + 1))
    for a in P.BOSS_M3_ANG:
        p = p.cut(cq.Workplane("XY").workplane(offset=-G.M3_INSERTO_PROF - 0.5).center(*_pol(P.BOSS_M3_R, a))
                  .circle(G.M3_INSERTO_FURO / 2).extrude(G.M3_INSERTO_PROF + 1))
    return p


def anel_decorativo():
    r0, r1, prof, h = P.ANEL_DECOR
    z0 = G.BANDEJA_FUNDO - prof
    return cq.Workplane("XY").workplane(offset=z0).circle(r1 - 0.15).circle(r0 + 0.15).extrude(h)


def plano_bandeja():
    """T dentro do H do punho esquerdo: centro da bandeja a ADAPT_L à frente da face do
    punho, fundo do cubo apoiado no topo do adaptador. x_T = −X_H, y_T = Z_H, z_T = Y_H."""
    return cq.Plane(origin=(0, P.ADAPT_Y_TOPO + P.BOSS_H, P.ADAPT_L), xDir=(-1, 0, 0), normal=(0, 1, 0))


def no_adaptador(wp_t):
    shp = wp_t.val() if hasattr(wp_t, "val") else wp_t
    return cq.Workplane("XY").add(shp.moved(cq.Location(plano_bandeja())))


BOM = [("Parafuso M3 × 8 cabeça chata (bandeja -> cubo, de cima)", 3),
       ("Inserto térmico M3 no cubo (bandeja)", 3),
       ("Inserto térmico M3 no cubo (IF-BANDEJA)", 2),
       ("Parafuso M3 × 12 (adaptador -> cubo, por baixo)", 2)]

if __name__ == "__main__":
    for nome, f in (("06A_bandeja", bandeja), ("06B_cubo", cubo), ("06C_anel_decorativo", anel_decorativo)):
        s = f()
        bb = s.val().BoundingBox()
        print(f"{nome:20s} {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:5.1f} valido={s.val().isValid()} "
              f"solidos={len(s.solids().vals())} vol={s.val().Volume()/1000:.1f} cm3")
