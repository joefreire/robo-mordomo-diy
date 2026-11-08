"""Parâmetros compartilhados do Robô Mordomo (mm).

Única fonte das medidas que mais de uma peça usa. Peça nenhuma redefine valor daqui.
Ver documentation/ALINHAMENTO.md para decisões e pendências.

Sistema de coordenadas (proposta em ALINHAMENTO.md §1):
  origem = centro da pegada da base, no plano da mesa (z = 0)
  X = largura (+ para a direita do robô), Y = profundidade (+ para a FRENTE), Z = para cima
  eixo do robô (pescoço, passa-cabos Ø25, centro do Ø110) em x = 0, y = 0
"""
import math

# ---------- impressão / folgas (PETG, A1, bico 0,4) ----------
FOLGA_ENCAIXE = 0.3        # folga por lado em encaixes deslizantes
FOLGA_FURO = 0.2           # folga extra em furo passante
CAMADA = 0.2

# ---------- fixadores (valores de catálogo comum; conferir com o lote real) ----------
M3_PASSANTE = 3.4          # furo de passagem M3
M3_INSERTO_FURO = 4.0      # furo p/ inserto térmico M3 (CONFERIR na ficha do inserto)
M3_INSERTO_PROF = 5.7      # comprimento do inserto (CONFERIR)

# ---------- base: contorno comum às Peças 01 e 02 ----------
BASE_LARG = 225.0          # X
BASE_PROF = 200.0          # Y
BASE_RAIO = 35.0           # raio dos cantos na planta, no plano da mesa
BASE_INCLINACAO = 6.0      # graus: laterais fecham para dentro ao subir

# ---------- Peça 01: base inferior ----------
P01_ALTURA = 25.0
P01_PAREDE = 3.0           # espessura horizontal da parede
P01_FUNDO = 4.0


M4_PASSANTE = 4.5
M4_CABECA_D = 7.0          # cabeça cilíndrica M4 (ISO 4762) — rebaixo usa +1,0
M4_CABECA_H = 4.0
M4_INSERTO_FURO = 5.6      # furo p/ inserto térmico M4 (CONFERIR na ficha do inserto)
M4_INSERTO_PROF = 8.1      # comprimento do inserto (CONFERIR)

# ---------- tronco: divisão traseira (esqueleto) x frontal (capa) ----------
# Decisão 07/11: cintura, ombros e pescoço inteiros na traseira. A traseira passa de
# 65 para 75 mm de profundidade para o padrão IF-CINTURA caber atrás do plano.
TRONCO_PROF = 105.0
TRONCO_PROF_TRASEIRA = 75.0
TRONCO_Y_FUNDO = -TRONCO_PROF / 2                        # costas (Y negativo = trás)
TRONCO_Y_DIVISAO = TRONCO_Y_FUNDO + TRONCO_PROF_TRASEIRA # +22,5: plano traseira|frontal

# ---------- IF-CINTURA: Peça 02 <-> cintura <-> tronco (mesmo padrão em cima e embaixo) ----------
# Retângulo 70 x 30 centrado no eixo do robô: simétrico em 180°, cabe inteiro atrás do
# plano de divisão (y máx 15 + boss 5 = 20 < 22,5).
IF_CINTURA_M4 = [(sx * 35.0, sy * 15.0) for sx in (-1, 1) for sy in (-1, 1)]
IF_CINTURA_CABO_D = 25.0                # passa-cabos (Peça 02, cubo da cintura)
IF_CINTURA_ABERTURA_TRONCO_D = 56.0     # furo no piso do tronco: cabos + acesso ao anel de ajuste
IF_CINTURA_ALTURA = 24.0                # face da Peça 02 -> piso do tronco (módulo manual e o motorizado)
IF_CINTURA_ENVELOPE_D = 102.0           # diâmetro máximo de qualquer módulo de cintura
IF_CINTURA_GIRO = 60.0                  # ± graus (V1 manual e V2)


# ---------- alturas da pilha (z de cada face) ----------
P02_ALTURA = 45.0
Z_TOPO_P02 = P01_ALTURA + P02_ALTURA                 # 70: face da Peça 02 = base da cintura
Z_PISO_TRONCO = Z_TOPO_P02 + IF_CINTURA_ALTURA       # 94
TRONCO_ALT = 190.0
TRONCO_LARG = 185.0

# ---------- IF-OMBRO: lateral do tronco (traseira) <-> módulo do ombro ----------
# Face plana circular na lateral do tronco. Centro dentro da traseira (esqueleto):
# y = -15 com raio 28 -> vai de -43 a +13 < divisão +22,5.
IF_OMBRO_X = TRONCO_LARG / 2                         # face externa da lateral (±)
IF_OMBRO_Y = -15.0
IF_OMBRO_Z = Z_PISO_TRONCO + TRONCO_ALT - 45.0       # 239
IF_OMBRO_FACE_D = 56.0                               # área plana reservada na carcaça
IF_OMBRO_M3_R = 20.0                                 # 4×M3 (insertos no tronco) a 45°,135°,...
IF_OMBRO_FURO_D = 16.0                               # centro: porca do eixo (V1) / eixo do servo + cabos (V2)
IF_OMBRO_ENVELOPE_D = 56.0                           # nenhum módulo de ombro passa disto
IF_OMBRO_ENVELOPE_L = 40.0                           # para fora da face do tronco
IF_OMBRO_ENVELOPE_INTERNO = (50.0, 60.0, 45.0)       # dentro do tronco (servo V2): Y × Z × X

# ---------- IF-BRAÇO: módulo do ombro <-> braço (Peça 05) ----------
# Lingueta radial na peça que gira; o braço encaixa por fora (3 lados) e parafusa
# no sentido do eixo, de fora para dentro (acesso lateral).
IF_BRACO_LING_LARG = 24.0      # tangencial
IF_BRACO_LING_ESP = 12.0       # ao longo do eixo do ombro
IF_BRACO_LING_R0 = 25.0        # começa neste raio
IF_BRACO_LING_R1 = 39.0        # termina neste raio (face de topo do braço)
IF_BRACO_M3_R = (29.0, 35.0)   # 2×M3 ao longo da lingueta, insertos na face de fora


# ---------- IF-PESCOÇO: topo do tronco (traseira) <-> módulo do pescoço ----------
# Prateleira plana no topo da traseira, centrada no eixo do robô. Furação dentro da
# traseira: y máx 15 + boss 4 = 19 < divisão 22,5.
Z_TOPO_TRONCO = Z_PISO_TRONCO + TRONCO_ALT          # 284
IF_PESCOCO_M3 = [(sx * 22.0, sy * 15.0) for sx in (-1, 1) for sy in (-1, 1)]
IF_PESCOCO_CABO_D = 16.0
IF_PESCOCO_FACE_D = 66.0                            # área plana reservada no topo do tronco
IF_PESCOCO_ENVELOPE = (75.0, 75.0, 80.0)            # X × Y × Z máx. de qualquer pescoço (V1 e V2)

# ---------- IF-CABEÇA: módulo do pescoço <-> cabeça (obrigatória no CAD da cabeça) ----------
# Placa plana; a cabeça parafusa por dentro (4×M3 de cima para baixo, insertos na placa)
# e se alinha por 2 pinos. Centro de cabos Ø16.
PESCOCO_ALTURA = 72.0                               # topo do tronco -> face de cima da placa
Z_IF_CABECA = Z_TOPO_TRONCO + PESCOCO_ALTURA        # 356
IF_CABECA_PLACA = (60.0, 50.0)                      # X × Y
IF_CABECA_M3 = [(sx * 22.0, sy * 17.0) for sx in (-1, 1) for sy in (-1, 1)]
IF_CABECA_PINOS = [(0.0, 19.0), (0.0, -19.0)]       # Ø4 × 3 mm, sobem da placa
IF_CABECA_PINO_D = 4.0
IF_CABECA_CABO_D = 16.0
IF_CABECA_INSERTO_PROF = 4.0                        # inserto M3 CURTO (M3×4) — a placa tem 6 mm



# ---------- base: união Peça 01 <-> Peça 02 (decisão 07/11) ----------
# 4×M3 POR BAIXO: atravessam o fundo da Peça 01 (rebaixo da cabeça embaixo) e prendem em
# insertos nas torres da Peça 02. Parafusos escondidos; acesso virando o robô.
BASE_TORRE_D = 10.0                                  # torres na Peça 01 e bosses na Peça 02
BASE_TORRES = [(sx * 70.0, sy * 84.0) for sx in (-1, 1) for sy in (-1, 1)]   # (±90,±75) caía no canto do contrapeso (validação 07/11)
CONTRAPESO = (180.0, 150.0, 3.0)                     # placa de aço de referência (não impressa)
PES_D, PES_PROF = 15.0, 2.0                          # pés de borracha adesivos
P02_PLATAFORMA_D = 110.0                             # topo plano da Peça 02 (recebe a cintura, colar Ø102)
P02_LED = (120.0, 12.0)                              # rasgo frontal do difusor (largura × altura), IF-LED

# ---------- tronco: forma externa (Peças 03 + 04) ----------
TRONCO_LARG_BASE = 150.0       # largura embaixo (cobre o colar da cintura Ø102 com folga)
TRONCO_PROF_BASE = 105.0
TRONCO_RAIO_PLANTA = 30.0      # raio dos cantos na planta
TRONCO_RAIO_TOPO = 35.0        # arredondado do topo/ombros (vista frontal)
TRONCO_PAREDE = 3.0
TRONCO_UNIAO_M3 = 6            # parafusos M3 de união traseira<->frontal (posições: Peça 03)
IF_TELA_PEITO_ENVELOPE = (100.0, 70.0, 25.0)   # L × A × profundidade máx. de qualquer tela do peito
IF_TELA_PEITO_Z = Z_PISO_TRONCO + 120.0        # centro da tela do peito

# ---------- braços: Peça 05 (esquerdo, bandeja), Peça 07 (direito, ferramenta); Peça 06 = bandeja ----------
# Especificações V2 de 07/11: casca REDONDA oca em 2 metades longitudinais (M3), sem cotovelo
# articulado. A ligação ao ombro é a lingueta IF-BRAÇO (já existe nas Peças 09/10).
BRACO_D = 40.0                 # diâmetro externo (38–42)
BRACO_PAREDE = 3.0
BRACO_ESQ_ALTURA = 135.0       # 05: do eixo do ombro até o eixo do segmento horizontal (130–140)
BRACO_ESQ_ALCANCE = 145.0      # 05: do plano do ombro até o centro da bandeja (horizontal)
BRACO_ESQ_RAIO_COTOVELO = 30.0 # 05: curva suave do L (raio na linha de centro)
BRACO_DIR_COMP = 115.0         # 07: reto, eixo do ombro -> face do punho. 155 (prancha) e 125 batiam a luva na base pendurado (validação 07/11)
# IF-PUNHO (flange de ferramenta, padrão reutilizável; igual nos dois braços)
IF_PUNHO_D = 36.0              # 35–40
IF_PUNHO_M3_R = 12.5           # 3×M3 com insertos no braço, ASSIMÉTRICOS: 90°, 200°, 340°
IF_PUNHO_M3_ANG = (90.0, 200.0, 340.0)
IF_PUNHO_CABO_D = 10.0
IF_PUNHO_CHAVE = (5.0, 2.0)    # ressalto de alinhamento (largura × altura), a 90°
# Bandeja (Peça 06) <-> adaptador V1 (no IF-PUNHO esquerdo): 2×M3 + chave assimétrica
BANDEJA_D, BANDEJA_BORDA, BANDEJA_FUNDO = 120.0, 10.0, 3.0
IF_BANDEJA_M3 = [(-12.0, 0.0), (12.0, 0.0)]          # insertos no boss central da bandeja
IF_BANDEJA_CHAVE = (14.0, 8.0, 3.0)                  # rasgo retangular fora de centro (L×A×prof.)
IF_BANDEJA_CHAVE_OFF = (0.0, 6.0)                    # deslocamento = assimetria (só entra de um jeito)

# ---------- cabeça (frente + traseira) ----------
CABECA = (205.0, 120.0, 145.0)                 # X × Y × Z externos
CABECA_RAIO = 30.0
IF_TELA_ROSTO_ENVELOPE = (110.0, 75.0, 20.0)   # maior tela SPI ~4" + moldura; janela real na moldura
IF_CAMERA_FURO_D = 12.0                        # testa, centro, acima da tela
ANTENA_SOQUETE = (8.0, 10.0)                   # Ø × profundidade do soquete da antena no topo
ORELHA_D, ORELHA_ESP = 50.0, 12.0



# ---------- IF-BASE: Peça 02 <-> módulo de base de baixo (V1 estática OU V2 com rodas) ----------
# O módulo de baixo é TROCÁVEL. Contrato: mesmo contorno externo inclinado até a borda em
# z = P01_ALTURA (25), mesma borda plana (a aba da 02 entra por dentro), 4×M3 por baixo em
# BASE_TORRES (insertos na 02), mesmo assento do difusor do LED na junta, passagem de cabos
# subindo pelo centro (Ø25 da 02). A Peça 02 deixa livres os envelopes RODAS_* abaixo.
#
# V2 com rodas (07/11, envelopes — conferir com o motor/roda comprados):
#   tração diferencial: 2 rodas no eixo X (y = 0), girando no próprio lugar; 2 rodízios
#   (frente e trás). A altura do robô não muda: o módulo com rodas tem a mesma borda em z=25
#   e o fundo RODAS_FOLGA_CHAO acima da mesa. Limite da roda: teto inclinado da Peça 02.
RODA_D_MAX = 48.0              # Ø máximo da roda (ex.: N20 + roda 43–48)
RODA_LARG = 20.0
RODA_X = 68.0                  # ± centro da roda (motores não se cruzam no centro; teto da 02 conferido)
RODA_FOLGA = 3.0               # folga da roda ao poço/parede
MOTOR_ENVELOPE = (38.0, 14.0, 14.0)    # comprimento (para dentro, ao longo de X) × Y × Z — N20 + redução + encoder
# 4 rodízios perto dos cantos (07/11): com 2 (frente/trás) o apoio era um losango e o robô
# tombava com ~5° com 300 g na bandeja. Ficam RODIZIO_ALIVIO acima da linha das rodas: as rodas
# sempre tracionam e, ao inclinar, o robô apoia nos rodízios (apoio ~ retângulo).
RODIZIOS = [(sx * 46.0, sy * 78.0) for sx in (-1, 1) for sy in (-1, 1)]
RODIZIO_ALIVIO = 1.0
RODIZIO_ENVELOPE = (22.0, 22.0, 18.0)  # X × Y × altura do rodízio de esfera (CONFERIR)
BATERIA_ENVELOPE = (80.0, 42.0, 22.0)  # suporte 2×18650 (X × Y × Z)
BATERIA_Y = 36.0               # centro (atrás do eixo das rodas: -BATERIA_Y)
DRIVER_ENVELOPE = (50.0, 30.0, 16.0)   # ponte H / controlador de motores
DRIVER_Y = 40.0                # centro (na frente: +DRIVER_Y)
RODAS_FOLGA_CHAO = 6.0         # fundo do módulo com rodas acima da mesa

# ---------- auto-carregamento (V2): contatos na traseira da base com rodas + doca ----------
# O robô entra DE RÉ na doca: 2 contatos de cobre na parede traseira da 01R (polaridades em
# x ±CARGA_X, alturas iguais) encostam em 2 contatos de mola da doca. Janela de IR no centro da
# traseira para o farol da doca (alinhamento). Guias em V da doca centram a base.
CARGA_X = 30.0                 # ± posição dos contatos
CARGA_Z = 14.0                 # altura do centro dos contatos (acima da mesa)
CARGA_PAD = (14.0, 8.0, 1.5)   # rebaixo da placa de contato (largura × altura × prof.)
CARGA_IR_D = 8.0               # janela do receptor de IR (centro da traseira)
CARGA_IR_Z = 16.0
CARREGADOR_ENVELOPE = (40.0, 25.0, 12.0)   # placa de carga/proteção da bateria (X × Y × Z)
DOCA_CURSO_MOLA = 4.0          # compressão dos contatos de mola da doca



def recuo(z: float, ang: float = BASE_INCLINACAO) -> float:
    """Quanto o contorno externo da base recua (por lado) na altura z."""
    return z * math.tan(math.radians(ang))
