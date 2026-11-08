"""Peça 08 — Cintura manual (V1). Gira à mão ±60°, fricção ajustável, trava, removível.

Componentes (todos PETG, cada um uma impressão):
  08A flange inferior  : parafusa na Peça 02 (IF-CINTURA, 4×M4 de cima para baixo).
                         Traz o CUBO central (eixo fixo, Ø25 livre) e o PINO do batente.
  08B flange superior  : gira no cubo; o tronco parafusa nela (4 insertos M4 por cima).
                         Rasgo em arco embaixo = batentes ±60°. Furo radial da trava.
  08C anel de retenção : parafusa no topo do cubo (3×M3). Prende a 08B (o tronco não sai
                         ao levantar) e comprime a arruela de silicone = ajuste da fricção.
  08D colar            : cosmético, creme. Desliza por cima da 08B, apoia no ressalto dela e
                         fica preso entre a 08B e o piso do tronco. Janela p/ a trava.
  08E sapata da trava  : pastilha entre o parafuso radial e o cubo (não marca o cubo).
Comprados: arruela PTFE (apoio, baixo atrito), arruela de silicone (fricção), parafusos.

Caminhos de carga (hipóteses na documentação):
  peso    : tronco -> 4×M4 -> 08B -> arruela PTFE -> 08A -> 4×M4 -> Peça 02
  levantar: 08B -> silicone -> 08C -> 3×M3 -> cubo/08A -> 4×M4 -> Peça 02
  tombar  : 08B no cubo (Ø42 × ~9 mm) + borda da arruela PTFE
A trava (radial) só impede o giro; não segura nada no eixo Z.

Coordenadas: z = 0 na face de cima da Peça 02; eixo do robô em (0, 0). +Y = frente.
Impressão: 08A e 08B de fundo na mesa; 08C deitado; 08D de cabeça para baixo.
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
H_TOTAL = G.IF_CINTURA_ALTURA          # 24
FOLGA_GIRO = 0.2                        # folga radial por lado, furo da 08B no cubo
FOLGA_COLAR = 0.3                       # folga radial por lado, colar sobre a 08B

# 08A flange inferior
FI_D = 86.0
FI_ESP = 8.0
CUBO_DE = 42.0                          # diâmetro externo do cubo (o "eixo")
CUBO_DI = G.IF_CINTURA_CABO_D           # passa-cabos Ø25 livre
M4_REBAIXO_D = G.M4_CABECA_D + 1.0
M4_REBAIXO_PROF = G.M4_CABECA_H + 0.5

# arruelas compradas
PTFE_DI, PTFE_DE, PTFE_ESP = 43.0, 58.0, 1.0
SIL_DI, SIL_DE, SIL_ESP = 43.0, 54.0, 2.0
SIL_COMPRESSAO_MAX = 0.8                # 40 %: o anel encosta no cubo e para de apertar

# 08B flange superior
FS_DE = 90.0
FS_ALT = 15.0
FS_ABA_D = 96.0                         # ressalto embaixo: apoio do colar
FS_ABA_ALT = 2.0
FS_REBAIXO_D = 56.0                     # alojamento do anel de retenção (por cima)
FS_REBAIXO_PROF = 7.0
FS_INSERTO_PROF = 9.0                   # furos dos insertos M4 (de cima)

# batente: pino fixo na 08A, rasgo em arco na 08B
PINO_R = 35.0                           # raio do pino
PINO_ANG = 90.0                         # na frente (+Y), escondido sob o colar
PINO_D = 6.0
PINO_ALT = 3.5
RASGO_FOLGA = 0.3
RASGO_PROF = 4.0
GIRO = G.IF_CINTURA_GIRO

# 08C anel de retenção
ANEL_DE = FS_REBAIXO_D - 2 * 0.5
ANEL_DI = G.IF_CINTURA_CABO_D + 1.0
ANEL_ESP = 4.0
ANEL_PARAF_R = (CUBO_DI / 2 + CUBO_DE / 2) / 2   # 16,75: meio da parede do cubo
ANEL_PARAF_N = 3

# trava radial (atrás, -Y: fica do lado de trás do robô)
TRAVA_ANG = 270.0
TRAVA_Z_REL = 4.5                       # altura do eixo do furo acima da base da 08B
SAPATA_D = 5.0
SAPATA_COMP = 6.0

# 08D colar
COLAR_DE = G.IF_CINTURA_ENVELOPE_D
COLAR_FOLGA_BASE = 1.0                  # vão acima da Peça 02
COLAR_FOLGA_TOPO = 0.3                  # vão abaixo do piso do tronco
JANELA_L, JANELA_A = 14.0, 9.0
MARCA_CENTRO = 1.2                      # entalhe em V no colar (frente) = posição 0°

# alturas derivadas (z absoluto, Peça 02 em z=0)
Z_FI_TOPO = FI_ESP
Z_FS_BASE = Z_FI_TOPO + PTFE_ESP
Z_FS_TOPO = Z_FS_BASE + FS_ALT
Z_REBAIXO = Z_FS_TOPO - FS_REBAIXO_PROF
Z_ANEL_BASE = Z_REBAIXO + SIL_ESP
Z_CUBO_TOPO = Z_ANEL_BASE - SIL_COMPRESSAO_MAX
Z_TRAVA = Z_FS_BASE + TRAVA_Z_REL
assert abs(Z_FS_TOPO - H_TOTAL) < 1e-6, f"altura {Z_FS_TOPO} != IF_CINTURA_ALTURA {H_TOTAL}"
assert Z_ANEL_BASE + ANEL_ESP < Z_FS_TOPO, "anel saindo acima da 08B (bateria no piso do tronco)"


def _pol(r, ang):
    a = math.radians(ang)
    return (r * math.cos(a), r * math.sin(a))


# ============================================================
# 08A — flange inferior + cubo + pino
# ============================================================
def flange_inferior():
    base = cq.Workplane("XY").circle(FI_D / 2).extrude(FI_ESP)
    base = base.faces(">Z").edges().fillet(1.0)
    cubo = (cq.Workplane("XY").workplane(offset=FI_ESP)
            .circle(CUBO_DE / 2).extrude(Z_CUBO_TOPO - FI_ESP))
    pino = (cq.Workplane("XY").workplane(offset=FI_ESP)
            .center(*_pol(PINO_R, PINO_ANG)).circle(PINO_D / 2).extrude(PINO_ALT))
    p = base.union(cubo).union(pino)
    # passa-cabos
    p = p.cut(cq.Workplane("XY").circle(CUBO_DI / 2).extrude(Z_CUBO_TOPO + 1))
    # 4×M4 para a Peça 02: passante + rebaixo da cabeça por cima
    for x, y in G.IF_CINTURA_M4:
        p = p.cut(cq.Workplane("XY").center(x, y).circle(G.M4_PASSANTE / 2).extrude(FI_ESP))
        p = p.cut(cq.Workplane("XY").workplane(offset=FI_ESP - M4_REBAIXO_PROF)
                  .center(x, y).circle(M4_REBAIXO_D / 2).extrude(M4_REBAIXO_PROF + 0.01))
    # insertos M3 no topo do cubo (anel de retenção)
    for i in range(ANEL_PARAF_N):
        x, y = _pol(ANEL_PARAF_R, 90 + i * 360 / ANEL_PARAF_N)
        p = p.cut(cq.Workplane("XY").workplane(offset=Z_CUBO_TOPO - (G.M3_INSERTO_PROF + 0.5))
                  .center(x, y).circle(G.M3_INSERTO_FURO / 2).extrude(G.M3_INSERTO_PROF + 0.6))
    return p


# ============================================================
# 08B — flange superior (gira com o tronco)
# ============================================================
def flange_superior():
    p = (cq.Workplane("XY").workplane(offset=Z_FS_BASE)
         .circle(FS_DE / 2).extrude(FS_ALT))
    aba = (cq.Workplane("XY").workplane(offset=Z_FS_BASE)
           .circle(FS_ABA_D / 2).extrude(FS_ABA_ALT))
    p = p.union(aba)
    p = p.faces(">Z").edges().fillet(1.0)
    # furo que gira no cubo
    p = p.cut(cq.Workplane("XY").workplane(offset=Z_FS_BASE - 1)
              .circle(CUBO_DE / 2 + FOLGA_GIRO).extrude(FS_ALT + 2))
    # alojamento do anel de retenção + arruela de silicone
    p = p.cut(cq.Workplane("XY").workplane(offset=Z_REBAIXO)
              .circle(FS_REBAIXO_D / 2).extrude(FS_REBAIXO_PROF + 1))
    # insertos M4 do tronco (de cima)
    for x, y in G.IF_CINTURA_M4:
        p = p.cut(cq.Workplane("XY").workplane(offset=Z_FS_TOPO - FS_INSERTO_PROF)
                  .center(x, y).circle(G.M4_INSERTO_FURO / 2).extrude(FS_INSERTO_PROF + 1))
    # rasgo em arco do batente (por baixo). No referencial da 08B, o pino fixo
    # percorre PINO_ANG - giro, com giro em [-GIRO, +GIRO].
    larg = PINO_D + 2 * RASGO_FOLGA
    a0, a1 = PINO_ANG - GIRO, PINO_ANG + GIRO
    rasgo = (cq.Workplane("XY").workplane(offset=Z_FS_BASE - 0.01)
             .center(*_pol(PINO_R, a0)).circle(larg / 2).extrude(RASGO_PROF))
    rasgo = rasgo.union(cq.Workplane("XY").workplane(offset=Z_FS_BASE - 0.01)
                        .center(*_pol(PINO_R, a1)).circle(larg / 2).extrude(RASGO_PROF))
    anel_ext = cq.Workplane("XY").workplane(offset=Z_FS_BASE - 0.01).circle(PINO_R + larg / 2).extrude(RASGO_PROF)
    anel_int = cq.Workplane("XY").workplane(offset=Z_FS_BASE - 0.01).circle(PINO_R - larg / 2).extrude(RASGO_PROF)
    setor = (cq.Workplane("XY").workplane(offset=Z_FS_BASE - 0.02)
             .polyline([(0, 0), _pol(80, a0), _pol(80, (a0 + a1) / 2), _pol(80, a1)]).close()
             .extrude(RASGO_PROF + 0.02))
    rasgo = rasgo.union(anel_ext.cut(anel_int).intersect(setor))
    p = p.cut(rasgo)
    # furo radial da trava: inserto M4 na ponta externa + guia da sapata até o cubo
    ax, ay = _pol(1, TRAVA_ANG)
    plano = cq.Plane(origin=(0, 0, Z_TRAVA), xDir=(-ay, ax, 0), normal=(ax, ay, 0))
    guia = cq.Workplane(plano).circle(SAPATA_D / 2 + 0.15).extrude(FS_DE / 2 + 1)
    inserto = (cq.Workplane(plano).workplane(offset=FS_DE / 2 - G.M4_INSERTO_PROF)
               .circle(G.M4_INSERTO_FURO / 2).extrude(G.M4_INSERTO_PROF + 2))
    p = p.cut(guia).cut(inserto)
    return p


# ============================================================
# 08C — anel de retenção / ajuste
# ============================================================
def anel_retencao():
    p = (cq.Workplane("XY").workplane(offset=Z_ANEL_BASE)
         .circle(ANEL_DE / 2).circle(ANEL_DI / 2).extrude(ANEL_ESP))
    for i in range(ANEL_PARAF_N):
        x, y = _pol(ANEL_PARAF_R, 90 + i * 360 / ANEL_PARAF_N)
        p = p.cut(cq.Workplane("XY").workplane(offset=Z_ANEL_BASE - 1)
                  .center(x, y).circle(G.M3_PASSANTE / 2).extrude(ANEL_ESP + 2))
        p = p.cut(cq.Workplane("XY").workplane(offset=Z_ANEL_BASE + ANEL_ESP - 1.8)
                  .center(x, y).circle(6.0 / 2).extrude(2))      # rebaixo da cabeça M3 (Ø5,5)
    return p


# ============================================================
# 08D — colar decorativo
# ============================================================
def colar():
    z0 = COLAR_FOLGA_BASE
    z_degrau = Z_FS_BASE + FS_ABA_ALT
    z1 = H_TOTAL - COLAR_FOLGA_TOPO
    p = cq.Workplane("XY").workplane(offset=z0).circle(COLAR_DE / 2).extrude(z1 - z0)
    p = p.edges().fillet(1.5)
    p = p.cut(cq.Workplane("XY").workplane(offset=z0 - 1)
              .circle(FS_ABA_D / 2 + FOLGA_COLAR).extrude(z_degrau - z0 + 1))
    p = p.cut(cq.Workplane("XY").workplane(offset=z_degrau)
              .circle(FS_DE / 2 + FOLGA_COLAR).extrude(z1 - z_degrau + 1))
    # janela da trava
    ax, ay = _pol(1, TRAVA_ANG)
    plano = cq.Plane(origin=(0, 0, Z_TRAVA), xDir=(-ay, ax, 0), normal=(ax, ay, 0))
    p = p.cut(cq.Workplane(plano).rect(JANELA_L, JANELA_A).extrude(COLAR_DE))
    # marca da posição central (frente)
    mx, my = _pol(COLAR_DE / 2, PINO_ANG)
    p = p.cut(cq.Workplane("XY").workplane(offset=z0 - 0.01).center(mx, my)
              .polygon(3, MARCA_CENTRO * 3).extrude(4))
    return p


# ============================================================
# 08E — sapata da trava
# ============================================================
def sapata():
    ax, ay = _pol(1, TRAVA_ANG)
    plano = cq.Plane(origin=(0, 0, Z_TRAVA), xDir=(-ay, ax, 0), normal=(ax, ay, 0))
    return cq.Workplane(plano).workplane(offset=CUBO_DE / 2 + 0.05).circle(SAPATA_D / 2).extrude(SAPATA_COMP)


PECAS = {
    "08A_flange_inferior": flange_inferior,
    "08B_flange_superior": flange_superior,
    "08C_anel_retencao": anel_retencao,
    "08D_colar": colar,
    "08E_sapata_trava": sapata,
}
GIRAM = {"08B_flange_superior", "08C_anel_retencao", "08D_colar", "08E_sapata_trava"}
# 08C gira? Não: o anel é fixo no cubo. Corrigido abaixo.
GIRAM.discard("08C_anel_retencao")

# Fixadores e comprados (lista de materiais)
BOM = [
    ("Parafuso M4 × 12 cabeça cilíndrica (08A -> Peça 02)", 4),
    ("Inserto térmico M4 na Peça 02 (IF-CINTURA)", 4),
    ("Parafuso M4 × 12 (tronco -> 08B; piso do tronco 5 mm + 7 no inserto)", 4),
    ("Inserto térmico M4 na 08B", 4),
    ("Parafuso M3 × 10 cabeça cilíndrica (08C -> cubo)", 3),
    ("Inserto térmico M3 no topo do cubo (08A)", 3),
    ("Parafuso M4 × 10 de trava (manípulo ou Allen), radial", 1),
    ("Inserto térmico M4 radial na 08B", 1),
    (f"Arruela PTFE Ø{PTFE_DI:g}×Ø{PTFE_DE:g}×{PTFE_ESP:g} (apoio, baixo atrito)", 1),
    (f"Arruela de silicone Ø{SIL_DI:g}×Ø{SIL_DE:g}×{SIL_ESP:g} (fricção ajustável)", 1),
]

if __name__ == "__main__":
    out = RAIZ / "exports" / "p08_cintura"
    out.mkdir(parents=True, exist_ok=True)
    for nome, fn in PECAS.items():
        s = fn()
        cq.exporters.export(s, str(out / f"{nome}.stl"), tolerance=0.01, angularTolerance=0.1)
        cq.exporters.export(s, str(out / f"{nome}.step"))
        bb = s.val().BoundingBox()
        print(f"{nome:24s} {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:5.1f}  "
              f"valido={s.val().isValid()} solidos={len(s.solids().vals())} vol={s.val().Volume()/1000:.1f} cm3")
