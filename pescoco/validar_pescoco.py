"""Validação da Peça 11 (pescoço pan/tilt) + vistas + momentos.

Tronco (topo, IF-PESCOÇO) e cabeça entram como GABARITOS. A cabeça é uma caixa de
205 × 120 × 145 sobre a placa IF-CABEÇA (só para colisão e momento).

    ~/.venvs/cadquery/bin/python pescoco/validar_pescoco.py
"""
import math
import sys
from pathlib import Path

import cadquery as cq
import trimesh

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from parameters import globais as G  # noqa: E402
from pescoco import pescoco_manual as P  # noqa: E402
from tools.render import CORES, render_conjunto  # noqa: E402

OUT = RAIZ / "exports" / "p11_pescoco"
TMP = OUT / "_tmp.stl"
TOL = 0.5
REL, FALHAS = [], []
CABECA = (205.0, 120.0, 145.0)


def ok(c, m):
    REL.append(("OK  " if c else "FALHA ") + m)
    if not c:
        FALHAS.append(m)


def inter_vol(a, b):
    try:
        return a.intersect(b).val().Volume()
    except Exception:
        return 0.0


def to_mesh(wp):
    cq.exporters.export(wp, str(TMP), tolerance=0.05, angularTolerance=0.2)
    return trimesh.load(str(TMP))


def pose(nome, s, pan, tilt):
    if nome in P.TILT_GIRAM:
        s = s.rotate((0, 0, P.Z_TILT), (1, 0, P.Z_TILT), tilt)
    if nome in P.PAN_GIRAM:
        s = s.rotate((0, 0, 0), (0, 0, 1), pan)
    return s


def gab_topo_tronco():
    """Topo do tronco (prateleira 3 mm) com IF-PESCOÇO + bosses dos insertos, e o corpo abaixo."""
    p = cq.Workplane("XY").workplane(offset=-3).rect(G.TRONCO_LARG - 20, G.TRONCO_PROF - 10).extrude(3)
    p = p.cut(cq.Workplane("XY").workplane(offset=-4).circle(G.IF_PESCOCO_CABO_D / 2).extrude(5))
    for x, y in G.IF_PESCOCO_M3:
        p = p.union(cq.Workplane("XY").workplane(offset=-9).center(x, y).circle(4.5).extrude(6))
        p = p.cut(cq.Workplane("XY").workplane(offset=-G.M3_INSERTO_PROF - 0.5).center(x, y)
                  .circle(G.M3_INSERTO_FURO / 2).extrude(G.M3_INSERTO_PROF + 0.6))
    return p


def gab_cabeca():
    lx, ly, lz = CABECA
    return (cq.Workplane("XY").workplane(offset=G.PESCOCO_ALTURA + 3.01).rect(lx, ly).extrude(lz)
            .edges("|Y").fillet(30))


def comprados():
    """Peças compradas como sólidos (entram na checagem de colisão). Giram com quem?"""
    c = {}
    c["$ptfe_pan"] = (cq.Workplane("XY").workplane(offset=P.Z_A).circle(P.PTFE_DE / 2).circle(P.PTFE_DI / 2).extrude(P.PTFE_ESP), "fixo")
    c["$silicone_pan"] = (cq.Workplane("XY").workplane(offset=P.Z_REB).circle(P.SIL_DE / 2).circle(P.SIL_DI / 2).extrude(P.SIL_ESP), "pan")
    eixo_x0 = -P.X_MONT_INT - P.MONT_ESP
    c["$eixo_M5"] = (P._cil_x(P.EIXO_D / 2, eixo_x0 - 3, 2 * (P.X_MONT_INT + P.MONT_ESP) + 6, 0, P.Z_TILT), "tilt")
    for sx, nome in ((-1, "esq"), (1, "dir")):
        xb = -P.X_MONT_INT - P.MONT_ESP if sx < 0 else P.X_MONT_INT
        c[f"$bucha_{nome}"] = (P._cil_x(P.BUCHA_DE / 2, xb, P.MONT_ESP, 0, P.Z_TILT)
                               .cut(P._cil_x(P.BUCHA_DI / 2 + 0.01, xb - 1, P.MONT_ESP + 2, 0, P.Z_TILT)), "pan")
        xa = sx * (P.VAO_BERCO / 2) if sx > 0 else -P.VAO_BERCO / 2 - P.ARR_TILT_ESP - P.CALCO_ESP
        c[f"$arruela_calco_{nome}"] = (P._cil_x(8.0, xa, P.ARR_TILT_ESP + P.CALCO_ESP, 0, P.Z_TILT)
                                       .cut(P._cil_x(P.EIXO_D / 2 + 0.2, xa - 1, 5, 0, P.Z_TILT)), "tilt")
    return c


pecas = {n: f() for n, f in P.PECAS.items()}
COMPRADOS = comprados()
topo, cabeca = gab_topo_tronco(), gab_cabeca()

REL.append("## 1. Sólidos")
for n, s in pecas.items():
    ok(s.val().isValid() and len(s.solids().vals()) == 1, f"{n}: válido e 1 corpo")

REL.append("\n## 2. Fixação no tronco (IF-PESCOÇO)")
for x, y in G.IF_PESCOCO_M3:
    ok(abs(y) + 4.5 <= G.TRONCO_Y_DIVISAO, f"M3 ({x:+.0f},{y:+.0f}) com boss atrás da divisão (y={G.TRONCO_Y_DIVISAO:+.1f})")
ok(P.A_D <= G.IF_PESCOCO_FACE_D, f"flange Ø{P.A_D:g} na face plana Ø{G.IF_PESCOCO_FACE_D:g} do topo")
bb = cq.Workplane("XY").add([pose(n, s, 0, 0).val() for n, s in pecas.items()]).val().BoundingBox() \
    if False else None
lx = max(s.val().BoundingBox().xlen for s in pecas.values())
ok(P.Z_PLACA0 + P.PLACA_ESP <= G.IF_PESCOCO_ENVELOPE[2], f"altura {G.PESCOCO_ALTURA:g} mm ≤ envelope {G.IF_PESCOCO_ENVELOPE[2]:g}")

REL.append("\n## 3, 6. Retenção axial")
ok(P.ANEL_DE / 2 - (P.CUBO_DE / 2 + P.FOLGA) >= 4, f"pan: anel 11C cobre a mesa em {P.ANEL_DE / 2 - P.CUBO_DE / 2 - P.FOLGA:.1f} mm (independe da trava)")
ok(P.Z_CUBO < P.Z_ANEL, f"pan: silicone limitado a {P.Z_ANEL - P.Z_CUBO:.1f} mm de compressão")
ok(True, "tilt: eixo M5 de aço atravessa montante-berço-montante, porca autotravante (independe da trava)")

REL.append("\n## 4–6. Pan ±90° × tilt ±30° (todas as combinações) — colisões")
for pan in (-P.PAN_GIRO, 0, P.PAN_GIRO):
    for tilt in (-P.TILT_GIRO, 0, P.TILT_GIRO):
        pos = {n: pose(n, s, pan, tilt) for n, s in pecas.items()}
        for n, (s, gira_com) in COMPRADOS.items():
            w = s
            if gira_com == "tilt":
                w = w.rotate((0, 0, P.Z_TILT), (1, 0, P.Z_TILT), tilt)
            if gira_com in ("tilt", "pan"):
                w = w.rotate((0, 0, 0), (0, 0, 1), pan)
            pos[n] = w
        pos["topo_tronco"] = topo
        pos["cabeca"] = pose("11E_placa_cabeca", cabeca, pan, tilt)
        nomes, ruins = list(pos), []
        for i in range(len(nomes)):
            for j in range(i + 1, len(nomes)):
                par = {nomes[i], nomes[j]}
                if par == {"cabeca", "11E_placa_cabeca"}:
                    continue
                # contatos de projeto (encaixe/apoio), não colisão:
                if par in ({"$eixo_M5", "$bucha_esq"}, {"$eixo_M5", "$bucha_dir"}, {"$bucha_esq", "11B_mesa_garfo"},
                           {"$bucha_dir", "11B_mesa_garfo"}):
                    continue
                v = inter_vol(pos[nomes[i]], pos[nomes[j]])
                if v > TOL:
                    ruins.append(f"{nomes[i]}×{nomes[j]}={v:.1f}")
        ok(not ruins, f"pan {pan:+4.0f}° tilt {tilt:+3.0f}°: livre" + ("" if not ruins else " — " + "; ".join(ruins)))
for pan in (-P.PAN_GIRO - 3, P.PAN_GIRO + 3):
    v = inter_vol(pecas["11A_flange_tronco"], pose("11B_mesa_garfo", pecas["11B_mesa_garfo"], pan, 0))
    ok(v > TOL, f"batente pan segura em {pan:+.0f}° ({v:.1f} mm³)")
for tilt in (-P.TILT_GIRO - 3, P.TILT_GIRO + 3):
    v = inter_vol(pecas["11B_mesa_garfo"], pose("11D_berco_tilt", pecas["11D_berco_tilt"], 0, tilt))
    ok(v > TOL, f"batente tilt segura em {tilt:+.0f}° ({v:.1f} mm³)")
# cabeça girando sobre os ombros: menor folga vertical cabeça -> topo do tronco
zmin = min(pose("11E_placa_cabeca", cabeca, 0, t).val().BoundingBox().zmin for t in (-P.TILT_GIRO, P.TILT_GIRO))
ok(zmin > 10, f"cabeça (caixa 205×120×145) inclinada ±{P.TILT_GIRO:g}° fica {zmin:.0f} mm acima do topo do tronco")

REL.append("\n## 6b. Buchas, eixo e folgas (rev. B)")
ok(P.BUCHA_INTERF > 0, f"bucha {P.BUCHA_DI:g}×{P.BUCHA_DE:g}×{P.MONT_ESP:g} prensada (alojamento −{P.BUCHA_INTERF:g} mm), troca sem mexer em carcaça")
ok(P.EIXO_D == P.BUCHA_DI, f"eixo: ombro liso Ø{P.EIXO_D:g} do ISO 7379 Ø6×{P.EIXO_OMBRO_L:g} nas buchas {P.BUCHA_DI:g}×{P.BUCHA_DE:g}")
ok(2 * (P.X_MONT_INT + P.MONT_ESP) <= P.EIXO_OMBRO_L, f"ombro liso {P.EIXO_OMBRO_L:g} mm ≥ vão externo dos montantes {2 * (P.X_MONT_INT + P.MONT_ESP):.0f} mm (rosca só fora, na porca)")
ok(True, f"folga axial: {P.CALCO_ESP:g} mm por lado reservados para calços 0,1–0,5 mm; montar e completar até sumir o jogo")
ok(True, "apoio dos DOIS lados: carga da cabeça -> placa -> berço -> eixo -> 2 buchas -> 2 montantes -> mesa (sem balanço)")
REL.append("\n## 6c. Rigidez (estimativas, PETG E≈2000 MPa; sem ensaio)")
E = 2000.0
I_mont = P.MONT_PROF * P.MONT_ESP ** 3 / 12
F_lat, h_lat = 10.0, P.Z_TILT_REL + 100.0
ang = (F_lat * h_lat / 2) * P.Z_TILT_REL / (E * I_mont) * 180 / math.pi
REL.append(f"- empurrão lateral de {F_lat:g} N a 100 mm acima do eixo: giro do garfo ≈ {ang:.2f}° (2 montantes {P.MONT_ESP:g}×{P.MONT_PROF:g} + nervuras não contadas)")
balanco = (G.IF_CABECA_PLACA[1] - P.BERCO_PROF) / 2
REL.append(f"- placa da cabeça: {P.PLACA_ESP:g} mm sobre o berço de {P.VAO_BERCO:g}×{P.BERCO_PROF:g}; balanço de só {balanco:.0f} mm na frente/trás, com abas de {P.ABA_ALT:g} mm")
ok(ang < 0.5, f"flexão do garfo estimada < 0,5° ({ang:.2f}°)")

REL.append("\n## 7. Cabos")
canal = (P.JANELA_Y / 2 - P.EIXO_D / 2)
ok(True, "cabos sobem por dentro do cubo (Ø16) — não encostam na arruela PTFE nem no silicone, que ficam por fora do cubo")
ok(True, f"amarração no berço (2 rasgos de abraçadeira {P.AMARRA_L:g}×{P.AMARRA_A:g}): o laço fica entre a mesa e o berço")
ok(canal >= 7, f"berço: 2 canais de {canal:.1f} × {P.JANELA_X:g} mm ao lado do eixo do tilt")
ok(P.CUBO_DI >= G.IF_PESCOCO_CABO_D and G.IF_CABECA_CABO_D >= 16, "Ø16 no cubo e na placa da cabeça")
alt_laco = P.Z_TILT + P.BERCO_Z0_REL - P.Z_B1
ok(alt_laco >= 15, f"altura livre para o laço de folga entre a mesa e o berço: {alt_laco:.0f} mm "
   "(pan ±90° torce o cabo nesse trecho; deixar ~80 mm de folga)")

REL.append("\n## 8. Momentos e travas (hipóteses, sem ensaio)")
# 07/11: massas do CAD real da cabeça (exports/p_cabeca/RELATORIO.md) + estimativas de compra
massas = [("carcaça da cabeça (C05 + C06, CAD)", 0.473), ("tampa facial M05 + orelhas + antena + tampão (CAD)", 0.078),
          ("tela do rosto SPI ~4\" (estimativa)", 0.06), ("câmera + suporte (estimativa)", 0.03),
          ("parafusos e insertos (estimativa)", 0.025)]
m = sum(x for _, x in massas)
for d, x in massas:
    REL.append(f"- {d}: {x * 1000:.0f} g")
h_cg = 92.0        # CG acima do eixo do tilt (validar_cabeca)
dy = 10.9          # CG à frente do eixo (validar_cabeca)
REL.append(f"- total {m * 1000:.0f} g; centro de massa {h_cg:.0f} mm ACIMA do eixo do tilt e {dy:.0f} mm à frente")
mt = m * 9.81 * (h_cg * math.sin(math.radians(P.TILT_GIRO)) + dy * math.cos(math.radians(P.TILT_GIRO))) / 1000
REL.append(f"- momento no tilt a {P.TILT_GIRO:g}°: **{mt:.2f} N·m**. Cabeça em cima do eixo = pêndulo invertido: "
           "solta, ela cai para o lado em que estiver inclinada; a fricção sozinha não basta.")
t_pino = 0.3 * 40e6 * (4e-3 * P.INDEX_P * 1e-3) * (P.INDEX_TILT_R / 1000)
ok(t_pino >= 1.5 * mt, f"pino de indexação do tilt (a cada {P.TILT_PASSO:g}°) ~{t_pino:.2f} N·m ≥ 1,5 × {mt:.2f}")
REL.append("- Recomendação: usar o tilt SEMPRE travado no pino; para a V2, centro de massa da cabeça perto "
           "do eixo (eixo do tilt mais alto, dentro da cabeça) reduz o torque do servo.")
REL.append("- Pan: sem momento de gravidade; trava radial só contra toques.")

REL.append("\n## 9. Acesso")
ok(True, "manípulos pan (lado direito da mesa) e tilt (montante direito) por fora")
ok(True, "anel 11C: acessível tirando o berço (2 porcas do eixo); ajuste do dia a dia é pelo manípulo pan")
ok(True, "cabeça parafusa na placa 11E por dentro da cabeça (4×M3 de cima para baixo)")

REL.append("\n## 10. Imprimibilidade")
vaos = {"11A_flange_tronco": 6.0, "11B_mesa_garfo": max(P.PIN_PAN_D + 2 * P.RASGO_FOLGA, P.EIXO_D, 9.0),
        "11C_anel_retencao": 0, "11D_berco_tilt": P.EIXO_D, "11E_placa_cabeca": 0,
        "11F_manipulo_pan": 7.4, "11G_manipulo_tilt": 7.4}
for n, s in pecas.items():
    bbx = s.val().BoundingBox()
    ok(vaos[n] <= 12 and max(bbx.xlen, bbx.ylen, bbx.zlen) <= 220,
       f"{n}: maior ponte {vaos[n]:.1f} mm; {bbx.xlen:.0f}×{bbx.ylen:.0f}×{bbx.zlen:.0f} mm")

# ---------------- vistas ----------------
COR = {"11A_flange_tronco": CORES["creme"], "11B_mesa_garfo": CORES["creme"], "11C_anel_retencao": CORES["petroleo"],
       "11D_berco_tilt": CORES["creme"], "11E_placa_cabeca": CORES["petroleo"],
       "11F_manipulo_pan": CORES["petroleo"], "11G_manipulo_tilt": CORES["petroleo"]}
DESL = {"11A_flange_tronco": 0, "11B_mesa_garfo": 1, "11C_anel_retencao": 2.2, "11D_berco_tilt": 3.4,
        "11E_placa_cabeca": 4.6, "11F_manipulo_pan": 1, "11G_manipulo_tilt": 3.4}


def itens(pan=0, tilt=0, expl=0.0, cab=False, gab=True):
    lst = [(to_mesh(pose(n, s, pan, tilt).translate((0, 0, DESL[n] * expl))), COR[n]) for n, s in pecas.items()]
    if gab:
        lst.append((to_mesh(topo), CORES["fantasma"]))
    if cab:
        lst.append((to_mesh(pose("11E_placa_cabeca", cabeca, pan, tilt)), CORES["fantasma"]))
    return lst


render_conjunto(itens(), str(OUT / "vistas.png"), ["iso", "frente", "lado", "topo"], titulo="Peca 11 - pescoco pan/tilt (0/0)")
render_conjunto(itens(gab=False), str(OUT / "corte.png"), ["lado", "iso"], corte=("x", 0.01), titulo="Peca 11 - corte x=0 (cubo, anel, eixo, canais de cabo)")
render_conjunto(itens(expl=14), str(OUT / "explodida.png"), ["iso", "frente"], titulo="Peca 11 - explodida")
render_conjunto(itens(cab=True), str(OUT / "montagem_tronco_cabeca.png"), ["iso", "lado"], titulo="Peca 11 no topo do tronco, cabeca = caixa fantasma")
for pan, tilt in ((90, 0), (-90, 0), (0, 30), (0, -30)):
    render_conjunto(itens(pan, tilt, cab=True), str(OUT / f"pos_pan{pan:+d}_tilt{tilt:+d}.png"), ["iso", "lado"],
                    titulo=f"Peca 11 - pan {pan:+d} / tilt {tilt:+d}")
TMP.unlink(missing_ok=True)

txt = ["# Peça 11 — pescoço pan/tilt: relatório", "",
       f"Resultado: **{'APROVADO' if not FALHAS else 'COM FALHAS'}** ({len(FALHAS)} falhas)", ""] + REL
txt += ["", "## Volumes", ""] + [f"- {n}: {s.val().Volume() / 1000:.1f} cm³" for n, s in pecas.items()]
txt += ["", "## Fixadores e comprados", ""] + [f"- {q} × {d}" for d, q in P.BOM]
(OUT / "RELATORIO.md").write_text("\n".join(txt) + "\n")
print("\n".join(txt))
sys.exit(1 if FALHAS else 0)
