"""Parâmetros PRÓPRIOS da cabeça (C05 frente, C06 traseira, M05, M07, antena, orelhas) — mm.

Tudo que é contrato (IF-CABEÇA, envelopes de tela/câmera, CABECA, ANTENA_SOQUETE, ORELHA_*)
vem de parameters/globais.py e NÃO é redefinido aqui. Este arquivo só guarda decisões de
desenho da cabeça. Referencial LOCAL da cabeça: z = 0 no fundo (= G.Z_IF_CABECA no robô),
y = 0 no eixo do robô (+Y = frente), x = 0 no centro.
"""
import math

# ---------- carcaça ----------
PAREDE = 2.4                 # 6 linhas de 0,4 — painéis de 205 mm sem "barriga"
CHANFRO = 6.0                # bordas da frente e de trás: chanfro 45° (imprime de face na mesa sem suporte)
CHANFRO_INT = CHANFRO - PAREDE * (2 - math.sqrt(2))   # chanfro da superfície interna (parede constante)
Y_DIVISAO = 35.0             # plano frente|traseira: frente = 25 mm (tela), traseira = 95 mm (IF-CABEÇA inteira)

# ---------- IF-CABEÇA no fundo (traseira) ----------
FUNDO_ESP = 6.0              # espessura do fundo sob a placa 11E (parede + almofada) -> parafuso M3×10
ALMOFADA = (68.0, 62.0)      # X × Y da almofada rígida sobre a placa (60 × 50)
CABO_FURO_D = 18.0           # ≥ IF_CABECA_CABO_D (16): folga para conector
PINO_FURO_D = 4.3            # furo dos pinos Ø4 da placa
PINO_FURO_P = 3.5            # pinos sobem 3 mm
NERVURAS_X = (42.0, 70.0)    # nervuras do fundo (±), no sentido Y (verticais na impressão)
NERVURA_ALT = 6.0
ACESSO_CHAVE_D = 9.0         # coluna livre sobre cada parafuso da IF (cabeça M3 Ø5,5 + chave)
ACESSO_CHAVE_H = 60.0

# ---------- tela (frente): abertura + rebaixo da moldura / M05 ----------
TELA_Z = 62.0                # centro da abertura (local)
REBAIXO_MARGEM = 9.0         # rebaixo P = envelope + folga + margem (por lado)
REBAIXO_PROF = 3.0           # espessura da moldura/M05 no assento (fica rente à face)
COLAR_LARG, COLAR_PROF = 4.0, 13.0      # colar interno em volta do rebaixo (paredes do rebaixo)
CANTO_L = 16.0               # assentos triangulares nos 4 cantos do rebaixo (catetos)
CANTO_PARAF = 4.6            # parafuso da moldura a (4,6; 4,6) do canto do rebaixo
BANDEJA_BOSS_D = 9.0
BANDEJA_BOSS_POS = [(sx * 74.0, TELA_Z + sz * 32.0) for sx in (-1, 1) for sz in (-1, 1)]
# boss da bandeja termina no fundo do envelope da tela (face da frente - profundidade do envelope)

# ---------- câmera (frente) ----------
CAMERA_Z = 126.0             # centro do furo IF_CAMERA_FURO_D na testa
CAMERA_RESERVA = (26.0, 24.0, 22.0)     # PROPOSTA (não há envelope em globais): X × Z × Y livres atrás do furo
CAMERA_BOSS_X, CAMERA_BOSS_D, CAMERA_BOSS_H = 18.0, 8.0, 10.0

# ---------- união frente <-> traseira ----------
PILAR_D, TUNEL_D = 11.0, 7.0            # pilar da traseira com túnel para a cabeça M3 (acesso por trás)
PILAR_PISO = 6.0                        # piso do túnel até o plano de divisão -> parafuso M3×12
PILAR_R_DIAG = 18.0                     # centro do pilar a 18 mm do centro do arco R30 do canto (a 45°)
BOSS_FRENTE_D = 10.0
PINO_ALINH_D, PINO_ALINH_H = 4.0, 5.0   # 2 pinos na frente, furos Ø4,6 (FOLGA_ENCAIXE) na traseira
PINOS_ALINH = [(45.0, "topo"), (-45.0, "fundo")]
BLOCO_PINO = 9.0

# ---------- antena (topo, traseira) ----------
ANTENA_Y = 0.0
ANTENA_ESCAREADO = 3.0       # escareado 45° na boca do soquete (assento da antena, sem suporte)
ANTENA_PISO = 3.0            # piso do soquete; M3 por dentro da cabeça
ANTENA_ALTURA = 49.0         # acima do topo da cabeça -> topo da bolinha em 550 mm
ANTENA_HASTE_D, ANTENA_BOLA_D = 5.0, 12.0
ANTENA_BOSS_R = 8.0

# ---------- orelhas (laterais, traseira) ----------
ORELHA_Y, ORELHA_Z = 0.0, 72.5
ORELHA_M3_R = 14.0           # 3 insertos na orelha, parafusos M3×10 por dentro da cabeça
ORELHA_ANEL = (19.0, 1.5)    # anel decorativo: raio interno × altura
ORELHA_ALMOFADA_D, ORELHA_ALMOFADA_ESP = 40.0, 2.0

# ---------- M05 tampa facial / M07 tampão ----------
M05_LABIO_ESP, M05_LABIO_PROF = 2.0, 6.0
RELEVO = 1.2                 # olhos e boca em relevo (troca de filamento na camada do relevo)
M07_FLANGE = (18.0, 2.0)
