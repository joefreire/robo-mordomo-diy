# Peça 01R — base com rodas (V2): relatório

Resultado: **APROVADO** (0 falhas)

## 1. Sólido
OK  01R válido e 1 corpo
OK  01R 224×199×19 mm cabe na A1 (256)

## 2. IF-BASE idêntica à Peça 01 (borda, contorno, torres)
OK  contorno e borda (z 21–25, faixa de 12 mm junto à parede) iguais à 01: diferença 0.00 mm³ (abaixo disso a 01R tem, de propósito, a janela de IR e os furos dos contatos na traseira)
OK  M3 de união (-70,-84) atravessa a torre da 01R livre (mesmo eixo da 01 e do inserto da 02)
OK  M3 de união (-70,+84) atravessa a torre da 01R livre (mesmo eixo da 01 e do inserto da 02)
OK  M3 de união (+70,-84) atravessa a torre da 01R livre (mesmo eixo da 01 e do inserto da 02)
OK  M3 de união (+70,+84) atravessa a torre da 01R livre (mesmo eixo da 01 e do inserto da 02)
OK  01R × 02 sem interferência (0.00 mm³)
OK  borda em z = 25.0 (= 01): altura do robô não muda
OK  fundo 6.0 mm acima da mesa

## 3. Envelopes V2 (rodas, motores, rodízios, bateria, driver) livres
OK  roda_esq: livre
OK  motor_esq: livre
OK  roda_dir: livre
OK  motor_dir: livre
OK  rodizio_0: livre
OK  rodizio_1: livre
OK  rodizio_2: livre
OK  rodizio_3: livre
OK  bateria: livre
OK  driver: livre
OK  carregador: livre
OK  roda_esq toca a mesa (z mín 0.00)
OK  roda_dir toca a mesa (z mín 0.00)
OK  4 rodízios 1 mm acima da mesa: as rodas sempre tracionam; ao inclinar o robô apoia neles
- roda Ø48: topo em z 48; folga ao teto da 02 conferida acima (sem interferência)

## 4. Estabilidade sobre rodas (polígono: 2 rodas + 2 rodízios)
- (hipótese) bateria 2×18650 + suporte: 110 g embaixo
- (hipótese) 2 motores N20 com redução: 40 g embaixo
- (hipótese) 2 rodas: 30 g embaixo
- (hipótese) 4 rodízios: 40 g embaixo
- (hipótese) driver dos motores: 25 g embaixo
- (hipótese) placa de carga: 15 g embaixo
- (hipótese) servo da cintura: 55 g em cima
- (hipótese) 2 servos dos ombros: 110 g em cima
- (hipótese) 2 servos pan/tilt: 40 g em cima
- (hipótese) tela do peito 3,5": 40 g em cima
- (hipótese) ESP32-S3 + áudio + fiação: 70 g em cima
OK  V2 repouso, bandeja vazia: 2155 g, CG (-8, +5, 176) 57 mm dentro do apoio; tomba com ~18°
OK  V2 bandeja com 300 g: 2455 g, CG (-21, +20, 176) 40 mm dentro do apoio; tomba com ~13°
OK  V2 braço esq. +60° e 300 g: 2455 g, CG (-21, +25, 208) 39 mm dentro do apoio; tomba com ~11°

## 5. Doca de carga (robô encaixado de ré)
OK  doca 250×100×32 mm cabe na A1
OK  doca × base, rodas, rodízios, braços, mão e bandeja: livre
OK  contato de mola passa 4.0 mm da face traseira; o rebaixo do contato tem 1.5 mm -> compressão ~2.5 mm sobre a placa de cobre
OK  pontas dos contatos batem só na placa de cobre do rebaixo (x ±30, z 14): 22.5 mm³ ≈ compressão prevista 62.8 mm³
OK  IR: emissor da doca e janela do robô no mesmo eixo (x 0, z 16)
- captura lateral das guias em V: ±9.5 mm na entrada (o IR faz o resto do alinhamento)
