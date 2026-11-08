"""Forma comum do tronco (Peças 03 e 04) e auxiliares de geometria.

Casca = loft externo − loft interno, ambos por seções horizontais (planta em cada z).
Planta: retângulo 2·w(z) × 105 com cantos R30; junto das faces de trás e da frente o arco
vira uma reta a 45° (canto em "gota"). Assim a traseira imprime de COSTAS na mesa e a frontal
de FRENTE na mesa sem suporte nas bordas. w(z) vem de parameters/tronco.meia_largura.
"""
import math
import sys
from functools import lru_cache
from pathlib import Path

import cadquery as cq

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
from parameters import globais as G  # noqa: E402
from parameters import tronco as T  # noqa: E402

V = cq.Vector
PAREDE = G.TRONCO_PAREDE
HD = G.TRONCO_PROF / 2                       # 52,5
Y_DIV = G.TRONCO_Y_DIVISAO                   # +22,5
Z0, Z1 = G.Z_PISO_TRONCO, G.Z_TOPO_TRONCO    # 94, 284
INS_FURO = G.M3_INSERTO_FURO
INS_PROF = G.M3_INSERTO_PROF + 0.8           # sobra para o plástico derretido


# ---------------- planta ----------------
def _planta(hw, hd, r, z):
    """Wire da planta na altura z: 12 arestas (4 lados, 4 arcos, 4 retas a 45°)."""
    cx, cy = hw - r, hd - r
    k = r * math.cos(math.radians(45))
    xf = cx + r * (math.sqrt(2) - 1)         # onde a reta a 45° encontra a face

    def p(x, y):
        return V(x, y, z)

    def arco(a0, a1, sx, sy):
        pts = [p(sx * cx + r * math.cos(math.radians(a)), sy * cy + r * math.sin(math.radians(a)))
               for a in (a0, (a0 + a1) / 2, a1)]
        return cq.Edge.makeThreePointArc(*pts)

    L = cq.Edge.makeLine
    e = [
        L(p(hw, -cy), p(hw, cy)),
        arco(0, 45, 1, 1), L(p(cx + k, cy + k), p(xf, hd)),
        L(p(xf, hd), p(-xf, hd)),
        L(p(-xf, hd), p(-cx - k, cy + k)),
    ]
    a = cq.Edge.makeThreePointArc(p(-cx - k, cy + k),
                                  p(-cx + r * math.cos(math.radians(157.5)), cy + r * math.sin(math.radians(157.5))),
                                  p(-hw, cy))
    e += [a, L(p(-hw, cy), p(-hw, -cy))]
    a = cq.Edge.makeThreePointArc(p(-hw, -cy),
                                  p(-cx + r * math.cos(math.radians(202.5)), -cy + r * math.sin(math.radians(202.5))),
                                  p(-cx - k, -cy - k))
    e += [a, L(p(-cx - k, -cy - k), p(-xf, -hd)), L(p(-xf, -hd), p(xf, -hd)), L(p(xf, -hd), p(cx + k, -cy - k))]
    a = cq.Edge.makeThreePointArc(p(cx + k, -cy - k),
                                  p(cx + r * math.cos(math.radians(337.5)), -cy + r * math.sin(math.radians(337.5))),
                                  p(hw, -cy))
    e.append(a)
    return cq.Wire.assembleEdges(e)


def _zs_externo():
    zs = [Z0 + i * (T.Z_LARG_CHEIA - Z0) / 18 for i in range(19)]
    zc = Z1 - G.TRONCO_RAIO_TOPO
    zs += [zc + G.TRONCO_RAIO_TOPO * math.sin(math.radians(a)) for a in range(0, 91, 6)]
    return sorted(set(round(z, 4) for z in zs))


def meia_largura_interna(z):
    zc = Z1 - G.TRONCO_RAIO_TOPO
    if z <= zc:
        return T.meia_largura(z) - PAREDE
    ri = G.TRONCO_RAIO_TOPO - PAREDE
    dz = min(z - zc, ri)
    return G.TRONCO_LARG / 2 - G.TRONCO_RAIO_TOPO + math.sqrt(max(ri * ri - dz * dz, 0.0))


@lru_cache(None)
def corpo_externo():
    r = T.CANTO_PLANTA_R
    ws = [_planta(T.meia_largura(z), HD, r, z) for z in _zs_externo()]
    return cq.Workplane("XY").add(cq.Solid.makeLoft(ws, ruled=True))


@lru_cache(None)
def cavidade():
    r = T.CANTO_PLANTA_R - PAREDE
    zi0 = Z0 + T.PISO_ESP
    zi1 = Z1 - PAREDE
    zc = Z1 - G.TRONCO_RAIO_TOPO
    zs = [z for z in _zs_externo() if zi0 < z < zc] + [zi0, zc]
    ri = G.TRONCO_RAIO_TOPO - PAREDE
    zs += [zc + ri * math.sin(math.radians(a)) for a in range(6, 91, 6)]
    zs = sorted(set(round(z, 4) for z in zs if zi0 <= z <= zi1 + 1e-6))
    ws = [_planta(meia_largura_interna(z), HD - PAREDE, r, z) for z in zs]
    return cq.Workplane("XY").add(cq.Solid.makeLoft(ws, ruled=True))


@lru_cache(None)
def casca():
    return corpo_externo().cut(cavidade())


def lado_y(y0, y1):
    """Caixa grande entre y0 e y1 (para separar traseira e frontal)."""
    return cq.Workplane("XY").box(400, y1 - y0, 400).translate((0, (y0 + y1) / 2, 200))


# ---------------- primitivas orientadas ----------------
def plano_x(x0):
    """Plano em x = x0, normal +X; local (u, v) = (Y, Z)."""
    return cq.Plane(origin=(x0, 0, 0), xDir=(0, 1, 0), normal=(1, 0, 0))


def plano_y(y1):
    """Plano em y = y1, normal −Y (extrusão vai para trás); local (u, v) = (X, Z)."""
    return cq.Plane(origin=(0, y1, 0), xDir=(1, 0, 0), normal=(0, -1, 0))


def cil_x(y, z, d, x0, x1):
    return cq.Workplane(plano_x(x0)).center(y, z).circle(d / 2).extrude(x1 - x0)


def cil_y(x, z, d, y0, y1):
    return cq.Workplane(plano_y(y1)).center(x, z).circle(d / 2).extrude(y1 - y0)


def cil_z(x, y, d, z0, z1):
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).circle(d / 2).extrude(z1 - z0)


def caixa(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0).translate(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))


def ret_y(x, z, w, h, y0, y1, r=0.0):
    """Retângulo (X × Z) de cantos arredondados extrudado entre y0 e y1."""
    wp = cq.Workplane(plano_y(y1)).center(x, z)
    if r > 0:
        return wp.sketch().rect(w, h).vertices().fillet(r).finalize().extrude(y1 - y0)
    return wp.rect(w, h).extrude(y1 - y0)


def anel_y(x, z, w, h, r, esp, y0, y1):
    """Anel retangular: contorno (w, h, r) por dentro, esp de largura para fora."""
    return ret_y(x, z, w + 2 * esp, h + 2 * esp, y0, y1, r + esp).cut(ret_y(x, z, w, h, y0 - 1, y1 + 1, r))


def estadio_y(x, za, zb, d, y0, y1):
    """Coluna em "estádio" (dois círculos em z = za e zb, mesmo x) entre y0 e y1."""
    p = cil_y(x, za, d, y0, y1).union(cil_y(x, zb, d, y0, y1))
    return p.union(caixa(x - d / 2, x + d / 2, y0, y1, min(za, zb), max(za, zb)))


def gota(plano, u, v, d, ang_ponta, comp):
    """Furo/ressalto em gota no plano (círculo + ponta a 45°). ang_ponta em graus no plano local."""
    r = d / 2
    a = math.radians(ang_ponta)
    ponta = (u + r * math.sqrt(2) * math.cos(a), v + r * math.sqrt(2) * math.sin(a))
    t1 = (u + r * math.cos(a + math.pi / 4), v + r * math.sin(a + math.pi / 4))
    t2 = (u + r * math.cos(a - math.pi / 4), v + r * math.sin(a - math.pi / 4))
    c = cq.Workplane(plano).center(u, v).circle(r).extrude(comp)
    tri = cq.Workplane(plano).polyline([(u, v), t1, ponta, t2]).close().extrude(comp)
    return c.union(tri)


def gota_x(y, z, d, x0, x1, ponta="+y"):
    """Cilindro ao longo de X em gota; ponta para +Y ou −Y (topo na impressão de costas)."""
    return gota(plano_x(x0), y, z, d, 0.0 if ponta == "+y" else 180.0, x1 - x0)


def gota_z(x, y, d, z0, z1, ponta="+y"):
    return gota(cq.Plane(origin=(0, 0, z0), xDir=(1, 0, 0), normal=(0, 0, 1)), x, y, d,
                90.0 if ponta == "+y" else -90.0, z1 - z0)


def valido(wp):
    s = wp.val()
    return s.isValid() and len(wp.solids().vals()) == 1
