# Peças 03 + 04 — tronco traseiro e frontal: relatório

Resultado: **APROVADO** (0 falhas)


## 1. Sólidos
OK  03A_tronco_traseiro: válido e 1 corpo
OK  03B_painel_traseiro: válido e 1 corpo
OK  04A_tronco_frontal: válido e 1 corpo
OK  04B_moldura_tela: válido e 1 corpo
OK  04C_bandeja_tela: válido e 1 corpo
OK  04D_tampa_manutencao: válido e 1 corpo
OK  04E_painel_decorativo_M06: válido e 1 corpo

## 2. Forma e interfaces da traseira (esqueleto)
OK  traseira de y=-52.5 a +22.5 (divisão +22.5)
OK  z 94.0..284.0 (piso 94, topo 284, altura 190)
OK  largura 185.0 (ombros 185); base 150 (TRONCO_LARG_BASE 150)
OK  IF-CINTURA: piso plano em z=94 cheio sobre a 08B (Ø90), 2716 mm² de apoio
OK  IF-OMBRO esquerda: face Ø56 plana e cheia em x=-92.5
OK  IF-OMBRO esquerda: nada passa de x=-92.5 (face ⟂ X)
OK  IF-OMBRO direita: face Ø56 plana e cheia em x=+92.5
OK  IF-OMBRO direita: nada passa de x=+92.5 (face ⟂ X)
OK  IF-PESCOÇO: prateleira Ø66 plana em z=284 (parte em y>+22.5 é a frontal, rebaixada 0,3)
OK  frontal não encosta na flange do pescoço (alívio 0,3): a carga vai só para a traseira
OK  frontal não apoia na 08B (alívio 0,3 no piso): a carga vai só para a traseira

## 3. Traseira × frontal: fechamento, folgas, união acessível
OK  03 × 04 sem interferência (0.00 mm³)
OK  traseira: borda de união com a casca inteira em y=+22.5 (sem degrau; falta -0.00 mm³)
OK  frontal: borda de união com a casca inteira em y=+22.5 (sem degrau; falta -0.00 mm³)
OK  pinos Ø4×5 em furos Ø4.6×6 (folga 0.3/lado, fundo livre 1 mm)
OK  união M3 (-54, 104): chave Ø6 entra reto pelas costas até o assento (y=+12), haste alinhada com o inserto da 04 (100% de material em volta)
OK  união M3 (+54, 104): chave Ø6 entra reto pelas costas até o assento (y=+12), haste alinhada com o inserto da 04 (100% de material em volta)
OK  união M3 (-66, 165): chave Ø6 entra reto pelas costas até o assento (y=+12), haste alinhada com o inserto da 04 (100% de material em volta)
OK  união M3 (+66, 165): chave Ø6 entra reto pelas costas até o assento (y=+12), haste alinhada com o inserto da 04 (100% de material em volta)
OK  união M3 (-45, 276): chave Ø6 entra reto pelas costas até o assento (y=+12), haste alinhada com o inserto da 04 (100% de material em volta)
OK  união M3 (+45, 276): chave Ø6 entra reto pelas costas até o assento (y=+12), haste alinhada com o inserto da 04 (100% de material em volta)
OK  M3 × 16 cabeça cilíndrica (ISO 4762): aperta 10.5 mm de traseira e rosca 5.5 mm no inserto

## 4. Montagem com a cintura REAL (Peça 08), giro −60° / 0° / +60°
OK  giro -60°: tronco × cintura sem colisão
OK  giro +0°: tronco × cintura sem colisão
OK  giro +60°: tronco × cintura sem colisão
OK  piso da traseira apoiado na 08B (distância 0.000 mm)
OK  M4 (-35,-15): furo do piso alinhado com o inserto da 08B
OK  M4 (-35,-15): cabeça Ø7 assenta e chave/soquete Ø10 desce na vertical (livre até z=165)
OK  M4 (-35,+15): furo do piso alinhado com o inserto da 08B
OK  M4 (-35,+15): cabeça Ø7 assenta e chave/soquete Ø10 desce na vertical (livre até z=165)
OK  M4 (+35,-15): furo do piso alinhado com o inserto da 08B
OK  M4 (+35,-15): cabeça Ø7 assenta e chave/soquete Ø10 desce na vertical (livre até z=165)
OK  M4 (+35,+15): furo do piso alinhado com o inserto da 08B
OK  M4 (+35,+15): cabeça Ø7 assenta e chave/soquete Ø10 desce na vertical (livre até z=165)
OK  parafusos do anel 08C alcançáveis pela abertura Ø56 do piso

## 5. Montagem com os ombros REAIS (Peças 09 e 10) + gabarito do braço, curso completo
OK  ombro esquerdo: flange/tampa/manípulo sem colisão com o tronco
OK  ombro esquerdo: flange 09A apoiada na face plana (distância 0.000 mm)
OK  ombro esquerdo: M3 (y=-0.9, z=253.1) — furo da 09A alinhado com o inserto do tronco
OK  ombro esquerdo: M3 (y=-29.1, z=253.1) — furo da 09A alinhado com o inserto do tronco
OK  ombro esquerdo: M3 (y=-29.1, z=224.9) — furo da 09A alinhado com o inserto do tronco
OK  ombro esquerdo: M3 (y=-0.9, z=224.9) — furo da 09A alinhado com o inserto do tronco
OK  ombro esquerdo: curso +0°..+60° (a cada 15°) sem bater no tronco; menor folga braço–tronco 7.0 mm
OK  ombro esquerdo: envelope do servo inteiro dentro da cavidade (a casca não precisa ser cortada)
OK  envelope do servo V2 (50×60×45, x de ±47.5 a ±83; a placa e os bosses ocupam o resto) livre: 0.00 mm³
OK  ombro direito: flange/tampa/manípulo sem colisão com o tronco
OK  ombro direito: flange 10A apoiada na face plana (distância 0.000 mm)
OK  ombro direito: M3 (y=-0.9, z=253.1) — furo da 10A alinhado com o inserto do tronco
OK  ombro direito: M3 (y=-29.1, z=253.1) — furo da 10A alinhado com o inserto do tronco
OK  ombro direito: M3 (y=-29.1, z=224.9) — furo da 10A alinhado com o inserto do tronco
OK  ombro direito: M3 (y=-0.9, z=224.9) — furo da 10A alinhado com o inserto do tronco
OK  ombro direito: curso -30°..+120° (a cada 15°) sem bater no tronco; menor folga braço–tronco 7.0 mm
OK  ombro direito: envelope do servo inteiro dentro da cavidade (a casca não precisa ser cortada)
OK  envelope do servo V2 (50×60×45, x de ±47.5 a ±83; a placa e os bosses ocupam o resto) livre: 0.00 mm³

## 6. Montagem com o pescoço REAL (Peça 11), pan ±90° × tilt ±30°
OK  pescoço em todas as 9 combinações sem bater no tronco
OK  cabeça (caixa 205×120×145) fica a ≥ 42 mm do tronco em todas as poses
OK  flange 11A apoiada na prateleira da traseira (distância 0.000 mm)
OK  pescoço M3 (-22,-15): furo da 11A alinhado com o inserto do tronco
OK  pescoço M3 (-22,+15): furo da 11A alinhado com o inserto do tronco
OK  pescoço M3 (+22,-15): furo da 11A alinhado com o inserto do tronco
OK  pescoço M3 (+22,+15): furo da 11A alinhado com o inserto do tronco

## 7. Frontal: tela do peito, moldura, bandeja, tampa, gravata
OK  envelope da tela 100×70×25 cabe (y +25.5..+50.5, centro z=214): 0.00 mm³
OK  a tela sai pela frente com a moldura tirada (troca sem abrir o tronco)
OK  moldura 04B encaixa sem interferência (0.00 mm³)
OK  painel M06 encaixa sem interferência (0.00 mm³)
OK  bandeja 04C encaixa sem interferência (0.00 mm³)
OK  tampa 04D encaixa sem interferência (0.00 mm³)
OK  painel 03B encaixa sem interferência (0.00 mm³)
OK  moldura/M06: 4×M3 alinhados com os insertos da frontal
OK  bandeja: 4×M3 alinhados com os insertos da frontal
OK  tampa: 4×M3 alinhados com os insertos da frontal
OK  gravata: 2×M3 alinhados com os insertos da frontal
OK  painel 03B: M3 (-32,175) alinhado com o inserto
OK  painel 03B: M3 (-32,245) alinhado com o inserto
OK  painel 03B: M3 (+32,175) alinhado com o inserto
OK  painel 03B: M3 (+32,245) alinhado com o inserto
OK  material entre os rebaixos da tela e da tampa: 11.4 mm (entre as aberturas: 30.0 mm)
OK  material abaixo da tampa: 9.7 mm
OK  gravata: insertos em z=268, 16 mm abaixo do topo; 5.7 mm de material entre o furo e o rebaixo da moldura
OK  moldura inteira na região plana da frente (impressão de frente na mesa)

## 8. Bandeja do ESP32, alto-falante, trilhos
OK  zona da bandeja do ESP32 livre (100×32×30, presa nos trilhos; abertura do painel atrás = USB-C)
OK  superfície do alto-falante Ø50 × 20 livre por dentro (grade Ø40)
OK  2 trilhos × 10 insertos M3, passo 10 (z 165..255)

## 9. Espessuras (do CAD e dos parâmetros)
OK  parede mínima entre o envelope do servo e a superfície externa: 3.53 mm (bordas do envelope em x = ±83)
OK  parede geral 3 mm
OK  moldura do painel traseiro: rebaixo 1.5 por fora + 1.5 por dentro = parede de 3
OK  fundo do rebaixo da moldura 5 mm; da tampa 3.5 mm
OK  IF-OMBRO: placa 6 + boss 3.5 para inserto de 6.5
OK  IF-PESCOÇO: 12 mm sob a prateleira (inserto 6.5)
OK  paredes em volta dos insertos ≥ 2 mm (boss 2.5; tubo da união 2.25)
OK  piso 5 mm + 4 nervuras de 4×10

## 10. Imprimibilidade (orientação de impressão, balanços > 44°, maior vão por região)
OK  03A_tronco_traseiro (de costas na mesa): 2724 mm² voltados para baixo; maiores vãos 7.5 (z 2), 4.0 (z 8), 4.0 (z 8) mm (≤ 12 sem suporte)
OK  03A_tronco_traseiro: 185 × 190 × 75 mm na mesa (≤ 220; A1 256)
OK  03B_painel_traseiro (face externa na mesa): 0 mm² voltados para baixo; maiores vãos — mm (≤ 12 sem suporte)
OK  03B_painel_traseiro: 76 × 82 × 4 mm na mesa (≤ 220; A1 256)
OK  04A_tronco_frontal (de frente na mesa): 5565 mm² voltados para baixo; maiores vãos 11.8 (z 2), 7.5 (z 2), 4.0 (z 9) mm (≤ 12 sem suporte)
OK  04A_tronco_frontal: 185 × 190 × 35 mm na mesa (≤ 220; A1 256)
OK  04B_moldura_tela (costas na mesa): 0 mm² voltados para baixo; maiores vãos — mm (≤ 12 sem suporte)
OK  04B_moldura_tela: 122 × 92 × 4 mm na mesa (≤ 220; A1 256)
OK  04C_bandeja_tela (deitada): 0 mm² voltados para baixo; maiores vãos — mm (≤ 12 sem suporte)
OK  04C_bandeja_tela: 124 × 70 × 3 mm na mesa (≤ 220; A1 256)
OK  04D_tampa_manutencao (face externa na mesa): 0 mm² voltados para baixo; maiores vãos — mm (≤ 12 sem suporte)
OK  04D_tampa_manutencao: 92 × 52 × 2 mm na mesa (≤ 220; A1 256)
OK  04E_painel_decorativo_M06 (costas na mesa): 0 mm² voltados para baixo; maiores vãos — mm (≤ 12 sem suporte)
OK  04E_painel_decorativo_M06: 122 × 92 × 4 mm na mesa (≤ 220; A1 256)
OK  03A_tronco_traseiro: anéis de sacrifício presentes no arquivo de impressão (297 mm³) -> as faixas dos rebaixos viram ponte
OK  04A_tronco_frontal: anéis de sacrifício presentes no arquivo de impressão (996 mm³) -> as faixas dos rebaixos viram ponte
- Anéis de sacrifício (0.8 mm) nas bordas das aberturas do painel 03B, da moldura e da tampa: cortar com estilete depois de imprimir (sem eles a faixa do rebaixo seria um balanço solto).

## 11. Volume e massa (PETG 1,27 g/cm³, peça maciça = limite superior)
- 03A_tronco_traseiro: 328.7 cm³ → 418 g
- 03B_painel_traseiro: 9.4 cm³ → 12 g
- 04A_tronco_frontal: 152.8 cm³ → 194 g
- 04B_moldura_tela: 21.3 cm³ → 27 g
- 04C_bandeja_tela: 19.1 cm³ → 24 g
- 04D_tampa_manutencao: 11.6 cm³ → 15 g
- 04E_painel_decorativo_M06: 39.5 cm³ → 50 g
- **total 740 g** (com 3 mm de parede, 4 paredes + 20 % giroide fica perto disso: a casca é quase toda perímetro)

## Fixadores e comprados

- 36 × Inserto térmico M3 (4 IF-OMBRO esq. + 4 dir. + 4 IF-PESCOÇO + 20 trilhos + 4 painel)
- 4 × Parafuso M4 × 12 cabeça cilíndrica (tronco -> insertos da 08B), de cima, por dentro
- 6 × Parafuso M3 × 16 cabeça cilíndrica (ISO 4762) (união 03 -> 04, POR TRÁS; chave Allen 2,5 longa ≥ 75 mm)
- 4 × Parafuso M3 × 6 cabeça abaulada ISO 7380 (painel 03B)
- 20 × Inserto térmico M3 (6 união + 4 moldura + 4 bandeja + 4 tampa + 2 gravata)
- 4 × Parafuso M3 × 8 cabeça abaulada ISO 7380 (moldura 04B ou painel M06, de frente)
- 4 × Parafuso M3 × 6 cabeça cilíndrica (bandeja 04C, por dentro)
- 4 × Parafuso M3 × 6 cabeça abaulada ISO 7380 (tampa 04D, de frente)
- 2 × Parafuso M3 × 8 (gravata, de frente; conferir com a gravata)
