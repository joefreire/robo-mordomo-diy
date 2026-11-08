# Peças 05 / 06 / 07 — braços V2, bandeja e mãos: relatório

Resultado: **APROVADO** (0 falhas, 0 avisos)

## 1. Sólidos, tamanho e orientação de impressão
OK  05A_metade_interna: válido e 1 corpo
OK  05A_metade_interna: 110×128×18 mm (≤ 220) — plano de divisão na mesa (face do tronco para cima)
OK  05B_metade_externa: válido e 1 corpo
OK  05B_metade_externa: 110×129×22 mm (≤ 220) — plano de divisão na mesa
OK  05C_anel_punho: válido e 1 corpo
OK  05C_anel_punho: 40×40×12 mm (≤ 220) — costas na mesa, face IF-PUNHO para cima
OK  05D_adaptador_v1: válido e 1 corpo
OK  05D_adaptador_v1: 40×70×48 mm (≤ 220) — em pé: fundo plano na mesa, face IF-BANDEJA para cima
OK  06B_cubo: válido e 1 corpo
OK  06B_cubo: 50×50×10 mm (≤ 220) — face da bandeja na mesa (rasgo da chave para cima)
OK  06A_bandeja: válido e 1 corpo
OK  06A_bandeja: 120×120×13 mm (≤ 220) — fundo na mesa (superfície útil para cima)
OK  06C_anel_decorativo: válido e 1 corpo
OK  06C_anel_decorativo: 106×106×2 mm (≤ 220) — deitado
OK  07A_metade_interna: válido e 1 corpo
OK  07A_metade_interna: 40×79×18 mm (≤ 220) — plano de divisão na mesa (face do tronco para cima)
OK  07B_metade_externa: válido e 1 corpo
OK  07B_metade_externa: 40×79×22 mm (≤ 220) — plano de divisão na mesa
OK  07F_friso: válido e 1 corpo
OK  07F_friso: 6×41×2 mm (≤ 220) — deitado
OK  07C_anel_punho: válido e 1 corpo
OK  07C_anel_punho: 40×40×12 mm (≤ 220) — costas na mesa, face IF-PUNHO para cima
OK  07E_mao_luva: válido e 1 corpo
OK  07E_mao_luva: 36×44×56 mm (≤ 220) — face do punho na mesa

## 2. Encaixe braço ↔ lingueta IF-BRAÇO (rotor real 09B/10B)
OK  05: soquete sem interferência com o rotor (0.00 mm³)
OK  05: lado +tangencial: folga entre 0,2 e 0,45 mm (encosta só com 0,45)
OK  05: lado −tangencial: folga entre 0,2 e 0,45 mm (encosta só com 0,45)
OK  05: lado face de fora: folga entre 0,2 e 0,45 mm (encosta só com 0,45)
OK  05: fundo do soquete encosta no topo da lingueta (r=39) com 0,45 mm
OK  05: M3 r=29: furo do braço coaxial ao inserto da lingueta (haste Ø2,9 livre: 0.00 mm³; deslocada 0,7 mm bate)
OK  05: M3 r=35: furo do braço coaxial ao inserto da lingueta (haste Ø2,9 livre: 0.00 mm³; deslocada 0,7 mm bate)
OK  07: soquete sem interferência com o rotor (0.00 mm³)
OK  07: lado +tangencial: folga entre 0,2 e 0,45 mm (encosta só com 0,45)
OK  07: lado −tangencial: folga entre 0,2 e 0,45 mm (encosta só com 0,45)
OK  07: lado face de fora: folga entre 0,2 e 0,45 mm (encosta só com 0,45)
OK  07: fundo do soquete encosta no topo da lingueta (r=39) com 0,45 mm
OK  07: M3 r=29: furo do braço coaxial ao inserto da lingueta (haste Ø2,9 livre: 0.00 mm³; deslocada 0,7 mm bate)
OK  07: M3 r=35: furo do braço coaxial ao inserto da lingueta (haste Ø2,9 livre: 0.00 mm³; deslocada 0,7 mm bate)

## 3. Curso do ombro a cada 15°: colisões (peças do ombro, tronco 185×105×190, base 225×200×70, mesa)
Convenção do validar_ombro.py (furos/batente reais). Bandeja avaliada à parte.
OK  05    +0°: braço + mão livres
OK  05   +15°: braço + mão livres
OK  05   +30°: braço + mão livres
OK  05   +45°: braço + mão livres
OK  05   +60°: braço + mão livres
OK  05: folga mínima braço ↔ tampa/manípulo do ombro no curso: 1.5 mm (≥ 0,5)
OK  07   -30°: braço + mão livres
OK  07   -15°: braço + mão livres
- obs. 07 +0°: toca a CAIXA da base, mas a base real está livre
OK  07    +0°: braço + mão livres
OK  07   +15°: braço + mão livres
OK  07   +30°: braço + mão livres
OK  07   +45°: braço + mão livres
OK  07   +60°: braço + mão livres
OK  07   +75°: braço + mão livres
OK  07   +90°: braço + mão livres
OK  07  +105°: braço + mão livres
OK  07  +120°: braço + mão livres
OK  07: folga mínima braço ↔ tampa/manípulo do ombro no curso: 1.5 mm (≥ 0,5)
- 05 com bandeja: livre em +0°, +15°, +30°, +45°, +60°
OK  05 em 0° (serviço) com bandeja: livre

## 4. IF-PUNHO igual nos dois braços (sondas no referencial H do punho)
OK  05: 3 insertos a (90.0, 200.0, 340.0) r=12.5, chave a 90°, cabo Ø10, 2 M3 do anel e furos da adaptador alinhados (16/16)
OK  07: 3 insertos a (90.0, 200.0, 340.0) r=12.5, chave a 90°, cabo Ø10, 2 M3 do anel e furos da mão alinhados (16/16)
OK  mesma assinatura nos dois punhos (mão, adaptador e garra futura servem nos dois)
OK  padrão assimétrico: a mão girada 20° não encontra os 3 insertos

## 5. Bandeja (Peça 06) na pose de serviço (ombro esquerdo 0°)
OK  fundo da bandeja horizontal: inclinação 0.000°
OK  alcance horizontal (plano do ombro -> centro da bandeja): 145.0 mm (alvo 145)
OK  bandeja centrada sobre o braço (x = -113.5)
- fundo da bandeja a z = 141 mm; segmento horizontal a z = 104 (altura 135 abaixo do eixo do ombro)
- borda de trás da bandeja a 18 mm da frente do tronco
OK  adaptador sai sem desmontar a bandeja: tirar 2×M3 (cubo) + 3×M3 (punho), descer 3,5, afastar 15 do punho (máx. interferência 0.00 mm³); cubo fica preso à bandeja
OK  língua do adaptador entra no rasgo assimétrico do cubo e a face IF-BANDEJA apoia o cubo
OK  cubo girado 180° não monta (chave fora de centro: 268 mm³ de interferência)

## 6. Massa real (PETG 1,27 g/cm³; casca 4 paredes + 15%; entre parênteses = sólido, limite superior)
- 05A_metade_interna: 47 g (47 g)
- 05B_metade_externa: 57 g (57 g)
- 05C_anel_punho: 10 g (14 g)
- 05D_adaptador_v1: 53 g (128 g)
- 06B_cubo: 15 g (24 g)
- 06A_bandeja: 56 g (56 g)
- 06C_anel_decorativo: 3 g (3 g)
- 07A_metade_interna: 25 g (25 g)
- 07B_metade_externa: 30 g (31 g)
- 07F_friso: 0 g (0 g)
- 07C_anel_punho: 10 g (14 g)
- 07E_mao_luva: 28 g (53 g)
- fixadores por braço (estimativa): 12 g

### Momento no eixo do ombro (máximo no curso, passo 1°)
| Lado | Itens | Massa (g) | M real (N·m) | M hipótese HIP (N·m) | Trava ~2,6 N·m |
|---|---|---|---|---|---|
| 05 | braço + adaptador + bandeja (vazia) | 254 | 0.34 (a +51°) | 0.98 | OK |
OK  05 braço + adaptador + bandeja (vazia): momento real 0.34 N·m ≤ trava 2.6 N·m
| 05 | … + 300 g na bandeja | 554 | 0.80 (a +36°) | 0.98 | OK |
OK  05 … + 300 g na bandeja: momento real 0.80 N·m ≤ trava 2.6 N·m
| 07 | braço + mão-luva | 106 | 0.09 (a +90°) | 0.78 | OK |
OK  07 braço + mão-luva: momento real 0.09 N·m ≤ trava 2.6 N·m
| 07 | braço + garra V2 120 g + objeto 100 g (hipóteses HIP) | 298 | 0.42 (a +90°) | 0.78 | OK |
OK  07 braço + garra V2 120 g + objeto 100 g (hipóteses HIP): momento real 0.42 N·m ≤ trava 2.6 N·m
- braço (casca + anel + fixadores): 05 = 126 g, 07 = 78 g (HIP: 180 g)

## 7. Esforços nos M3 com 300 g (estático, × 2 para choque)
OK  IF-PUNHO (05): momento 0.19 N·m na face; tração no M3 de cima ≈ 9 N (com choque ×2); cisalhamento 2.8 N/parafuso; inserto ~400 N -> FS 46.1
OK  IF-BANDEJA: 300 g na borda (r=57) tomba sobre o adaptador: tração máx. ≈ 6 N por M3 (choque ×2) -> FS 62.4; peso apoiado na face, não nos parafusos
- IF-PUNHO (07, luva): momento máx. 0.007 N·m (desprezível)

## 8. Canal de cabos contínuo (feixe de teste Ø6 da entrada no ombro até a face do punho)
OK  05: feixe Ø6 passa da entrada (r=58) pelas presilhas até a face do punho sem tocar torres/paredes (0.00 mm³)
OK  07: feixe Ø6 passa da entrada (r=58) pelas presilhas até a face do punho sem tocar torres/paredes (0.40 mm³)
OK  07: espaço livre 20×12×25 mm para conector removível antes da parede do punho (0.00 mm³)

## 9. Imprimibilidade (vão sem apoio = 2 × raio inscrito das regiões voltadas para baixo > 60°; limite ~12 mm)
OK  05A_metade_interna: maior vão sem apoio 11.7 mm (ponte/balanço > 60°, área 1842 mm²), sem suporte — plano de divisão na mesa (face do tronco para cima)
OK  05B_metade_externa: maior vão sem apoio 11.7 mm (ponte/balanço > 60°, área 1842 mm²), sem suporte — plano de divisão na mesa
OK  05C_anel_punho: maior vão sem apoio 0.0 mm (ponte/balanço > 60°, área 0 mm²), sem suporte — costas na mesa, face IF-PUNHO para cima; 4 paredes, 40% (insertos)
OK  05D_adaptador_v1: maior vão sem apoio 8.4 mm (ponte/balanço > 60°, área 84 mm²), sem suporte — em pé: fundo plano na mesa, face IF-BANDEJA para cima; 4 paredes, 25% (insertos)
OK  06B_cubo: maior vão sem apoio 4.0 mm (ponte/balanço > 60°, área 13 mm²), sem suporte — face da bandeja na mesa (rasgo da chave para cima); 4 paredes, 40% (insertos)
OK  06A_bandeja: maior vão sem apoio 0.0 mm (ponte/balanço > 60°, área 0 mm²), sem suporte — fundo na mesa (superfície útil para cima)
OK  06C_anel_decorativo: maior vão sem apoio 0.0 mm (ponte/balanço > 60°, área 0 mm²), sem suporte — deitado
OK  07A_metade_interna: maior vão sem apoio 11.7 mm (ponte/balanço > 60°, área 584 mm²), sem suporte — plano de divisão na mesa (face do tronco para cima)
OK  07B_metade_externa: maior vão sem apoio 11.7 mm (ponte/balanço > 60°, área 584 mm²), sem suporte — plano de divisão na mesa
OK  07F_friso: maior vão sem apoio 0.0 mm (ponte/balanço > 60°, área 0 mm²), sem suporte — deitado
OK  07C_anel_punho: maior vão sem apoio 0.0 mm (ponte/balanço > 60°, área 0 mm²), sem suporte — costas na mesa, face IF-PUNHO para cima; 4 paredes, 40% (insertos)
OK  07E_mao_luva: maior vão sem apoio 10.0 mm (ponte/balanço > 60°, área 79 mm²), sem suporte — face do punho na mesa; 3 paredes, 15%
- teto da cavidade em gota (52° da vertical): ponte 11.7 mm

## Fixadores (por braço)

- 2 × Parafuso M3 × 10 (braço -> lingueta do ombro, de fora)
- 4 (05) / 3 (07) × Parafuso M3 × 16 (torres: metade interna -> externa)
- 4 (05) / 3 (07) × Inserto térmico M3 (torres, metade externa)
- 2 × Pino Ø3 × 10 (aço ou filamento 3 mm) — alinhamento das metades
- 2 × Parafuso M3 × 12 (anel do punho -> braço)
- 2 × Inserto térmico M3 (ponta do braço, anel do punho)
- 3 × Inserto térmico M3 (anel do punho, IF-PUNHO)
- 3 × Parafuso M3 × 10 (mão/adaptador -> IF-PUNHO)
- 06: 3 × Parafuso M3 × 8 cabeça chata (bandeja -> cubo, de cima)
- 06: 3 × Inserto térmico M3 no cubo (bandeja)
- 06: 2 × Inserto térmico M3 no cubo (IF-BANDEJA)
- 06: 2 × Parafuso M3 × 12 (adaptador -> cubo, por baixo)
