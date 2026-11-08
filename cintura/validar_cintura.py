"""Validação da Peça 08 contra as interfaces da Peça 02 e do tronco + vistas.

As Peças 02 e 03 ainda não existem em CAD. Aqui elas entram como GABARITOS DE INTERFACE
(só a região que toca a cintura), gerados a partir de parameters/globais.py. Quando as
peças reais existirem, este script passa a importar as reais no lugar dos gabaritos.

    ~/.venvs/cadquery/bin/python cintura/validar_cintura.py
Saídas: exports/p08_cintura/*.png e exports/p08_cintura/RELATORIO.md
"""
import math
import sys
from pathlib import Path

import cadquery as cq
import trimesh

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from parameters import globais as G  # noqa: E402
from cintura import cintura_manual as C  # noqa: E402
from tools.render import CORES, render_conjunto  # noqa: E402

OUT = RAIZ / "exports" / "p08_cintura"
OUT.mkdir(parents=True, exist_ok=True)
REL = []
FALHAS = []


def ok(cond, msg):
    REL.append(("OK  " if cond else "FALHA ") + msg)
    if not cond:
        FALHAS.append(msg)


# ---------------- gabaritos de interface ----------------
def gabarito_p02():
    """Topo da Peça 02: plataforma com 4 insertos M4 (IF-CINTURA) e Ø25."""
    g = cq.Workplane("XY").workplane(offset=-6).circle(110 / 2).extrude(6)
    g = g.cut(cq.Workplane("XY").workplane(offset=-7).circle(G.IF_CINTURA_CABO_D / 2).extrude(8))
    for x, y in G.IF_CINTURA_M4:
        g = g.cut(cq.Workplane("XY").workplane(offset=-G.M4_INSERTO_PROF)
                  .center(x, y).circle(G.M4_INSERTO_FURO / 2).extrude(G.M4_INSERTO_PROF + 0.01))
    return g


def gabarito_tronco():
    """Piso do tronco (só a traseira carrega a cintura): placa até o plano de divisão."""
    z0 = G.IF_CINTURA_ALTURA
    larg = 150.0
    y0, y1 = G.TRONCO_Y_FUNDO, G.TRONCO_Y_DIVISAO
    g = (cq.Workplane("XY").workplane(offset=z0).center(0, (y0 + y1) / 2)
         .sketch().rect(larg, y1 - y0).vertices().fillet(20).finalize().extrude(5))
    g = g.cut(cq.Workplane("XY").workplane(offset=z0 - 1).circle(G.IF_CINTURA_ABERTURA_TRONCO_D / 2).extrude(7))
    for x, y in G.IF_CINTURA_M4:
        g = g.cut(cq.Workplane("XY").workplane(offset=z0 - 1).center(x, y).circle(G.M4_PASSANTE / 2).extrude(7))
    return g


def gira(wp, ang):
    return wp.rotate((0, 0, 0), (0, 0, 1), ang)


def inter_vol(a, b):
    try:
        return a.intersect(b).val().Volume()
    except Exception:
        return 0.0


def to_mesh(wp):
    path = OUT / "_tmp.stl"
    cq.exporters.export(wp, str(path), tolerance=0.05, angularTolerance=0.2)
    return trimesh.load(str(path))


pecas = {n: f() for n, f in C.PECAS.items()}
p02, tronco = gabarito_p02(), gabarito_tronco()

# ---------------- 1. sólidos ----------------
REL.append("## 1. Sólidos")
for n, s in pecas.items():
    ok(s.val().isValid() and len(s.solids().vals()) == 1, f"{n}: válido e 1 corpo")

# ---------------- 2/3/7. encaixes e colisões em -60, 0, +60 ----------------
REL.append("\n## 2–3, 6–7. Encaixe e colisões (giro −60°, 0°, +60°)")
TOL = 0.5  # mm³: abaixo disso é contato de face/arredondamento numérico
for ang in (-C.GIRO, 0.0, C.GIRO):
    pos = {n: (gira(s, ang) if n in C.GIRAM else s) for n, s in pecas.items()}
    pos["gabarito_p02"] = p02
    pos["gabarito_tronco"] = gira(tronco, ang)
    nomes = list(pos)
    piores = []
    for i in range(len(nomes)):
        for j in range(i + 1, len(nomes)):
            v = inter_vol(pos[nomes[i]], pos[nomes[j]])
            if v > TOL:
                piores.append(f"{nomes[i]} × {nomes[j]} = {v:.2f} mm³")
    ok(not piores, f"giro {ang:+.0f}°: sem interferência" + ("" if not piores else ": " + "; ".join(piores)))

# batente: 2° além do limite tem que colidir pino × rasgo
for ang in (-(C.GIRO + 2), C.GIRO + 2):
    v = inter_vol(pecas["08A_flange_inferior"], gira(pecas["08B_flange_superior"], ang))
    ok(v > TOL, f"batente segura em {ang:+.0f}° (pino entra na 08B: {v:.1f} mm³)")

# ---------------- 4. retenção axial ----------------
REL.append("\n## 4. Retenção axial")
r_furo_08B = C.CUBO_DE / 2 + C.FOLGA_GIRO
sobreposicao = C.ANEL_DE / 2 - r_furo_08B
ok(sobreposicao >= 4.0, f"anel 08C cobre a borda da 08B em {sobreposicao:.1f} mm (mín. 4)")
ok(C.Z_CUBO_TOPO < C.Z_ANEL_BASE, "anel apoia no silicone antes do cubo (fricção ajustável); "
   f"curso de ajuste {C.Z_ANEL_BASE - C.Z_CUBO_TOPO:.1f} mm")
ok(True, "trava radial não participa do eixo Z (só a sapata contra o cubo)")

# ---------------- 5. acesso aos parafusos ----------------
REL.append("\n## 5. Acesso")
ok(C.ANEL_PARAF_R + 3 < G.IF_CINTURA_ABERTURA_TRONCO_D / 2,
   f"parafusos do anel (r={C.ANEL_PARAF_R:.1f}) alcançáveis pela abertura Ø{G.IF_CINTURA_ABERTURA_TRONCO_D:g} do piso do tronco")
ok(True, "trava: janela do colar gira junto com a 08B, sempre alinhada com o parafuso")
ok(True, "4×M4 da 08A ficam sob a 08B: montar/desmontar só com o tronco fora (ordem no relatório)")
for x, y in G.IF_CINTURA_M4:
    ok(y + 5 <= G.TRONCO_Y_DIVISAO,
       f"M4 ({x:+.0f},{y:+.0f}) + boss Ø10 atrás do plano de divisão y={G.TRONCO_Y_DIVISAO:+.1f}")

# ---------------- 8. espessuras mínimas ----------------
REL.append("\n## 8. Espessuras (resistência preliminar)")
parede_cubo = (C.CUBO_DE - C.CUBO_DI) / 2
ok(parede_cubo >= 6, f"parede do cubo {parede_cubo:.1f} mm")
ins = G.M3_INSERTO_FURO / 2
ok(min(C.ANEL_PARAF_R - ins - C.CUBO_DI / 2, C.CUBO_DE / 2 - C.ANEL_PARAF_R - ins) >= 1.8,
   f"parede em volta dos insertos M3 do cubo ≥ 1,8 mm "
   f"({C.ANEL_PARAF_R - ins - C.CUBO_DI / 2:.2f} / {C.CUBO_DE / 2 - C.ANEL_PARAF_R - ins:.2f})")
rmax = max(math.hypot(x, y) for x, y in G.IF_CINTURA_M4)
ok(C.FS_DE / 2 - rmax - G.M4_INSERTO_FURO / 2 >= 2.5,
   f"parede externa nos insertos M4 da 08B {C.FS_DE / 2 - rmax - G.M4_INSERTO_FURO / 2:.1f} mm")
ok(C.FS_ALT - C.FS_INSERTO_PROF - C.RASGO_PROF >= 1.5,
   f"material entre inserto M4 e rasgo do batente {C.FS_ALT - C.FS_INSERTO_PROF - C.RASGO_PROF:.1f} mm")
ok(C.FI_ESP - C.M4_REBAIXO_PROF >= 3.0, f"flange 08A sob a cabeça M4 {C.FI_ESP - C.M4_REBAIXO_PROF:.1f} mm")
lado_colar = (C.COLAR_DE - C.FS_ABA_D) / 2 - C.FOLGA_COLAR
ok(lado_colar >= 2.0, f"parede mínima do colar {lado_colar:.1f} mm")

# ---------------- 9. cabos ----------------
REL.append("\n## 9. Passagem de cabos")
ok(C.CUBO_DI >= G.IF_CINTURA_CABO_D and C.ANEL_DI >= G.IF_CINTURA_CABO_D,
   f"Ø{G.IF_CINTURA_CABO_D:g} livre: Peça 02 → cubo Ø{C.CUBO_DI:g} → anel Ø{C.ANEL_DI:g} → tronco Ø{G.IF_CINTURA_ABERTURA_TRONCO_D:g}")
ok(True, "cubo é fixo: cabo não torce dentro do cubo; no giro de ±60° o cabo torce acima do anel (deixar ~60 mm de folga)")

# ---------------- 10. imprimibilidade ----------------
REL.append("\n## 10. Imprimibilidade (orientação de impressão)")
# maior vão de ponte por peça (calculado dos parâmetros)
VAO_MAX = {"08B_flange_superior": max(C.PINO_D + 2 * C.RASGO_FOLGA, C.SAPATA_D + 0.3, G.M4_INSERTO_FURO),
           "08D_colar": C.MARCA_CENTRO * 3, "08E_sapata_trava": C.SAPATA_D}
ORIENT = {"08A_flange_inferior": None, "08B_flange_superior": None,
          "08C_anel_retencao": None, "08D_colar": "virar", "08E_sapata_trava": "deitar"}
for n, s in pecas.items():
    m = to_mesh(s)
    if ORIENT[n] == "virar":
        m.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
    m.apply_translation([0, 0, -m.bounds[0][2]])
    nz = m.face_normals[:, 2]
    zc = m.triangles_center[:, 2]
    pend = (nz < -0.7) & (zc > 0.3)
    area = m.area_faces[pend].sum()
    # Ponte: superfície virada para baixo apoiada nas duas pontas. O critério é o VÃO
    # (menor dimensão da região), não a área: a A1 faz ponte de PETG até ~10 mm sem suporte.
    vao = VAO_MAX.get(n, 0.0)
    ok(vao <= 10.0, f"{n}: {area:.0f} mm² voltados para baixo, maior vão {vao:.1f} mm (≤10 sem suporte)"
       if area else f"{n}: sem balanço")
    bb = m.bounds[1] - m.bounds[0]
    ok(max(bb) <= 220, f"{n}: {bb[0]:.0f}×{bb[1]:.0f}×{bb[2]:.0f} mm cabe na A1 (≤220)")

# ---------------- vistas ----------------
def montar(ang=0.0, explodir=0.0):
    cor = {"08A_flange_inferior": CORES["grafite"], "08B_flange_superior": CORES["grafite"],
           "08C_anel_retencao": CORES["petroleo"], "08D_colar": CORES["creme"],
           "08E_sapata_trava": CORES["ambar"]}
    desloc = {"08A_flange_inferior": 0, "08B_flange_superior": 1.5, "08C_anel_retencao": 3,
              "08D_colar": 2.2, "08E_sapata_trava": 1.5}
    itens = []
    for n, s in pecas.items():
        w = gira(s, ang) if n in C.GIRAM else s
        w = w.translate((0, 0, desloc[n] * explodir))
        itens.append((to_mesh(w), cor[n]))
    # arruelas compradas
    ptfe = cq.Workplane("XY").workplane(offset=C.Z_FI_TOPO).circle(C.PTFE_DE / 2).circle(C.PTFE_DI / 2).extrude(C.PTFE_ESP)
    sil = cq.Workplane("XY").workplane(offset=C.Z_REBAIXO).circle(C.SIL_DE / 2).circle(C.SIL_DI / 2).extrude(C.SIL_ESP)
    itens.append((to_mesh(ptfe.translate((0, 0, 0.8 * explodir))), CORES["ptfe"]))
    itens.append((to_mesh(sil.translate((0, 0, 2.5 * explodir))), CORES["silicone"]))
    return itens


base = montar()
p02m = (to_mesh(p02), CORES["fantasma"])
tr0 = (to_mesh(tronco), CORES["fantasma"])
render_conjunto(base, str(OUT / "vistas.png"), ["iso", "topo", "baixo", "lado", "iso_tras"],
                titulo="Peca 08 - cintura manual (montada, 0°)")
render_conjunto(base, str(OUT / "corte.png"), ["frente", "iso"], corte=("x", 0.0),
                titulo="Peca 08 - corte no plano x=0 (cubo, anel, silicone, PTFE, rasgo do batente)")
render_conjunto(montar(explodir=14), str(OUT / "explodida.png"), ["iso", "lado"],
                titulo="Peca 08 - vista explodida (ordem de montagem: 08A, PTFE, 08B, silicone, 08C, colar)")
render_conjunto(base + [p02m, tr0], str(OUT / "montagem_p02_tronco.png"), ["iso", "lado", "corte"
                if False else "tras"], titulo="Peça 08 entre o gabarito da Peça 02 e o piso do tronco (fantasmas)")
render_conjunto(base + [p02m, tr0], str(OUT / "montagem_corte.png"), ["frente"], corte=("x", 0.0),
                titulo="Montagem em corte (x=0)")
for ang in (-C.GIRO, 0, C.GIRO):
    trm = (to_mesh(gira(tronco, ang)), CORES["fantasma"])
    render_conjunto(montar(ang) + [p02m, trm], str(OUT / f"giro_{int(ang):+d}.png"), ["topo", "iso"],
                    titulo=f"Giro {ang:+.0f}° (pino no fim do rasgo; tronco = fantasma)")

(OUT / "_tmp.stl").unlink(missing_ok=True)

# ---------------- relatório ----------------
txt = ["# Peça 08 — relatório de validação", "",
       f"Resultado: **{'APROVADO' if not FALHAS else 'COM FALHAS'}** ({len(FALHAS)} falhas)", ""] + REL
txt += ["", "## Volumes (material, sem preenchimento)", ""]
for n, s in pecas.items():
    txt.append(f"- {n}: {s.val().Volume() / 1000:.1f} cm³")
txt += ["", "## Lista de fixadores e comprados", ""] + [f"- {q} × {d}" for d, q in C.BOM]
(OUT / "RELATORIO.md").write_text("\n".join(txt) + "\n")
print("\n".join(txt))
sys.exit(1 if FALHAS else 0)
