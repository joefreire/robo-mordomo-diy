"""Peça 01R — módulo de base COM RODAS e AUTO-CARREGAMENTO (V2). Troca a Peça 01 sem mexer no resto.

Mesma interface IF-BASE da Peça 01: o contorno externo inclinado e a borda plana em z = 25 são
gerados pela MESMA função da 01 (base_inferior.forma), então a aba da Peça 02, as torres M3 de
união (BASE_TORRES, parafuso por baixo) e o assento do difusor do LED batem igual.
Diferenças: fundo RODAS_FOLGA_CHAO acima da mesa (altura do robô igual); poços das 2 rodas de
tração (y = 0, giro no lugar); 4 rodízios perto dos cantos passando pelo fundo; sapatas com
insertos para os suportes dos motores (adaptador impresso conforme o motor comprado); berço da
bateria (faz o papel do contrapeso); bases do driver e da placa de carga; na TRASEIRA, 2
rebaixos para os contatos de carga e a janela do receptor de IR (encontra a doca, ver
base/doca_carga.py).

Comprados só como ENVELOPES (parameters/globais.py). Conferir com as peças reais.
Impressão: fundo na mesa, abertura para cima (como a 01).
"""
import math
import sys
from pathlib import Path

import cadquery as cq

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from parameters import globais as G  # noqa: E402
from base import base_inferior as B1  # noqa: E402

# ============================================================
Z0 = G.RODAS_FOLGA_CHAO          # fundo do módulo (6)
FUNDO = 3.0
ZF = Z0 + FUNDO                  # face de cima do fundo
R_RODA = G.RODA_D_MAX / 2
POCO_COMP = G.RODA_D_MAX + 2 * G.RODA_FOLGA        # ao longo de Y
POCO_LARG = G.RODA_LARG + 2 * G.RODA_FOLGA         # ao longo de X
PAREDE_POCO = 2.4
POCO_TOPO = R_RODA - G.MOTOR_ENVELOPE[2] / 2 - 1.0   # a parede do poço passa por baixo do motor
SAPATA = (40.0, 26.0, 4.0)       # sapata do suporte do motor (X × Y × altura), insertos M3 nos cantos
RODIZIO_FURO = G.RODIZIO_ENVELOPE[0] + 0.6
RODIZIO_MOLDURA = RODIZIO_FURO + 8.0
RODIZIO_MOLDURA_ALT = 3.0
BATERIA_TRAVA = (6.0, 2.5)       # rasgos para cinta/abraçadeira
CARREGADOR_POS = (G.RODA_X - 3.0, -46.0)
PAREDE = G.P01_PAREDE


def _cil(x, y, d, z0, z1):
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).circle(d / 2).extrude(z1 - z0)


def _caixa(cx, cy, lx, ly, z0, z1):
    return cq.Workplane("XY").workplane(offset=z0).center(cx, cy).rect(lx, ly).extrude(z1 - z0)


def y_traseira(z):
    """y da face externa traseira na altura z (parede inclinada)."""
    return -(G.BASE_PROF / 2 - G.recuo(z))


def casca():
    """Forma da 01 (mesmo contorno e borda), cortada em Z0 e com fundo novo."""
    f = B1.forma().cut(_caixa(0, 0, 400, 400, -10, Z0))
    r0 = G.recuo(Z0)
    fundo = (cq.Workplane("XY").workplane(offset=Z0)
             .sketch().rect(G.BASE_LARG - 2 * r0, G.BASE_PROF - 2 * r0).vertices().fillet(G.BASE_RAIO - r0).finalize()
             .extrude(FUNDO, taper=G.BASE_INCLINACAO))
    return f.union(fundo)


def modelo():
    p = casca()
    # torres de união (mesma posição e furo da 01)
    for x, y in G.BASE_TORRES:
        p = p.union(_cil(x, y, G.BASE_TORRE_D, ZF - 0.5, B1.B.Z_TORRE_TOPO))
        p = p.cut(_cil(x, y, G.M3_PASSANTE, Z0 - 1, B1.B.Z_TORRE_TOPO + 1))
        p = p.cut(_cil(x, y, B1.REBAIXO_M3_D, Z0 - 1, Z0 + B1.REBAIXO_M3_PROF))
    # poços das rodas + sapatas dos motores
    for sx in (-1, 1):
        cx = sx * G.RODA_X
        p = p.union(_caixa(cx, 0, POCO_LARG + 2 * PAREDE_POCO, POCO_COMP + 2 * PAREDE_POCO, ZF - 0.5, POCO_TOPO))
        p = p.cut(_caixa(cx, 0, POCO_LARG, POCO_COMP, Z0 - 1, POCO_TOPO + 1))
        xin = cx - sx * (POCO_LARG / 2 + PAREDE_POCO)
        scx = xin - sx * SAPATA[0] / 2
        p = p.union(_caixa(scx, 0, SAPATA[0], SAPATA[1], ZF - 0.5, ZF + SAPATA[2]))
        for dx in (-SAPATA[0] / 2 + 5, SAPATA[0] / 2 - 5):
            for dy in (-SAPATA[1] / 2 + 5, SAPATA[1] / 2 - 5):
                p = p.cut(_cil(scx + dx, dy, G.M3_INSERTO_FURO, ZF + SAPATA[2] - G.M3_INSERTO_PROF, ZF + SAPATA[2] + 0.1))
    # rodízios: furo do corpo pelo fundo + moldura com 4 insertos para a flange
    for cx, cy in G.RODIZIOS:
        p = p.union(_caixa(cx, cy, RODIZIO_MOLDURA, RODIZIO_MOLDURA, ZF - 0.5, ZF + RODIZIO_MOLDURA_ALT))
        p = p.cut(_caixa(cx, cy, RODIZIO_FURO, RODIZIO_FURO, Z0 - 1, ZF + RODIZIO_MOLDURA_ALT + 1))
    # berço da bateria (guias laterais) + rasgos de cinta
    bx, by, _ = G.BATERIA_ENVELOPE
    cyb = -G.BATERIA_Y
    for sx in (-1, 1):
        p = p.union(_caixa(sx * (bx / 2 + 2.0), cyb, 3.0, by * 0.7, ZF - 0.5, ZF + 8))
    for dx in (-bx / 4, bx / 4):
        for sy in (-1, 1):
            p = p.cut(_caixa(dx, cyb + sy * (by / 2 + 3), BATERIA_TRAVA[0], BATERIA_TRAVA[1] + 0.4, Z0 - 1, ZF + 1))
    # driver (frente) e placa de carga (atrás, ao lado da bateria): 4 bosses com inserto M3
    for (cx, cy), (ex, ey, _) in (((0.0, G.DRIVER_Y), G.DRIVER_ENVELOPE), (CARREGADOR_POS, G.CARREGADOR_ENVELOPE)):
        for sx in (-1, 1):
            for sy in (-1, 1):
                x, y = cx + sx * (ex / 2 - 4), cy + sy * (ey / 2 - 4)
                p = p.union(_cil(x, y, 8, ZF - 0.5, ZF + 5))
                p = p.cut(_cil(x, y, G.M3_INSERTO_FURO, ZF + 5 - G.M3_INSERTO_PROF, ZF + 5.1))
    # TRASEIRA: rebaixos dos contatos de carga, furo do fio + boss com inserto atrás de cada um
    pl, pa, pp = G.CARGA_PAD
    for sx in (-1, 1):
        x = sx * G.CARGA_X
        yt = y_traseira(G.CARGA_Z)
        p = p.cut(_caixa(x, yt + pp / 2 - 0.01, pl, pp + 0.02, G.CARGA_Z - pa / 2, G.CARGA_Z + pa / 2))
        p = p.union(_caixa(x, yt + PAREDE + 4, 10, 8, ZF - 0.5, G.CARGA_Z + 4))
        p = p.cut(cq.Workplane("XZ", origin=(0, yt - 1, 0)).center(x, G.CARGA_Z).circle(1.6).extrude(-(PAREDE + 6)))
        p = p.cut(cq.Workplane("XZ", origin=(0, yt + PAREDE + 8.1, 0)).center(x, G.CARGA_Z).circle(G.M3_INSERTO_FURO / 2)
                  .extrude(G.M3_INSERTO_PROF))
    # janela do receptor de IR
    yt = y_traseira(G.CARGA_IR_Z)
    p = p.cut(cq.Workplane("XZ", origin=(0, yt - 1, 0)).center(0, G.CARGA_IR_Z).circle(G.CARGA_IR_D / 2).extrude(-(PAREDE + 2)))
    return p


def envelopes():
    """Comprados da V2 como volumes (colisão e visualizador)."""
    e = {}
    ml, my, mz = G.MOTOR_ENVELOPE
    for sx, n in ((-1, "esq"), (1, "dir")):
        cx = sx * G.RODA_X
        e[f"roda_{n}"] = (cq.Workplane("YZ").workplane(offset=cx - G.RODA_LARG / 2).center(0, R_RODA)
                          .circle(R_RODA).extrude(G.RODA_LARG))
        x_ini = cx - sx * (POCO_LARG / 2 + PAREDE_POCO)
        x0, x1 = sorted((x_ini, x_ini - sx * ml))
        e[f"motor_{n}"] = _caixa((x0 + x1) / 2, 0, x1 - x0, my, R_RODA - mz / 2, R_RODA + mz / 2)
    rx, ry, rz = G.RODIZIO_ENVELOPE
    for i, (cx, cy) in enumerate(G.RODIZIOS):
        e[f"rodizio_{i}"] = _caixa(cx, cy, rx, ry, G.RODIZIO_ALIVIO, G.RODIZIO_ALIVIO + rz)
    bx, by, bz = G.BATERIA_ENVELOPE
    e["bateria"] = _caixa(0, -G.BATERIA_Y, bx, by, ZF, ZF + bz)
    dx, dy, dz = G.DRIVER_ENVELOPE
    e["driver"] = _caixa(0, G.DRIVER_Y, dx, dy, ZF + 5, ZF + 5 + dz)
    cx, cy = CARREGADOR_POS
    ex, ey, ez = G.CARREGADOR_ENVELOPE
    e["carregador"] = _caixa(cx, cy, ex, ey, ZF + 5, ZF + 5 + ez)
    return e


PECAS = {"01R_base_rodas": modelo}

if __name__ == "__main__":
    out = RAIZ / "exports" / "p01R_base_rodas"
    out.mkdir(parents=True, exist_ok=True)
    s = modelo()
    cq.exporters.export(s, str(out / "01R_base_rodas.stl"), tolerance=0.01, angularTolerance=0.1)
    cq.exporters.export(s, str(out / "01R_base_rodas.step"))
    bb = s.val().BoundingBox()
    print(f"01R {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} z {bb.zmin:.1f}..{bb.zmax:.1f} valido={s.val().isValid()} "
          f"solidos={len(s.solids().vals())} vol={s.val().Volume() / 1000:.1f} cm3")
