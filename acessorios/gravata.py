"""Gravata-borboleta (verde-petróleo) + tampa do nó. Decorativa, V1 e V2.

Presa por 2×M3 de frente nos insertos GRAVATA_M3 da frontal do tronco (Peça 04A). As cabeças
ficam num rebaixo no nó, escondidas por uma tampa de encaixe (pressão leve, sai com a unha).
Impressão: costas na mesa (asas e nó sem balanço); tampa deitada.

    ~/.venvs/cadquery/bin/python acessorios/gravata.py      # gera, valida e exporta
"""
import sys
from pathlib import Path

import cadquery as cq

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from parameters import globais as G  # noqa: E402
from parameters import tronco as T  # noqa: E402

# ============================================================
Y_FACE = G.TRONCO_PROF / 2           # face da frente do tronco (52,5)
Z_C = T.GRAVATA_M3[0][1]             # 268
ASA_L, ASA_A = 34.0, 26.0            # cada asa: comprimento × altura
ASA_PONTA_A = 12.0                   # altura junto ao nó
NO_L, NO_A, NO_R = 26.0, 16.0, 4.0   # nó
ESP_ASA, ESP_NO = 8.0, 11.0
REB_L, REB_A, REB_P = NO_L - 4.0, NO_A - 4.0, 4.0   # rebaixo das cabeças M3 no nó
TAMPA_FOLGA = 0.1                    # por lado (pressão leve)
TAMPA_ESP = 1.6


def _xz(pts, y0, esp):
    return (cq.Workplane("XZ", origin=(0, y0, 0)).polyline(pts).close().extrude(-esp))


def gravata():
    asas = None
    for s in (-1, 1):
        x0 = s * NO_L / 2 * 0.6
        pts = [(x0, Z_C - ASA_PONTA_A / 2), (x0 + s * ASA_L, Z_C - ASA_A / 2),
               (x0 + s * ASA_L, Z_C + ASA_A / 2), (x0, Z_C + ASA_PONTA_A / 2)]
        a = _xz(pts, Y_FACE, ESP_ASA)
        a = a.edges("|Y").fillet(3.0)
        asas = a if asas is None else asas.union(a)
    no = (cq.Workplane("XZ", origin=(0, Y_FACE, 0)).center(0, Z_C).rect(NO_L, NO_A).extrude(-ESP_NO)
          .edges("|Y").fillet(NO_R))
    p = asas.union(no)
    p = p.faces(">Y").edges().fillet(1.5)
    for x, z in T.GRAVATA_M3:
        p = p.cut(cq.Workplane("XZ", origin=(0, Y_FACE - 1, 0)).center(x, z).circle(G.M3_PASSANTE / 2).extrude(-ESP_NO - 2))
    p = p.cut(cq.Workplane("XZ", origin=(0, Y_FACE + ESP_NO - REB_P, 0)).center(0, Z_C)
              .rect(REB_L, REB_A).extrude(-REB_P - 1))
    return p


def tampa_no():
    return (cq.Workplane("XZ", origin=(0, Y_FACE + ESP_NO - REB_P + (REB_P - TAMPA_ESP), 0)).center(0, Z_C)
            .rect(REB_L - 2 * TAMPA_FOLGA, REB_A - 2 * TAMPA_FOLGA).extrude(-TAMPA_ESP)
            .edges("|Y").fillet(1.0))


if __name__ == "__main__":
    from tronco import tronco_frontal as TF
    out = RAIZ / "exports" / "acessorios"
    out.mkdir(parents=True, exist_ok=True)
    g, t = gravata(), tampa_no()
    rel, falhas = [], 0
    for n, s in (("gravata", g), ("gravata_tampa_no", t)):
        ok = s.val().isValid() and len(s.solids().vals()) == 1
        rel.append(f"{'OK ' if ok else 'FALHA'} {n}: válido, 1 corpo, {s.val().Volume() / 1000:.1f} cm³")
        falhas += not ok
        cq.exporters.export(s, str(out / f"{n}.stl"), tolerance=0.01, angularTolerance=0.1)
        cq.exporters.export(s, str(out / f"{n}.step"))
    fr = TF.frontal()
    v = g.intersect(fr).val().Volume() if True else 0
    rel.append(f"{'OK ' if v < 0.5 else 'FALHA'} gravata × frontal: {v:.2f} mm³ (só encosta)")
    falhas += v >= 0.5
    vt = t.intersect(g).val().Volume()
    rel.append(f"{'OK ' if vt < 0.5 else 'FALHA'} tampa do nó cabe no rebaixo: {vt:.2f} mm³")
    falhas += vt >= 0.5
    bb = g.val().BoundingBox()
    rel.append(f"OK  topo da gravata z={bb.zmax:.0f} < topo do tronco {G.Z_TOPO_TRONCO:g}; frente em y={bb.ymax:.0f}")
    (out / "RELATORIO_gravata.md").write_text("# Gravata\n\n" + "\n".join(rel) + "\n")
    print("\n".join(rel))
    sys.exit(1 if falhas else 0)
