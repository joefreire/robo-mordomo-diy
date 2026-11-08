"""Cabeça do Robô Mordomo — C05 frente, C06 traseira e acessórios da V1.

Peças:
  C05 frente     : abertura do envelope IF-TELA-ROSTO, rebaixo da moldura (assentos nos 4 cantos
                   com insertos M3), 4 bosses M3 da futura bandeja da tela, furo IF-CÂMERA na testa
                   + 2 bosses do suporte futuro, bosses dos parafusos de união e 2 pinos de alinhamento.
  C06 traseira   : fundo com a IF-CABEÇA exata (4 furos M3 passantes com acesso de cima, por dentro,
                   2 furos Ø4,3 dos pinos, furo de cabos Ø18), nervuras, amarração de cabo,
                   4 pilares com túnel (parafusos de união M3×12 por TRÁS), soquete da antena,
                   almofadas das orelhas.
  M05 tampa facial V1 (olhos "^ ^" e sorriso em relevo) — ocupa o rebaixo, presa nos furos da moldura.
  M07 tampão da câmera (encaixe de pressão com 2 garras).
  Antena (soquete no topo, M3 por dentro) e 2 orelhas (3×M3 por dentro em insertos na orelha).

A moldura V2 (janela da tela real) NÃO é modelada: depende da tela comprada. Ela usa o mesmo
rebaixo, os mesmos 4 parafusos e o mesmo lábio de centragem da M05.

Referencial: as funções devolvem as peças MONTADAS no referencial do robô (fundo da cabeça em
z = G.Z_IF_CABECA, eixo do robô em x = y = 0, +Y = frente), pan 0 / tilt 0.
Exportação: STEP montado (referencial do robô) e STL já na ORIENTAÇÃO DE IMPRESSÃO (ver IMPRESSAO).
"""
import math
import sys
from pathlib import Path

import cadquery as cq

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from parameters import cabeca as K  # noqa: E402
from parameters import globais as G  # noqa: E402

W, D, H = G.CABECA                 # 205 (X) × 120 (Y) × 145 (Z)
R = G.CABECA_RAIO
T = K.PAREDE
F = G.FOLGA_ENCAIXE
Z0 = G.Z_IF_CABECA                 # fundo da cabeça no robô (356)
YF = D / 2                         # face da frente (local)
YT = -D / 2                        # face de trás

# rebaixo (P) e abertura
ENV_L, ENV_A, ENV_P = G.IF_TELA_ROSTO_ENVELOPE
P_L = ENV_L + 2 * F + 2 * K.REBAIXO_MARGEM
P_A = ENV_A + 2 * F + 2 * K.REBAIXO_MARGEM
Y_ASSENTO = YF - K.REBAIXO_PROF            # face de apoio da moldura/M05
Y_COLAR = YF - K.COLAR_PROF                # fundo do colar / face dos insertos da moldura
Y_BANDEJA = YF - ENV_P                     # topo dos bosses da bandeja = fundo do envelope


# ============================================================ utilidades
def _cil_z(r, x, y, z0, z1):
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).circle(r).extrude(z1 - z0)


def _cil_y(r, x, z, y0, y1):
    pl = cq.Plane(origin=(x, y0, z), xDir=(1, 0, 0), normal=(0, 1, 0))
    return cq.Workplane(pl).circle(r).extrude(y1 - y0)


def _cil_x(r, y, z, x0, x1):
    pl = cq.Plane(origin=(x0, y, z), xDir=(0, 1, 0), normal=(1, 0, 0))
    return cq.Workplane(pl).circle(r).extrude(x1 - x0)


def _prisma_xz(pts, y0, y1):
    """Polígono (x, z) extrudado em Y de y0 a y1."""
    pl = cq.Plane(origin=(0, y0, 0), xDir=(1, 0, 0), normal=(0, 1, 0))   # v local = -z
    return cq.Workplane(pl).polyline([(x, -z) for x, z in pts]).close().extrude(y1 - y0)


def _prisma_yz(pts, x0, x1):
    """Polígono (y, z) extrudado em X de x0 a x1."""
    pl = cq.Plane(origin=(x0, 0, 0), xDir=(0, 1, 0), normal=(1, 0, 0))
    return cq.Workplane(pl).polyline(pts).close().extrude(x1 - x0)


def _prisma_xy(pts, z0, z1):
    return cq.Workplane("XY").workplane(offset=z0).polyline(pts).close().extrude(z1 - z0)


def _caixa(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0).translate(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))


def _cone_z(r0, r1, z0, z1, x=0.0, y=0.0):
    return cq.Workplane("XY").add(cq.Solid.makeCone(r0, r1, z1 - z0, cq.Vector(x, y, z0), cq.Vector(0, 0, 1)))


def _cone_y(r0, r1, y0, y1, x=0.0, z=0.0):
    d = 1 if y1 > y0 else -1
    return cq.Workplane("XY").add(cq.Solid.makeCone(r0, r1, abs(y1 - y0), cq.Vector(x, y0, z), cq.Vector(0, d, 0)))


def _corpo(w, d, h, r, c, z0):
    """Monitor: retângulo arredondado (vista de frente, R) extrudado em Y, frente e trás chanfradas 45°."""
    b = cq.Workplane("XY").box(w, d, h).translate((0, 0, z0 + h / 2)).edges("|Y").fillet(r)
    b = b.faces(">Y").edges().chamfer(c)
    return b.faces("<Y").edges().chamfer(c)


def externo():
    return _corpo(W, D, H, R, K.CHANFRO, 0)


def cavidade():
    return _corpo(W - 2 * T, D - 2 * T, H - 2 * T, R - T, K.CHANFRO_INT, T)


def _robo(wp):
    return wp.translate((0, 0, Z0))


# posições compartilhadas -------------------------------------------------------------
def pilares():
    """Centros (x, z) dos 4 pilares de união: a 45° nos cantos R30, a PILAR_R_DIAG do centro do arco."""
    out = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            cx, cz = sx * (W / 2 - R), H / 2 + sz * (H / 2 - R)
            d = K.PILAR_R_DIAG / math.sqrt(2)
            out.append((cx + sx * d, cz + sz * d, sx, sz))
    return out


def cantos_moldura():
    """Centros (x, z) dos 4 parafusos da moldura/M05 (nos assentos de canto)."""
    return [(sx * (P_L / 2 - K.CANTO_PARAF), K.TELA_Z + sz * (P_A / 2 - K.CANTO_PARAF))
            for sx in (-1, 1) for sz in (-1, 1)]


def pinos_alinh():
    """(x, z) dos pinos de alinhamento frente->traseira."""
    out = []
    for x, onde in K.PINOS_ALINH:
        z = H - T - K.BLOCO_PINO / 2 if onde == "topo" else T + K.BLOCO_PINO / 2
        out.append((x, z))
    return out


def furos_orelha():
    """(y, z) dos 3 parafusos de cada orelha (iguais nos dois lados)."""
    return [(K.ORELHA_Y + K.ORELHA_M3_R * math.cos(math.radians(a)),
             K.ORELHA_Z + K.ORELHA_M3_R * math.sin(math.radians(a))) for a in (90, 210, 330)]


def _rib_canto(x, z, sx, sz, y0, y1, esp=3.0, comp=16.0):
    """Nervura do pilar até a parede do canto, a 45°."""
    u = (sx / math.sqrt(2), sz / math.sqrt(2))
    n = (-u[1] * esp / 2, u[0] * esp / 2)
    p0, p1 = (x, z), (x + u[0] * comp, z + u[1] * comp)
    pts = [(p0[0] + n[0], p0[1] + n[1]), (p1[0] + n[0], p1[1] + n[1]), (p1[0] - n[0], p1[1] - n[1]), (p0[0] - n[0], p0[1] - n[1])]
    return _prisma_xz(pts, y0, y1)


# ============================================================ C05 — frente
def frente_local():
    ext, cav = externo(), cavidade()
    casca = ext.cut(cav).intersect(_caixa(-W, W, K.Y_DIVISAO, D, -1, H + 1))
    dentro = []   # features internas (são cortadas pela cavidade antes de unir)
    # colar em volta do rebaixo (paredes do rebaixo + apoio dos assentos)
    dentro.append(_caixa(-P_L / 2 - K.COLAR_LARG, P_L / 2 + K.COLAR_LARG, Y_COLAR, YF,
                         K.TELA_Z - P_A / 2 - K.COLAR_LARG, K.TELA_Z + P_A / 2 + K.COLAR_LARG))
    # bosses da bandeja da tela (até o fundo do envelope)
    for x, z in K.BANDEJA_BOSS_POS:
        dentro.append(_cil_y(K.BANDEJA_BOSS_D / 2, x, z, Y_BANDEJA, YF))
    # bosses do suporte da câmera
    for sx in (-1, 1):
        dentro.append(_cil_y(K.CAMERA_BOSS_D / 2, sx * K.CAMERA_BOSS_X, K.CAMERA_Z, YF - T - K.CAMERA_BOSS_H, YF))
    # bosses de união (recebem os insertos; parafuso vem da traseira)
    for x, z, sx, sz in pilares():
        dentro.append(_cil_y(K.BOSS_FRENTE_D / 2, x, z, K.Y_DIVISAO, YF))
        dentro.append(_rib_canto(x, z, sx, sz, K.Y_DIVISAO, YF))
    # blocos dos pinos de alinhamento
    for x, z in pinos_alinh():
        b = K.BLOCO_PINO
        dentro.append(_caixa(x - b / 2, x + b / 2, K.Y_DIVISAO, YF, z - b / 2 - 2, z + b / 2 + 2))
    p = casca
    for f in dentro:
        p = p.union(f.intersect(cav))
    # rebaixo + abertura (atravessa parede e colar)
    p = p.cut(_caixa(-P_L / 2, P_L / 2, Y_COLAR - 1, YF + 1, K.TELA_Z - P_A / 2, K.TELA_Z + P_A / 2))
    # assentos triangulares nos cantos (fundo do rebaixo), com inserto M3 por dentro
    for sx in (-1, 1):
        for sz in (-1, 1):
            cx, cz = sx * P_L / 2, K.TELA_Z + sz * P_A / 2
            tri = [(cx, cz), (cx - sx * K.CANTO_L, cz), (cx, cz - sz * K.CANTO_L)]
            p = p.union(_prisma_xz(tri, Y_COLAR, Y_ASSENTO))
    for x, z in cantos_moldura():
        p = p.cut(_cil_y(G.M3_PASSANTE / 2, x, z, Y_COLAR - 1, Y_ASSENTO + 0.5))
        p = p.cut(_cil_y(G.M3_INSERTO_FURO / 2, x, z, Y_COLAR - 1, Y_COLAR + G.M3_INSERTO_PROF + 0.5))
    # bandeja: insertos de cima (lado de dentro)
    for x, z in K.BANDEJA_BOSS_POS:
        p = p.cut(_cil_y(G.M3_INSERTO_FURO / 2, x, z, Y_BANDEJA - 1, Y_BANDEJA + G.M3_INSERTO_PROF + 0.5))
    # câmera: furo na testa + insertos dos bosses
    p = p.cut(_cil_y(G.IF_CAMERA_FURO_D / 2, 0, K.CAMERA_Z, YF - T - 2, YF + 1))
    for sx in (-1, 1):
        y0 = YF - T - K.CAMERA_BOSS_H
        p = p.cut(_cil_y(G.M3_INSERTO_FURO / 2, sx * K.CAMERA_BOSS_X, K.CAMERA_Z, y0 - 1, y0 + G.M3_INSERTO_PROF + 0.5))
    # insertos de união (da face de divisão)
    for x, z, _, _ in pilares():
        p = p.cut(_cil_y(G.M3_INSERTO_FURO / 2, x, z, K.Y_DIVISAO - 1, K.Y_DIVISAO + G.M3_INSERTO_PROF + 0.5))
    # pinos de alinhamento (saem da face de divisão para dentro da traseira)
    for x, z in pinos_alinh():
        p = p.union(_cil_y(K.PINO_ALINH_D / 2, x, z, K.Y_DIVISAO - K.PINO_ALINH_H, K.Y_DIVISAO + 0.5))
    return p


# ============================================================ C06 — traseira
def traseira_local():
    ext, cav = externo(), cavidade()
    casca = ext.cut(cav).intersect(_caixa(-W, W, -D, K.Y_DIVISAO, -1, H + 1))
    dentro = []
    ax, ay = K.ALMOFADA
    # almofada da IF-CABEÇA (chanfro 45° atrás: na impressão o -Y fica para baixo)
    alt = K.FUNDO_ESP - T
    dentro.append(_prisma_yz([(-ay / 2 - alt, T - 0.01), (ay / 2, T - 0.01), (ay / 2, K.FUNDO_ESP), (-ay / 2, K.FUNDO_ESP)],
                             -ax / 2, ax / 2))
    # nervuras do fundo (no sentido Y)
    for xn in K.NERVURAS_X:
        for sx in (-1, 1):
            dentro.append(_caixa(sx * xn - T / 2, sx * xn + T / 2, YT, ay / 2, 0, T + K.NERVURA_ALT))
    # amarração de cabo: 2 alças ao lado do furo
    for sx in (-1, 1):
        dentro.append(_caixa(sx * 13 - 3, sx * 13 + 3, -4, 4, K.FUNDO_ESP - 0.01, K.FUNDO_ESP + 4.5))
    # pilares de união (túnel da cabeça do parafuso, aberto atrás)
    for x, z, sx, sz in pilares():
        dentro.append(_cil_y(K.PILAR_D / 2, x, z, YT, K.Y_DIVISAO))
        dentro.append(_rib_canto(x, z, sx, sz, YT, K.Y_DIVISAO))
    # blocos dos furos dos pinos (chanfro 45° embaixo na impressão)
    for x, z in pinos_alinh():
        b = K.BLOCO_PINO
        z0, z1 = z - b / 2 - 2, z + b / 2 + 2
        y1, y0 = K.Y_DIVISAO, K.Y_DIVISAO - 10
        topo = z > H / 2
        zw, zl = (z1, z0) if topo else (z0, z1)          # zw = lado da parede
        dentro.append(_prisma_yz([(y1, zw), (y1, zl), (y0, zl), (y0 - abs(zl - zw), zw)], x - b / 2, x + b / 2))
    # soquete da antena: boss em gota (ponta para -Y)
    zt = H - G.ANTENA_SOQUETE[1] - K.ANTENA_PISO
    rb = K.ANTENA_BOSS_R
    gota = _cil_z(rb, 0, K.ANTENA_Y, zt, H).union(
        _prisma_xy([(-rb / math.sqrt(2), K.ANTENA_Y - rb / math.sqrt(2)), (0, K.ANTENA_Y - rb * math.sqrt(2)),
                    (rb / math.sqrt(2), K.ANTENA_Y - rb / math.sqrt(2)), (0, K.ANTENA_Y)], zt, H))
    dentro.append(gota)
    # almofadas das orelhas
    for sx in (-1, 1):
        x0 = sx * (W / 2 - T - K.ORELHA_ALMOFADA_ESP)
        dentro.append(_cil_x(K.ORELHA_ALMOFADA_D / 2, K.ORELHA_Y, K.ORELHA_Z, min(x0, sx * W / 2), max(x0, sx * W / 2)))
    p = casca
    for f in dentro:
        p = p.union(f.intersect(cav))
    # --- furos da IF-CABEÇA
    p = p.cut(_cil_z(K.CABO_FURO_D / 2, 0, 0, -1, K.FUNDO_ESP + 5))
    p = p.cut(_cone_z(K.CABO_FURO_D / 2, K.CABO_FURO_D / 2 + 1.5, K.FUNDO_ESP - 0.01, K.FUNDO_ESP + 1.5))
    for x, y in G.IF_CABECA_M3:
        p = p.cut(_cil_z(G.M3_PASSANTE / 2, x, y, -1, K.FUNDO_ESP + 1))
    for x, y in G.IF_CABECA_PINOS:
        p = p.cut(_cil_z(K.PINO_FURO_D / 2, x, y, -1, K.PINO_FURO_P))
    # rasgos das alças de amarração (verticais na impressão)
    for sx in (-1, 1):
        p = p.cut(_caixa(sx * 13 - 2.2, sx * 13 + 2.2, -5, 5, K.FUNDO_ESP + 0.6, K.FUNDO_ESP + 2.8))
    # --- túneis de união
    for x, z, _, _ in pilares():
        p = p.cut(_cil_y(K.TUNEL_D / 2, x, z, YT - 1, K.Y_DIVISAO - K.PILAR_PISO))
        p = p.cut(_cil_y(G.M3_PASSANTE / 2, x, z, YT, K.Y_DIVISAO + 1))
    # --- furos dos pinos de alinhamento
    for x, z in pinos_alinh():
        p = p.cut(_cil_y(K.PINO_ALINH_D / 2 + F, x, z, K.Y_DIVISAO - K.PINO_ALINH_H - 1, K.Y_DIVISAO + 1))
    # --- soquete da antena (Ø8 × 10 + escareado 45°) e furo M3 do piso
    rs, ps = G.ANTENA_SOQUETE[0] / 2, G.ANTENA_SOQUETE[1]
    p = p.cut(_cil_z(rs, 0, K.ANTENA_Y, H - ps, H + 1))
    e = K.ANTENA_ESCAREADO
    p = p.cut(_cone_z(rs, rs + e + 0.01, H - e, H + 0.01, 0, K.ANTENA_Y))
    p = p.cut(_cil_z(G.M3_PASSANTE / 2, 0, K.ANTENA_Y, H - ps - K.ANTENA_PISO - 1, H - ps + 0.1))
    # --- orelhas: 3 M3 passantes em cada lado
    for sx in (-1, 1):
        for y, z in furos_orelha():
            p = p.cut(_cil_x(G.M3_PASSANTE / 2, y, z, sx * (W / 2 - 10), sx * (W / 2 + 1)) if sx > 0 else
                      _cil_x(G.M3_PASSANTE / 2, y, z, -W / 2 - 1, -W / 2 + 10))
    return p


# ============================================================ M05 — tampa facial
def _arco_y(cx, cz, r, larg, a0, a1, y0, y1):
    """Traço em arco (a0 -> a1, graus no plano XZ, 0 = +X, 90 = +Z) extrudado em Y, pontas redondas."""
    anel = _cil_y(r + larg / 2, cx, cz, y0, y1).cut(_cil_y(r - larg / 2, cx, cz, y0 - 1, y1 + 1))
    pts = [(cx, cz)]
    for i in range(13):
        a = math.radians(a0 + (a1 - a0) * i / 12)
        pts.append((cx + 3 * r * math.cos(a), cz + 3 * r * math.sin(a)))
    p = anel.intersect(_prisma_xz(pts, y0 - 1, y1 + 1))
    for a in (a0, a1):
        p = p.union(_cil_y(larg / 2, cx + r * math.cos(math.radians(a)), cz + r * math.sin(math.radians(a)), y0, y1))
    return p


def m05_relevo_local():
    """Rosto em relevo da M05: olhos "^ ^", sorriso e bochechas (cor trocada na camada do relevo)."""
    zc = K.TELA_Z
    y0, y1 = YF - 0.01, YF + K.RELEVO
    p = _arco_y(0.0, zc - 8.0, 15.0, 5.5, 205, 335, y0, y1)
    for sx in (-1, 1):
        p = p.union(_arco_y(sx * 30.0, zc + 6.0, 13.0, 6.0, 25, 155, y0, y1))
        for dx in (-3.5, 3.5):
            cx, cz = sx * 46.0 + dx, zc - 12.0
            ang = math.radians(70)
            u = (math.cos(ang) * 3.5, math.sin(ang) * 3.5)
            n = (-math.sin(ang) * 1.2, math.cos(ang) * 1.2)
            p = p.union(_prisma_xz([(cx - u[0] + n[0], cz - u[1] + n[1]), (cx + u[0] + n[0], cz + u[1] + n[1]),
                                    (cx + u[0] - n[0], cz + u[1] - n[1]), (cx - u[0] - n[0], cz - u[1] - n[1])], y0, y1))
    return p


def m05_local():
    lx, lz = P_L - 2 * F, P_A - 2 * F
    zc = K.TELA_Z
    p = _caixa(-lx / 2, lx / 2, Y_ASSENTO, YF, zc - lz / 2, zc + lz / 2).edges("|Y").fillet(1.5)
    # lábio de centragem (entra no rebaixo/colar), recortado nos assentos dos cantos
    e = K.M05_LABIO_ESP
    labio = _caixa(-lx / 2, lx / 2, Y_ASSENTO - K.M05_LABIO_PROF, Y_ASSENTO + 0.01, zc - lz / 2, zc + lz / 2).cut(
        _caixa(-lx / 2 + e, lx / 2 - e, Y_ASSENTO - K.M05_LABIO_PROF - 1, Y_ASSENTO + 1, zc - lz / 2 + e, zc + lz / 2 - e))
    for sx in (-1, 1):
        for sz in (-1, 1):
            cx, cz = sx * P_L / 2, zc + sz * P_A / 2
            folga = K.CANTO_L + 2 * F + 1
            tri = [(cx + sx, cz + sz), (cx - sx * folga, cz + sz), (cx + sx, cz - sz * folga)]
            labio = labio.cut(_prisma_xz(tri, Y_ASSENTO - K.M05_LABIO_PROF - 1, Y_ASSENTO + 0.005))
    p = p.union(labio)
    # furos escareados (M3 cabeça chata DIN 7991) — escareado na face, que fica para CIMA na impressão
    for x, z in cantos_moldura():
        p = p.cut(_cil_y(G.M3_PASSANTE / 2, x, z, Y_ASSENTO - 1, YF + 1))
        p = p.cut(_cone_y(G.M3_PASSANTE / 2, 3.2, YF - 1.6, YF + 0.01, x, z))
    return p.union(m05_relevo_local())


# ============================================================ M07 — tampão da câmera
def m07_local():
    rf, ef = K.M07_FLANGE[0] / 2, K.M07_FLANGE[1]
    zc = K.CAMERA_Z
    rh = G.IF_CAMERA_FURO_D / 2
    p = _cil_y(rf, 0, zc, YF, YF + ef)
    p = p.cut(_cil_y(rf - 2.0, 0, zc, YF + ef - 0.6, YF + ef + 1).cut(_cil_y(rf - 3.2, 0, zc, YF, YF + ef + 2)))  # sulco decorativo
    y_garra = YF - T - 0.2                                 # face de trava logo atrás da parede
    p = p.union(_cil_y(rh - 0.2, 0, zc, y_garra - 1.6, YF + 0.01))
    p = p.union(_cone_y(rh - 0.6, rh + 0.35, y_garra - 1.6, y_garra, 0, zc))   # garra (rampa de entrada)
    p = p.cut(_cil_y(rh - 2.2, 0, zc, y_garra - 2, YF - 0.6))
    p = p.cut(_caixa(-1.0, 1.0, y_garra - 2, YF - 0.6, zc - rh - 1, zc + rh + 1))    # fenda: 2 garras flexíveis
    return p


# ============================================================ antena
def antena_local():
    rs, ps = G.ANTENA_SOQUETE[0] / 2, G.ANTENA_SOQUETE[1]
    e = K.ANTENA_ESCAREADO
    rp = rs - F
    y = K.ANTENA_Y
    p = _cil_z(rp, 0, y, H - ps + 0.5, H - e)                       # pino (0,5 mm de folga no fundo)
    p = p.union(_cone_z(rs, rs + e, H - e, H, 0, y))               # assenta no escareado
    p = p.union(_cil_z(rs + e, 0, y, H - 0.01, H + 2.0))           # colar
    rh = K.ANTENA_HASTE_D / 2
    p = p.union(_cone_z(rs + e, rh, H + 2.0, H + 2.0 + (rs + e - rh), 0, y))
    rb = K.ANTENA_BOLA_D / 2
    zb = H + K.ANTENA_ALTURA - rb
    z_cone = zb - rb / math.sqrt(2) - (rb / math.sqrt(2) - rh)
    p = p.union(_cil_z(rh, 0, y, H + 2.0, z_cone + 0.01))
    p = p.union(_cone_z(rh, rb / math.sqrt(2), z_cone, zb - rb / math.sqrt(2) + 0.01, 0, y))
    p = p.union(cq.Workplane("XY").sphere(rb).translate((0, y, zb)))
    p = p.cut(_cil_z(G.M3_INSERTO_FURO / 2, 0, y, H - ps, H - ps + 0.5 + G.M3_INSERTO_PROF + 0.5))
    return p


# ============================================================ orelhas
def orelha_local(sx):
    x0 = sx * W / 2
    esp, (ri, anel_h) = G.ORELHA_ESP, K.ORELHA_ANEL
    r = G.ORELHA_D / 2
    corpo_h = esp - anel_h

    def cx(a, b):  # cilindro em X entre as distâncias a e b da parede
        return lambda rr: _cil_x(rr, K.ORELHA_Y, K.ORELHA_Z, min(x0 + sx * a, x0 + sx * b), max(x0 + sx * a, x0 + sx * b))
    p = cx(0, corpo_h)(r)
    p = p.union(cx(corpo_h - 0.01, esp)(r).cut(cx(corpo_h - 1, esp + 1)(ri)))
    p = p.union(cx(corpo_h - 0.01, corpo_h + 0.6)(ri - 4.0))             # disco central levemente saliente
    for y, z in furos_orelha():
        a, b = x0, x0 + sx * (G.M3_INSERTO_PROF + 0.5)
        p = p.cut(_cil_x(G.M3_INSERTO_FURO / 2, y, z, min(a, b) - 0.01 * sx, max(a, b)) if sx > 0 else
                  _cil_x(G.M3_INSERTO_FURO / 2, y, z, min(a, b), max(a, b) + 0.01))
    return p


# ============================================================ peças no robô
def frente():
    return _robo(frente_local())


def traseira():
    return _robo(traseira_local())


def m05_tampa_facial():
    return _robo(m05_local())


def m07_tampao_camera():
    return _robo(m07_local())


def antena():
    return _robo(antena_local())


def orelha_esquerda():
    return _robo(orelha_local(-1))


def orelha_direita():
    return _robo(orelha_local(1))


PECAS = {"C05_cabeca_frente": frente, "C06_cabeca_traseira": traseira, "M05_tampa_facial": m05_tampa_facial,
         "M07_tampao_camera": m07_tampao_camera, "CA1_antena": antena,
         "CA2_orelha_esquerda": orelha_esquerda, "CA3_orelha_direita": orelha_direita}

# rotação para a mesa: (eixo, ângulo) — a face indicada fica para baixo
IMPRESSAO = {
    "C05_cabeca_frente": (((1, 0, 0), -90), "face da frente na mesa (chanfro 45° e assentos de canto sem suporte)"),
    "C06_cabeca_traseira": (((1, 0, 0), 90), "costas na mesa, aberta para cima (paredes em pé; túneis verticais)"),
    "M05_tampa_facial": (((1, 0, 0), 90), "lábio na mesa, rosto para CIMA; trocar filamento na 1ª camada do relevo"),
    "M07_tampao_camera": (((1, 0, 0), -90), "flange na mesa, garras para cima"),
    "CA1_antena": (((0, 0, 1), 0), "em pé, pino na mesa (bolinha com cone 45°)"),
    "CA2_orelha_esquerda": (((0, 1, 0), 90), "face de encosto na mesa, anel para cima"),
    "CA3_orelha_direita": (((0, 1, 0), -90), "face de encosto na mesa, anel para cima"),
}

BOM = [
    ("Parafuso M3 × 10 cabeça cilíndrica (cabeça -> placa 11E, por dentro, de cima)", 4),
    ("Parafuso M3 × 12 cabeça cilíndrica (união traseira -> frente, por trás, chave longa ≥ 100 mm)", 4),
    ("Inserto térmico M3 (frente: união)", 4),
    ("Parafuso M3 × 10 cabeça chata DIN 7991 (M05 / moldura)", 4),
    ("Inserto térmico M3 (frente: assentos da moldura, por dentro)", 4),
    ("Inserto térmico M3 (frente: bosses da bandeja da tela — V2)", 4),
    ("Inserto térmico M3 (frente: bosses do suporte da câmera — V2)", 2),
    ("Parafuso M3 × 8 (antena, por dentro) + inserto M3 na antena", 1),
    ("Parafuso M3 × 10 (orelhas, por dentro) + inserto M3 na orelha", 6),
    ("Abraçadeira de nylon 2,5 mm (amarração no fundo)", 1),
]


def para_mesa(nome, wp):
    (eixo, ang), _ = IMPRESSAO[nome]
    s = wp.rotate((0, 0, 0), eixo, ang) if ang else wp
    bb = s.val().BoundingBox()
    return s.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))


if __name__ == "__main__":
    out = RAIZ / "exports" / "p_cabeca"
    out.mkdir(parents=True, exist_ok=True)
    for nome, fn in PECAS.items():
        s = fn()
        cq.exporters.export(s, str(out / f"{nome}.step"))
        m = para_mesa(nome, s)
        cq.exporters.export(m, str(out / f"{nome}.stl"), tolerance=0.02, angularTolerance=0.15)
        bb = m.val().BoundingBox()
        print(f"{nome:22s} {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:5.1f}  valido={s.val().isValid()} "
              f"solidos={len(s.solids().vals())} vol={s.val().Volume()/1000:.1f} cm3")
