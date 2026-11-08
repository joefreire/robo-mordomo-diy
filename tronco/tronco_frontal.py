"""Peça 04 — Tronco frontal = CAPA (creme), sem carga. Profundidade 105 − 75 = 30.

Peças geradas:
  04A tronco frontal      : casca de y = +22,5 a +52,5 (aberta atrás).
  04B moldura da tela     : verde-petróleo, removível pela frente (4×M3 de frente).
  04C bandeja da tela     : placa genérica atrás do envelope da tela; furação da tela em RASGOS
                            PLACEHOLDER (sem tela comprada). Parafusa por dentro nas colunas.
  04D tampa de manutenção : abertura de baixo (4×M3 de frente).
  04E painel decorativo M06 (V1): tampa falsa da tela; usa os 4 furos da moldura.

Frente: região central PLANA (y = +52,5) até x = ±(w − 17,6); cantos da planta em gota (45°).
  Isso permite imprimir DE FRENTE NA MESA, sem suporte: paredes, colunas e bosses sobem da
  face; os rebaixos da moldura e da tampa ficam na mesa e usam ANEL DE SACRIFÍCIO (0,8 mm) na
  borda da abertura -> ponte de ≤ 10,3 mm. Cortar os anéis com estilete depois de imprimir.
Topo: alívio de 0,3 mm sob a flange do pescoço (a carga vai só para a traseira). Piso: alívio
  de 0,3 mm sobre a 08B pelo mesmo motivo.
União: 6 colunas Ø11 com inserto M3 (o parafuso vem por trás, pela traseira) + 2 pinos Ø4.
Gravata: 2 insertos M3 de frente logo abaixo do topo (a gravata não é modelada aqui).
"""
import sys
from functools import reduce
from pathlib import Path

import cadquery as cq

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from parameters import globais as G  # noqa: E402
from parameters import tronco as T  # noqa: E402
from tronco import forma as F  # noqa: E402
from tronco.tronco_traseiro import _tubo_uniao  # noqa: E402

Y_DIV, Y_FRENTE = G.TRONCO_Y_DIVISAO, G.TRONCO_PROF / 2       # 22,5 e 52,5
Y_INT = Y_FRENTE - F.PAREDE                                    # 49,5
FO = G.FOLGA_ENCAIXE
ZT = G.IF_TELA_PEITO_Z

# rebaixos (contorno = peça + folga)
TELA_AB_W, TELA_AB_H = T.TELA_ABERTURA
REB_TELA = (T.MOLDURA_EXT[0] + 2 * FO, T.MOLDURA_EXT[1] + 2 * FO, T.MOLDURA_R + FO)
Y_REB_TELA = Y_FRENTE - T.MOLDURA_REBAIXO                      # 50,5 = face do vidro
TAMPA_EXT = (T.TAMPA_ABERTURA[0] + 2 * T.TAMPA_FAIXA, T.TAMPA_ABERTURA[1] + 2 * T.TAMPA_FAIXA)
REB_TAMPA = (TAMPA_EXT[0] + 2 * FO, TAMPA_EXT[1] + 2 * FO, T.TAMPA_R + T.TAMPA_FAIXA + FO)
Y_REB_TAMPA = Y_FRENTE - T.TAMPA_REBAIXO                       # 50
ESP_ANEL = 3.0                                                 # engrossamento por dentro em volta das aberturas


def _uniao(lst):
    return reduce(lambda a, b: a.union(b), lst)


# ============================================================
def frontal(sacrificio=True):
    ext = F.corpo_externo()
    p = F.casca().intersect(F.lado_y(Y_DIV, Y_FRENTE + 1))

    internos = []
    for x, z in T.UNIAO_M3:                                         # colunas da união
        internos.append(_tubo_uniao(x, z, Y_DIV, Y_FRENTE))
    for x, z in T.MOLDURA_M3:                                       # colunas moldura/bandeja
        internos.append(F.cil_y(x, z, 9.0, T.TELA_Y_FUNDO, Y_FRENTE))
    internos.append(F.anel_y(0, ZT, TELA_AB_W, TELA_AB_H, T.TELA_ABERTURA_R,
                             T.MOLDURA_FAIXA + FO + ESP_ANEL, Y_REB_TELA - 4.0, Y_FRENTE))
    internos.append(F.anel_y(0, T.TAMPA_Z, *T.TAMPA_ABERTURA, T.TAMPA_R,
                             T.TAMPA_FAIXA + FO + ESP_ANEL, Y_REB_TAMPA - 3.0, Y_FRENTE))
    for x, z in T.TAMPA_M3:
        internos.append(F.cil_y(x, z, 8.0, Y_REB_TAMPA - F.INS_PROF - 1.5, Y_FRENTE))
    for x, z in T.GRAVATA_M3:
        internos.append(F.cil_y(x, z, 8.0, Y_FRENTE - F.INS_PROF - 2.0, Y_FRENTE))
    p = p.union(_uniao(internos).intersect(ext).intersect(F.lado_y(Y_DIV, Y_FRENTE + 1)))

    cortes = [
        F.ret_y(0, ZT, TELA_AB_W, TELA_AB_H, Y_DIV + 5, Y_FRENTE + 1, T.TELA_ABERTURA_R),
        F.ret_y(0, ZT, REB_TELA[0], REB_TELA[1], Y_REB_TELA, Y_FRENTE + 1, REB_TELA[2]),
        F.ret_y(0, T.TAMPA_Z, *T.TAMPA_ABERTURA, Y_DIV + 5, Y_FRENTE + 1, T.TAMPA_R),
        F.ret_y(0, T.TAMPA_Z, REB_TAMPA[0], REB_TAMPA[1], Y_REB_TAMPA, Y_FRENTE + 1, REB_TAMPA[2]),
        # piso: entalhe da abertura Ø56 e alívio de 0,3 sobre a 08B
        F.cil_z(0, 0, G.IF_CINTURA_ABERTURA_TRONCO_D, G.Z_PISO_TRONCO - 1, G.Z_PISO_TRONCO + T.PISO_ESP + 1),
        F.cil_z(0, 0, 2 * 48.0, G.Z_PISO_TRONCO - 1, G.Z_PISO_TRONCO + 0.3),
        # topo: alívio de 0,3 sob a flange do pescoço
        F.cil_z(0, 0, G.IF_PESCOCO_FACE_D + 1.0, G.Z_TOPO_TRONCO - 0.3, G.Z_TOPO_TRONCO + 1),
    ]
    for x, z in T.MOLDURA_M3:
        cortes.append(F.cil_y(x, z, F.INS_FURO, Y_REB_TELA - F.INS_PROF, Y_REB_TELA + 0.5))   # moldura (de frente)
        cortes.append(F.cil_y(x, z, F.INS_FURO, T.TELA_Y_FUNDO - 0.5, T.TELA_Y_FUNDO + F.INS_PROF))  # bandeja (por dentro)
    for x, z in T.TAMPA_M3:
        cortes.append(F.cil_y(x, z, F.INS_FURO, Y_REB_TAMPA - F.INS_PROF, Y_REB_TAMPA + 0.5))
    for x, z in T.GRAVATA_M3:
        cortes.append(F.cil_y(x, z, F.INS_FURO, Y_FRENTE - F.INS_PROF, Y_FRENTE + 1))
    for x, z in T.UNIAO_M3:
        cortes.append(F.cil_y(x, z, F.INS_FURO, Y_DIV - 1, Y_DIV + F.INS_PROF))
    p = p.cut(_uniao(cortes))

    # pinos de alinhamento (entram nos furos da traseira)
    for x, z in T.UNIAO_PINOS:
        pino = F.cil_y(x, z, T.PINO_D, Y_DIV - T.PINO_L, Y_DIV + 0.5)
        p = p.union(pino.faces("<Y").chamfer(0.6))
    if sacrificio:
        p = p.union(F.anel_y(0, ZT, TELA_AB_W, TELA_AB_H, T.TELA_ABERTURA_R, T.SACRIFICIO_ESP,
                             Y_REB_TELA - 0.01, Y_FRENTE))
        p = p.union(F.anel_y(0, T.TAMPA_Z, *T.TAMPA_ABERTURA, T.TAMPA_R, T.SACRIFICIO_ESP,
                             Y_REB_TAMPA - 0.01, Y_FRENTE))
    return p


# ============================================================
def _placa_moldura():
    w, h = T.MOLDURA_EXT
    p = F.ret_y(0, ZT, w, h, Y_REB_TELA, Y_REB_TELA + T.MOLDURA_ESP, T.MOLDURA_R)
    p = p.faces(">Y").edges().fillet(1.5)
    for x, z in T.MOLDURA_M3:
        p = p.cut(F.cil_y(x, z, G.M3_PASSANTE, Y_REB_TELA - 1, Y_REB_TELA + T.MOLDURA_ESP + 1))
    return p


def moldura():  # 04B
    jw, jh = T.MOLDURA_JANELA
    p = _placa_moldura().cut(F.ret_y(0, ZT, jw, jh, Y_REB_TELA - 1, Y_FRENTE + 5, 3.0))
    # chanfro de 45° na janela, do lado de fora (vista limpa da tela)
    return p.cut(cq.Workplane(F.plano_y(Y_REB_TELA + T.MOLDURA_ESP + 0.01)).center(0, ZT)
                 .rect(jw + 3, jh + 3).workplane(offset=1.5).rect(jw, jh).loft())


def painel_m06():  # 04E — tampa falsa da tela (V1)
    p = _placa_moldura()
    jw, jh = T.MOLDURA_JANELA
    y1 = Y_REB_TELA + T.MOLDURA_ESP
    p = p.cut(F.ret_y(0, ZT, jw + 4, jh + 4, y1 - 0.8, y1 + 1, 4.0))           # "tela" rebaixada 0,8
    for k in (-1, 0, 1):                                                       # 3 "botões" em relevo
        p = p.union(F.cil_y(k * 22.0, ZT - jh / 2 + 10, 9.0, y1 - 0.81, y1 - 0.2))
    return p


def bandeja():  # 04C
    bw, bh = T.BANDEJA_EXT
    y0, y1 = Y_DIV, T.TELA_Y_FUNDO
    p = F.ret_y(0, ZT, bw, bh, y0, y1, 5.0)
    p = p.cut(F.ret_y(0, ZT, *T.BANDEJA_JANELA, y0 - 1, y1 + 1, 4.0))
    for x, z in T.MOLDURA_M3:
        p = p.cut(F.cil_y(x, z, G.M3_PASSANTE, y0 - 1, y1 + 1))
    s = T.BANDEJA_TELA_RASGO
    for dx, dz in T.BANDEJA_TELA_FUROS:
        p = p.cut(F.ret_y(dx, ZT + dz, s + G.M3_PASSANTE, G.M3_PASSANTE, y0 - 1, y1 + 1, G.M3_PASSANTE / 2 - 0.01))
    return p


def tampa():  # 04D
    w, h = TAMPA_EXT
    p = F.ret_y(0, T.TAMPA_Z, w, h, Y_REB_TAMPA, Y_FRENTE, T.TAMPA_R + T.TAMPA_FAIXA)
    for x, z in T.TAMPA_M3:
        p = p.cut(F.cil_y(x, z, G.M3_PASSANTE, Y_REB_TAMPA - 1, Y_FRENTE + 1))
    return p


PECAS = {"04A_tronco_frontal": frontal, "04B_moldura_tela": moldura, "04C_bandeja_tela": bandeja,
         "04D_tampa_manutencao": tampa, "04E_painel_decorativo_M06": painel_m06}

BOM = [
    ("Inserto térmico M3 (6 união + 4 moldura + 4 bandeja + 4 tampa + 2 gravata)", 20),
    ("Parafuso M3 × 8 cabeça abaulada ISO 7380 (moldura 04B ou painel M06, de frente)", 4),
    ("Parafuso M3 × 6 cabeça cilíndrica (bandeja 04C, por dentro)", 4),
    ("Parafuso M3 × 6 cabeça abaulada ISO 7380 (tampa 04D, de frente)", 4),
    ("Parafuso M3 × 8 (gravata, de frente; conferir com a gravata)", 2),
]

if __name__ == "__main__":
    out = RAIZ / "exports" / "p03_p04_tronco"
    out.mkdir(parents=True, exist_ok=True)
    for nome, fn in PECAS.items():
        s = fn()
        cq.exporters.export(s, str(out / f"{nome}.stl"), tolerance=0.02, angularTolerance=0.15)
        cq.exporters.export(s, str(out / f"{nome}.step"))
        bb = s.val().BoundingBox()
        print(f"{nome:28s} {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:5.1f}  valido={s.val().isValid()} "
              f"solidos={len(s.solids().vals())} vol={s.val().Volume()/1000:.1f} cm3")
