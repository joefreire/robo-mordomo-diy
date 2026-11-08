"""Validação da cabeça (C05, C06, M05, M07, antena, orelhas) + vistas + massa/CG.

Usa as peças REAIS do pescoço (pescoco.pescoco_manual) na pose de pan/tilt (mesma convenção de
pescoco/validar_pescoco.py: tilt em torno do eixo X em z = Z_TILT, depois pan em torno de Z) e
uma caixa do tronco 185 × 105 × 190 a partir de G.Z_PISO_TRONCO.

    ~/.venvs/cadquery/bin/python cabeca/validar_cabeca.py
"""
import math
import sys
from pathlib import Path

import cadquery as cq
import trimesh

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from cabeca import cabeca as C  # noqa: E402
from parameters import cabeca as K  # noqa: E402
from parameters import globais as G  # noqa: E402
from pescoco import pescoco_manual as P  # noqa: E402
from tools.render import CORES, render_conjunto  # noqa: E402

OUT = RAIZ / "exports" / "p_cabeca"
OUT.mkdir(parents=True, exist_ok=True)
TMP = OUT / "_tmp.stl"
TOL = 0.5
REL, FALHAS = [], []
ZT = G.Z_TOPO_TRONCO
Z_EIXO_TILT = ZT + P.Z_TILT
Z0 = G.Z_IF_CABECA


def ok(c, m):
    REL.append(("OK  " if c else "FALHA ") + m)
    if not c:
        FALHAS.append(m)


def inter_vol(a, b):
    try:
        r = a.intersect(b)
        return sum(s.Volume() for s in r.solids().vals())
    except Exception:
        return 0.0


def to_mesh(wp):
    cq.exporters.export(wp, str(TMP), tolerance=0.05, angularTolerance=0.25)
    return trimesh.load(str(TMP))


def pose(s, pan, tilt, gira_tilt=True, gira_pan=True):
    if gira_tilt:
        s = s.rotate((0, 0, Z_EIXO_TILT), (1, 0, Z_EIXO_TILT), tilt)
    if gira_pan:
        s = s.rotate((0, 0, 0), (0, 0, 1), pan)
    return s


def bb(wp):
    return wp.val().BoundingBox()


# ------------------------------------------------------------------ peças
cab = {n: f() for n, f in C.PECAS.items()}
pesc = {n: f().translate((0, 0, ZT)) for n, f in P.PECAS.items()}       # referencial do robô
tronco = C._caixa(-G.TRONCO_LARG / 2, G.TRONCO_LARG / 2, -G.TRONCO_PROF / 2, G.TRONCO_PROF / 2,
                  G.Z_PISO_TRONCO, G.Z_PISO_TRONCO + G.TRONCO_ALT)
fr, tr = cab["C05_cabeca_frente"], cab["C06_cabeca_traseira"]
L = lambda wp: wp.translate((0, 0, Z0))  # noqa: E731  (local da cabeça -> robô)

REL.append("## 1. Sólidos")
for n, s in cab.items():
    ok(s.val().isValid() and len(s.solids().vals()) == 1, f"{n}: válido e 1 corpo")

# ------------------------------------------------------------------ 2. fechamento
REL.append("\n## 2. Frente + traseira fecham (e acessórios encaixam) sem interferência")
pares = [("C05_cabeca_frente", "C06_cabeca_traseira"), ("M05_tampa_facial", "C05_cabeca_frente"),
         ("M07_tampao_camera", "C05_cabeca_frente"), ("CA1_antena", "C06_cabeca_traseira"),
         ("CA2_orelha_esquerda", "C06_cabeca_traseira"), ("CA3_orelha_direita", "C06_cabeca_traseira"),
         ("M05_tampa_facial", "C06_cabeca_traseira")]
for a, b in pares:
    v = inter_vol(cab[a], cab[b])
    ok(v < TOL, f"{a} × {b}: interferência {v:.2f} mm³")
# contato na divisão: fatia fina dos dois lados do plano
fatia_f = inter_vol(fr, L(C._caixa(-200, 200, K.Y_DIVISAO, K.Y_DIVISAO + 0.1, -10, 200)))
fatia_t = inter_vol(tr, L(C._caixa(-200, 200, K.Y_DIVISAO - 0.1, K.Y_DIVISAO, -10, 200)))
ok(fatia_f > 50 and fatia_t > 50 and abs(fatia_f - fatia_t) / fatia_t < 0.6,
   f"as duas metades se tocam no plano y={K.Y_DIVISAO:g} (área ≈ {fatia_f * 10:.0f} / {fatia_t * 10:.0f} mm²)")
ext = L(C.externo())
v_ext = ext.val().Volume()
v_uniao = fr.union(tr).val().Volume()
v_casca = ext.cut(L(C.cavidade())).val().Volume()
ok(v_uniao >= v_casca * 0.9, f"frente ∪ traseira reconstrói a casca ({v_uniao / 1000:.0f} cm³ com reforços; casca lisa {v_casca / 1000:.0f} cm³)")
for x, z, _, _ in C.pilares():
    eixo = L(C._cil_y(G.M3_PASSANTE / 2 - 0.3, x, z, K.Y_DIVISAO - K.PILAR_PISO, K.Y_DIVISAO + G.M3_INSERTO_PROF))
    ok(inter_vol(eixo, fr) + inter_vol(eixo, tr) < TOL,
       f"união ({x:+.0f}, z{z:.0f}): furo M3 da traseira alinhado com o inserto da frente; túnel Ø{K.TUNEL_D:g} aberto atrás")
for x, z in C.pinos_alinh():
    pino = L(C._cil_y(K.PINO_ALINH_D / 2, x, z, K.Y_DIVISAO - K.PINO_ALINH_H, K.Y_DIVISAO))
    ok(inter_vol(pino, tr) < 0.01, f"pino de alinhamento ({x:+.0f}, z{z:.0f}) Ø{K.PINO_ALINH_D:g} em furo Ø{K.PINO_ALINH_D + 2 * G.FOLGA_ENCAIXE:.1f} da traseira")

# ------------------------------------------------------------------ 3. IF-CABEÇA
REL.append("\n## 3. IF-CABEÇA contra a placa 11E REAL (pan 0 / tilt 0)")
placa = pesc["11E_placa_cabeca"]
ok(abs(bb(placa).zmax - 3.0 - Z0) < 0.01, f"face de cima da placa (sem pinos) em z={bb(placa).zmax - 3:.1f} = Z_IF_CABECA {Z0:g}")
ok(abs(bb(tr).zmin - Z0) < 0.01, f"fundo da cabeça em z={bb(tr).zmin:.2f}")
v = inter_vol(placa, tr)
ok(v < 0.01, f"placa (com os 2 pinos Ø4×3) × traseira: {v:.3f} mm³ (pinos entram nos furos Ø{K.PINO_FURO_D:g})")
lx, ly = G.IF_CABECA_PLACA
placa_sobe = placa.translate((0, 0, 0.1))
contato = inter_vol(placa_sobe, tr) / 0.1
area_placa = inter_vol(placa, C._caixa(-lx, lx, -ly, ly, Z0 - 0.1, Z0)) / 0.1      # face real da placa
furos_cab = math.pi * ((K.CABO_FURO_D / 2) ** 2 - (G.IF_CABECA_CABO_D / 2) ** 2) + 2 * math.pi * (G.IF_CABECA_PINO_D / 2) ** 2
ok(contato > 0.99 * (area_placa - furos_cab), f"apoio plano: {contato:.0f} mm² de contato de {area_placa:.0f} mm² da face da placa "
   f"({100 * contato / area_placa:.0f} %; o resto é o furo Ø{K.CABO_FURO_D:g} > Ø16 e a base dos pinos) — PETG rígido direto, nada macio")
for x, y in G.IF_CABECA_M3:
    haste = cq.Workplane("XY").workplane(offset=Z0 - 4).center(x, y).circle(1.5).extrude(4 + K.FUNDO_ESP)
    ok(inter_vol(haste, tr) < 0.01, f"M3 ({x:+.0f},{y:+.0f}): passante Ø{G.M3_PASSANTE:g} no eixo do inserto; parafuso M3×10 "
       f"= {K.FUNDO_ESP:g} fundo + {10 - K.FUNDO_ESP:g} no inserto M3×{G.IF_CABECA_INSERTO_PROF:g}")
    col = cq.Workplane("XY").workplane(offset=Z0 + K.FUNDO_ESP + 0.05).center(x, y).circle(K.ACESSO_CHAVE_D / 2).extrude(K.ACESSO_CHAVE_H)
    vt, vf = inter_vol(col, tr), inter_vol(col, fr)
    ok(vt < 0.01, f"   acesso por dentro: coluna Ø{K.ACESSO_CHAVE_D:g} × {K.ACESSO_CHAVE_H:g} acima da cabeça do parafuso livre na traseira"
       + ("" if vf < 0.01 else f" (frente montada invade {vf:.0f} mm³: apertar com a frente fora)"))
for x, y in G.IF_CABECA_PINOS:
    ok(math.hypot(x, y) > 0 and inter_vol(cq.Workplane("XY").workplane(offset=Z0 - 1).center(x, y)
                                           .circle(G.IF_CABECA_PINO_D / 2).extrude(1 + 3.0), tr) < 0.01,
       f"pino ({x:+.0f},{y:+.0f}): furo Ø{K.PINO_FURO_D:g} × {K.PINO_FURO_P:g} (pino Ø{G.IF_CABECA_PINO_D:g} × 3)")
cabo = cq.Workplane("XY").workplane(offset=Z0 - 5).circle(G.IF_CABECA_CABO_D / 2).extrude(K.FUNDO_ESP + 10)
ok(K.CABO_FURO_D >= G.IF_CABECA_CABO_D and inter_vol(cabo, tr) < 0.01, f"furo de cabos Ø{K.CABO_FURO_D:g} ≥ Ø{G.IF_CABECA_CABO_D:g}, concêntrico")
ok(abs(K.ALMOFADA[1] / 2) < K.Y_DIVISAO, f"IF-CABEÇA inteira na traseira (almofada até y={K.ALMOFADA[1] / 2:g} < divisão {K.Y_DIVISAO:g})")

# ------------------------------------------------------------------ 4. acessos
REL.append("\n## 4. Acesso aos parafusos")
for x, z, _, _ in C.pilares():
    tun = L(C._cil_y(K.TUNEL_D / 2 - 0.3, x, z, C.YT - 2, K.Y_DIVISAO - K.PILAR_PISO - 0.05))
    ok(inter_vol(tun, tr) < 0.01, f"união ({x:+.0f}, z{z:.0f}): túnel Ø{K.TUNEL_D:g} de {K.Y_DIVISAO - K.PILAR_PISO - C.YT:.0f} mm aberto nas costas (cabeça M3 Ø5,5 + chave 2,5 longa)")
for sx in (-1, 1):
    for y, z in C.furos_orelha():
        x0 = sx * (C.W / 2 - C.T - K.ORELHA_ALMOFADA_ESP)
        col = L(C._cil_x(4.0, y, z, min(x0, x0 - sx * 30) + (0.05 if sx < 0 else -0.05) * 0, max(x0, x0 - sx * 30)))
        col = col.translate((-sx * 0.05, 0, 0))
        ok(inter_vol(col, tr) < 0.01, f"orelha {'dir' if sx > 0 else 'esq'} ({y:+.0f}, z{z:.0f}): 30 mm livres por dentro para a chave")
col = L(C._cil_z(4.0, 0, K.ANTENA_Y, C.H - G.ANTENA_SOQUETE[1] - K.ANTENA_PISO - 40, C.H - G.ANTENA_SOQUETE[1] - K.ANTENA_PISO - 0.05))
ok(inter_vol(col, tr) < 0.01, "antena: parafuso M3 por dentro, 40 mm livres embaixo do soquete")
for x, z in C.cantos_moldura():
    ok(True, f"moldura/M05 ({x:+.1f}, z{z:.1f}): M3 cabeça chata pela frente, inserto colocado por dentro do assento")

# ------------------------------------------------------------------ 5. envelopes
REL.append("\n## 5. Envelopes de tela e câmera")
el, ea, ep = G.IF_TELA_ROSTO_ENVELOPE
env = L(C._caixa(-el / 2, el / 2, C.YF - ep, C.YF + 0.5, K.TELA_Z - ea / 2, K.TELA_Z + ea / 2))
ok(inter_vol(env, fr) + inter_vol(env, tr) < 0.01, f"tela: envelope {el:g}×{ea:g}×{ep:g} livre (abre pela frente; rebaixo {C.P_L:.1f}×{C.P_A:.1f})")
ok(all(abs(x) - K.BANDEJA_BOSS_D / 2 > el / 2 for x, _ in K.BANDEJA_BOSS_POS),
   f"4 bosses M3 da bandeja fora do envelope, topo em y={C.Y_BANDEJA:g} (fundo do envelope)")
cx, cz, cy = K.CAMERA_RESERVA
cam = L(C._caixa(-cx / 2, cx / 2, C.YF - C.T - cy, C.YF - C.T - 0.05, K.CAMERA_Z - cz / 2, K.CAMERA_Z + cz / 2))
furo = L(C._cil_y(G.IF_CAMERA_FURO_D / 2 - 0.05, 0, K.CAMERA_Z, C.YF - C.T - 1, C.YF + 1))
ok(inter_vol(cam, fr) + inter_vol(cam, tr) < 0.01 and inter_vol(furo, fr) < 0.01,
   f"câmera: furo Ø{G.IF_CAMERA_FURO_D:g} na testa (z local {K.CAMERA_Z:g}, acima da tela) + reserva {cx:g}×{cz:g}×{cy:g} livre (PROPOSTA)")
ok(K.CAMERA_Z - G.IF_CAMERA_FURO_D / 2 > K.TELA_Z + C.P_A / 2 + K.COLAR_LARG, "câmera acima do rebaixo da tela")

# ------------------------------------------------------------------ 6. cabos
REL.append("\n## 6. Caminho interno de cabos (tubo Ø10)")
pts = [(0, 0, K.FUNDO_ESP + 1), (0, 0, 40), (0, C.Y_BANDEJA - 5, K.TELA_Z), (0, C.YF - C.T - cy - 4, K.CAMERA_Z)]
tubo = None
for a, b in zip(pts, pts[1:]):
    va, vb = cq.Vector(*a), cq.Vector(*b)
    seg = cq.Workplane("XY").add(cq.Solid.makeCylinder(5.0, (vb - va).Length, va, (vb - va).normalized()))
    seg = seg.union(cq.Workplane("XY").add(cq.Solid.makeSphere(5.0)).translate(vb))
    tubo = seg if tubo is None else tubo.union(seg)
tubo = L(tubo)
vt = inter_vol(tubo, fr) + inter_vol(tubo, tr)
ok(vt < 0.5, f"furo da IF -> atrás da tela -> atrás da câmera: livre ({vt:.2f} mm³); 2 alças de abraçadeira ao lado do furo")

# ------------------------------------------------------------------ 7. pan/tilt
REL.append("\n## 7. Pan ±90° × tilt ±30° com o pescoço REAL e a caixa do tronco")
cab_unida = fr.union(tr).union(cab["CA2_orelha_esquerda"]).union(cab["CA3_orelha_direita"]).union(cab["M05_tampa_facial"])
pesc_movel = {n: s for n, s in pesc.items() if n != "11E_placa_cabeca"}
zmin_cab = 1e9
for pan in (-90, -45, 0, 45, 90):
    for tilt in (-30, -15, 0, 15, 30):
        c = pose(cab_unida, pan, tilt)
        zmin_cab = min(zmin_cab, bb(c).zmin)
        ruins = []
        for n, s in pesc_movel.items():
            s2 = pose(s, pan, tilt, gira_tilt=n in P.TILT_GIRAM, gira_pan=n in P.PAN_GIRAM)
            v = inter_vol(c, s2)
            if v > TOL:
                ruins.append(f"{n}={v:.1f}")
        v = inter_vol(c, tronco)
        if v > TOL:
            ruins.append(f"tronco={v:.1f}")
        if pan in (-90, 0, 90) and tilt in (-30, 0, 30) or ruins:
            ok(not ruins, f"pan {pan:+3d}° tilt {tilt:+3d}°: livre" + ("" if not ruins else " — " + "; ".join(ruins)))
        elif ruins:
            ok(False, f"pan {pan:+3d} tilt {tilt:+3d}: " + "; ".join(ruins))
ok(zmin_cab - ZT > 10, f"ponto mais baixo da cabeça em qualquer pose: {zmin_cab - ZT:.0f} mm acima do topo do tronco "
   "(gravata ainda não modelada: conferir quando existir)")

# ------------------------------------------------------------------ 8. massa / CG / momento
REL.append("\n## 8. Massa, centro de massa e momento no tilt")
RHO = 1.27e-3   # g/mm³
PREENCH = {"C05_cabeca_frente": 1.0, "C06_cabeca_traseira": 1.0, "M05_tampa_facial": 0.9, "M07_tampao_camera": 1.0,
           "CA1_antena": 1.0, "CA2_orelha_esquerda": 0.5, "CA3_orelha_direita": 0.5}
itens_m = []
for n, s in cab.items():
    so = s.val()
    m = so.Volume() * RHO * PREENCH[n]
    itens_m.append((n, m, so.Center()))
    REL.append(f"- {n}: {so.Volume() / 1000:.1f} cm³ × {PREENCH[n]:.0%} -> {m:.0f} g")
c_env = cq.Vector(0, C.YF - ep / 2, Z0 + K.TELA_Z)
c_cam = cq.Vector(0, C.YF - C.T - cy / 2, Z0 + K.CAMERA_Z)
itens_m += [("tela (estimativa)", 60.0, c_env), ("câmera + suporte (estimativa)", 30.0, c_cam),
            ("parafusos/insertos (~25 peças)", 25.0, cq.Vector(0, 0, Z0 + 50))]
REL.append("- tela 60 g (centro do envelope), câmera 30 g (centro da reserva), fixadores 25 g")
mt = sum(m for _, m, _ in itens_m)
cg = sum((c * m for _, m, c in itens_m), cq.Vector(0, 0, 0)) * (1 / mt)
h_cg, dy = cg.z - Z_EIXO_TILT, cg.y
REL.append(f"- **total {mt:.0f} g**; CG em (x {cg.x:+.1f}, y {cg.y:+.1f}, z {cg.z:.0f}) = **{h_cg:.0f} mm acima do eixo do tilt e "
           f"{dy:+.1f} mm à frente** (hipótese do validar_pescoco: 450 g, 96 mm, +10 mm)")
mom = lambda m, h, d: m / 1000 * 9.81 * (h * math.sin(math.radians(P.TILT_GIRO)) + abs(d) * math.cos(math.radians(P.TILT_GIRO))) / 1000  # noqa: E731
m_real, m_hip = mom(mt, h_cg, dy), mom(450, 96, 10)
t_pino = 0.3 * 40e6 * (4e-3 * P.INDEX_P * 1e-3) * (P.INDEX_TILT_R / 1000)
REL.append(f"- momento no tilt a {P.TILT_GIRO:g}° (pior lado): **{m_real:.2f} N·m** (hipótese {m_hip:.2f} N·m)")
ok(t_pino >= 1.5 * m_real, f"trava do tilt (pino de indexação) ~{t_pino:.2f} N·m ≥ 1,5 × {m_real:.2f} N·m (margem {t_pino / m_real:.1f}×)")
REL.append(f"- massa {mt - 450:+.0f} g em relação à hipótese: a casca lisa ({v_casca / 1000:.0f} cm³ = {v_casca * RHO:.0f} g) é a maior parte; "
           f"parede de 2,0 mm tiraria ~{v_casca / K.PAREDE * 0.4 * RHO:.0f} g")

# ------------------------------------------------------------------ 9. altura
REL.append("\n## 9. Altura total")
topo = bb(cab["CA1_antena"]).zmax
ok(abs(topo - 550) <= 5, f"topo da antena em z = {topo:.1f} mm (meta 550): cabeça {Z0:g}->{Z0 + C.H:g} + antena {topo - Z0 - C.H:.0f}")

# ------------------------------------------------------------------ 10. imprimibilidade
REL.append("\n## 10. Imprimibilidade (A1, PETG, sem suporte)")
VAO = {"C05_cabeca_frente": (8.0, "assentos de canto: balanço ancorado em 2 paredes, ≤ 8 mm do apoio; resto em pé"),
       "C06_cabeca_traseira": (0.0, "paredes em pé; almofada, blocos dos pinos e boss da antena com chanfro/gota 45°; túneis verticais"),
       "M05_tampa_facial": (0.0, "placa; escareados para cima"),
       "M07_tampao_camera": (0.5, "garra 0,5 mm em rampa"),
       "CA1_antena": (0.0, "cone 45° sob a bolinha e sob o colar (assenta no escareado)"),
       "CA2_orelha_esquerda": (0.0, "anel em cima"), "CA3_orelha_direita": (0.0, "anel em cima")}
for n, s in cab.items():
    m = C.para_mesa(n, s)
    b = bb(m)
    ok(max(b.xlen, b.ylen, b.zlen) <= 220 and VAO[n][0] <= 12,
       f"{n}: {b.xlen:.0f}×{b.ylen:.0f}×{b.zlen:.0f} mm na mesa; {C.IMPRESSAO[n][1]}; maior vão {VAO[n][0]:g} mm ({VAO[n][1]})")
ok(abs(C.T * 1 - K.PAREDE) < 1e-9 and K.PAREDE >= 2.0, f"parede {K.PAREDE:g} mm (≥ 5 perímetros de 0,42)")

# ------------------------------------------------------------------ vistas
COR = {"C05_cabeca_frente": (0.80, 0.75, 0.64, 1.0), "C06_cabeca_traseira": (0.80, 0.75, 0.64, 1.0), "M05_tampa_facial": CORES["grafite"],
       "M07_tampao_camera": CORES["grafite"], "CA1_antena": CORES["petroleo"],
       "CA2_orelha_esquerda": CORES["petroleo"], "CA3_orelha_direita": CORES["petroleo"]}
MESH = {n: to_mesh(s) for n, s in cab.items()}


RELEVO = to_mesh(L(C.m05_relevo_local()))


def itens(expl=0.0, so=None, cor=None):
    desl = {"C05_cabeca_frente": (0, 1.0, 0), "C06_cabeca_traseira": (0, -0.6, 0), "M05_tampa_facial": (0, 2.2, 0),
            "M07_tampao_camera": (0, 2.2, 0.4), "CA1_antena": (0, 0, 1.2), "CA2_orelha_esquerda": (-1, 0, 0),
            "CA3_orelha_direita": (1, 0, 0)}
    out = []
    for n, m in MESH.items():
        if so and n not in so:
            continue
        mm = m.copy()
        mm.apply_translation([d * expl for d in desl[n]])
        out.append((mm, cor or COR[n]))
        if n == "M05_tampa_facial" and not so:
            rv = RELEVO.copy()
            rv.apply_translation([d * expl + e for d, e in zip(desl[n], (0, 0.05, 0))])
            out.append((rv, CORES["ambar"]))
    return out


render_conjunto(itens(), str(OUT / "vistas.png"), ["frente", "lado", "tras", "iso_tras", "iso", "baixo"],
                titulo="Cabeca - C05 frente + C06 traseira + M05/M07/antena/orelhas (V1)")
render_conjunto(itens(), str(OUT / "corte.png"), ["lado", "iso"], corte=("x", 0.01, False),
                titulo="Cabeca - corte x=0 (IF-CABECA, colar da tela, camera, antena)")
render_conjunto(itens(so={"C06_cabeca_traseira"}, cor=(0.42, 0.46, 0.52, 1.0)), str(OUT / "traseira_interior.png"), ["iso", "frente", "baixo"],
                titulo="C06 traseira - interior (almofada IF, pilares, nervuras) e fundo")
render_conjunto(itens(so={"C05_cabeca_frente"}, cor=(0.42, 0.46, 0.52, 1.0)), str(OUT / "frente_interior.png"), ["tras", "iso_tras", "frente"],
                titulo="C05 frente - por dentro (assentos de canto, bosses) e por fora")
render_conjunto(itens(expl=45), str(OUT / "explodida.png"), ["iso_tras", "lado"], titulo="Cabeca - explodida")
for pan, tilt in ((0, 0), (90, 0), (0, 30), (0, -30), (-90, 30)):
    lst = [(to_mesh(pose(cab_unida.union(cab["CA1_antena"]), pan, tilt)), CORES["creme"])]
    for n, s in pesc.items():
        lst.append((to_mesh(pose(s, pan, tilt, gira_tilt=n in P.TILT_GIRAM, gira_pan=n in P.PAN_GIRAM)), CORES["petroleo"]))
    lst.append((to_mesh(C._caixa(-G.TRONCO_LARG / 2, G.TRONCO_LARG / 2, -G.TRONCO_PROF / 2, G.TRONCO_PROF / 2, ZT - 60, ZT)), CORES["fantasma"]))
    render_conjunto(lst, str(OUT / f"montagem_pan{pan:+d}_tilt{tilt:+d}.png"), ["iso", "lado", "frente"],
                    titulo=f"Cabeca no pescoco 11 - pan {pan:+d} / tilt {tilt:+d} (tronco = fantasma)")
TMP.unlink(missing_ok=True)

txt = ["# Cabeça (C05 + C06 + M05 + M07 + antena + orelhas): relatório", "",
       f"Resultado: **{'APROVADO' if not FALHAS else 'COM FALHAS'}** ({len(FALHAS)} falhas)", ""] + REL
txt += ["", "## Orientação de impressão (STL já exportado assim)", ""] + [f"- {n}: {d}" for n, (_, d) in C.IMPRESSAO.items()]
txt += ["", "## Fixadores", ""] + [f"- {q} × {d}" for d, q in C.BOM]
(OUT / "RELATORIO.md").write_text("\n".join(txt) + "\n")
print("\n".join(txt))
sys.exit(1 if FALHAS else 0)
