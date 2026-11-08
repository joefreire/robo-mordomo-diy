# Peça 11 — pescoço pan/tilt: relatório

Resultado: **APROVADO** (0 falhas)

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
OK  batente pan segura em -93° (8.6 mm³)
OK  batente pan segura em +93° (8.6 mm³)
OK  batente tilt segura em -33° (1.6 mm³)
OK  batente tilt segura em +33° (1.6 mm³)
OK  cabeça (caixa 205×120×145) inclinada ±30° fica 42 mm acima do topo do tronco

## 6b. Buchas, eixo e folgas (rev. B)
OK  bucha 6×10×10 prensada (alojamento −0.05 mm), troca sem mexer em carcaça
OK  eixo: ombro liso Ø6 do ISO 7379 Ø6×65 nas buchas 6×10
OK  ombro liso 65 mm ≥ vão externo dos montantes 63 mm (rosca só fora, na porca)
OK  folga axial: 0.5 mm por lado reservados para calços 0,1–0,5 mm; montar e completar até sumir o jogo
OK  apoio dos DOIS lados: carga da cabeça -> placa -> berço -> eixo -> 2 buchas -> 2 montantes -> mesa (sem balanço)

## 6c. Rigidez (estimativas, PETG E≈2000 MPa; sem ensaio)
- empurrão lateral de 10 N a 100 mm acima do eixo: giro do garfo ≈ 0.22° (2 montantes 10×30 + nervuras não contadas)
- placa da cabeça: 6 mm sobre o berço de 40×40; balanço de só 5 mm na frente/trás, com abas de 5 mm
OK  flexão do garfo estimada < 0,5° (0.22°)

## 7. Cabos
OK  cabos sobem por dentro do cubo (Ø16) — não encostam na arruela PTFE nem no silicone, que ficam por fora do cubo
OK  amarração no berço (2 rasgos de abraçadeira 4×2.5): o laço fica entre a mesa e o berço
OK  berço: 2 canais de 8.0 × 24 mm ao lado do eixo do tilt
OK  Ø16 no cubo e na placa da cabeça
OK  altura livre para o laço de folga entre a mesa e o berço: 18 mm (pan ±90° torce o cabo nesse trecho; deixar ~80 mm de folga)

## 8. Momentos e travas (hipóteses, sem ensaio)
- carcaça da cabeça (C05 + C06, CAD): 473 g
- tampa facial M05 + orelhas + antena + tampão (CAD): 78 g
- tela do rosto SPI ~4" (estimativa): 60 g
- câmera + suporte (estimativa): 30 g
- parafusos e insertos (estimativa): 25 g
- total 666 g; centro de massa 92 mm ACIMA do eixo do tilt e 11 mm à frente
- momento no tilt a 30°: **0.36 N·m**. Cabeça em cima do eixo = pêndulo invertido: solta, ela cai para o lado em que estiver inclinada; a fricção sozinha não basta.
OK  pino de indexação do tilt (a cada 10°) ~1.32 N·m ≥ 1,5 × 0.36
- Recomendação: usar o tilt SEMPRE travado no pino; para a V2, centro de massa da cabeça perto do eixo (eixo do tilt mais alto, dentro da cabeça) reduz o torque do servo.
- Pan: sem momento de gravidade; trava radial só contra toques.

## 9. Acesso
OK  manípulos pan (lado direito da mesa) e tilt (montante direito) por fora
OK  anel 11C: acessível tirando o berço (2 porcas do eixo); ajuste do dia a dia é pelo manípulo pan
OK  cabeça parafusa na placa 11E por dentro da cabeça (4×M3 de cima para baixo)

## 10. Imprimibilidade
OK  11A_flange_tronco: maior ponte 6.0 mm; 64×64×15 mm
OK  11B_mesa_garfo: maior ponte 9.0 mm; 70×70×57 mm
OK  11C_anel_retencao: maior ponte 0.0 mm; 47×47×4 mm
OK  11D_berco_tilt: maior ponte 6.0 mm; 40×40×27 mm
OK  11E_placa_cabeca: maior ponte 0.0 mm; 60×50×14 mm
OK  11F_manipulo_pan: maior ponte 7.4 mm; 10×19×17 mm
OK  11G_manipulo_tilt: maior ponte 7.4 mm; 10×19×17 mm

## Volumes

- 11A_flange_tronco: 24.0 cm³
- 11B_mesa_garfo: 55.0 cm³
- 11C_anel_retencao: 5.8 cm³
- 11D_berco_tilt: 25.9 cm³
- 11E_placa_cabeca: 17.3 cm³
- 11F_manipulo_pan: 2.3 cm³
- 11G_manipulo_tilt: 2.3 cm³

## Fixadores e comprados

- 4 × Parafuso M3 × 10 (11A -> topo do tronco)
- 4 × Inserto térmico M3 no topo do tronco (IF-PESCOÇO)
- 3 × Parafuso M3 × 10 (anel 11C -> cubo)
- 3 × Inserto térmico M3 no cubo (11A)
- 1 × Parafuso com ombro ISO 7379 Ø6 × 65, rosca M5 (eixo do tilt)
- 1 × Porca M5 autotravante + arruela M5
- 2 × Bucha bronze sinterizado 6×10×10 (ou impressa)
- 1 × Calço Ø6×Ø12 0,1/0,2/0,3 mm (jogo)
- 1 × Parafuso M4 × 20 (manípulo pan, radial)
- 1 × Parafuso M4 × 20 (manípulo tilt)
- 2 × Inserto térmico M4 (mesa e montante)
- 4 × Parafuso M3 × 8 escareado (placa 11E -> berço)
- 4 × Inserto térmico M3 no berço
- 4 × Inserto térmico M3 na placa 11E (a cabeça parafusa aqui)
- 1 × Arruela PTFE Ø34.5×Ø52×1 (pan)
- 1 × Arruela de silicone Ø34.5×Ø46×2 (pan)
- 2 × Arruela PTFE Ø6,2×Ø16×1 (tilt, uma de cada lado)
