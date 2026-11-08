"""Peças 09 (ombro ESQUERDO) e 10 (ombro DIREITO) — articulação manual do ombro (V1).

Um só código: construir(lado, giro_min, giro_max). O direito é o esquerdo ESPELHADO
(peças impressas espelhadas) com curso próprio. Componentes comprados são os mesmos.

Componentes (PETG):
  09A flange do tronco : 4×M3 no IF-OMBRO. Cubo central (mancal do braço), pino do batente,
                         alojamento da porca M6 do eixo (lado do tronco).
  09B rotor do braço   : gira no cubo. Lingueta IF-BRAÇO (o braço encaixa e parafusa).
                         Rasgo em arco = batentes. Furos de indexação a cada 15° (trava positiva).
  09C tampa de pressão : chaveada no cubo (não gira). Comprime a arruela de fricção.
                         Inserto M4 do manípulo.
  09D manípulo         : cabeça de parafuso M4 embutida; a ponta é um PINO que entra num dos
                         furos de indexação da 09B (posição travada) ou só encosta (fricção).
Comprados: parafuso M6 (eixo) + porca M6 autotravante, arruela PTFE, arruela de borracha/
cortiça, parafuso M4 do manípulo, parafusos M3.

Retenção axial = eixo M6 + porca autotravante (aperto fixo, só limita a compressão da arruela
de fricção; a tampa encosta no cubo). O manípulo NÃO segura o braço no eixo.

Referencial LOCAL (o código desenha aqui): Z = eixo do ombro para FORA do tronco,
X = para TRÁS do robô, Y = para CIMA. Braço em 0° aponta para baixo (−Y local).
Giro positivo = braço para a FRENTE. LOCAL -> robô em posicionar().
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
# Curso por lado (0 = braço para baixo, + = para a frente/cima). O braço fica por fora da
# lateral do tronco, então o giro no plano lateral não encosta no tronco: o limite vem do
# rasgo do batente (máx. ~200° com o pino) e do uso.
CURSO = {"esquerdo": (0.0, 60.0),     # 07/11: < 0° o L e a bandeja batem na base/tronco
         "direito": (-30.0, 120.0)}   # cumprimento: levanta até acima da horizontal
GIRO_MIN, GIRO_MAX = CURSO["esquerdo"]
PASSO_INDEX = 15.0                     # posições de trava positiva
FOLGA_GIRO = 0.2

# 09A
A_D = G.IF_OMBRO_FACE_D - 4            # 52
A_ESP = 6.0
CUBO_D = 20.0
EIXO_PASSANTE = 6.4                    # M6
PORCA_M6_S = 10.0                      # entre faces (CONFERIR a porca comprada)
PORCA_M6_H = 8.0                       # autotravante
M3_REBAIXO_D, M3_REBAIXO_P = 6.0, 3.2

# arruelas
PTFE_DI, PTFE_DE, PTFE_ESP = 20.5, 40.0, 1.0
FRIC_DI, FRIC_DE, FRIC_ESP = 20.5, 36.0, 2.0      # borracha/cortiça
FRIC_COMPRESSAO = 0.6

# 09B
B_D = A_D
B_ESP = G.IF_BRACO_LING_ESP            # 12, igual à lingueta
LING_ANG = 270.0                       # lingueta para baixo em 0°

# batente (pino na 09A, rasgo na face interna da 09B)
PINO_R, PINO_ANG, PINO_D, PINO_ALT = 22.5, 90.0, 5.0, 2.5
RASGO_FOLGA, RASGO_PROF = 0.3, 3.0

# indexação (furos na face externa da 09B, pino do manípulo)
INDEX_R = 22.0
INDEX_ANG = 30.0                       # onde fica o manípulo (atrás/em cima, longe da lingueta)
INDEX_D, INDEX_PROF = 4.6, 2.5         # furo p/ ponta do manípulo Ø4 (sapata)

# 09C
C_D = 50.0
C_ESP = 6.0
CHAVE_PLANO = 8.0                      # cubo com 2 planos: distância entre planos = CUBO_D - 2*... (meia-lua)

# 09D manípulo
MANIP_D, MANIP_H = 22.0, 12.0
M4_CABECA_S = 7.0                      # sextavado da cabeça? Allen cilíndrica Ø7: aloja cilindro

# alturas locais (z)
Z_A = A_ESP
Z_B0 = Z_A + PTFE_ESP
Z_B1 = Z_B0 + B_ESP
Z_C0 = Z_B1 + FRIC_ESP
Z_CUBO_FIM = Z_C0 - FRIC_COMPRESSAO
Z_C1 = Z_C0 + C_ESP


def _pol(r, a):
    a = math.radians(a)
    return (r * math.cos(a), r * math.sin(a))


def _cil(r, z0, h, xy=(0, 0)):
    return cq.Workplane("XY").workplane(offset=z0).center(*xy).circle(r).extrude(h)


def _arco(r, larg, a0, a1, z0, h):
    p = _cil(r + larg / 2, z0, h).cut(_cil(r - larg / 2, z0 - 1, h + 2))
    meio = (a0 + a1) / 2
    setor = (cq.Workplane("XY").workplane(offset=z0 - 0.5)
             .polyline([(0, 0), _pol(100, a0), _pol(100, meio), _pol(100, a1)]).close().extrude(h + 1))
    p = p.intersect(setor)
    for a in (a0, a1):
        p = p.union(_cil(larg / 2, z0, h, _pol(r, a)))
    return p


# ============================================================
def flange_tronco():  # 09A
    p = _cil(A_D / 2, 0, A_ESP).faces(">Z").edges().fillet(1.0)
    cubo = _cil(CUBO_D / 2, A_ESP, Z_CUBO_FIM - A_ESP)
    # chaveta: dois planos no último trecho do cubo (a tampa 09C não gira)
    corte_chave = (cq.Workplane("XY").workplane(offset=Z_B1)
                   .rect(CUBO_D + 2, CUBO_D + 2).extrude(Z_CUBO_FIM - Z_B1 + 1)
                   .cut(cq.Workplane("XY").workplane(offset=Z_B1 - 1).rect(CUBO_D + 4, CHAVE_PLANO * 2).extrude(20)))
    cubo = cubo.cut(corte_chave)
    p = p.union(cubo).union(_cil(PINO_D / 2, A_ESP, PINO_ALT, _pol(PINO_R, PINO_ANG)))
    p = p.cut(_cil(EIXO_PASSANTE / 2, -1, Z_CUBO_FIM + 2))
    # porca M6 sextavada presa por dentro (lado do tronco)
    p = p.cut(cq.Workplane("XY").workplane(offset=-0.01).polygon(6, PORCA_M6_S / math.cos(math.pi / 6) + 0.3)
              .extrude(PORCA_M6_H * 0.6))
    for k in range(4):
        x, y = _pol(G.IF_OMBRO_M3_R, 45 + 90 * k)
        p = p.cut(_cil(G.M3_PASSANTE / 2, -1, A_ESP + 2, (x, y)))
        p = p.cut(_cil(M3_REBAIXO_D / 2, A_ESP - M3_REBAIXO_P, M3_REBAIXO_P + 1, (x, y)))
    return p


def rotor_braco(giro_min=GIRO_MIN, giro_max=GIRO_MAX):  # 09B / 10B
    p = _cil(B_D / 2, Z_B0, B_ESP)
    a = math.radians(LING_ANG)
    # lingueta radial (IF-BRAÇO)
    w = G.IF_BRACO_LING_LARG
    r0, r1 = G.IF_BRACO_LING_R0 - 4, G.IF_BRACO_LING_R1
    ling = (cq.Workplane("XY").workplane(offset=Z_B0)
            .transformed(rotate=(0, 0, LING_ANG - 90))
            .center(0, -(r0 + r1) / 2 * -1 if False else (r0 + r1) / 2)
            .rect(w, r1 - r0).extrude(B_ESP))
    ling = ling.rotate((0, 0, 0), (0, 0, 1), 0)
    p = p.union(ling).edges("|Z").fillet(1.0)
    p = p.cut(_cil(CUBO_D / 2 + FOLGA_GIRO, Z_B0 - 1, B_ESP + 2))
    # batente: rasgo em arco na face interna
    larg = PINO_D + 2 * RASGO_FOLGA
    # 07/11: sinal corrigido (era PINO_ANG − giro). Com girar() o rotor gira −θ no referencial
    # local; o ponto do rasgo que fica sob o pino fixo é PINO_ANG + θ.
    p = p.cut(_arco(PINO_R, larg, PINO_ANG + giro_min, PINO_ANG + giro_max, Z_B0 - 0.01, RASGO_PROF))
    # indexação: furos na face externa. Com o braço em θ, o pino fixo (INDEX_ANG) cai no
    # furo que, no referencial da 09B, fica em INDEX_ANG − θ.
    n = int(round((giro_max - giro_min) / PASSO_INDEX)) + 1
    for i in range(n):
        th = giro_min + i * PASSO_INDEX
        p = p.cut(_cil(INDEX_D / 2, Z_B1 - INDEX_PROF, INDEX_PROF + 0.1, _pol(INDEX_R, INDEX_ANG + th)))   # sinal corrigido 07/11
    # insertos M3 do IF-BRAÇO na face de fora da lingueta
    for r in G.IF_BRACO_M3_R:
        p = p.cut(_cil(G.M3_INSERTO_FURO / 2, Z_B1 - G.M3_INSERTO_PROF - 0.5, G.M3_INSERTO_PROF + 1, _pol(r, LING_ANG)))
    return p


def tampa_pressao():  # 09C
    p = _cil(C_D / 2, Z_C0, C_ESP).faces(">Z").edges().fillet(1.0)
    # furo chaveado (encaixa nos planos do cubo) + passagem do eixo
    furo = (cq.Workplane("XY").workplane(offset=Z_C0 - 1).circle(CUBO_D / 2 + FOLGA_GIRO).extrude(C_ESP + 2)
            .intersect(cq.Workplane("XY").workplane(offset=Z_C0 - 1).rect(CUBO_D + 4, CHAVE_PLANO * 2 + 2 * FOLGA_GIRO).extrude(C_ESP + 2)))
    # o cubo termina em Z_CUBO_FIM < Z_C0: o furo chaveado só tem 1 mm de profundidade útil,
    # então a chave real é o rebaixo: a tampa encaixa SOBRE o fim do cubo.
    p = p.cut(furo.translate((0, 0, 0)).intersect(_cil(50, Z_C0 - 1, 1 + FRIC_COMPRESSAO + 1.0)))
    p = p.cut(_cil(EIXO_PASSANTE / 2, Z_C0 - 1, C_ESP + 2))
    p = p.cut(_cil(11.0 / 2, Z_C1 - 4.5, 5))            # rebaixo da cabeça M6 (Ø10)
    # inserto M4 do manípulo
    p = p.cut(_cil(G.M4_INSERTO_FURO / 2, Z_C0 - 1, C_ESP + 2, _pol(INDEX_R, INDEX_ANG)))
    return p


def manipulo():  # 09D
    z0 = Z_C1 + 3
    corpo = cq.Workplane("XY").workplane(offset=z0).center(*_pol(INDEX_R, INDEX_ANG)).polygon(6, MANIP_D).extrude(MANIP_H)
    corpo = corpo.edges("|Z").fillet(3.0).faces(">Z").edges().fillet(2.0)
    corpo = corpo.cut(_cil(G.M4_PASSANTE / 2, z0 - 1, MANIP_H + 2, _pol(INDEX_R, INDEX_ANG)))
    corpo = corpo.cut(_cil(7.4 / 2, z0 + MANIP_H - 4.5, 5, _pol(INDEX_R, INDEX_ANG)))   # cabeça M4 Ø7
    return corpo


GIRAM = {"B_rotor_braco"}
NUMERO = {"esquerdo": "09", "direito": "10"}


def construir(lado="esquerdo"):
    """Peças no referencial LOCAL do lado pedido. Direito = esquerdo espelhado em X local."""
    gmin, gmax = CURSO[lado]
    pecas = {"A_flange_tronco": flange_tronco(), "B_rotor_braco": rotor_braco(gmin, gmax),
             "C_tampa_pressao": tampa_pressao(), "D_manipulo": manipulo()}
    if lado == "direito":
        pecas = {k: v.mirror("YZ") for k, v in pecas.items()}
    return pecas


# compatibilidade com o validador (lado esquerdo)
PECAS = {f"09{k}": (lambda k=k: construir("esquerdo")[k]) for k in
         ("A_flange_tronco", "B_rotor_braco", "C_tampa_pressao", "D_manipulo")}

BOM = [
    ("Parafuso M6 × 30 cabeça cilíndrica (eixo)", 1),
    ("Porca M6 autotravante (presa na 09A)", 1),
    ("Parafuso M3 × 10 (09A -> tronco)", 4),
    ("Inserto térmico M3 no tronco (IF-OMBRO)", 4),
    ("Parafuso M3 × 10 (braço -> lingueta, de fora; cabeça embutida no soquete)", 2),
    ("Inserto térmico M3 na lingueta (09B)", 2),
    ("Parafuso M4 × 25 (manípulo; ponta entra no furo de indexação)", 1),
    ("Inserto térmico M4 na tampa 09C", 1),
    (f"Arruela PTFE Ø{PTFE_DI:g}×Ø{PTFE_DE:g}×{PTFE_ESP:g}", 1),
    (f"Arruela de borracha/cortiça Ø{FRIC_DI:g}×Ø{FRIC_DE:g}×{FRIC_ESP:g} (fricção)", 1),
]


def girar(wp, ang, lado="esquerdo"):
    """Gira a peça móvel do ombro para o ângulo físico do braço (0 = para baixo, + = para a
    FRENTE/cima), no referencial LOCAL do lado. ÚNICA convenção do projeto: todo validador
    usa esta função. Esquerdo (X local = trás): −ang. Direito (X local = frente): +ang."""
    return wp.rotate((0, 0, 0), (0, 0, 1), -ang if lado == "esquerdo" else ang)


def posicionar(wp, lado="esquerdo"):
    """LOCAL -> robô. Esquerdo: eixo para −X, X local = trás. Direito (já espelhado):
    eixo para +X, X local = frente. Nos dois, Y local = cima."""
    if lado == "esquerdo":
        plano = cq.Plane(origin=(-G.IF_OMBRO_X, G.IF_OMBRO_Y, G.IF_OMBRO_Z), xDir=(0, -1, 0), normal=(-1, 0, 0))
    else:
        plano = cq.Plane(origin=(G.IF_OMBRO_X, G.IF_OMBRO_Y, G.IF_OMBRO_Z), xDir=(0, 1, 0), normal=(1, 0, 0))
    shp = wp.val() if hasattr(wp, "val") else wp
    return cq.Workplane("XY").add(shp.moved(cq.Location(plano)))


if __name__ == "__main__":
  for lado in ("esquerdo", "direito"):
    out = RAIZ / "exports" / f"p{NUMERO[lado]}_ombro_{lado}"
    out.mkdir(parents=True, exist_ok=True)
    for k, s in construir(lado).items():
        nome = NUMERO[lado] + k
        cq.exporters.export(s, str(out / f"{nome}.stl"), tolerance=0.01, angularTolerance=0.1)
        cq.exporters.export(s, str(out / f"{nome}.step"))
        bb = s.val().BoundingBox()
        print(f"{nome:20s} {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:5.1f}  valido={s.val().isValid()} "
              f"solidos={len(s.solids().vals())} vol={s.val().Volume()/1000:.1f} cm3")
