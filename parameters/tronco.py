"""Parâmetros do tronco (Peças 03 traseira e 04 frontal + peças soltas) em mm.

Tudo que vem do contrato entre peças continua em globais.py (IF_CINTURA_*, IF_OMBRO_*,
IF_PESCOCO_*, TRONCO_*, IF_TELA_PEITO_*). Aqui ficam os valores NOVOS que o tronco definiu e
que outra peça pode precisar ler (bandeja do ESP32, gravata, painel, tela do peito).

Coordenadas: as do robô (globais.py). x = largura (+ direita), y = profundidade (+ frente),
z = altura a partir da mesa.
"""
import math

from parameters import globais as G

# ---------- forma externa ----------
# Meia-largura externa w(z): 75 no piso (TRONCO_LARG_BASE/2), sobe em "S" (cosseno) até
# 92,5 em Z_LARG_CHEIA, reta até o início do arredondado do topo (R35 na vista frontal).
Z_LARG_CHEIA = 205.0               # a partir daqui a lateral é plana em x = ±92,5 (IF-OMBRO começa em 211)
CANTO_PLANTA_R = G.TRONCO_RAIO_PLANTA      # 30
CANTO_CHANFRO = 45.0               # cantos da planta = arco R30 + reta a 45° junto da face (imprimir deitada)
PISO_ESP = 5.0                     # piso da traseira e da frontal (IF-CINTURA; parafuso M4 × 12)

# ---------- união 03 x 04 (decisão: parafusos POR TRÁS) ----------
# M3 de cabeça cilíndrica entram pelas costas, descem num tubo Ø6,5 até o assento em y = +12 e
# prendem em insertos M3 nas colunas da frontal. Acessíveis com o robô montado (chave Allen
# longa, ≥ 75 mm). Pinos Ø4 na frontal entram em furos na traseira (alinhamento).
UNIAO_M3 = [(-54.0, 104.5), (54.0, 104.5),       # (x, z) embaixo
            (-66.0, 165.0), (66.0, 165.0),       # meio
            (-45.0, 276.0), (45.0, 276.0)]       # em cima
assert len(UNIAO_M3) == G.TRONCO_UNIAO_M3
UNIAO_PINOS = [(-66.0, 152.0), (66.0, 152.0)]    # pinos Ø4 da frontal -> furos na traseira
UNIAO_TUBO_D = 11.0                # tubo da traseira e coluna da frontal
UNIAO_ROSCA_FURO = 6.5             # passagem da cabeça M3 (Ø5,5) e da chave
UNIAO_ASSENTO_Y = 12.0             # y do assento da cabeça (10,5 mm de aperto até a divisão)
UNIAO_PARAFUSO = "M3 × 16 cabeça cilíndrica (ISO 4762)"
PINO_D, PINO_L = 4.0, 5.0
PINO_FURO_D = PINO_D + 2 * G.FOLGA_ENCAIXE
PINO_FURO_PROF = PINO_L + 1.0

# ---------- piso (IF-CINTURA) ----------
PISO_NERVURAS_X = [-47.0, -23.0, 23.0, 47.0]     # nervuras ao longo de Y (imprimem em pé)
PISO_NERVURA_ESP, PISO_NERVURA_ALT = 4.0, 10.0

# ---------- laterais (IF-OMBRO) ----------
OMBRO_PLACA_ESP = 6.0              # placa plana sob a face Ø56 (parede local)
OMBRO_BOSS_D, OMBRO_BOSS_ALT = 9.0, 3.5          # bosses dos insertos, para dentro da placa
OMBRO_RESSALTO_R = 31.0            # ressalto externo (gota) que cobre os cantos curvos
# Envelope interno do servo (IF_OMBRO_ENVELOPE_INTERNO 50 × 60 × 45, só o TAMANHO está em
# globais.py): centro deslocado 6 mm para a FRENTE e 6 mm para BAIXO do eixo do ombro. Centrado
# no eixo, o canto de cima/trás sairia da casca (o topo arredonda R35 e as costas R30). O eixo
# continua dentro, a 19 mm da borda de trás e a 24 mm da de cima. Vale para a V2 (suporte do servo).
OMBRO_ENVELOPE_CENTRO = (G.IF_OMBRO_Y + 6.0, G.IF_OMBRO_Z - 6.0)   # (y, z) = (−9, 233)

# ---------- topo (IF-PESCOÇO) ----------
PESCOCO_NERVURA_X = 22.0           # duas nervuras ao longo de Y sob os insertos (x = ±22)
PESCOCO_NERVURA_LARG, PESCOCO_NERVURA_ALT = 9.0, 12.0   # altura medida do topo (z 272..284)

# ---------- IF-ELETRÔNICA: trilhos verticais na parede de trás ----------
TRILHO_X = 46.0                    # ±46 (bandeja do ESP32 de 80–90 mm entre os trilhos)
TRILHO_LARG, TRILHO_PROF = 10.0, 8.0
TRILHO_Z = (160.0, 262.0)
TRILHO_PASSO = 10.0
TRILHO_FUROS_Z = [165.0 + TRILHO_PASSO * i for i in range(10)]   # 165..255, insertos M3 de frente (+Y)
# Bandeja do ESP32 (removível, parafusa nos trilhos): envelope livre x0, x1, z0, z1, y0, y1.
# Fica ABAIXO do envelope do servo do ombro (z 209) e na frente da abertura do painel (USB-C).
ESP32_ZONA = (-50.0, 50.0, 170.0, 202.0, -41.5, -11.5)

# ---------- painel de manutenção traseiro (03B, verde-petróleo) ----------
PAINEL_ABERTURA = (60.0, 66.0)     # largura × altura do furo na parede (atrás do ESP32: USB-C)
PAINEL_Z = 210.0                   # centro
PAINEL_MOLDURA = 8.0               # faixa rebaixada em volta
PAINEL_REBAIXO = 1.5               # só na moldura; a faixa ganha 1,5 por dentro (parede segue 3)
PAINEL_RAIO = 4.0
PAINEL_M3 = [(sx * 32.0, PAINEL_Z + sz * 35.0) for sx in (-1, 1) for sz in (-1, 1)]

# ---------- alto-falante (só superfície e grade) ----------
FALANTE_CENTRO = (-30.0, 137.0)    # x, z: parede de trás, embaixo, lado ESQUERDO do robô (x < 0)
FALANTE_ZONA_D = 50.0              # superfície plana livre por dentro
FALANTE_GRADE_D = 40.0
FALANTE_FURO_D = 3.0

# ---------- tela do peito (IF-TELA-PEITO) na frontal ----------
TELA_FOLGA = 1.0                   # por lado, entre o envelope e a abertura
TELA_ABERTURA = (G.IF_TELA_PEITO_ENVELOPE[0] + 2 * TELA_FOLGA, G.IF_TELA_PEITO_ENVELOPE[1] + 2 * TELA_FOLGA)
TELA_ABERTURA_R = 1.5
MOLDURA_FAIXA = 10.0               # moldura cobre 10 mm em volta da abertura
MOLDURA_ESP = 4.0                  # 2 dentro do rebaixo + 2 saliente
MOLDURA_REBAIXO = 2.0
MOLDURA_EXT = (TELA_ABERTURA[0] + 2 * MOLDURA_FAIXA, TELA_ABERTURA[1] + 2 * MOLDURA_FAIXA)
MOLDURA_R = 6.0
MOLDURA_JANELA = (92.0, 62.0)      # PLACEHOLDER: área visível da tela real
MOLDURA_M3 = [(sx * (TELA_ABERTURA[0] / 2 + 5.0), G.IF_TELA_PEITO_Z + sz * 25.0)
              for sx in (-1, 1) for sz in (-1, 1)]
TELA_Y_VIDRO = G.TRONCO_PROF / 2 - MOLDURA_REBAIXO       # 50,5: face da tela encosta na moldura
TELA_Y_FUNDO = TELA_Y_VIDRO - G.IF_TELA_PEITO_ENVELOPE[2]  # 25,5
BANDEJA_ESP = 3.0                  # bandeja interna: y 22,5..25,5 (atrás do envelope)
BANDEJA_EXT = (124.0, 70.0)
BANDEJA_JANELA = (60.0, 36.0)
# Furação da TELA na bandeja: PLACEHOLDER (sem tela comprada). Rasgos de ±RASGO na horizontal
# cobrem os módulos 3,5" comuns; trocar pela furação real e reimprimir só a bandeja.
BANDEJA_TELA_FUROS = [(sx * 45.0, sz * 27.0) for sx in (-1, 1) for sz in (-1, 1)]   # relativos ao centro
BANDEJA_TELA_RASGO = 6.0

# ---------- abertura de manutenção da frontal + tampa (04D) ----------
TAMPA_ABERTURA = (76.0, 36.0)
TAMPA_Z = 130.0
TAMPA_FAIXA = 8.0
TAMPA_REBAIXO = 2.5
TAMPA_R = 4.0
TAMPA_M3 = [(sx * 40.0, TAMPA_Z + sz * 20.0) for sx in (-1, 1) for sz in (-1, 1)]

# ---------- gravata (não modelada) ----------
GRAVATA_M3 = [(-10.0, 268.0), (10.0, 268.0)]     # insertos M3 de frente

# ---------- anel de sacrifício (imprimibilidade dos rebaixos que ficam na mesa) ----------
SACRIFICIO_ESP = 0.8               # parede fina na borda da abertura, sob a faixa do rebaixo: vira ponte
                                   # de no máx. ~10 mm. CORTAR com estilete depois de imprimir.

# ---------- materiais ----------
PETG_DENS = 1.27                   # g/cm³


def meia_largura(z: float) -> float:
    """Meia-largura externa do tronco na altura z (vista frontal)."""
    z0, z1 = G.Z_PISO_TRONCO, Z_LARG_CHEIA
    w0, w1 = G.TRONCO_LARG_BASE / 2, G.TRONCO_LARG / 2
    r = G.TRONCO_RAIO_TOPO
    zc = G.Z_TOPO_TRONCO - r
    if z <= z0:
        return w0
    if z < z1:
        t = (z - z0) / (z1 - z0)
        return w0 + (w1 - w0) * (1 - math.cos(math.pi * t)) / 2
    if z <= zc:
        return w1
    dz = min(z - zc, r)
    return w1 - r + math.sqrt(max(r * r - dz * dz, 0.0))
