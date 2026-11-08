"""Peça 01 — Base inferior (verde-petróleo) + presilha do contrapeso.

Forma (fase 1, mantida): 225 × 200 × 25, parede 3, fundo 4, cantos R35, laterais
inclinadas 6°, aberta em cima, borda superior plana e contínua.
Fase 2 (este arquivo):
  - 4 torres Ø10 com furo passante M3 e rebaixo da cabeça POR BAIXO. O parafuso sobe
    pela torre e prende num inserto no boss da Peça 02 (decisão 07/11). A borda de cima
    não é furada: a Peça 02 apoia nela e os parafusos ficam escondidos.
  - Contrapeso: placa de aço G.CONTRAPESO APOIADA no fundo (fundo não é rebaixado),
    centrada por 4 guias em L nos cantos e presa por 4 presilhas parafusadas (bosses
    com inserto M3 aqui; a presilha é peça separada).
  - 4 alojamentos de pés de borracha por baixo, sem perfurar o fundo.

Rodar a partir da pasta robot-butler/:
    ~/.venvs/cadquery/bin/python base/base_inferior.py
Impressão: fundo na mesa, abertura para cima (PETG, 0,2 mm, 4 paredes, 15–20% giroide).
Únicas pontes: teto do rebaixo das cabeças M3 (Ø6,5) e dos pés (Ø15, ver relatório).
A presilha imprime de cabeça para baixo (face lisa na mesa).
"""
import sys
from pathlib import Path

import cadquery as cq

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from parameters import globais as G  # noqa: E402
from parameters import base as B  # noqa: E402

# ============================================================
# PARÂMETROS LOCAIS (o resto vem de parameters/globais.py e parameters/base.py)
# ============================================================
FILETE_TOPO = 1.5          # arredondamento da aresta externa de cima
CHANFRO_BASE = 1.0         # chanfro da aresta da mesa (chanfro imprime, filete não)
FILETE_FUNDO_INTERNO = 2.0 # concordância fundo x parede por dentro
EPS = 0.01

L, P, H = G.BASE_LARG, G.BASE_PROF, G.P01_ALTURA
R, ANG = G.BASE_RAIO, G.BASE_INCLINACAO
W, F = G.P01_PAREDE, G.P01_FUNDO

# torres / união por baixo
TORRE_D = G.BASE_TORRE_D
REBAIXO_M3_D = B.M3_CABECA_D + 1.0         # 6,5: folga para a chave e a cabeça
REBAIXO_M3_PROF = B.M3_CABECA_H + 0.5      # 3,5: cabeça fica 0,5 para dentro do fundo

# contrapeso
CP_X, CP_Y, CP_ESP = G.CONTRAPESO
CP_FOLGA = B.CONTRAPESO_FOLGA
Z_CP_TOPO = F + CP_ESP                     # 7: face de cima da placa
GUIA_ESP = 3.0                             # espessura das guias em L
GUIA_BRACO = 12.0                          # comprimento de cada braço do L
GUIA_ALT = CP_ESP + 2.0                    # 5: passa 2 mm da placa (encaixe fácil)

# presilhas (4, no meio de cada lado da placa)
PRES_BOSS_D = G.M3_INSERTO_FURO + 2 * 2.5  # 9: parede de 2,5 em volta do inserto
PRES_DEGRAU = 2.0                          # boss sobe 2 mm acima da placa (inserto mais fundo)
Z_PRES_BOSS = Z_CP_TOPO + PRES_DEGRAU      # 9: topo do boss
PRES_ESP = 3.0                             # espessura da presilha sobre o boss
PRES_LARG = 12.0
PRES_SOBRE_PLACA = 6.0                     # quanto o pé da presilha cobre a placa
PRES_FURO_PROF = G.M3_INSERTO_PROF + 0.5   # 6,2: furo do inserto (fundo do furo em z=2,8)
PRES_PARAF = "M3 × 8 cabeça cilíndrica"
_BOSS_OFF = CP_FOLGA + PRES_BOSS_D / 2     # da borda nominal da placa ao centro do boss
# (x, y, direção para dentro da placa) — direção em graus no plano XY
PRESILHAS = [
    (0.0, CP_Y / 2 + _BOSS_OFF, 270.0),
    (0.0, -(CP_Y / 2 + _BOSS_OFF), 90.0),
    (CP_X / 2 + _BOSS_OFF, 0.0, 180.0),
    (-(CP_X / 2 + _BOSS_OFF), 0.0, 0.0),
]

# pés de borracha adesivos
PES = [(sx * 88.0, sy * 68.0) for sx in (-1, 1) for sy in (-1, 1)]


# ============================================================
# FORMA (fase 1, sem mudança)
# ============================================================
def corpo_externo():
    return (
        cq.Workplane("XY")
        .sketch().rect(L, P).vertices().fillet(R).finalize()
        .extrude(H, taper=ANG)
    )


def cavidade():
    # contorno interno = contorno externo na altura do fundo, recuado pela parede
    r0 = G.recuo(F)
    li, pi = L - 2 * (r0 + W), P - 2 * (r0 + W)
    ri = R - r0 - W
    return (
        cq.Workplane("XY").workplane(offset=F)
        .sketch().rect(li, pi).vertices().fillet(ri).finalize()
        .extrude(H - F + 1.0, taper=ANG)
    )


def forma():
    ext = corpo_externo()
    ext = ext.faces(">Z").edges().fillet(FILETE_TOPO)
    ext = ext.faces("<Z").edges().chamfer(CHANFRO_BASE)
    cav = cavidade().faces("<Z").edges().fillet(FILETE_FUNDO_INTERNO)
    return ext.cut(cav)


# ============================================================
# DETALHES (fase 2)
# ============================================================
def _cil(x, y, d, z0, z1):
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).circle(d / 2).extrude(z1 - z0)


def _caixa(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY").workplane(offset=z0)
            .center((x0 + x1) / 2, (y0 + y1) / 2).rect(x1 - x0, y1 - y0).extrude(z1 - z0))


def torres():
    s = None
    for x, y in B.BASE_TORRES:
        t = _cil(x, y, TORRE_D, F - 0.5, B.Z_TORRE_TOPO)
        s = t if s is None else s.union(t)
    return s


def guias_contrapeso():
    """4 guias em L por fora dos cantos da placa (folga CP_FOLGA)."""
    s = None
    cx, cy = CP_X / 2 + CP_FOLGA, CP_Y / 2 + CP_FOLGA      # canto interno da guia
    for sx in (-1, 1):
        for sy in (-1, 1):
            # braço paralelo a X (fica além da borda em Y)
            bx = _caixa(cx - GUIA_BRACO, cx + GUIA_ESP, cy, cy + GUIA_ESP, F - 0.5, F + GUIA_ALT)
            # braço paralelo a Y (fica além da borda em X)
            by = _caixa(cx, cx + GUIA_ESP, cy - GUIA_BRACO, cy + GUIA_ESP, F - 0.5, F + GUIA_ALT)
            g = bx.union(by).mirror("YZ") if sx < 0 else bx.union(by)
            g = g.mirror("XZ") if sy < 0 else g
            s = g if s is None else s.union(g)
    return s


def bosses_presilha():
    s = None
    for x, y, _ in PRESILHAS:
        b = _cil(x, y, PRES_BOSS_D, F - 0.5, Z_PRES_BOSS)
        s = b if s is None else s.union(b)
    return s


def modelo():
    p = forma()
    p = p.union(torres()).union(guias_contrapeso()).union(bosses_presilha())
    # união por baixo: furo passante M3 na torre + rebaixo da cabeça no fundo
    for x, y in B.BASE_TORRES:
        p = p.cut(_cil(x, y, G.M3_PASSANTE, -1, B.Z_TORRE_TOPO + 1))
        p = p.cut(_cil(x, y, REBAIXO_M3_D, -1, REBAIXO_M3_PROF))
    # insertos M3 das presilhas (de cima)
    for x, y, _ in PRESILHAS:
        p = p.cut(_cil(x, y, G.M3_INSERTO_FURO, Z_PRES_BOSS - PRES_FURO_PROF, Z_PRES_BOSS + 1))
    # alojamentos dos pés (por baixo, sem perfurar)
    for x, y in PES:
        p = p.cut(_cil(x, y, G.PES_D, -1, G.PES_PROF))
    return p


def presilha_local():
    """Presilha no referencial local: boss em (0,0), placa no sentido +X.
    Corpo apoiado no boss (z 9..12) e pé que desce 2 mm e aperta a placa (z 7..9)."""
    x_borda = _BOSS_OFF                      # borda nominal da placa
    x_ponta = x_borda + PRES_SOBRE_PLACA
    x_tras = -PRES_BOSS_D / 2
    corpo = _caixa(x_tras, x_ponta, -PRES_LARG / 2, PRES_LARG / 2, Z_PRES_BOSS, Z_PRES_BOSS + PRES_ESP)
    # o pé começa depois do boss + folga da placa (não encosta no boss nem na borda)
    pe = _caixa(x_borda + 0.5, x_ponta, -PRES_LARG / 2, PRES_LARG / 2, Z_CP_TOPO, Z_PRES_BOSS + 0.01)
    p = corpo.union(pe)
    p = p.edges("|Z").fillet(2.0)
    p = p.cut(_cil(0, 0, G.M3_PASSANTE, Z_PRES_BOSS - 1, Z_PRES_BOSS + PRES_ESP + 1))
    return p


def presilha(i=0):
    """Presilha i posicionada no robô (para montagem/validação)."""
    x, y, ang = PRESILHAS[i]
    return presilha_local().rotate((0, 0, 0), (0, 0, 1), ang).translate((x, y, 0))


def contrapeso():
    """Placa de aço de referência (comprada, não impressa)."""
    return _caixa(-CP_X / 2, CP_X / 2, -CP_Y / 2, CP_Y / 2, F, F + CP_ESP)


PECAS = {"01_base_inferior": modelo, "01P_presilha": presilha_local}
BOM = [
    (f"Parafuso M{3} × {B.M3_UNIAO_COMP:g} cabeça cilíndrica ISO 4762 (01 -> 02, por baixo)", 4),
    ("Inserto térmico M3 nos bosses da Peça 02", 4),
    (f"Placa de aço {CP_X:g} × {CP_Y:g} × {CP_ESP:g} (contrapeso, cantos vivos ou R≤3)", 1),
    (f"Parafuso {PRES_PARAF} (presilhas)", 4),
    ("Inserto térmico M3 nos bosses das presilhas (Peça 01)", 4),
    (f"Pé de borracha adesivo Ø{G.PES_D:g} (alojamento {G.PES_PROF:g} mm)", 4),
]


def exportar(out):
    out.mkdir(parents=True, exist_ok=True)
    for nome, fn in PECAS.items():
        s = fn()
        cq.exporters.export(s, str(out / f"{nome}.stl"), tolerance=0.01, angularTolerance=0.1)
        cq.exporters.export(s, str(out / f"{nome}.step"))
        bb = s.val().BoundingBox()
        print(f"{nome:20s} {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:5.1f}  valido={s.val().isValid()}  "
              f"solidos={len(s.solids().vals())}  volume={s.val().Volume()/1000:.1f} cm3")
    # cópia no caminho antigo (compatibilidade)
    cq.exporters.export(modelo(), str(RAIZ / "exports" / "p01_base_inferior.stl"),
                        tolerance=0.01, angularTolerance=0.1)


if __name__ == "__main__":
    exportar(RAIZ / "exports" / "p01_p02_base")
