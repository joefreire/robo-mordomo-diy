"""Parâmetros LOCAIS das Peças 05 (braço esquerdo), 06 (bandeja) e 07 (braço direito) (mm).

Só valores que nenhuma outra peça usa. Os contratos (IF-BRAÇO, IF-PUNHO, IF-BANDEJA,
BRACO_D, alcances) vêm de parameters/globais.py e não são redefinidos aqui.

Referencial LOCAL = o do ombro (ombro/ombro_manual.py): Z = eixo do ombro para FORA do
tronco, X = para TRÁS (esquerdo), Y = para CIMA; braço em 0° aponta para −Y. O braço é
desenhado no referencial do ombro ESQUERDO e o direito é o espelho (como o ombro).
"""
from parameters import globais as G

# ---------- tubo ----------
Z_TUBO = 21.0            # eixo do tubo ao longo do eixo do ombro: Ø40 vai de z=1 a z=41
                         # (z<0 = dentro do tronco; z≥30 perto do eixo = manípulo do ombro)
R_TUBO = G.BRACO_D / 2
R_CAV = R_TUBO - G.BRACO_PAREDE                 # 17: cavidade
CAV_ANG_TETO = 52.0      # graus da vertical: teto da cavidade em "gota" (imprime sem suporte)
Z_SPLIT = 19.3           # plano das metades = topo do encaixe da lingueta (Z_B1 + folga)
TUBO_Y0 = 38.0           # raio onde começa o tubo (manípulo do ombro vai até r≈33)

# ---------- encaixe na lingueta IF-BRAÇO (soquete integrado às metades) ----------
SOQ_LARG = 36.0          # bloco do soquete (tangencial)
SOQ_Z0, SOQ_Z1 = 1.5, 29.0   # fora do tronco (z>0) e abaixo do manípulo (z 30..42)
SOQ_R0 = 26.5            # começa fora do rotor Ø52 e da tampa Ø50 do ombro
SOQ_R1 = 46.0
SOQ_M3_CBORE_D, SOQ_M3_ASSENTO_Z = 6.5, 24.0    # cabeça M3 embutida; M3×10 rosca ~5 mm
REFORCO_OMBRO = 8.0      # parede maciça depois do fundo do encaixe
REFORCO_PUNHO = 8.0      # parede maciça na ponta (insertos do anel do punho)

# ---------- torres M3 das metades, pinos, presilhas ----------
TORRE_D = 8.0
TORRE_S = 12.5           # deslocamento da torre no plano (entra 0,5 na parede; lado oposto ao canal)
TORRE_CBORE_D = 6.5
TORRE_ASSENTO_Z = 9.5    # assento da cabeça (metade interna) -> M3×16 até o fim do inserto
PINO_D, PINO_FURO_D, PINO_PROF = 3.0, 3.15, 5.0  # pino de aço/filamento Ø3 × 10
CANAL_S = -12.5          # linha do canal de cabos (lado oposto às torres)
CABO_TESTE_D = 6.0       # feixe de teste do canal contínuo (4 fios + folga)
ENTRADA_CABO = (10.0, 16.0)   # rasgo na face interna, perto do ombro (cabo do tronco, V2)
ENTRADA_CABO_R = 58.0

# ---------- anel do punho (grafite): leva o IF-PUNHO, 2×M3 no braço ----------
ANEL_ESP = 10.0
ANEL_D = G.BRACO_D
ANEL_M3_ANG = (20.0, 160.0)   # parafusos anel->braço (simétricos ao eixo de 90°)
ANEL_CBORE_D, ANEL_CBORE_P = 6.2, 3.5
CHAVE_R0 = 15.0          # ressalto IF-PUNHO de r=15 a r=18 (inserto de 90° vai até 14,5)

# ---------- braço esquerdo (05) ----------
ADAPT_L = 45.0           # face do punho -> centro da bandeja (horizontal)
ESQ_PUNHO_X = G.BRACO_ESQ_ALCANCE - ADAPT_L      # 100: face do punho a 100 mm do plano do ombro
ESQ_TORRES = [("v", 65.0), ("v", 95.0), ("h", 50.0), ("h", 75.0)]
ESQ_PRESILHAS = [("v", 80.0), ("h", 62.0)]

# ---------- braço direito (07) ----------
DIR_TORRES = [50.0, 62.0]          # última torre antes do espaço do conector (braço de 115)
DIR_PRESILHAS = [61.0, 66.0]       # depois da entrada do cabo (r 58) e antes do espaço do conector
FRISO = (6.0, 42.0, 1.2)       # rebaixo da faixa verde-petróleo (largura × comprimento × prof.)
FRISO_Y0 = 55.0
CONECTOR_ENVELOPE = (20.0, 12.0, 25.0)   # espaço livre p/ conector antes da parede do punho

# ---------- adaptador fixo V1 (IF-PUNHO -> IF-BANDEJA) ----------
ADAPT_FLANGE_ESP = 6.0
ADAPT_PESCOCO_D, ADAPT_PESCOCO_L = 16.0, 10.0    # vão para chave Allen de ponta esférica
ADAPT_LARG = 40.0
ADAPT_Y_BASE = -18.0     # fundo plano (imprime em pé)
ADAPT_Y_TOPO = 27.0      # face IF-BANDEJA (acima do eixo do antebraço)
ADAPT_Z_FIM = 70.0
ADAPT_M3_CBORE_D, ADAPT_M3_ASSENTO = 6.5, 21.0   # M3×12 por baixo, 6 mm na placa + 6 no inserto

# ---------- bandeja (06) ----------
BOSS_D, BOSS_H = 50.0, 10.0          # cubo aparafusado embaixo da bandeja (IF-BANDEJA)
BOSS_M3_R, BOSS_M3_ANG = 19.0, (90.0, 210.0, 330.0)   # bandeja -> cubo: 3×M3 escareados de cima
BANDEJA_PAREDE = 3.0
BANDEJA_RAIO_INT = 3.0
ANEL_DECOR = (50.0, 53.0, 1.2, 2.4)  # canal r 50..53, prof 1,2; anel opcional altura 2,4

# ---------- mão-luva (07, grafite) ----------
LUVA_PUNHO_L = 12.0
LUVA_SEMI = (16.0, 20.0, 24.0)       # semi-eixos (X_H, Y_H, Z_H) da luva (07/11: menor, folga sobre a base)
LUVA_Z = 32.0
LUVA_POLEGAR = ((4.0, 16.0, 30.0), (8.0, 8.0, 13.0))   # centro, semi-eixos
ACESSO_D = 6.5                       # canais da chave/cabeça M3 na mão

# ---------- material / massa ----------
PETG_DENS = 1.27         # g/cm³
PAREDES_MM = 4 * 0.45    # 4 perímetros
PREENCH = 0.15
