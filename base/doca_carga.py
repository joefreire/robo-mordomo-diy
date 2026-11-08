"""Doca de carga (V2) — o robô com a base 01R entra DE RÉ e carrega sozinho.

Bloco apoiado na mesa atrás do robô. A face da frente acompanha a traseira da base (parede
inclinada) com folga DOCA_FOLGA; dois braços em V centram a base nos últimos milímetros. Na face:
2 alojamentos para contatos de mola (CONTATO_*) na altura e no espaçamento dos contatos da 01R,
o emissor de IR alinhado com a janela do robô, e atrás o conector de alimentação.
Comprados (conferir): 2 contatos de mola (pogo) Ø CONTATO_D, LED IR, conector P4/barril, fonte.
Impressão: fundo na mesa.

Coordenadas: as do robô na posição "encaixado" (robô em x=y=0).
"""
import sys
from pathlib import Path

import cadquery as cq

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from parameters import globais as G  # noqa: E402
from base import base_rodas as BR  # noqa: E402

DOCA_FOLGA = 1.5                 # entre a traseira da base e a face da doca (encaixado)
DOCA_PROF = 45.0                 # profundidade do bloco (Y)
DOCA_ALT = 32.0                  # altura (abaixo dos braços do robô)
GUIA_COMP = 55.0                 # braços em V para a frente
GUIA_ABERTURA = 8.0              # quanto cada guia abre para fora na ponta (captura lateral; 256 da A1 limita)
GUIA_ESP, GUIA_ALT = 5.0, 20.0
CONTATO_D = 6.0                  # corpo do contato de mola (CONFERIR)
CONTATO_PONTA_D = 4.0
CONTATO_SALIENCIA = DOCA_FOLGA + G.DOCA_CURSO_MOLA   # ponta solta sai isto da face
IR_D = 5.2                       # LED IR 5 mm
JACK_D = 8.0                     # conector P4 de painel (CONFERIR)
CANAL = (8.0, 6.0)               # canal de fio por baixo (largura × altura)


_MEIA_GUIA = G.BASE_LARG / 2 - G.recuo(GUIA_ALT) + DOCA_FOLGA
DOCA_LARG = 2 * (_MEIA_GUIA + GUIA_ESP)      # o bloco vai até a raiz das guias (uma peça só)


def y_face(z):
    return BR.y_traseira(z) - DOCA_FOLGA


def bloco():
    y1 = y_face(0)                         # face da frente acompanha a inclinação: perfil no plano YZ
    y0 = y1 - DOCA_PROF
    yt = y_face(DOCA_ALT)
    perfil = (cq.Workplane("YZ", origin=(-DOCA_LARG / 2, 0, 0))
              .polyline([(y0, 0), (y1, 0), (yt, DOCA_ALT), (y0, DOCA_ALT)]).close().extrude(DOCA_LARG))
    p = perfil.edges("|X and >Z").fillet(4.0)
    # guias em V (ficam por fora do contorno da base, abrindo para a frente)
    meia = _MEIA_GUIA
    for sx in (-1, 1):
        a = (sx * (meia + GUIA_ESP / 2), y1 - 2)
        b = (sx * (meia + GUIA_ESP / 2 + GUIA_ABERTURA), y1 + GUIA_COMP)
        guia = (cq.Workplane("XY").polyline([(a[0] - GUIA_ESP / 2, a[1]), (a[0] + GUIA_ESP / 2, a[1]),
                                             (b[0] + GUIA_ESP / 2, b[1]), (b[0] - GUIA_ESP / 2, b[1])]).close()
                .extrude(GUIA_ALT))
        p = p.union(guia)
    # contatos de mola: furo do corpo atravessando a face, na altura e no x dos contatos da 01R
    for sx in (-1, 1):
        p = p.cut(cq.Workplane("XZ", origin=(0, y_face(G.CARGA_Z) + 1, 0)).center(sx * G.CARGA_X, G.CARGA_Z)
                  .circle(CONTATO_D / 2 + 0.1).extrude(DOCA_PROF - 6))
    p = p.cut(cq.Workplane("XZ", origin=(0, y_face(G.CARGA_IR_Z) + 1, 0)).center(0, G.CARGA_IR_Z)
              .circle(IR_D / 2).extrude(DOCA_PROF - 6))
    # conector de alimentação atrás + canal de fio por baixo até os contatos
    y0 = y1 - DOCA_PROF
    p = p.cut(cq.Workplane("XZ", origin=(0, y0 - 1, 0)).center(0, 14).circle(JACK_D / 2).extrude(-12))
    p = p.cut(cq.Workplane("XY").workplane(offset=-0.01).center(0, y0 + 20).rect(2 * G.CARGA_X + CANAL[0], CANAL[0])
              .extrude(CANAL[1]))
    return p


def contatos_soltos():
    """Pontas dos contatos de mola SOLTAS (fora da doca), para checar o toque nos rebaixos da 01R."""
    s = None
    for sx in (-1, 1):
        c = (cq.Workplane("XZ", origin=(0, y_face(G.CARGA_Z), 0)).center(sx * G.CARGA_X, G.CARGA_Z)
             .circle(CONTATO_PONTA_D / 2).extrude(-CONTATO_SALIENCIA))
        s = c if s is None else s.union(c)
    return s


PECAS = {"DC_doca_carga": bloco}

if __name__ == "__main__":
    out = RAIZ / "exports" / "p01R_base_rodas"
    out.mkdir(parents=True, exist_ok=True)
    s = bloco()
    cq.exporters.export(s, str(out / "DC_doca_carga.stl"), tolerance=0.01, angularTolerance=0.1)
    cq.exporters.export(s, str(out / "DC_doca_carga.step"))
    bb = s.val().BoundingBox()
    print(f"doca {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} valido={s.val().isValid()} solidos={len(s.solids().vals())}")
