# Cabeça (C05 + C06 + M05 + M07 + antena + orelhas): relatório

Resultado: **APROVADO** (0 falhas)

## 1. Sólidos
OK  C05_cabeca_frente: válido e 1 corpo
OK  C06_cabeca_traseira: válido e 1 corpo
OK  M05_tampa_facial: válido e 1 corpo
OK  M07_tampao_camera: válido e 1 corpo
OK  CA1_antena: válido e 1 corpo
OK  CA2_orelha_esquerda: válido e 1 corpo
OK  CA3_orelha_direita: válido e 1 corpo

## 2. Frente + traseira fecham (e acessórios encaixam) sem interferência
OK  C05_cabeca_frente × C06_cabeca_traseira: interferência 0.00 mm³
OK  M05_tampa_facial × C05_cabeca_frente: interferência 0.00 mm³
OK  M07_tampao_camera × C05_cabeca_frente: interferência 0.00 mm³
OK  CA1_antena × C06_cabeca_traseira: interferência 0.00 mm³
OK  CA2_orelha_esquerda × C06_cabeca_traseira: interferência 0.00 mm³
OK  CA3_orelha_direita × C06_cabeca_traseira: interferência 0.00 mm³
OK  M05_tampa_facial × C06_cabeca_traseira: interferência 0.00 mm³
OK  as duas metades se tocam no plano y=35 (área ≈ 2056 / 2097 mm²)
OK  frente ∪ traseira reconstrói a casca (373 cm³ com reforços; casca lisa 306 cm³)
OK  união (-85, z17): furo M3 da traseira alinhado com o inserto da frente; túnel Ø7 aberto atrás
OK  união (-85, z128): furo M3 da traseira alinhado com o inserto da frente; túnel Ø7 aberto atrás
OK  união (+85, z17): furo M3 da traseira alinhado com o inserto da frente; túnel Ø7 aberto atrás
OK  união (+85, z128): furo M3 da traseira alinhado com o inserto da frente; túnel Ø7 aberto atrás
OK  pino de alinhamento (+45, z138) Ø4 em furo Ø4.6 da traseira
OK  pino de alinhamento (-45, z7) Ø4 em furo Ø4.6 da traseira

## 3. IF-CABEÇA contra a placa 11E REAL (pan 0 / tilt 0)
OK  face de cima da placa (sem pinos) em z=356.0 = Z_IF_CABECA 356
OK  fundo da cabeça em z=356.00
OK  placa (com os 2 pinos Ø4×3) × traseira: 0.000 mm³ (pinos entram nos furos Ø4.3)
OK  apoio plano: 2507 mm² de contato de 2589 mm² da face da placa (97 %; o resto é o furo Ø18 > Ø16 e a base dos pinos) — PETG rígido direto, nada macio
OK  M3 (-22,-17): passante Ø3.4 no eixo do inserto; parafuso M3×10 = 6 fundo + 4 no inserto M3×4
OK     acesso por dentro: coluna Ø9 × 60 acima da cabeça do parafuso livre na traseira
OK  M3 (-22,+17): passante Ø3.4 no eixo do inserto; parafuso M3×10 = 6 fundo + 4 no inserto M3×4
OK     acesso por dentro: coluna Ø9 × 60 acima da cabeça do parafuso livre na traseira
OK  M3 (+22,-17): passante Ø3.4 no eixo do inserto; parafuso M3×10 = 6 fundo + 4 no inserto M3×4
OK     acesso por dentro: coluna Ø9 × 60 acima da cabeça do parafuso livre na traseira
OK  M3 (+22,+17): passante Ø3.4 no eixo do inserto; parafuso M3×10 = 6 fundo + 4 no inserto M3×4
OK     acesso por dentro: coluna Ø9 × 60 acima da cabeça do parafuso livre na traseira
OK  pino (+0,+19): furo Ø4.3 × 3.5 (pino Ø4 × 3)
OK  pino (+0,-19): furo Ø4.3 × 3.5 (pino Ø4 × 3)
OK  furo de cabos Ø18 ≥ Ø16, concêntrico
OK  IF-CABEÇA inteira na traseira (almofada até y=31 < divisão 35)

## 4. Acesso aos parafusos
OK  união (-85, z17): túnel Ø7 de 89 mm aberto nas costas (cabeça M3 Ø5,5 + chave 2,5 longa)
OK  união (-85, z128): túnel Ø7 de 89 mm aberto nas costas (cabeça M3 Ø5,5 + chave 2,5 longa)
OK  união (+85, z17): túnel Ø7 de 89 mm aberto nas costas (cabeça M3 Ø5,5 + chave 2,5 longa)
OK  união (+85, z128): túnel Ø7 de 89 mm aberto nas costas (cabeça M3 Ø5,5 + chave 2,5 longa)
OK  orelha esq (+0, z86): 30 mm livres por dentro para a chave
OK  orelha esq (-12, z66): 30 mm livres por dentro para a chave
OK  orelha esq (+12, z66): 30 mm livres por dentro para a chave
OK  orelha dir (+0, z86): 30 mm livres por dentro para a chave
OK  orelha dir (-12, z66): 30 mm livres por dentro para a chave
OK  orelha dir (+12, z66): 30 mm livres por dentro para a chave
OK  antena: parafuso M3 por dentro, 40 mm livres embaixo do soquete
OK  moldura/M05 (-59.7, z19.8): M3 cabeça chata pela frente, inserto colocado por dentro do assento
OK  moldura/M05 (-59.7, z104.2): M3 cabeça chata pela frente, inserto colocado por dentro do assento
OK  moldura/M05 (+59.7, z19.8): M3 cabeça chata pela frente, inserto colocado por dentro do assento
OK  moldura/M05 (+59.7, z104.2): M3 cabeça chata pela frente, inserto colocado por dentro do assento

## 5. Envelopes de tela e câmera
OK  tela: envelope 110×75×20 livre (abre pela frente; rebaixo 128.6×93.6)
OK  4 bosses M3 da bandeja fora do envelope, topo em y=40 (fundo do envelope)
OK  câmera: furo Ø12 na testa (z local 126, acima da tela) + reserva 26×24×22 livre (PROPOSTA)
OK  câmera acima do rebaixo da tela

## 6. Caminho interno de cabos (tubo Ø10)
OK  furo da IF -> atrás da tela -> atrás da câmera: livre (0.00 mm³); 2 alças de abraçadeira ao lado do furo

## 7. Pan ±90° × tilt ±30° com o pescoço REAL e a caixa do tronco
OK  pan -90° tilt -30°: livre
OK  pan -90° tilt  +0°: livre
OK  pan -90° tilt +30°: livre
OK  pan  +0° tilt -30°: livre
OK  pan  +0° tilt  +0°: livre
OK  pan  +0° tilt +30°: livre
OK  pan +90° tilt -30°: livre
OK  pan +90° tilt  +0°: livre
OK  pan +90° tilt +30°: livre
OK  ponto mais baixo da cabeça em qualquer pose: 42 mm acima do topo do tronco (gravata ainda não modelada: conferir quando existir)

## 8. Massa, centro de massa e momento no tilt
- C05_cabeca_frente: 111.6 cm³ × 100% -> 142 g
- C06_cabeca_traseira: 260.9 cm³ × 100% -> 331 g
- M05_tampa_facial: 40.2 cm³ × 90% -> 46 g
- M07_tampao_camera: 0.7 cm³ × 100% -> 1 g
- CA1_antena: 2.7 cm³ × 100% -> 3 g
- CA2_orelha_esquerda: 22.1 cm³ × 50% -> 14 g
- CA3_orelha_direita: 22.1 cm³ × 50% -> 14 g
- tela 60 g (centro do envelope), câmera 30 g (centro da reserva), fixadores 25 g
- **total 666 g**; CG em (x +0.0, y +10.9, z 427) = **92 mm acima do eixo do tilt e +10.9 mm à frente** (hipótese do validar_pescoco: 450 g, 96 mm, +10 mm)
- momento no tilt a 30° (pior lado): **0.36 N·m** (hipótese 0.25 N·m)
OK  trava do tilt (pino de indexação) ~1.32 N·m ≥ 1,5 × 0.36 N·m (margem 3.6×)
- massa +216 g em relação à hipótese: a casca lisa (306 cm³ = 389 g) é a maior parte; parede de 2,0 mm tiraria ~65 g

## 9. Altura total
OK  topo da antena em z = 550.0 mm (meta 550): cabeça 356->501 + antena 49

## 10. Imprimibilidade (A1, PETG, sem suporte)
OK  C05_cabeca_frente: 205×145×30 mm na mesa; face da frente na mesa (chanfro 45° e assentos de canto sem suporte); maior vão 8 mm (assentos de canto: balanço ancorado em 2 paredes, ≤ 8 mm do apoio; resto em pé)
OK  C06_cabeca_traseira: 205×145×95 mm na mesa; costas na mesa, aberta para cima (paredes em pé; túneis verticais); maior vão 0 mm (paredes em pé; almofada, blocos dos pinos e boss da antena com chanfro/gota 45°; túneis verticais)
OK  M05_tampa_facial: 128×93×10 mm na mesa; lábio na mesa, rosto para CIMA; trocar filamento na 1ª camada do relevo; maior vão 0 mm (placa; escareados para cima)
OK  M07_tampao_camera: 18×18×6 mm na mesa; flange na mesa, garras para cima; maior vão 0.5 mm (garra 0,5 mm em rampa)
OK  CA1_antena: 14×14×58 mm na mesa; em pé, pino na mesa (bolinha com cone 45°); maior vão 0 mm (cone 45° sob a bolinha e sob o colar (assenta no escareado))
OK  CA2_orelha_esquerda: 50×50×12 mm na mesa; face de encosto na mesa, anel para cima; maior vão 0 mm (anel em cima)
OK  CA3_orelha_direita: 50×50×12 mm na mesa; face de encosto na mesa, anel para cima; maior vão 0 mm (anel em cima)
OK  parede 2.4 mm (≥ 5 perímetros de 0,42)

## Orientação de impressão (STL já exportado assim)

- C05_cabeca_frente: face da frente na mesa (chanfro 45° e assentos de canto sem suporte)
- C06_cabeca_traseira: costas na mesa, aberta para cima (paredes em pé; túneis verticais)
- M05_tampa_facial: lábio na mesa, rosto para CIMA; trocar filamento na 1ª camada do relevo
- M07_tampao_camera: flange na mesa, garras para cima
- CA1_antena: em pé, pino na mesa (bolinha com cone 45°)
- CA2_orelha_esquerda: face de encosto na mesa, anel para cima
- CA3_orelha_direita: face de encosto na mesa, anel para cima

## Fixadores

- 4 × Parafuso M3 × 10 cabeça cilíndrica (cabeça -> placa 11E, por dentro, de cima)
- 4 × Parafuso M3 × 12 cabeça cilíndrica (união traseira -> frente, por trás, chave longa ≥ 100 mm)
- 4 × Inserto térmico M3 (frente: união)
- 4 × Parafuso M3 × 10 cabeça chata DIN 7991 (M05 / moldura)
- 4 × Inserto térmico M3 (frente: assentos da moldura, por dentro)
- 4 × Inserto térmico M3 (frente: bosses da bandeja da tela — V2)
- 2 × Inserto térmico M3 (frente: bosses do suporte da câmera — V2)
- 1 × Parafuso M3 × 8 (antena, por dentro) + inserto M3 na antena
- 6 × Parafuso M3 × 10 (orelhas, por dentro) + inserto M3 na orelha
- 1 × Abraçadeira de nylon 2,5 mm (amarração no fundo)
