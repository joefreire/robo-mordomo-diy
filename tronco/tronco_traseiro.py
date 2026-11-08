"""Peça 03 — Tronco traseiro = ESQUELETO (creme). Toda a carga passa por ela.

Peças geradas:
  03A tronco traseiro : casca de y = −52,5 a +22,5 (frente aberta no plano de divisão).
  03B painel traseiro : tampa de manutenção verde-petróleo (4×M3), atrás da bandeja do ESP32.

Interfaces (números em parameters/globais.py; os novos em parameters/tronco.py):
  IF-CINTURA (piso, z = 94): 4 furos passantes M4 (o parafuso desce por dentro e prende nos
      insertos da 08B), abertura Ø56, piso de 5 mm com nervuras ao longo de Y, apoio plano.
  IF-OMBRO (laterais, x = ±92,5): face plana Ø56 ⟂ X sobre uma placa de 6 mm; ressalto em gota
      cobre os cantos curvos; 4 bosses com inserto M3 (r 20, 45°…); furo Ø16 (em gota);
      envelope interno 50 × 60 × 45 do servo da V2 sem nervura nenhuma (centro em
      y = −9, z = 233: ver parameters/tronco.OMBRO_ENVELOPE_CENTRO).
  IF-PESCOÇO (topo, z = 284): prateleira plana Ø66, 4 insertos M3 em (±22, ±15) sobre duas
      nervuras ao longo de Y, passa-cabos Ø16 (em gota).
  IF-ELETRÔNICA: 2 trilhos verticais (x = ±46) com insertos M3 a cada 10 mm; zona livre da
      bandeja removível do ESP32 entre eles; superfície + grade do alto-falante; painel
      traseiro com rebaixo de 1,5 mm SÓ na moldura (a faixa engrossa 1,5 por dentro).
  União com a frontal: 6×M3 POR TRÁS (tubos Ø11 com furo Ø6,5 até o assento em y = +12;
      insertos nas colunas da 04) + 2 furos para os pinos Ø4 da 04.

Impressão: DE COSTAS NA MESA (y = −52,5 para baixo). Paredes, trilhos, tubos, nervuras e bosses
  sobem da mesa; cantos da planta em gota (45°); furos horizontais grandes em gota. A faixa do
  rebaixo do painel fica 1,5 mm acima da mesa: o ANEL DE SACRIFÍCIO (0,8 mm) na borda da
  abertura transforma o balanço numa ponte de 8 mm. Cortar o anel com estilete depois.
  Precisa: 185 × 190 na mesa (A1: 256 × 256), 75 de altura. 4 paredes, 20–25 % giroide.
"""
import math
import sys
from functools import reduce
from pathlib import Path

import cadquery as cq

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from parameters import globais as G  # noqa: E402
from parameters import tronco as T  # noqa: E402
from tronco import forma as F  # noqa: E402

Y_FUNDO, Y_DIV = G.TRONCO_Y_FUNDO, G.TRONCO_Y_DIVISAO
Y_INT = Y_FUNDO + F.PAREDE                     # face interna das costas (−49,5)

# envelope interno do servo do ombro (V2), lado +X; o −X é espelhado
ENV_Y, ENV_Z, ENV_X = G.IF_OMBRO_ENVELOPE_INTERNO
X_PLACA = G.IF_OMBRO_X - T.OMBRO_PLACA_ESP      # 86,5: face interna da placa
X_BOSS = X_PLACA - T.OMBRO_BOSS_ALT             # 83,0: ponta dos bosses
_ENV_YC, _ENV_ZC = T.OMBRO_ENVELOPE_CENTRO
ENV_OMBRO = (G.IF_OMBRO_X - ENV_X, X_BOSS,      # x de 47,5 a 83 tem que ficar vazio
             _ENV_YC - ENV_Y / 2, _ENV_YC + ENV_Y / 2,
             _ENV_ZC - ENV_Z / 2, _ENV_ZC + ENV_Z / 2)


def _faixa(sx, a, b):
    """Intervalo em x entre ±a e ±b do lado sx (sempre crescente)."""
    return (min(sx * a, sx * b), max(sx * a, sx * b))


def _uniao(lst):
    return reduce(lambda a, b: a.union(b), lst)


def furos_ombro(sx):
    """(y, z) dos 4 insertos M3 do IF-OMBRO (45°, 135°, …: simétrico, vale para os dois lados)."""
    r = G.IF_OMBRO_M3_R
    return [(G.IF_OMBRO_Y + r * math.cos(math.radians(a)), G.IF_OMBRO_Z + r * math.sin(math.radians(a)))
            for a in (45, 135, 225, 315)]


def _tubo_uniao(x, z, y0, y1):
    """Tubo (traseira) ou coluna (frontal) de um ponto de união; vira estádio se houver pino ao lado."""
    for xp, zp in T.UNIAO_PINOS:
        if abs(xp - x) < 1e-6 and abs(zp - z) < 20:
            return F.estadio_y(x, z, zp, T.UNIAO_TUBO_D, y0, y1)
    return F.cil_y(x, z, T.UNIAO_TUBO_D, y0, y1)


# ============================================================
def traseira(sacrificio=True):
    ext = F.corpo_externo()
    p = F.casca()

    # ---------- estruturas internas (aparadas pelo contorno externo) ----------
    internos = []
    z_piso = G.Z_PISO_TRONCO + T.PISO_ESP
    for x in T.PISO_NERVURAS_X:                                   # nervuras do piso
        y_fim = -17.0 if abs(x) < 30 else Y_DIV - 2.5
        internos.append(F.caixa(x - T.PISO_NERVURA_ESP / 2, x + T.PISO_NERVURA_ESP / 2,
                                Y_FUNDO + 1, y_fim, z_piso - 1, z_piso + T.PISO_NERVURA_ALT))
    for sx in (-1, 1):                                            # nervuras do pescoço
        x = sx * T.PESCOCO_NERVURA_X
        internos.append(F.caixa(x - T.PESCOCO_NERVURA_LARG / 2, x + T.PESCOCO_NERVURA_LARG / 2,
                                Y_FUNDO + 1, Y_DIV, G.Z_TOPO_TRONCO - T.PESCOCO_NERVURA_ALT, G.Z_TOPO_TRONCO - 1))
    for sx in (-1, 1):                                            # trilhos IF-ELETRÔNICA
        x = sx * T.TRILHO_X
        internos.append(F.caixa(x - T.TRILHO_LARG / 2, x + T.TRILHO_LARG / 2,
                                Y_FUNDO + 1, Y_INT + T.TRILHO_PROF, *T.TRILHO_Z))
    for x, z in T.UNIAO_M3:                                       # tubos da união
        internos.append(_tubo_uniao(x, z, Y_FUNDO, Y_DIV))
    pa_w, pa_h = T.PAINEL_ABERTURA                                # painel: faixa engrossada + bosses
    internos.append(F.anel_y(0, T.PAINEL_Z, pa_w, pa_h, T.PAINEL_RAIO, T.PAINEL_MOLDURA + 3.0,
                             Y_FUNDO + 1, Y_INT + T.PAINEL_REBAIXO))
    for x, z in T.PAINEL_M3:
        internos.append(F.cil_y(x, z, 8.0, Y_FUNDO + 1, Y_FUNDO + T.PAINEL_REBAIXO + F.INS_PROF + 1.5))
    p = p.union(_uniao(internos).intersect(ext))

    # ---------- IF-OMBRO: ressalto em gota + placa plana + bosses ----------
    for sx in (-1, 1):
        y, z = G.IF_OMBRO_Y, G.IF_OMBRO_Z
        res = F.gota_x(y, z, 2 * T.OMBRO_RESSALTO_R, *_faixa(sx, 80.0, G.IF_OMBRO_X), ponta="-y")
        res = res.intersect(F.lado_y(Y_FUNDO, Y_DIV)).cut(F.cavidade())
        placa = F.gota_x(y, z, G.IF_OMBRO_FACE_D, *_faixa(sx, X_PLACA, G.IF_OMBRO_X), ponta="-y")
        placa = placa.intersect(F.lado_y(Y_FUNDO, Y_DIV))
        bosses = _uniao([F.cil_x(yy, zz, T.OMBRO_BOSS_D, *_faixa(sx, X_BOSS, X_PLACA + 0.5))
                         for yy, zz in furos_ombro(sx)])
        p = p.union(res).union(placa).union(bosses)

    p = p.intersect(F.lado_y(Y_FUNDO - 1, Y_DIV))

    # ---------- furos e recortes ----------
    cortes = []
    # IF-CINTURA
    for x, y in G.IF_CINTURA_M4:
        cortes.append(F.cil_z(x, y, G.M4_PASSANTE, G.Z_PISO_TRONCO - 1, z_piso + 0.5))
    cortes.append(F.cil_z(0, 0, G.IF_CINTURA_ABERTURA_TRONCO_D, G.Z_PISO_TRONCO - 1, z_piso + T.PISO_NERVURA_ALT + 1))
    # IF-OMBRO
    for sx in (-1, 1):
        xf = sx * G.IF_OMBRO_X
        for yy, zz in furos_ombro(sx):
            cortes.append(F.cil_x(yy, zz, F.INS_FURO, *_faixa(sx, G.IF_OMBRO_X - F.INS_PROF, G.IF_OMBRO_X + 1)))
        cortes.append(F.gota_x(G.IF_OMBRO_Y, G.IF_OMBRO_Z, G.IF_OMBRO_FURO_D, *_faixa(sx, 70.0, G.IF_OMBRO_X + 1), ponta="+y"))
        x0, x1, y0, y1, z0, z1 = ENV_OMBRO
        cortes.append(F.caixa(*_faixa(sx, x0, x1), y0, y1, z0, z1))      # garante o envelope livre
        del xf
    # IF-PESCOÇO
    zt = G.Z_TOPO_TRONCO
    for x, y in G.IF_PESCOCO_M3:
        cortes.append(F.cil_z(x, y, F.INS_FURO, zt - F.INS_PROF, zt + 1))
    cortes.append(F.gota_z(0, 0, G.IF_PESCOCO_CABO_D, zt - T.PESCOCO_NERVURA_ALT - 1, zt + 1, ponta="+y"))
    # trilhos
    for sx in (-1, 1):
        for zz in T.TRILHO_FUROS_Z:
            yf = Y_INT + T.TRILHO_PROF
            cortes.append(F.cil_y(sx * T.TRILHO_X, zz, F.INS_FURO, yf - F.INS_PROF, yf + 0.5))
    # união com a frontal: passagem da cabeça + rosca + furos dos pinos
    for x, z in T.UNIAO_M3:
        cortes.append(F.cil_y(x, z, T.UNIAO_ROSCA_FURO, Y_FUNDO - 1, T.UNIAO_ASSENTO_Y))
        cortes.append(F.cil_y(x, z, G.M3_PASSANTE, T.UNIAO_ASSENTO_Y - 0.5, Y_DIV + 1))
    for x, z in T.UNIAO_PINOS:
        cortes.append(F.cil_y(x, z, T.PINO_FURO_D, Y_DIV - T.PINO_FURO_PROF, Y_DIV + 1))
    # painel traseiro: abertura + rebaixo da moldura + insertos
    cortes.append(F.ret_y(0, T.PAINEL_Z, pa_w, pa_h, Y_FUNDO - 1, Y_INT + T.PAINEL_REBAIXO + 0.5, T.PAINEL_RAIO))
    rb_w, rb_h = pa_w + 2 * T.PAINEL_MOLDURA + 2 * G.FOLGA_ENCAIXE, pa_h + 2 * T.PAINEL_MOLDURA + 2 * G.FOLGA_ENCAIXE
    cortes.append(F.ret_y(0, T.PAINEL_Z, rb_w, rb_h, Y_FUNDO - 1, Y_FUNDO + T.PAINEL_REBAIXO,
                          T.PAINEL_RAIO + T.PAINEL_MOLDURA + G.FOLGA_ENCAIXE))
    for x, z in T.PAINEL_M3:
        y0 = Y_FUNDO + T.PAINEL_REBAIXO
        cortes.append(F.cil_y(x, z, F.INS_FURO, y0 - 0.5, y0 + F.INS_PROF))
    # grade do alto-falante
    fx, fz = T.FALANTE_CENTRO
    pts, passo = [], 5.0
    for i in range(-6, 7):
        for j in range(-6, 7):
            u = fx + passo * (i + 0.5 * (j % 2))
            v = fz + passo * math.sqrt(3) / 2 * j
            if math.hypot(u - fx, v - fz) + T.FALANTE_FURO_D / 2 <= T.FALANTE_GRADE_D / 2:
                pts.append((u, v))
    cortes.append(cq.Workplane(F.plano_y(Y_INT + 0.5)).pushPoints(pts).circle(T.FALANTE_FURO_D / 2)
                  .extrude(F.PAREDE + 2))
    p = p.cut(_uniao(cortes))

    if sacrificio:
        p = p.union(F.anel_y(0, T.PAINEL_Z, pa_w, pa_h, T.PAINEL_RAIO, T.SACRIFICIO_ESP,
                             Y_FUNDO, Y_FUNDO + T.PAINEL_REBAIXO + 0.01))
    return p


# ============================================================
def painel_traseiro():
    """03B: tampa de manutenção (verde-petróleo). Faixa de 1,5 no rebaixo + aba que entra na abertura."""
    pa_w, pa_h = T.PAINEL_ABERTURA
    w, h = pa_w + 2 * T.PAINEL_MOLDURA, pa_h + 2 * T.PAINEL_MOLDURA
    p = F.ret_y(0, T.PAINEL_Z, w, h, Y_FUNDO, Y_FUNDO + T.PAINEL_REBAIXO, T.PAINEL_RAIO + T.PAINEL_MOLDURA)
    aba_w, aba_h = pa_w - 2 * G.FOLGA_ENCAIXE, pa_h - 2 * G.FOLGA_ENCAIXE
    aba = F.anel_y(0, T.PAINEL_Z, aba_w - 4, aba_h - 4, max(T.PAINEL_RAIO - 2.3, 0.5), 2.0,
                   Y_FUNDO + T.PAINEL_REBAIXO - 0.01, Y_FUNDO + T.PAINEL_REBAIXO + 2.5)
    p = p.union(aba)
    for x, z in T.PAINEL_M3:
        p = p.cut(F.cil_y(x, z, G.M3_PASSANTE, Y_FUNDO - 1, Y_FUNDO + 5))
    for k in range(-2, 3):                                        # ventilação
        p = p.cut(F.ret_y(0, T.PAINEL_Z + 9.0 * k, 40.0, 3.0, Y_FUNDO - 1, Y_FUNDO + 5, 1.4))
    return p


PECAS = {"03A_tronco_traseiro": traseira, "03B_painel_traseiro": painel_traseiro}

BOM = [
    ("Inserto térmico M3 (4 IF-OMBRO esq. + 4 dir. + 4 IF-PESCOÇO + 20 trilhos + 4 painel)", 36),
    ("Parafuso M4 × 12 cabeça cilíndrica (tronco -> insertos da 08B), de cima, por dentro", 4),
    (f"Parafuso {T.UNIAO_PARAFUSO} (união 03 -> 04, POR TRÁS; chave Allen 2,5 longa ≥ 75 mm)", 6),
    ("Parafuso M3 × 6 cabeça abaulada ISO 7380 (painel 03B)", 4),
]

if __name__ == "__main__":
    out = RAIZ / "exports" / "p03_p04_tronco"
    out.mkdir(parents=True, exist_ok=True)
    for nome, fn in PECAS.items():
        s = fn()
        cq.exporters.export(s, str(out / f"{nome}.stl"), tolerance=0.02, angularTolerance=0.15)
        cq.exporters.export(s, str(out / f"{nome}.step"))
        bb = s.val().BoundingBox()
        print(f"{nome:24s} {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:5.1f}  valido={s.val().isValid()} "
              f"solidos={len(s.solids().vals())} vol={s.val().Volume()/1000:.1f} cm3")
