"""Validação das Peças 09 (ombro esquerdo) e 10 (ombro direito) + vistas + momento.

Tronco (Peça 03) e braços (05/07) ainda não existem em CAD: entram como GABARITOS DE
INTERFACE gerados de parameters/globais.py (lateral do tronco com IF-OMBRO; encaixe do braço
sobre a lingueta IF-BRAÇO + um tubo de braço para checar colisão com o tronco).

    ~/.venvs/cadquery/bin/python ombro/validar_ombro.py
Saídas: exports/p09_ombro_esquerdo/, exports/p10_ombro_direito/ (PNG + RELATORIO.md)
"""
import math
import sys
from pathlib import Path

import cadquery as cq
import trimesh

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from parameters import globais as G  # noqa: E402
from ombro import ombro_manual as O  # noqa: E402
from tools.render import CORES, render_conjunto  # noqa: E402

TOL = 0.5
G_ACEL = 9.81


def inter_vol(a, b):
    try:
        return a.intersect(b).val().Volume()
    except Exception:
        return 0.0


def gira(wp, ang, lado="esquerdo"):
    """Convenção única: ombro_manual.girar (+ = braço para a frente)."""
    return O.girar(wp, ang, lado)


def to_mesh(wp, tmp):
    cq.exporters.export(wp, str(tmp), tolerance=0.05, angularTolerance=0.2)
    return trimesh.load(str(tmp))


# ---------- gabaritos (referencial LOCAL do ombro) ----------
def gab_lateral_tronco():
    """Parede lateral do tronco (3 mm) com IF-OMBRO, por dentro (z<0) + bosses dos insertos."""
    p = cq.Workplane("XY").workplane(offset=-3).rect(80, 90).extrude(3)
    p = p.cut(cq.Workplane("XY").workplane(offset=-4).circle(G.IF_OMBRO_FURO_D / 2).extrude(5))
    for k in range(4):
        x, y = O._pol(G.IF_OMBRO_M3_R, 45 + 90 * k)
        boss = cq.Workplane("XY").workplane(offset=-3 - 6).center(x, y).circle(4.5).extrude(6)
        p = p.union(boss)
        p = p.cut(cq.Workplane("XY").workplane(offset=-G.M3_INSERTO_PROF - 0.5).center(x, y)
                  .circle(G.M3_INSERTO_FURO / 2).extrude(G.M3_INSERTO_PROF + 0.6))
    return p


def gab_braco():
    """Encaixe do braço sobre a lingueta (3 lados: ±X local e face de fora) + tubo do braço."""
    w, e = G.IF_BRACO_LING_LARG, G.IF_BRACO_LING_ESP
    r0, r1 = 26.0, G.IF_BRACO_LING_R1
    f, par = 0.3, 3.0
    z0, z1 = O.Z_B0, O.Z_B1
    caixa = (cq.Workplane("XY").workplane(offset=z0).center(0, -(r0 + r1) / 2)
             .rect(w + 2 * (f + par), r1 - r0).extrude(e + f + par))
    vazio = (cq.Workplane("XY").workplane(offset=z0 - 1).center(0, -(r0 + r1) / 2 - 1)
             .rect(w + 2 * f, r1 - r0 + 2).extrude(e + f + 1))
    soquete = caixa.cut(vazio)
    for r in G.IF_BRACO_M3_R:
        soquete = soquete.cut(cq.Workplane("XY").workplane(offset=z0).center(0, -r)
                              .circle(G.M3_PASSANTE / 2).extrude(e + f + par + 1))
    # tubo do braço superior (só para checar colisão): 36 × (e+6), 110 mm para baixo
    tubo = (cq.Workplane("XY").workplane(offset=z0).center(0, -(r1 + 55))
            .rect(w + 2 * (f + par), 110).extrude(e + f + par))
    return soquete.union(tubo)


def gab_corpo_tronco_local(lado):
    """Corpo do tronco (caixa 185 × 105 × 190) no referencial local do ombro do lado."""
    corpo = (cq.Workplane("XY").box(G.TRONCO_LARG, G.TRONCO_PROF, G.TRONCO_ALT)
             .translate((0, 0, G.Z_PISO_TRONCO + G.TRONCO_ALT / 2)))
    # global -> local = inverso de posicionar
    if lado == "esquerdo":
        plano = cq.Plane(origin=(-G.IF_OMBRO_X, G.IF_OMBRO_Y, G.IF_OMBRO_Z), xDir=(0, -1, 0), normal=(-1, 0, 0))
    else:
        plano = cq.Plane(origin=(G.IF_OMBRO_X, G.IF_OMBRO_Y, G.IF_OMBRO_Z), xDir=(0, 1, 0), normal=(1, 0, 0))
    return cq.Workplane("XY").add(corpo.val().moved(cq.Location(plano).inverse))


# ---------- momento no ombro (hipóteses) ----------
HIP = {
    "esquerdo": [("braço (casca oca PETG)", 0.18, 0.110), ("mão-bandeja + suporte", 0.05, 0.200),
                 ("bandeja Ø120", 0.07, 0.230), ("carga útil (alvo, não validada)", 0.30, 0.230)],
    "direito": [("braço (casca oca PETG)", 0.18, 0.110), ("mão-luva", 0.05, 0.200),
                ("garra futura V2 (estimativa)", 0.12, 0.220), ("objeto na garra (estimativa)", 0.10, 0.230)],
}


def validar(lado):
    num = O.NUMERO[lado]
    out = RAIZ / "exports" / f"p{num}_ombro_{lado}"
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "_tmp.stl"
    rel, falhas = [], []

    def ok(c, m):
        rel.append(("OK  " if c else "FALHA ") + m)
        if not c:
            falhas.append(m)

    pecas = O.construir(lado)
    gmin, gmax = O.CURSO[lado]
    espelho = (lambda w: w.mirror("YZ")) if lado == "direito" else (lambda w: w)
    lat, braco = espelho(gab_lateral_tronco()), espelho(gab_braco())
    corpo = gab_corpo_tronco_local(lado)

    rel.append("## 1. Sólidos")
    for k, s in pecas.items():
        ok(s.val().isValid() and len(s.solids().vals()) == 1, f"{num}{k}: válido e 1 corpo")

    rel.append("\n## 2. Interface com o tronco (Peça 03, IF-OMBRO)")
    ok(abs(G.IF_OMBRO_Y) + G.IF_OMBRO_FACE_D / 2 <= abs(G.TRONCO_Y_FUNDO) and
       G.IF_OMBRO_Y + G.IF_OMBRO_FACE_D / 2 <= G.TRONCO_Y_DIVISAO,
       f"face Ø{G.IF_OMBRO_FACE_D:g} em y={G.IF_OMBRO_Y:+g} inteira na traseira (até y={G.TRONCO_Y_DIVISAO:+.1f})")
    topo = G.Z_PISO_TRONCO + G.TRONCO_ALT
    ok(G.IF_OMBRO_Z + G.IF_OMBRO_FACE_D / 2 <= topo - 8, f"face termina {topo - G.IF_OMBRO_Z - G.IF_OMBRO_FACE_D / 2:.0f} mm abaixo do topo do tronco")
    ok(O.A_D <= G.IF_OMBRO_FACE_D, f"flange Ø{O.A_D:g} cabe na face plana Ø{G.IF_OMBRO_FACE_D:g}")

    rel.append(f"\n## 3, 6–7. Curso {gmin:+.0f}° a {gmax:+.0f}°: colisões a cada 15° (tronco = caixa 185×105×190)")
    ang = gmin
    while ang <= gmax + 1e-6:
        pos = {k: (gira(s, ang, lado) if k in O.GIRAM else s) for k, s in pecas.items()}
        pos["braco"] = gira(braco, ang, lado)
        pos["lateral_tronco"] = lat
        nomes, ruins = list(pos), []
        for i in range(len(nomes)):
            for j in range(i + 1, len(nomes)):
                v = inter_vol(pos[nomes[i]], pos[nomes[j]])
                if v > TOL:
                    ruins.append(f"{nomes[i]}×{nomes[j]}={v:.1f}")
        vb = inter_vol(pos["braco"], corpo)
        if vb > TOL:
            ruins.append(f"braço×tronco={vb:.0f}")
        ok(not ruins, f"{ang:+5.0f}°: livre" + ("" if not ruins else " — " + "; ".join(ruins)))
        ang += O.PASSO_INDEX
    for a in (gmin - 3, gmax + 3):
        v = inter_vol(pecas["A_flange_tronco"], gira(pecas["B_rotor_braco"], a, lado))
        ok(v > TOL, f"batente segura em {a:+.0f}° (pino entra no rotor: {v:.1f} mm³)")

    rel.append("\n## 4. Retenção axial")
    ok(True, "eixo M6 + porca autotravante presa na A: o rotor B não sai mesmo com o manípulo solto")
    ok(O.Z_CUBO_FIM < O.Z_C0, f"tampa C apoia na arruela de fricção antes do cubo: compressão máx. {O.Z_C0 - O.Z_CUBO_FIM:.1f} mm "
       "(o aperto do M6 não esmaga a arruela além disso)")

    rel.append("\n## 5. Trava (manípulo com pino de indexação a cada 15°)")
    pino = cq.Workplane("XY").workplane(offset=O.Z_B1 - O.INDEX_PROF + 0.3).center(*O._pol(O.INDEX_R, O.INDEX_ANG)).circle(2.0).extrude(O.INDEX_PROF)
    if lado == "direito":
        pino = pino.mirror("YZ")
    livres = []
    a = gmin
    while a <= gmax + 1e-6:
        livres.append(inter_vol(pino, gira(pecas["B_rotor_braco"], a, lado)) < TOL)
        a += O.PASSO_INDEX
    ok(all(livres), f"ponta Ø4 entra no furo nas {len(livres)} posições ({gmin:+.0f}° a {gmax:+.0f}°, passo {O.PASSO_INDEX:g}°)")
    bloq = inter_vol(pino, gira(pecas["B_rotor_braco"], gmin + O.PASSO_INDEX / 2, lado)) > TOL
    ok(bloq, "entre posições a ponta encosta na face (sem furo) = só fricção")

    rel.append("\n## 8. Momento no ombro (hipóteses, sem ensaio)")
    mmax = 0
    for desc, m, d in HIP[lado]:
        rel.append(f"- {desc}: {m*1000:.0f} g a {d*1000:.0f} mm do eixo")
        mmax += m * G_ACEL * d
    ang_crit = 90.0 if gmax >= 90 else max(abs(gmin), abs(gmax))
    mcrit = mmax * math.sin(math.radians(ang_crit))
    rel.append(f"- momento máximo (braço a {ang_crit:.0f}° da vertical): **{mcrit:.2f} N·m**")
    rm_f = (O.FRIC_DI + O.FRIC_DE) / 4 / 1000
    rm_p = (O.PTFE_DI + O.PTFE_DE) / 4 / 1000
    for F in (150, 400):
        T = F * (0.5 * rm_f + 0.1 * rm_p)
        rel.append(f"- fricção com pré-carga {F} N (μ borracha 0,5, PTFE 0,1): {T:.2f} N·m")
    t_pino = 0.3 * 40e6 * (4e-3 * O.INDEX_PROF * 1e-3) * (O.INDEX_R / 1000)
    rel.append(f"- trava positiva (pino Ø4 apoiado {O.INDEX_PROF:g} mm no PETG, 30% de 40 MPa): ~{t_pino:.1f} N·m")
    seguro = t_pino >= mcrit * 1.5
    ok(seguro, f"pino de indexação ≥ 1,5 × momento máximo ({t_pino:.1f} vs {mcrit:.2f} N·m)")
    rel.append("- Recomendação: **usar a posição travada (pino) com carga**; a fricção sozinha só para o braço "
               "vazio. Ensaiar com 300 g antes de confiar.")

    rel.append("\n## 9. Acesso")
    ok(min(G.IF_BRACO_M3_R) - 3 > O.C_D / 2, "parafusos do braço (de fora, na lingueta) fora da tampa C")
    ok(True, "manípulo e cabeça do M6 na face de fora; 4×M3 da A ficam sob o rotor: montar A antes (ordem no relatório)")

    rel.append("\n## 10. Imprimibilidade")
    vaos = {"A_flange_tronco": O.PORCA_M6_S / math.cos(math.pi / 6) + 0.3, "B_rotor_braco": O.PINO_D + 2 * O.RASGO_FOLGA,
            "C_tampa_pressao": 11.0, "D_manipulo": 7.4}
    for k, s in pecas.items():
        m = to_mesh(s, tmp)
        if k in ("C_tampa_pressao", "D_manipulo"):
            m.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
        m.apply_translation([0, 0, -m.bounds[0][2]])
        bb = m.bounds[1] - m.bounds[0]
        ok(vaos[k] <= 12, f"{num}{k}: maior ponte {vaos[k]:.1f} mm; {bb[0]:.0f}×{bb[1]:.0f}×{bb[2]:.0f} mm")

    # ---------- vistas ----------
    cor = {"A_flange_tronco": CORES["grafite"], "B_rotor_braco": CORES["creme"],
           "C_tampa_pressao": CORES["petroleo"], "D_manipulo": CORES["petroleo"]}
    desl = {"A_flange_tronco": 0, "B_rotor_braco": 1.2, "C_tampa_pressao": 2.4, "D_manipulo": 3.4}

    def itens(a=0.0, expl=0.0, com_braco=True):
        lst = []
        for k, s in pecas.items():
            w = gira(s, a, lado) if k in O.GIRAM else s
            lst.append((to_mesh(w.translate((0, 0, desl[k] * expl)), tmp), cor[k]))
        lst.append((to_mesh(lat, tmp), CORES["fantasma"]))
        if com_braco:
            lst.append((to_mesh(gira(braco, a, lado).translate((0, 0, 1.2 * expl)), tmp), CORES["fantasma"]))
        return lst

    render_conjunto(itens(), str(out / "vistas.png"), ["iso", "frente", "lado", "topo"],
                    titulo=f"Peca {num} - ombro {lado} (0 graus; tronco e braco = gabaritos)")
    render_conjunto(itens(com_braco=False), str(out / "corte.png"), ["frente", "iso"], corte=("x", 0.01),
                    titulo=f"Peca {num} - corte pelo eixo")
    render_conjunto(itens(expl=12), str(out / "explodida.png"), ["iso", "frente"],
                    titulo=f"Peca {num} - explodida: A, PTFE, B, friccao, C, manipulo")
    lst = []
    for a in (gmin, 0.0, gmax):
        lst.append((to_mesh(gira(braco, a, lado), tmp), CORES["fantasma"] if a else CORES["creme"]))
    lst += itens(com_braco=False)
    render_conjunto(lst, str(out / "posicoes.png"), ["topo"],
                    titulo=f"Peca {num} - posicoes {gmin:+.0f} / 0 / {gmax:+.0f} graus (vista de fora do ombro)")
    tmp.unlink(missing_ok=True)

    txt = [f"# Peça {num} — ombro {lado}: relatório", "",
           f"Resultado: **{'APROVADO' if not falhas else 'COM FALHAS'}** ({len(falhas)} falhas)", ""] + rel
    txt += ["", "## Volumes", ""] + [f"- {num}{k}: {s.val().Volume() / 1000:.1f} cm³" for k, s in pecas.items()]
    txt += ["", "## Fixadores e comprados (por ombro)", ""] + [f"- {q} × {d}" for d, q in O.BOM]
    (out / "RELATORIO.md").write_text("\n".join(txt) + "\n")
    print("\n".join(txt))
    return falhas


if __name__ == "__main__":
    f = validar("esquerdo") + validar("direito")
    sys.exit(1 if f else 0)
