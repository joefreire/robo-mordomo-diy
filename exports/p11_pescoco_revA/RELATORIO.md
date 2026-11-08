# Peça 11 — pescoço pan/tilt: relatório

Resultado: **COM FALHAS** (2 falhas)

## 1. Sólidos
OK  11A_flange_tronco: válido e 1 corpo
OK  11B_mesa_garfo: válido e 1 corpo
OK  11C_anel_retencao: válido e 1 corpo
OK  11D_berco_tilt: válido e 1 corpo
OK  11E_placa_cabeca: válido e 1 corpo
OK  11F_manipulo_pan: válido e 1 corpo
OK  11G_manipulo_tilt: válido e 1 corpo

## 2. Fixação no tronco (IF-PESCOÇO)
OK  M3 (-22,-15) com boss atrás da divisão (y=+22.5)
OK  M3 (-22,+15) com boss atrás da divisão (y=+22.5)
OK  M3 (+22,-15) com boss atrás da divisão (y=+22.5)
OK  M3 (+22,+15) com boss atrás da divisão (y=+22.5)
OK  flange Ø64 na face plana Ø66 do topo
OK  altura 72 mm ≤ envelope 80

## 3, 6. Retenção axial
OK  pan: anel 11C cobre a mesa em 6.3 mm (independe da trava)
OK  pan: silicone limitado a 0.6 mm de compressão
OK  tilt: eixo M5 de aço atravessa montante-berço-montante, porca autotravante (independe da trava)

## 4–6. Pan ±90° × tilt ±30° (todas as combinações) — colisões
OK  pan  -90° tilt -30°: livre
OK  pan  -90° tilt  +0°: livre
OK  pan  -90° tilt +30°: livre
OK  pan   +0° tilt -30°: livre
OK  pan   +0° tilt  +0°: livre
OK  pan   +0° tilt +30°: livre
OK  pan  +90° tilt -30°: livre
OK  pan  +90° tilt  +0°: livre
OK  pan  +90° tilt +30°: livre
OK  batente pan segura em -93° (8.4 mm³)
OK  batente pan segura em +93° (8.4 mm³)
FALHA batente tilt segura em -33° (0.0 mm³)
FALHA batente tilt segura em +33° (0.0 mm³)
OK  cabeça (caixa 205×120×145) inclinada ±30° fica 42 mm acima do topo do tronco

## 7. Cabos
OK  berço: 2 canais de 8.3 × 24 mm ao lado do eixo do tilt
OK  Ø16 no cubo e na placa da cabeça
OK  altura livre para o laço de folga entre a mesa e o berço: 23 mm (pan ±90° torce o cabo nesse trecho; deixar ~80 mm de folga)

## 8. Momentos e travas (hipóteses, sem ensaio)
- carcaça da cabeça (2 metades PETG): 300 g
- tela do rosto SPI ~4": 60 g
- câmera + suporte: 30 g
- antena, orelhas, parafusos, LEDs: 60 g
- total 450 g; centro de massa 96 mm ACIMA do eixo do tilt e 10 mm à frente
- momento no tilt a 30°: **0.25 N·m**. Cabeça em cima do eixo = pêndulo invertido: solta, ela cai para o lado em que estiver inclinada; a fricção sozinha não basta.
OK  pino de indexação do tilt (a cada 10°) ~1.32 N·m ≥ 1,5 × 0.25
- Recomendação: usar o tilt SEMPRE travado no pino; para a V2, centro de massa da cabeça perto do eixo (eixo do tilt mais alto, dentro da cabeça) reduz o torque do servo.
- Pan: sem momento de gravidade; trava radial só contra toques.

## 9. Acesso
OK  manípulos pan (lado direito da mesa) e tilt (montante direito) por fora
OK  anel 11C: acessível tirando o berço (2 porcas do eixo); ajuste do dia a dia é pelo manípulo pan
OK  cabeça parafusa na placa 11E por dentro da cabeça (4×M3 de cima para baixo)

## 10. Imprimibilidade
OK  11A_flange_tronco: maior ponte 6.0 mm; 64×64×11 mm
OK  11B_mesa_garfo: maior ponte 9.0 mm; 64×64×58 mm
OK  11C_anel_retencao: maior ponte 0.0 mm; 47×47×4 mm
OK  11D_berco_tilt: maior ponte 5.4 mm; 40×36×27 mm
OK  11E_placa_cabeca: maior ponte 0.0 mm; 60×50×8 mm
OK  11F_manipulo_pan: maior ponte 7.4 mm; 10×19×17 mm
OK  11G_manipulo_tilt: maior ponte 7.4 mm; 10×19×17 mm

## Volumes

- 11A_flange_tronco: 21.2 cm³
- 11B_mesa_garfo: 32.1 cm³
- 11C_anel_retencao: 5.8 cm³
- 11D_berco_tilt: 21.9 cm³
- 11E_placa_cabeca: 13.4 cm³
- 11F_manipulo_pan: 2.3 cm³
- 11G_manipulo_tilt: 2.3 cm³

## Fixadores e comprados

- 4 × Parafuso M3 × 10 (11A -> topo do tronco)
- 4 × Inserto térmico M3 no topo do tronco (IF-PESCOÇO)
- 3 × Parafuso M3 × 10 (anel 11C -> cubo)
- 3 × Inserto térmico M3 no cubo (11A)
- 1 × Parafuso M5 × 70 cabeça cilíndrica (eixo do tilt)
- 1 × Porca M5 autotravante
- 1 × Parafuso M4 × 20 (manípulo pan, radial)
- 1 × Parafuso M4 × 20 (manípulo tilt)
- 2 × Inserto térmico M4 (mesa e montante)
- 4 × Parafuso M3 × 8 escareado (placa 11E -> berço)
- 4 × Inserto térmico M3 no berço
- 4 × Inserto térmico M3 na placa 11E (a cabeça parafusa aqui)
- 1 × Arruela PTFE Ø34.5×Ø54×1 (pan)
- 1 × Arruela de silicone Ø34.5×Ø46×2 (pan)
- 2 × Arruela PTFE/feltro Ø5,3×Ø16×1.5 (tilt, uma de cada lado)
