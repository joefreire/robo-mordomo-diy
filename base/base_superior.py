"""Peça 02 — Base superior (creme) + difusor cego do LED (módulo M08, V1).

Casca de 45 mm (z 25 -> 70) sobre a Peça 01:
  - contorno de baixo = topo da Peça 01; laterais continuam a inclinação de 6°;
  - transição para o topo: faixa a 40° da vertical + filete grande (suave e imprimível
    de cabeça para baixo); topo plano em z = 70 com a plataforma Ø110 marcada por um
    sulco raso (a face inteira é plana, a cintura apoia em qualquer ponto dela);
  - aba perimetral de 3 mm que desce 3 mm POR DENTRO da parede da 01, seguindo a
    inclinação, com FOLGA_ENCAIXE por lado; a borda de baixo da 02 apoia na borda da 01;
  - 4 bosses com inserto M3 (parafusos vêm por baixo, pela Peça 01), ligados à parede
    por uma nervura cada;
  - IF-CINTURA: 4 insertos M4, passa-cabos Ø25, teto engrossado sob a plataforma, anel
    de nervura Ø100 e 6 nervuras radiais de 3 mm até a casca;
  - IF-LED (frente, +Y): rasgo de 120 × 12 aberto para baixo, na junta com a 01, com
    moldura interna (bochechas + lábio). O difusor é um "trecho de parede" removível:
    apoia na borda da 01, entra na 01 como a aba (não sai para fora), sobe atrás da
    verga (não sai para fora) e encosta no lábio (não cai para dentro). Para trocar:
    tirar os 4 M3 de baixo e levantar a 02. Na V2 a régua de LED vai no mesmo lugar.

Impressão: DE CABEÇA PARA BAIXO (topo z = 70 na mesa). Escolhido em vez de "abertura
para baixo" porque: (1) o teto inteiro apoia na mesa — nenhuma ponte (de pé, o teto de
~180 × 150 viraria pontes de até 40 mm entre nervuras); (2) a face da IF-CINTURA sai
plana da mesa; (3) laterais de 6° e a transição a 40° da vertical imprimem sem suporte;
(4) nervuras, bosses, aba e moldura do LED crescem a partir do teto. O rasgo do LED é
aberto na junta justamente para não ter verga em ponte nesta orientação.

Rodar a partir da pasta robot-butler/:
    ~/.venvs/cadquery/bin/python base/base_superior.py
"""
import math
import sys
from pathlib import Path

import cadquery as cq

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from parameters import globais as G  # noqa: E402
from parameters import base as B  # noqa: E402

# ============================================================
# PARÂMETROS LOCAIS
# ============================================================
L, P, R, ANG = G.BASE_LARG, G.BASE_PROF, G.BASE_RAIO, G.BASE_INCLINACAO
T = B.TAN_INCL
W = G.P01_PAREDE                     # parede da 02 = parede da 01 (3)
Z0 = G.P01_ALTURA                    # 25: borda de baixo (apoia no topo da 01)
Z1 = G.Z_TOPO_P02                    # 70: face de cima (IF-CINTURA)
FOLGA = G.FOLGA_ENCAIXE

# forma externa
Z_TRANS = 48.0                       # começa a transição para o topo
TRANS_TAPER = 40.0                   # graus da vertical (≤ 45: imprime de cabeça para baixo)
FILETE_TRANS = 25.0                  # concordância parede 6° -> faixa 40°
FILETE_TOPO = 3.0                    # aresta do topo (na mesa: balanço < 1 mm de altura)
FILETE_BASE = 1.5                    # aresta de baixo = filete do topo da 01 (sulco de junta)

# aba de encaixe
ABA_RAIZ = 4.5                       # altura da raiz da aba acima da junta (une aba à parede)

# plataforma / IF-CINTURA
PLAT_D = G.P02_PLATAFORMA_D
PLAT_ESP = 6.0                       # teto engrossado sob a plataforma (casca = 3)
PLAT_ESP_D = 104.0                   # diâmetro do engrosso (dentro do anel)
SULCO_LARG, SULCO_PROF = 1.2, 0.4    # marca da plataforma Ø110 na face de cima
M4_FURO_PROF = 10.0                  # parafuso M4×12 da 08A chega a 8,5 abaixo da face
M4_BOSS_D = G.M4_INSERTO_FURO + 2 * 2.5
M4_BOSS_ALT = M4_FURO_PROF + 2.5     # do topo para baixo
CABO_COLAR_D = G.IF_CINTURA_CABO_D + 2 * 3.0

# nervuras
NERV_ESP = 3.0
NERV_ALT = 15.0                      # descem do teto até z = 55
ANEL_R = 50.0                        # anel de nervura (centro da espessura)
NERV_ANGS = [0.0, 60.0, 120.0, 180.0, 240.0, 300.0]   # evitam os bosses M3 (≈50°, 130°…)

# bosses M3 (união com a 01, insertos por baixo)
M3_FURO_PROF = 8.0                   # M3×25 sai 6,5 acima da junta; inserto 5,7
BOSS_M3_D = G.BASE_TORRE_D
NERV_BOSS_Z0 = Z0                    # nervura boss->parede começa acima da junta

# IF-LED (rasgo frontal, aberto para baixo na junta)
LED_L, LED_A = G.P02_LED             # 120 × 12 visível
LED_Z_TOPO = Z0 + LED_A              # 37: verga
LED_LINGUETA = 6.0                   # difusor sobe 6 mm atrás da verga
LED_LABIO = 3.0                      # lábio atrás do difusor
LED_MOLD_LADO = 6.0                  # bochechas da moldura além do rasgo (cada lado)
LED_MOLD_SOBRE = 3.0                 # moldura passa 3 mm acima da lingueta antes do chanfro 45°

# coordenada "u" ao longo da frente: u = y + T·z (u constante = plano paralelo à parede)
U_EXT = P / 2                        # 100: face externa (01 e 02)
U_INT = U_EXT - W                    # 97: face interna da parede
U_ABA_EXT = U_INT - FOLGA            # 96,7: face externa da aba
U_ABA_INT = U_ABA_EXT - B.ABA_ESP    # 93,7: face interna da aba = trás do difusor
U_LABIO = U_ABA_INT - LED_LABIO      # 90,7
Z_LING_TOPO = LED_Z_TOPO + LED_LINGUETA   # 43


# ============================================================
# AUXILIARES
# ============================================================
def perfil(z0, h, taper, extra=0.0):
    """Contorno da base na altura z0 recuado de `extra` (horizontal), extrudado h com taper."""
    r0 = G.recuo(z0) + extra
    return (cq.Workplane("XY").workplane(offset=z0).sketch()
            .rect(L - 2 * r0, P - 2 * r0).vertices().fillet(R - r0).finalize()
            .extrude(h, taper=taper))


def _cil(x, y, d, z0, z1):
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).circle(d / 2).extrude(z1 - z0)


def _uz(pts):
    """(u, z) -> (y, z) no plano YZ (para perfis que seguem a parede da frente)."""
    return [(u - T * z, z) for u, z in pts]


def _prisma_frente(pts_uz, x0, x1):
    return (cq.Workplane("YZ").workplane(offset=x0)
            .polyline(_uz(pts_uz)).close().extrude(x1 - x0))


# ============================================================
# PEÇA 02
# ============================================================
def solido_externo():
    a = perfil(Z0, Z_TRANS - Z0, ANG)
    b = perfil(Z_TRANS, Z1 - Z_TRANS, TRANS_TAPER)
    s = a.union(b)
    s = s.edges(cq.selectors.BoxSelector((-200, -200, Z_TRANS - 0.1), (200, 200, Z_TRANS + 0.1))
                ).fillet(FILETE_TRANS)
    return s


def casca():
    ext = solido_externo()
    c = ext.faces("<Z").shell(-W)
    sol = c.val()
    # filetes externos depois da casca (o offset interno não degenera)
    topo = [e for e in sol.Edges() if abs(e.Center().z - Z1) < 1e-3]
    sol = sol.fillet(FILETE_TOPO, topo)
    fundo = cq.Workplane(obj=sol).faces("<Z").val().outerWire().Edges()
    sol = sol.fillet(FILETE_BASE, fundo)
    return cq.Workplane(obj=sol), ext


def aba():
    s1 = perfil(B.Z_JUNTA, Z0 - B.Z_JUNTA, ANG, W + FOLGA).union(
        perfil(Z0, ABA_RAIZ, ANG, W - 0.5))
    e_int = W + FOLGA + B.ABA_ESP
    s2 = perfil(B.Z_JUNTA - 0.01, Z0 - B.Z_JUNTA + 0.01, ANG, e_int).union(
        perfil(Z0, ABA_RAIZ + 0.5, -45.0, e_int))          # raiz a 45° (imprime sem apoio)
    return s1.cut(s2)


def nervuras():
    z0 = Z1 - NERV_ALT
    s = _cil(0, 0, 2 * ANEL_R + NERV_ESP, z0, Z1).cut(_cil(0, 0, 2 * ANEL_R - NERV_ESP, z0 - 1, Z1 + 1))
    for a in NERV_ANGS:
        n = (cq.Workplane("XY").workplane(offset=z0).center(ANEL_R + 40, 0)
             .rect(80, NERV_ESP).extrude(NERV_ALT)
             .rotate((0, 0, 0), (0, 0, 1), a))
        s = s.union(n)
    return s


def plataforma():
    s = _cil(0, 0, PLAT_ESP_D, Z1 - PLAT_ESP, Z1)
    s = s.union(_cil(0, 0, CABO_COLAR_D, Z1 - M4_BOSS_ALT, Z1))
    for x, y in G.IF_CINTURA_M4:
        s = s.union(_cil(x, y, M4_BOSS_D, Z1 - M4_BOSS_ALT, Z1))
    return s


def bosses_m3():
    s = None
    for x, y in B.BASE_TORRES:
        b = _cil(x, y, BOSS_M3_D, B.Z_JUNTA, Z1)
        sy = 1 if y > 0 else -1
        web = (cq.Workplane("XY").workplane(offset=NERV_BOSS_Z0).center(x, y + sy * 15)
               .rect(NERV_ESP, 30).extrude(Z1 - NERV_BOSS_Z0))
        b = b.union(web)
        s = b if s is None else s.union(b)
    return s


def moldura_led():
    x = LED_L / 2 + LED_MOLD_LADO
    zb = Z_LING_TOPO + LED_MOLD_SOBRE
    pts = [(U_LABIO, B.Z_JUNTA), (U_ABA_EXT, B.Z_JUNTA), (U_ABA_EXT, Z0), (U_EXT - 1, Z0),
           (U_EXT - 1, zb + (U_EXT - 1 - U_LABIO)), (U_LABIO, zb)]      # topo a 45°
    return _prisma_frente(pts, -x, x)


def rasgo_led():
    pts = [(U_ABA_INT, B.Z_JUNTA - 1), (U_EXT + 1, B.Z_JUNTA - 1), (U_EXT + 1, LED_Z_TOPO),
           (U_INT, LED_Z_TOPO), (U_INT, Z_LING_TOPO), (U_ABA_INT, Z_LING_TOPO)]
    return _prisma_frente(pts, -LED_L / 2, LED_L / 2)


def modelo():
    p, ext = casca()
    interno = (aba().union(nervuras()).union(plataforma()).union(bosses_m3())
               .union(moldura_led()))
    # nada interno sai da casca, nem desce abaixo da junta
    limite = ext.union(perfil(B.Z_JUNTA, Z0 - B.Z_JUNTA, ANG, W + FOLGA))
    p = p.union(interno.intersect(limite))
    # furos
    p = p.cut(_cil(0, 0, G.IF_CINTURA_CABO_D, Z1 - 30, Z1 + 1))
    for x, y in G.IF_CINTURA_M4:
        p = p.cut(_cil(x, y, G.M4_INSERTO_FURO, Z1 - M4_FURO_PROF, Z1 + 1))
    for x, y in B.BASE_TORRES:
        p = p.cut(_cil(x, y, G.M3_INSERTO_FURO, B.Z_JUNTA - 1, B.Z_JUNTA + M3_FURO_PROF))
    sulco = _cil(0, 0, PLAT_D + SULCO_LARG, Z1 - SULCO_PROF, Z1 + 1).cut(
        _cil(0, 0, PLAT_D - SULCO_LARG, Z1 - 2, Z1 + 2))
    p = p.cut(sulco)
    p = p.cut(rasgo_led())
    return p


# ============================================================
# DIFUSOR CEGO (M08, V1) — mesmo contorno do rasgo, com folga
# ============================================================
def difusor_cego():
    g = FOLGA
    pts = [(U_ABA_INT + g, B.Z_JUNTA), (U_ABA_EXT, B.Z_JUNTA), (U_ABA_EXT, Z0), (U_EXT, Z0),
           (U_EXT, LED_Z_TOPO - g), (U_INT - g, LED_Z_TOPO - g), (U_INT - g, Z_LING_TOPO - g),
           (U_ABA_INT + g, Z_LING_TOPO - g)]
    return _prisma_frente(pts, -LED_L / 2 + g, LED_L / 2 - g)


PECAS = {"02_base_superior": modelo, "02L_difusor_cego": difusor_cego}
BOM = [
    ("Inserto térmico M4 na face de cima (IF-CINTURA)", 4),
    ("Inserto térmico M3 nos bosses de baixo (união com a 01)", 4),
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


if __name__ == "__main__":
    exportar(RAIZ / "exports" / "p01_p02_base")
