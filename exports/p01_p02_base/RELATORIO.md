# Peças 01 e 02 (base) — relatório de validação

Resultado: **APROVADO** (0 falhas)

## 1. Sólidos
OK  01_base_inferior: válido e 1 corpo
OK  01P_presilha: válido e 1 corpo
OK  02_base_superior: válido e 1 corpo
OK  02L_difusor_cego: válido e 1 corpo

## 2. Alturas da pilha
OK  topo da 01 em z = 25.00 (P01_ALTURA 25)
OK  topo da 02 em z = 70.00 = 25 + 45 = Z_TOPO_P02 70
OK  ponto mais baixo da 02 (aba/bosses) z = 22.00 = Z_JUNTA 22
OK  borda de cima da 01 contínua (sólida no meio da frente, z 24,9)

## 3. Encaixe 01 ↔ 02
OK  01 × 02 sem interferência (0.00 mm³)
OK  folga aba × parede da 01 = 0.298 mm na normal (0,3 na horizontal → 0.298)
OK  02 apoia na borda da 01 em (+70,+96) (as duas sólidas a ±0,1 de z=25)
OK  02 apoia na borda da 01 em (+30,-96) (as duas sólidas a ±0,1 de z=25)
OK  02 apoia na borda da 01 em (+108,+0) (as duas sólidas a ±0,1 de z=25)
OK  02 apoia na borda da 01 em (-108,+0) (as duas sólidas a ±0,1 de z=25)

## 4. Torres (01) × bosses (02) e parafusos M3 por baixo
OK  (-70,-84): furo da torre e furo do inserto no mesmo eixo
OK  (-70,-84): vão torre→boss 0.20 (borda é o apoio)
OK  (-70,-84): parafuso M3×25 livre na 01 e na 02 (0.00 mm³)
OK  (-70,-84): rebaixo aberto por baixo (chave entra virando o robô)
OK  (-70,+84): furo da torre e furo do inserto no mesmo eixo
OK  (-70,+84): vão torre→boss 0.20 (borda é o apoio)
OK  (-70,+84): parafuso M3×25 livre na 01 e na 02 (0.00 mm³)
OK  (-70,+84): rebaixo aberto por baixo (chave entra virando o robô)
OK  (+70,-84): furo da torre e furo do inserto no mesmo eixo
OK  (+70,-84): vão torre→boss 0.20 (borda é o apoio)
OK  (+70,-84): parafuso M3×25 livre na 01 e na 02 (0.00 mm³)
OK  (+70,-84): rebaixo aberto por baixo (chave entra virando o robô)
OK  (+70,+84): furo da torre e furo do inserto no mesmo eixo
OK  (+70,+84): vão torre→boss 0.20 (borda é o apoio)
OK  (+70,+84): parafuso M3×25 livre na 01 e na 02 (0.00 mm³)
OK  (+70,+84): rebaixo aberto por baixo (chave entra virando o robô)
OK  M3×25: entra 6.5 mm acima da junta (inserto 5.7, furo 8)
OK  cabeça M3 embutida 0.5 mm no fundo
OK  pé (-88,-68): 13.3 mm do rebaixo M3, 16.6 mm da borda
OK  pé (-88,+68): 13.3 mm do rebaixo M3, 16.6 mm da borda
OK  pé (+88,-68): 13.3 mm do rebaixo M3, 16.6 mm da borda
OK  pé (+88,+68): 13.3 mm do rebaixo M3, 16.6 mm da borda

## 5. Contrapeso e presilhas
OK  placa 180×150×3 × 01: 0.00 mm³
OK  placa 180×150×3 × 02: 0.00 mm³
OK  placa 180×150×3 × difusor: 0.00 mm³
OK  torre a 3.0 mm da placa deslocada até a guia (mín. 2)
OK  folga placa × guias/bosses 1.00 mm
OK  presilha 0: sem interferência com 01/placa/02/difusor (0.00 mm³)
OK  presilha 0: pé encosta na placa (aperta)
OK  presilha 0: parafuso M3 × 8 cabeça cilíndrica livre (0.00 mm³)
OK  presilha 1: sem interferência com 01/placa/02/difusor (0.00 mm³)
OK  presilha 1: pé encosta na placa (aperta)
OK  presilha 1: parafuso M3 × 8 cabeça cilíndrica livre (0.00 mm³)
OK  presilha 2: sem interferência com 01/placa/02/difusor (0.00 mm³)
OK  presilha 2: pé encosta na placa (aperta)
OK  presilha 2: parafuso M3 × 8 cabeça cilíndrica livre (0.00 mm³)
OK  presilha 3: sem interferência com 01/placa/02/difusor (0.00 mm³)
OK  presilha 3: pé encosta na placa (aperta)
OK  presilha 3: parafuso M3 × 8 cabeça cilíndrica livre (0.00 mm³)
OK  fundo do furo do inserto da presilha 2.8 mm acima da mesa

## 6. IF-LED e difusor cego
OK  difusor × 01: 0.00 mm³
OK  difusor × 02: 0.00 mm³
OK  folga difusor × 02 0.30 mm
OK  janela 120 × 12 preenchida pelo difusor, face rente à parede
OK  difusor preso para fora (+Y): deslocar 1 mm colide 727 mm³
OK  difusor preso para dentro (−Y): deslocar 1 mm colide 1730 mm³
OK  difusor preso para cima: deslocar 1 mm colide 476 mm³
OK  difusor preso para baixo: deslocar 1 mm colide 313 mm³
OK  lábio atrás do difusor existe (x=0)

## 7. Montagem com a cintura (Peça 08 real, z += Z_TOPO_P02)
OK  giro -60°: cintura sem interferência com 01/02
OK  giro +0°: cintura sem interferência com 01/02
OK  giro +60°: cintura sem interferência com 01/02
OK  M4 (-35,-15): furo do inserto da 02 sob o furo passante da 08A
OK  M4 (-35,+15): furo do inserto da 02 sob o furo passante da 08A
OK  M4 (+35,-15): furo do inserto da 02 sob o furo passante da 08A
OK  M4 (+35,+15): furo do inserto da 02 sob o furo passante da 08A
OK  parafuso M4×12 0: livre na 08A e no furo do inserto (0.00 mm³)
OK  parafuso M4×12 1: livre na 08A e no furo do inserto (0.00 mm³)
OK  parafuso M4×12 2: livre na 08A e no furo do inserto (0.00 mm³)
OK  parafuso M4×12 3: livre na 08A e no furo do inserto (0.00 mm³)
OK  furo M4 10 mm ≥ inserto 8.1 e ponta do M4×12 (8.5)
OK  passa-cabos Ø25 livre até dentro da base
OK  plataforma Ø110 cobre 08A Ø86 e colar Ø102
OK  topo plano (meia-largura útil 73.5) contém a plataforma Ø110

## 8. Imprimibilidade (orientação de impressão)
OK  01_base_inferior (fundo na mesa): 802 mm² voltados para baixo; maior ponte 15.0 mm (≤15.5)
OK  01_base_inferior: 224.8 × 199.8 × 25.0 mm na mesa — passa da meta 220 (cabe na A1 256)
OK  01P_presilha (face de cima na mesa): 0 mm² voltados para baixo; maior ponte 0.0 mm (≤12)
OK  01P_presilha: 16.0 × 12.0 × 5.0 mm na mesa
OK  02_base_superior (de cabeça para baixo (face z=70 na mesa)): 98 mm² voltados para baixo; maior ponte 5.6 mm (≤12)
OK  02_base_superior: 219.4 × 194.7 × 48.0 mm na mesa
OK  02L_difusor_cego (face aparente na mesa): 1081 mm² voltados para baixo; maior ponte 0.0 mm (≤12)
OK  02L_difusor_cego: 119.4 × 21.1 × 6.0 mm na mesa
- Nota: o único vão > 12 mm é o teto dos alojamentos dos pés (Ø15, 2 mm acima da mesa): ponte circular curta, a A1 faz em PETG sem suporte. Na 02 (invertida) as únicas pontes são os fundos dos 4 furos cegos M4 (Ø5,6); o resto voltado para baixo são as raízes a 45° da aba e da moldura do LED e a faixa de transição a 40° da vertical. Nenhum teto em ponte, nenhum suporte.

## 9. Espessuras
OK  parede do boss M3 da 02 3.0 mm
OK  parede da torre da 01 3.3 mm
OK  parede do boss M4 2.5 mm
OK  fundo do furo M4 2.5 mm
OK  fundo sobre os pés 2.0 mm
OK  verga do LED até a transição 11 mm (+ moldura interna com lábio e bochechas)

## Volume e massa (sólido, PETG 1,27 g/cm³; com preenchimento real fica ~45–60%)

- 01_base_inferior: 229.5 cm³ → 291 g
- 01P_presilha: 0.7 cm³ → 1 g (× 4)
- 02_base_superior: 258.0 cm³ → 328 g
- 02L_difusor_cego: 11.3 cm³ → 14 g
- contrapeso de aço 180×150×3: 636 g

## Impressão

| Peça | Orientação | Observação |
|---|---|---|
| 01 base inferior | fundo na mesa | 4 paredes, 20% giroide; insertos M3 das presilhas depois |
| 01P presilha (×4) | face de cima na mesa | 3 paredes, 40% |
| 02 base superior | de cabeça para baixo (topo na mesa) | 4 paredes, 20% giroide; sem suporte; insertos M4 (topo) e M3 (bosses) depois |
| 02L difusor cego | face aparente na mesa | âmbar/translúcido; 3 paredes |

## Ordem de montagem

1. Insertos: 4×M3 nos bosses da 02, 4×M3 nos bosses de presilha da 01, 4×M4 no topo da 02.
2. Pés de borracha embaixo da 01. Placa de aço entre as guias; 4 presilhas com M3×8.
3. Difusor na janela da 02 (entra por dentro: lingueta atrás da verga, encostado no lábio).
4. 02 sobre a 01 (a aba entra por dentro da parede). Virar o conjunto e apertar 4×M3×25 por baixo.
5. Cintura 08A por cima com 4×M4×12 nos insertos da 02.

## Fixadores e comprados

- 4 × Parafuso M3 × 25 cabeça cilíndrica ISO 4762 (01 -> 02, por baixo)
- 4 × Inserto térmico M3 nos bosses da Peça 02
- 1 × Placa de aço 180 × 150 × 3 (contrapeso, cantos vivos ou R≤3)
- 4 × Parafuso M3 × 8 cabeça cilíndrica (presilhas)
- 4 × Inserto térmico M3 nos bosses das presilhas (Peça 01)
- 4 × Pé de borracha adesivo Ø15 (alojamento 2 mm)
- 4 × Inserto térmico M4 na face de cima (IF-CINTURA)
- 4 × Inserto térmico M3 nos bosses de baixo (união com a 01)
