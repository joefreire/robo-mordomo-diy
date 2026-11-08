"""Parâmetros compartilhados pelas Peças 01 e 02 (base) que NÃO existem em globais.py.

Só entra aqui o que mais de um arquivo da base usa (base_inferior, base_superior,
validar_base). Valores locais de cada peça ficam no topo do arquivo da peça.
Tudo em mm, no referencial do robô (ver globais.py).
"""
import math

from parameters import globais as G

TAN_INCL = math.tan(math.radians(G.BASE_INCLINACAO))

# ---------- fixadores da união 01 <-> 02 (catálogo comum; CONFERIR no lote) ----------
M3_CABECA_D = 5.5          # cabeça cilíndrica M3 (ISO 4762) — CONFERIR
M3_CABECA_H = 3.0          # CONFERIR
M3_UNIAO_COMP = 25.0       # parafuso M3 × 25 ISO 4762 (fundo da 01 -> inserto na 02)

# ---------- torres da Peça 01 / bosses da Peça 02 ----------
# SUBSTITUI G.BASE_TORRES (±90, ±75): essas posições caem exatamente no canto da placa
# de contrapeso 180 × 150 (colisão) e, no canto R35, não sobra lugar entre o canto da
# placa e a aba da Peça 02. Movidas para fora da placa, na frente e atrás:
#   placa+folga até y = 76 -> torre começa em y = 79 (3 mm);
#   torre/boss termina em y = 89 -> aba da 02 começa em y ≈ 91,4 (2,4 mm).
BASE_TORRES = G.BASE_TORRES   # valor adotado em globais.py (07/11)

# ---------- encaixe 01 <-> 02 ----------
ABA_ALT = 3.0                              # quanto a aba da 02 desce dentro da 01
ABA_ESP = 3.0                              # espessura horizontal da aba
Z_JUNTA = G.P01_ALTURA - ABA_ALT           # 22: plano mais baixo da Peça 02 (aba e bosses)
FOLGA_TORRE = 0.2                          # vão torre(01) -> boss(02): a borda é o apoio,
Z_TORRE_TOPO = Z_JUNTA - FOLGA_TORRE       # o parafuso fecha a costura, não a torre

# ---------- contrapeso (placa de aço comprada, G.CONTRAPESO) ----------
CONTRAPESO_FOLGA = 1.0                     # por lado: corte de chapa varia ±0,5
