"""Peça 11 — Pescoço manual pan/tilt (V1) — REVISÃO B (rigidez para câmera).

Mudanças da rev. A (congelada em pescoco_manual_revA.py):
  - tilt apoiado dos DOIS lados em BUCHAS substituíveis (bronze sinterizado 5×8×L ou
    impressa), eixo M5 de corpo liso (parcialmente roscado) — o liso fica nas buchas;
  - CALÇOS finos entre berço e montantes zeram a folga axial sem reimprimir nada;
  - montantes mais grossos e fundos + nervuras (garfo sem balanço);
  - mesa do pan mais alta (mancal mais longo no cubo) e arruela PTFE maior (menos inclinação);
  - placa da cabeça mais grossa, com abas de reforço, apoiada num berço mais largo;
  - pontos de amarração de cabo no berço; cabos não tocam superfícies de fricção;
  - corrigido: o pino do batente do tilt saía para dentro do montante (não batia).
Nada de material macio entre a placa da cabeça e o mecanismo (amortecimento só no suporte
interno da câmera, na cabeça).


PAN (eixo vertical, ±90°)              TILT (eixo horizontal X, ±30°)
  11A flange do tronco + cubo fixo        11B garfo: 2 montantes sobre a mesa (uma peça com ela)
  11B mesa giratória (+ garfo)            11D berço: gira no eixo M5; leva a placa da cabeça
  11C anel de retenção (cubo, 3×M3)       eixo M5 aço + porca autotravante = retenção
  trava pan: manípulo radial M4 + sapata  trava tilt: manípulo M4 no montante, pino em furos
  batente: pino em rasgo de arco            de indexação a cada 10° no berço
                                          batente: pino no montante em rasgo de arco no berço
  11E placa da cabeça (IF-CABEÇA), parafusada no berço; a cabeça parafusa nela.

Retenção axial nos dois eixos independe das travas: anel 11C no cubo (pan) e M5 + porca
autotravante (tilt). As travas só seguram o giro.

Coordenadas: z = 0 no topo do tronco (IF-PESCOÇO); eixo do robô em (0,0). +Y = frente.
Impressão: 11A, 11B e 11D de fundo na mesa (garfo em pé); 11C, 11E deitados; manípulos de
cabeça para baixo.
"""
import math
import sys
from pathlib import Path

import cadquery as cq

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from parameters import globais as G  # noqa: E402

# ============================================================
# PARÂMETROS
# ============================================================
PAN_GIRO = 90.0
TILT_GIRO = 30.0
TILT_PASSO = 10.0
FOLGA = 0.2

# 11A
A_D, A_ESP = 64.0, 6.0               # ≤ IF_PESCOCO_FACE_D (66)
CUBO_DE, CUBO_DI = 34.0, G.IF_PESCOCO_CABO_D
M3_REB_D, M3_REB_P = 6.0, 3.2

# arruelas pan
PTFE_DI, PTFE_DE, PTFE_ESP = 34.5, 52.0, 1.0   # tem que ficar por dentro do pino do batente (r 27,0)
SIL_DI, SIL_DE, SIL_ESP, SIL_COMP = 34.5, 46.0, 2.0, 0.6

# 11B mesa
B_D, B_ESP = 70.0, 14.0               # rev B: mesa Ø70 (≤75), mancal de 14 mm no cubo
REBAIXO_D, REBAIXO_P = 48.0, 7.0
ANEL_DE, ANEL_ESP = REBAIXO_D - 1.0, 4.0
ANEL_PARAF_R, ANEL_N = (CUBO_DI / 2 + CUBO_DE / 2) / 2, 3     # 12,5
PIN_PAN_R, PIN_PAN_ANG, PIN_PAN_D, PIN_PAN_H = 29.5, 270.0, 5.0, 2.5   # atrás; rev A cruzava a arruela PTFE
RASGO_FOLGA, RASGO_P = 0.3, 3.0
TRAVA_PAN_ANG, TRAVA_PAN_ZREL, SAPATA_D = 0.0, 4.0, 5.0       # lado direito do robô

# garfo
VAO_BERCO = 40.0                      # largura do berço (X)
ARR_TILT_ESP = 1.0                    # arruela PTFE de cada lado (encosto)
CALCO_ESP = 0.5                       # pacote de calços 0,1–0,5 mm por lado (ajuste da folga axial)
MONT_ESP = 10.0                       # rev B (era 8)
MONT_PROF = 30.0                      # Y (era 26)
NERV_ESP, NERV_COMP, NERV_ALT = 4.0, 10.0, 16.0   # nervuras na frente/atrás de cada montante
Z_TILT_REL = 30.0                     # eixo do tilt acima do topo da mesa
MONT_ACIMA = 11.0
# eixo e buchas do tilt
# Eixo = parafuso com OMBRO (ISO 7379) Ø6 × 65, rosca M5 + porca autotravante. O ombro liso
# cobre as duas buchas inteiras (vão externo dos montantes = 63 mm). Um M5×70 comum só tem
# ~48 mm lisos: a rosca rodaria dentro da bucha (achado na validação da rev. B).
EIXO_D = 6.0
EIXO_OMBRO_L = 65.0
EIXO_FOLGA_BERCO = 0.05               # berço justo no eixo (o eixo gira nas buchas)
BUCHA_DE, BUCHA_DI = 10.0, 6.0        # bucha comercial 6×10×10 (bronze sinterizado) ou impressa
BUCHA_INTERF = 0.05                   # alojamento menor que a bucha (prensada à mão)
PIN_TILT_R, PIN_TILT_D = 11.0, 4.0
INDEX_TILT_R, INDEX_D, INDEX_P = 11.0, 4.6, 2.5

# 11D berço
BERCO_PROF = 40.0                     # Y (rev B: mais largo, apoia melhor a placa)
BERCO_Z0_REL, BERCO_Z1_REL = -12.0, 15.0       # em relação ao eixo do tilt
PLACA_ESP = 6.0                       # rev B (era 5)
ABA_ALT, ABA_LARG, ABA_X = 5.0, 3.5, 36.0   # abas de reforço sob a placa (frente e trás), entre os montantes
AMARRA_L, AMARRA_A = 4.0, 2.5               # rasgo de abraçadeira no berço
JANELA_X, JANELA_Y = 24.0, 22.0         # passagem de cabos no berço (2 canais de ~8 mm ao lado do eixo)
PLACA_FIX = [(sx * 16.0, sy * 14.0) for sx in (-1, 1) for sy in (-1, 1)]   # 11E -> berço, fora da janela

# alturas (z a partir do topo do tronco)
Z_A = A_ESP
Z_B0 = Z_A + PTFE_ESP
Z_B1 = Z_B0 + B_ESP
Z_REB = Z_B1 - REBAIXO_P
Z_ANEL = Z_REB + SIL_ESP
Z_CUBO = Z_ANEL - SIL_COMP
Z_TILT = Z_B1 + Z_TILT_REL
Z_PLACA0 = G.PESCOCO_ALTURA - PLACA_ESP
X_MONT_INT = VAO_BERCO / 2 + ARR_TILT_ESP + CALCO_ESP
PIN_TILT_H = ARR_TILT_ESP + CALCO_ESP + 2.0     # atravessa arruela+calço e entra 2 mm no rasgo
assert Z_TILT + BERCO_Z1_REL <= Z_PLACA0 + 0.01, "berço invade a placa da cabeça"


def _pol(r, a):
    a = math.radians(a)
    return (r * math.cos(a), r * math.sin(a))


def _cil(r, z0, h, xy=(0, 0)):
    return cq.Workplane("XY").workplane(offset=z0).center(*xy).circle(r).extrude(h)


def _cil_x(r, x0, comp, y=0.0, z=0.0):
    """Cilindro ao longo de X, começando em x0."""
    return cq.Workplane("YZ").workplane(offset=x0).center(y, z).circle(r).extrude(comp)


def _arco(r, larg, a0, a1, z0, h, plano="XY"):
    wp = lambda: cq.Workplane(plano)  # noqa: E731
    p = wp().workplane(offset=z0).circle(r + larg / 2).circle(r - larg / 2).extrude(h)
    meio = (a0 + a1) / 2
    setor = wp().workplane(offset=z0 - 0.5).polyline([(0, 0), _pol(200, a0), _pol(200, meio), _pol(200, a1)]).close().extrude(h + 1)
    p = p.intersect(setor)
    for a in (a0, a1):
        p = p.union(wp().workplane(offset=z0).center(*_pol(r, a)).circle(larg / 2).extrude(h))
    return p


# ============================================================
def flange_tronco():  # 11A
    p = _cil(A_D / 2, 0, A_ESP).faces(">Z").edges().fillet(1.0)
    p = p.union(_cil(CUBO_DE / 2, A_ESP, Z_CUBO - A_ESP))
    p = p.union(_cil(PIN_PAN_D / 2, A_ESP, PIN_PAN_H, _pol(PIN_PAN_R, PIN_PAN_ANG)))
    p = p.cut(_cil(CUBO_DI / 2, -1, Z_CUBO + 2))
    for x, y in G.IF_PESCOCO_M3:
        p = p.cut(_cil(G.M3_PASSANTE / 2, -1, A_ESP + 2, (x, y)))
        p = p.cut(_cil(M3_REB_D / 2, A_ESP - M3_REB_P, M3_REB_P + 1, (x, y)))
    for i in range(ANEL_N):
        p = p.cut(_cil(G.M3_INSERTO_FURO / 2, Z_CUBO - G.M3_INSERTO_PROF - 0.5, G.M3_INSERTO_PROF + 1,
                       _pol(ANEL_PARAF_R, 90 + 120 * i)))
    return p


def mesa_garfo():  # 11B
    p = _cil(B_D / 2, Z_B0, B_ESP)
    for sx in (-1, 1):
        x0 = X_MONT_INT if sx > 0 else -X_MONT_INT - MONT_ESP
        mont = (cq.Workplane("XY").workplane(offset=Z_B1 - 0.01).center(x0 + MONT_ESP / 2, 0)
                .rect(MONT_ESP, MONT_PROF).extrude(Z_TILT_REL + MONT_ACIMA))
        mont = mont.edges("|X and >Z").fillet(MONT_PROF / 2 - 0.5)
        p = p.union(mont)
        # nervuras na frente e atrás do montante (triângulo no plano YZ, espessura no X)
        for sy in (-1, 1):
            y0 = sy * MONT_PROF / 2
            tri = (cq.Workplane("YZ").workplane(offset=x0 + (MONT_ESP - NERV_ESP) / 2)
                   .polyline([(y0, Z_B1 - 0.01), (y0 + sy * NERV_COMP, Z_B1 - 0.01), (y0, Z_B1 + NERV_ALT)])
                   .close().extrude(NERV_ESP))
            p = p.union(tri)
    p = p.cut(_cil(CUBO_DE / 2 + FOLGA, Z_B0 - 1, B_ESP + 2))
    p = p.cut(_cil(REBAIXO_D / 2, Z_REB, REBAIXO_P + 1))
    p = p.cut(_arco(PIN_PAN_R, PIN_PAN_D + 2 * RASGO_FOLGA, PIN_PAN_ANG - PAN_GIRO, PIN_PAN_ANG + PAN_GIRO,
                    Z_B0 - 0.01, RASGO_P))
    # alojamento das BUCHAS nos dois montantes (atravessa o montante inteiro)
    for x0 in (-X_MONT_INT - MONT_ESP - 0.5, X_MONT_INT - 0.5):
        p = p.cut(_cil_x((BUCHA_DE - BUCHA_INTERF) / 2, x0, MONT_ESP + 1, 0, Z_TILT))
    # alojamento da porca M5 (lado esquerdo, por fora) e rebaixo da cabeça (direito)
    # (porca M5 e cabeça do parafuso de ombro ficam POR FORA dos montantes, encostadas nas buchas)
    # pino do batente do tilt (montante esquerdo, face interna)
    py, pz = _pol(PIN_TILT_R, 90)
    p = p.union(cq.Workplane("YZ").workplane(offset=-X_MONT_INT - 0.5).center(py, Z_TILT + pz)
                .circle(PIN_TILT_D / 2).extrude(PIN_TILT_H + 0.5))
    # trava do tilt: inserto M4 no montante direito, no raio da indexação, em cima (frente)
    ty, tz = _pol(INDEX_TILT_R, 150)
    p = p.cut(cq.Workplane("YZ").workplane(offset=X_MONT_INT - 0.5).center(ty, Z_TILT + tz)
              .circle(G.M4_INSERTO_FURO / 2).extrude(MONT_ESP + 1))
    # trava do pan: inserto M4 radial na mesa + guia da sapata até o cubo
    ax, ay = _pol(1, TRAVA_PAN_ANG)
    pl = cq.Plane(origin=(0, 0, Z_B0 + TRAVA_PAN_ZREL), xDir=(-ay, ax, 0), normal=(ax, ay, 0))
    p = p.cut(cq.Workplane(pl).circle(SAPATA_D / 2 + 0.15).extrude(B_D / 2 + 1))
    p = p.cut(cq.Workplane(pl).workplane(offset=B_D / 2 - G.M4_INSERTO_PROF).circle(G.M4_INSERTO_FURO / 2)
              .extrude(G.M4_INSERTO_PROF + 2))
    # passagem de cabos sobe pelo centro (furo da mesa = furo do cubo)
    return p


def anel_retencao():  # 11C
    p = cq.Workplane("XY").workplane(offset=Z_ANEL).circle(ANEL_DE / 2).circle(CUBO_DI / 2 + 0.5).extrude(ANEL_ESP)
    for i in range(ANEL_N):
        xy = _pol(ANEL_PARAF_R, 90 + 120 * i)
        p = p.cut(_cil(G.M3_PASSANTE / 2, Z_ANEL - 1, ANEL_ESP + 2, xy))
        p = p.cut(_cil(3.0, Z_ANEL + ANEL_ESP - 1.8, 2, xy))
    return p


def berco():  # 11D (gira no eixo do tilt)
    z0, z1 = Z_TILT + BERCO_Z0_REL, Z_TILT + BERCO_Z1_REL
    p = (cq.Workplane("XY").workplane(offset=z0).rect(VAO_BERCO, BERCO_PROF).extrude(z1 - z0)
         .edges("|X and <Z").fillet(10.0))
    # janela central para os cabos (de baixo até a placa)
    # o eixo M5 cruza a janela no meio (y=0): os cabos passam em dois canais, um de cada lado
    p = p.cut(cq.Workplane("XY").workplane(offset=z0 - 1).rect(JANELA_X, JANELA_Y).extrude(z1 - z0 + 2))
    p = p.cut(_cil_x(EIXO_D / 2 + EIXO_FOLGA_BERCO, -VAO_BERCO, 2 * VAO_BERCO, 0, Z_TILT))
    # amarração de cabo: rasgos para abraçadeira nas paredes da frente e de trás da janela
    for sy in (-1, 1):
        p = p.cut(cq.Workplane("XY").workplane(offset=z1 - 7).center(0, sy * (JANELA_Y / 2 + (BERCO_PROF - JANELA_Y) / 4))
                  .rect(AMARRA_L, (BERCO_PROF - JANELA_Y) / 2 + 0.02).extrude(AMARRA_A))
    # rasgo do batente na face esquerda (pino do montante); berço gira ±TILT_GIRO
    larg = PIN_TILT_D + 2 * RASGO_FOLGA
    rasgo = _arco(PIN_TILT_R, larg, 90 - TILT_GIRO, 90 + TILT_GIRO, 0, RASGO_P, plano="YZ")
    p = p.cut(rasgo.translate((-VAO_BERCO / 2 - 0.01, 0, Z_TILT)))
    # furos de indexação na face direita (manípulo do montante direito)
    n = int(round(2 * TILT_GIRO / TILT_PASSO)) + 1
    for i in range(n):
        th = -TILT_GIRO + i * TILT_PASSO
        y, z = _pol(INDEX_TILT_R, 150 - th)
        p = p.cut(cq.Workplane("YZ").workplane(offset=VAO_BERCO / 2 - INDEX_P).center(y, Z_TILT + z)
                  .circle(INDEX_D / 2).extrude(INDEX_P + 0.1))
    # 2 insertos M3 no topo para a placa 11E
    for xy in PLACA_FIX:
        p = p.cut(_cil(G.M3_INSERTO_FURO / 2, z1 - G.M3_INSERTO_PROF - 0.5, G.M3_INSERTO_PROF + 1, xy))
    return p


def placa_cabeca():  # 11E — IF-CABEÇA
    lx, ly = G.IF_CABECA_PLACA
    p = (cq.Workplane("XY").workplane(offset=Z_PLACA0).rect(lx, ly).extrude(PLACA_ESP)
         .edges("|Z").fillet(6.0))
    p = p.cut(_cil(G.IF_CABECA_CABO_D / 2, Z_PLACA0 - 1, PLACA_ESP + 2))
    for xy in G.IF_CABECA_M3:
        p = p.cut(_cil(G.M3_INSERTO_FURO / 2, G.PESCOCO_ALTURA - G.IF_CABECA_INSERTO_PROF - 0.5,
                       G.IF_CABECA_INSERTO_PROF + 1, xy))                   # inserto M3 curto, de cima
    # abas de reforço (frente e trás), entre os montantes, por fora do berço
    for sy in (-1, 1):
        p = p.union(cq.Workplane("XY").workplane(offset=Z_PLACA0 - ABA_ALT + 0.01)
                    .center(0, sy * (ly / 2 - ABA_LARG / 2)).rect(ABA_X, ABA_LARG).extrude(ABA_ALT))
    for xy in G.IF_CABECA_PINOS:
        p = p.union(_cil(G.IF_CABECA_PINO_D / 2, G.PESCOCO_ALTURA, 3.0, xy))
    # fixação no berço: 4×M3 escareados de cima
    for x, y in PLACA_FIX:
        p = p.cut(_cil(G.M3_PASSANTE / 2, Z_PLACA0 - 1, PLACA_ESP + 2, (x, y)))
        p = p.cut(_cil(3.2, G.PESCOCO_ALTURA - 1.8, 2, (x, y)))          # rebaixo da cabeça M3
    return p


def manipulo(pos_plano):
    """Manípulo sextavado com cabeça M4 embutida (mesmo desenho do ombro)."""
    corpo = cq.Workplane("XY").polygon(6, 20.0).extrude(10.0).edges("|Z").fillet(2.5)
    corpo = corpo.cut(cq.Workplane("XY").circle(G.M4_PASSANTE / 2).extrude(11))
    corpo = corpo.cut(cq.Workplane("XY").workplane(offset=10 - 4.5).circle(3.7).extrude(5))
    return cq.Workplane("XY").add(corpo.val().moved(cq.Location(pos_plano)))


def manipulo_pan():
    ax, ay = _pol(1, TRAVA_PAN_ANG)
    pl = cq.Plane(origin=(ax * (B_D / 2 + 3), ay * (B_D / 2 + 3), Z_B0 + TRAVA_PAN_ZREL), xDir=(-ay, ax, 0), normal=(ax, ay, 0))
    return manipulo(pl)


def manipulo_tilt():
    ty, tz = _pol(INDEX_TILT_R, 150)
    pl = cq.Plane(origin=(X_MONT_INT + MONT_ESP + 3, ty, Z_TILT + tz), xDir=(0, 1, 0), normal=(1, 0, 0))
    return manipulo(pl)


PECAS = {"11A_flange_tronco": flange_tronco, "11B_mesa_garfo": mesa_garfo, "11C_anel_retencao": anel_retencao,
         "11D_berco_tilt": berco, "11E_placa_cabeca": placa_cabeca,
         "11F_manipulo_pan": manipulo_pan, "11G_manipulo_tilt": manipulo_tilt}
PAN_GIRAM = {"11B_mesa_garfo", "11D_berco_tilt", "11E_placa_cabeca", "11F_manipulo_pan", "11G_manipulo_tilt"}
TILT_GIRAM = {"11D_berco_tilt", "11E_placa_cabeca"}

BOM = [
    ("Parafuso M3 × 10 (11A -> topo do tronco)", 4), ("Inserto térmico M3 no topo do tronco (IF-PESCOÇO)", 4),
    ("Parafuso M3 × 10 (anel 11C -> cubo)", 3), ("Inserto térmico M3 no cubo (11A)", 3),
    ("Parafuso com ombro ISO 7379 Ø6 × 65, rosca M5 (eixo do tilt)", 1), ("Porca M5 autotravante + arruela M5", 1),
    (f"Bucha bronze sinterizado {BUCHA_DI:g}×{BUCHA_DE:g}×{MONT_ESP:g} (ou impressa)", 2), ("Calço Ø6×Ø12 0,1/0,2/0,3 mm (jogo)", 1),
    ("Parafuso M4 × 20 (manípulo pan, radial)", 1), ("Parafuso M4 × 20 (manípulo tilt)", 1),
    ("Inserto térmico M4 (mesa e montante)", 2),
    ("Parafuso M3 × 8 escareado (placa 11E -> berço)", 4), ("Inserto térmico M3 no berço", 4),
    ("Inserto térmico M3 na placa 11E (a cabeça parafusa aqui)", 4),
    (f"Arruela PTFE Ø{PTFE_DI:g}×Ø{PTFE_DE:g}×{PTFE_ESP:g} (pan)", 1),
    (f"Arruela de silicone Ø{SIL_DI:g}×Ø{SIL_DE:g}×{SIL_ESP:g} (pan)", 1),
    (f"Arruela PTFE Ø6,2×Ø16×{ARR_TILT_ESP:g} (tilt, uma de cada lado)", 2),
]

if __name__ == "__main__":
    out = RAIZ / "exports" / "p11_pescoco"
    out.mkdir(parents=True, exist_ok=True)
    for nome, fn in PECAS.items():
        s = fn()
        cq.exporters.export(s, str(out / f"{nome}.stl"), tolerance=0.01, angularTolerance=0.1)
        cq.exporters.export(s, str(out / f"{nome}.step"))
        bb = s.val().BoundingBox()
        print(f"{nome:20s} {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:5.1f}  valido={s.val().isValid()} "
              f"solidos={len(s.solids().vals())} vol={s.val().Volume()/1000:.1f} cm3")
