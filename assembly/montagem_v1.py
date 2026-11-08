"""Montagem virtual do robô completo (V1 estática) + envelopes da V2.

Junta TODAS as peças no referencial do robô, checa colisão entre grupos vizinhos, soma massa,
acha o centro de massa e avalia o tombamento (pés de borracha como polígono de apoio), com a
bandeja vazia e carregada. Gera vistas e a lista de fixadores agregada.

    ~/.venvs/cadquery/bin/python assembly/montagem_v1.py [--rapido]
Saídas: exports/montagem/ (RELATORIO.md, PNGs, STEP do conjunto)
"""
import math
import sys
from pathlib import Path

import cadquery as cq
import trimesh

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from parameters import globais as G  # noqa: E402
from parameters import tronco as TP  # noqa: E402
from base import base_inferior as B1, base_superior as B2  # noqa: E402
from cintura import cintura_manual as C  # noqa: E402
from tronco import tronco_traseiro as T3, tronco_frontal as T4  # noqa: E402
from ombro import ombro_manual as O  # noqa: E402
from braco import braco as BR, maos as MA, bandeja as BJ  # noqa: E402
from pescoco import pescoco_manual as P  # noqa: E402
from cabeca import cabeca as CB  # noqa: E402
from acessorios import gravata as GV  # noqa: E402
from tools.render import CORES, render_conjunto  # noqa: E402

OUT = RAIZ / "exports" / "montagem"
OUT.mkdir(parents=True, exist_ok=True)
TMP = OUT / "_tmp.stl"
RHO_PETG = 1.27e-3            # g/mm³
FATOR_IMPRESSO = 0.55         # 4 paredes + 15–40% de preenchimento ≈ 55% do maciço (estimativa)
PES = B1.PES                  # polígono de apoio
ACO_G = 636.0                 # placa de contrapeso (CAD da base)
CARGA_BANDEJA_G = 300.0
REL, FALHAS = [], []


def ok(c, m):
    REL.append(("OK  " if c else "FALHA ") + m)
    if not c:
        FALHAS.append(m)


def pose_pescoco(wp, pan, tilt, tilt_tambem=True):
    zt = G.Z_TOPO_TRONCO + P.Z_TILT
    if tilt_tambem:
        wp = wp.rotate((0, 0, zt), (1, 0, zt), tilt)
    return wp.rotate((0, 0, 0), (0, 0, 1), pan)


def montar(cintura=0.0, ombro_esq=0.0, ombro_dir=0.0, pan=0.0, tilt=0.0):
    """{grupo: {nome: (wp, cor)}} no referencial do robô."""
    g = {}
    g["base"] = {"01": (B1.modelo(), "petroleo"), "02": (B2.modelo(), "creme"),
                 "02L_difusor": (B2.difusor_cego(), "ambar"), "aco": (B1.contrapeso(), "aco")}
    for i in range(4):
        g["base"][f"01P_{i}"] = (B1.presilha(i), "petroleo")
    gc = {}
    for n, f in C.PECAS.items():
        w = f().translate((0, 0, G.Z_TOPO_P02))
        if n in C.GIRAM:
            w = w.rotate((0, 0, 0), (0, 0, 1), cintura)
        gc[n] = (w, "grafite" if n in ("08A_flange_inferior", "08B_flange_superior") else "creme")
    g["cintura"] = gc
    gira_tronco = lambda w: w.rotate((0, 0, 0), (0, 0, 1), cintura)  # noqa: E731
    g["tronco"] = {"03A": (gira_tronco(T3.traseira(sacrificio=False)), "creme"),
                   "03B": (gira_tronco(T3.painel_traseiro()), "petroleo"),
                   "04A": (gira_tronco(T4.frontal(sacrificio=False)), "creme"),
                   "04E_M06": (gira_tronco(T4.painel_m06()), "grafite"),
                   "04D": (gira_tronco(T4.tampa()), "creme"),
                   "gravata": (gira_tronco(GV.gravata()), "petroleo")}
    for lado, ang in (("esquerdo", ombro_esq), ("direito", ombro_dir)):
        num = O.NUMERO[lado]
        d = {}
        for k, s in O.construir(lado).items():
            w = O.girar(s, ang, lado) if k in O.GIRAM else s
            d[num + k] = (gira_tronco(O.posicionar(w, lado)), "creme" if k == "B_rotor_braco" else "grafite")
        conj = {}
        for k, s in BR.construir(lado).items():
            conj[BR.NUMERO[lado] + k] = (s, "petroleo" if k == "F_friso" else ("grafite" if k == "C_anel_punho" else "creme"))
        if lado == "esquerdo":
            conj["05D_adaptador"] = (BR.no_punho(MA.adaptador_v1(), lado), "creme")
            conj["06B_cubo"] = (BR.no_punho(BJ.no_adaptador(BJ.cubo()), lado), "grafite")
            conj["06A_bandeja"] = (BR.no_punho(BJ.no_adaptador(BJ.bandeja()), lado), "grafite")
        else:
            conj["07E_luva"] = (BR.no_punho(MA.luva(), lado), "grafite")
        for k, (s, cor) in conj.items():
            d[k] = (gira_tronco(O.posicionar(O.girar(s, ang, lado), lado)), cor)
        g["braco_" + lado] = d
    gp = {}
    for n, f in P.PECAS.items():
        w = f().translate((0, 0, G.Z_TOPO_TRONCO))
        w = pose_pescoco(w, pan, tilt, n in P.TILT_GIRAM) if n in P.PAN_GIRAM else w
        gp[n] = (gira_tronco(w), "petroleo" if n in ("11C_anel_retencao", "11E_placa_cabeca", "11F_manipulo_pan", "11G_manipulo_tilt") else "creme")
    g["pescoco"] = gp
    gh = {}
    cor_cab = {"C05_cabeca_frente": "creme", "C06_cabeca_traseira": "creme", "M05_tampa_facial": "grafite",
               "M07_tampao_camera": "grafite", "CA1_antena": "grafite", "CA2_orelha_esquerda": "petroleo", "CA3_orelha_direita": "petroleo"}
    for n, f in CB.PECAS.items():
        gh[n] = (gira_tronco(pose_pescoco(f(), pan, tilt)), cor_cab[n])
    g["cabeca"] = gh
    return g


def vol(wp):
    return sum(s.Volume() for s in wp.solids().vals())


def centro(wp):
    tot, cx, cy, cz = 0.0, 0.0, 0.0, 0.0
    for s in wp.solids().vals():
        v = s.Volume()
        c = s.Center()
        tot += v; cx += c.x * v; cy += c.y * v; cz += c.z * v
    return tot, (cx / tot, cy / tot, cz / tot)


def massa_cg(grupos, carga_bandeja=0.0):
    m_tot, mx, my, mz = 0.0, 0.0, 0.0, 0.0
    linhas = []
    for gn, d in grupos.items():
        mg = 0.0
        for n, (w, _) in d.items():
            v, (x, y, z) = centro(w)
            m = ACO_G if n == "aco" else v * RHO_PETG * FATOR_IMPRESSO
            mg += m; m_tot += m; mx += m * x; my += m * y; mz += m * z
        linhas.append(f"- {gn}: {mg:.0f} g")
    if carga_bandeja:
        _, (x, y, z) = centro(grupos["braco_esquerdo"]["06A_bandeja"][0])
        m_tot += carga_bandeja; mx += carga_bandeja * x; my += carga_bandeja * y; mz += carga_bandeja * (z + 30)
    return m_tot, (mx / m_tot, my / m_tot, mz / m_tot), linhas


def margem_apoio(cg):
    """Menor distância do CG (projeção) até a borda do retângulo dos pés (positiva = dentro)."""
    xs = [p[0] for p in PES]; ys = [p[1] for p in PES]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    return min(cg[0] - x0, x1 - cg[0], cg[1] - y0, y1 - cg[1])


def to_mesh(wp):
    cq.exporters.export(wp, str(TMP), tolerance=0.1, angularTolerance=0.3)
    return trimesh.load(str(TMP))


if __name__ == "__main__":
    rapido = "--rapido" in sys.argv
    g = montar()

    REL.append("## 1. Colisões entre grupos (pose de repouso: tudo em 0°)")
    VIZ = [("base", "cintura"), ("cintura", "tronco"), ("tronco", "braco_esquerdo"), ("tronco", "braco_direito"),
           ("base", "braco_esquerdo"), ("base", "braco_direito"), ("tronco", "pescoco"), ("pescoco", "cabeca"),
           ("tronco", "cabeca"), ("braco_esquerdo", "cabeca"), ("braco_direito", "cabeca"), ("cintura", "braco_esquerdo"),
           ("cintura", "braco_direito")]
    for a, b in VIZ:
        ruins = []
        for na, (wa, _) in g[a].items():
            ba = wa.val().BoundingBox()
            for nb, (wb, _) in g[b].items():
                bb = wb.val().BoundingBox()
                if ba.xmax < bb.xmin or bb.xmax < ba.xmin or ba.ymax < bb.ymin or bb.ymax < ba.ymin or ba.zmax < bb.zmin or bb.zmax < ba.zmin:
                    continue
                try:
                    v = wa.intersect(wb).val().Volume()
                except Exception:
                    v = 0.0
                if v > 0.5:
                    ruins.append(f"{na}×{nb}={v:.1f} mm³")
        ok(not ruins, f"{a} × {b}: " + ("livre" if not ruins else "; ".join(ruins)))

    REL.append("\n## 2. Massa e centro de massa (PETG impresso ≈ 55% do maciço; aço 636 g)")
    for carga, titulo in ((0.0, "bandeja vazia"), (CARGA_BANDEJA_G, f"bandeja com {CARGA_BANDEJA_G:.0f} g")):
        m, cg, linhas = massa_cg(g, carga)
        if not carga:
            REL.extend(linhas)
        mar = margem_apoio(cg)
        ang = math.degrees(math.atan2(mar, cg[2]))
        REL.append(f"- {titulo}: total {m:.0f} g, CG em x={cg[0]:+.1f}, y={cg[1]:+.1f}, z={cg[2]:.0f} mm")
        ok(mar > 10, f"{titulo}: CG {mar:.1f} mm dentro do apoio dos pés; tomba com inclinação de ~{ang:.1f}°")
    g60 = montar(ombro_esq=60.0)
    m, cg, _ = massa_cg(g60, CARGA_BANDEJA_G)
    mar = margem_apoio(cg)
    ok(mar > 10, f"braço esquerdo a +60° e bandeja com 300 g: CG {mar:.1f} mm dentro do apoio "
       f"(tomba com ~{math.degrees(math.atan2(mar, cg[2])):.1f}°)")

    zmax = max(w.val().BoundingBox().zmax for d in g.values() for w, _ in d.values())
    xmax = max(abs(v) for d in g.values() for w, _ in d.values() for v in (w.val().BoundingBox().xmin, w.val().BoundingBox().xmax))
    REL.append(f"\n## 3. Dimensões gerais\n- altura total {zmax:.0f} mm (alvo 550); largura com braços {2 * xmax:.0f} mm")
    ok(abs(zmax - 550) <= 15, f"altura {zmax:.0f} mm dentro de 550 ± 15")

    # ---------- vistas ----------
    itens = [(to_mesh(w), CORES[c]) for d in g.values() for w, c in d.values()]
    render_conjunto(itens, str(OUT / "v1_vistas.png"), ["iso", "frente", "lado", "tras"], titulo="Robo Mordomo V1 - montagem completa (repouso)")
    if not rapido:
        gp = montar(cintura=30, ombro_esq=30, ombro_dir=90, pan=-30, tilt=-10)
        itens2 = [(to_mesh(w), CORES[c]) for d in gp.values() for w, c in d.values()]
        render_conjunto(itens2, str(OUT / "v1_pose_servico.png"), ["iso", "frente"],
                        titulo="V1 posada a mao: cintura +30, bandeja +30, aceno +90, cabeca pan -30 tilt -10")
        # envelopes da V2 (o que vai entrar sem reimprimir carcaça)
        env = []
        env.append(cq.Workplane("XY").workplane(offset=G.Z_TOPO_P02).circle(G.IF_CINTURA_ENVELOPE_D / 2).extrude(G.IF_CINTURA_ALTURA))
        ex, ey, ez = G.IF_PESCOCO_ENVELOPE
        env.append(cq.Workplane("XY").workplane(offset=G.Z_TOPO_TRONCO).rect(ex, ey).extrude(ez))
        lx, lz, ly = G.IF_TELA_PEITO_ENVELOPE
        env.append(cq.Workplane("XY").box(lx, ly, lz).translate((0, G.TRONCO_PROF / 2 - ly / 2 - 3, G.IF_TELA_PEITO_Z)))
        rx, rz, ry = G.IF_TELA_ROSTO_ENVELOPE
        env.append(cq.Workplane("XY").box(rx, ry, rz).translate((0, G.CABECA[1] / 2 - ry / 2 - 3, G.Z_IF_CABECA + 62)))
        try:
            x0, x1, y0, y1, z0, z1 = T3.ENV_OMBRO
            for sx in (-1, 1):
                xa, xb = sorted((sx * x0, sx * x1))
                env.append(cq.Workplane("XY").box(xb - xa, y1 - y0, z1 - z0).translate(((xa + xb) / 2, (y0 + y1) / 2, (z0 + z1) / 2)))
        except Exception:
            pass
        itens_env = [(m_, (c[0], c[1], c[2], 0.25)) for m_, c in itens] + [(to_mesh(e), CORES["ambar"]) for e in env]
        render_conjunto(itens_env, str(OUT / "v2_envelopes.png"), ["iso", "lado"],
                        titulo="V2: envelopes reservados (ambar) dentro das carcacas da V1 - cintura, pescoco, telas, servos dos ombros")
    TMP.unlink(missing_ok=True)

    # ---------- fixadores agregados ----------
    REL.append("\n## 4. Fixadores e comprados por módulo (detalhe nos RELATORIO de cada peça)")
    for nome, mod, mult in (("cintura 08", C, 1), ("ombros 09+10", O, 2), ("pescoço 11", P, 1), ("tronco 04", T4, 1),
                            ("tronco 03", T3, 1)):
        bom = getattr(mod, "BOM", None)
        if bom:
            REL.append(f"- {nome}: " + "; ".join(f"{q * mult}× {d}" for d, q in bom))

    txt = ["# Montagem V1 — robô completo", "",
           f"Resultado: **{'APROVADO' if not FALHAS else 'COM FALHAS'}** ({len(FALHAS)} falhas)", ""] + REL
    (OUT / "RELATORIO.md").write_text("\n".join(txt) + "\n")
    print("\n".join(txt))
    sys.exit(1 if FALHAS else 0)
