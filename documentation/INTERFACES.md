# Robô Mordomo — Interfaces mecânicas (contrato entre peças)

Fonte única dos números: `parameters/globais.py`. Esta página explica; se divergir, **o
arquivo de parâmetros vale**. Toda peça nova lê os valores de lá (nunca copia número).

## Sistema de coordenadas do robô

- Origem: centro da pegada da base, no plano da mesa (z = 0).
- **X** = largura, + para a **direita do robô**. **Y** = profundidade, + para a **frente**.
  **Z** = para cima.
- Eixo do robô (cintura, pescoço, passa-cabos) em x = 0, y = 0.
- Tronco: traseira = **esqueleto** (de y = −52,5 até y = +22,5, `TRONCO_PROF_TRASEIRA` 75);
  frontal = capa (de +22,5 a +52,5). Cintura, ombros e pescoço ficam inteiros na traseira.

## Pilha vertical (z de cada face)

| Face | z (mm) | Parâmetro |
|---|---|---|
| Mesa | 0 | — |
| Topo da Peça 01 (base inferior) | 25 | `P01_ALTURA` |
| Topo da Peça 02 = base da cintura | 70 | `Z_TOPO_P02` |
| Piso do tronco = topo da cintura | 94 | `Z_PISO_TRONCO` |
| Eixo dos ombros | 239 | `IF_OMBRO_Z` |
| Topo do tronco = base do pescoço | 284 | `Z_TOPO_TRONCO` |
| Face de cima da placa da cabeça | **356** | `Z_IF_CABECA` |
| Cabeça ~145 + antena ~40 | ~541 | (cabeça ainda não projetada) |

## IF-BASE (Peça 02 ↔ módulo de base de baixo) — V1 estática ou V2 com rodas

O módulo de baixo é trocável: Peça 01 (V1, pés de borracha + contrapeso de aço) ou Peça 01R (V2,
rodas + bateria + auto-carregamento). Contrato: mesmo contorno externo inclinado e borda plana em
z = 25 (a aba da 02 entra por dentro), 4×M3 por baixo em `BASE_TORRES` (±70, ±84) com insertos na
02, mesmo assento do difusor do LED na junta, cabos sobem pelo centro (Ø25 da 02). A Peça 02 deixa
livres os envelopes da V2 (validado em `base/validar_base_rodas.py`).

V2 (envelopes, conferir com as peças compradas): 2 rodas de tração Ø ≤ 48 × 20 em x = ±68, y = 0
(giro no lugar; o teto inclinado da 02 limita o diâmetro); motores N20 38×14×14 para dentro; 4
rodízios de esfera em (±46, ±78), 1 mm acima da linha das rodas; bateria 2×18650 atrás do eixo;
driver na frente; placa de carga ao lado da bateria. Fundo da 01R a 6 mm da mesa: **a altura do robô
não muda**.

## Auto-carregamento (V2)

Robô entra **de ré** na doca (`base/doca_carga.py`, 250×100×32, uma impressão). Na traseira da 01R:
2 rebaixos de 14×8×1,5 para placas de cobre em x = ±30, z = 14 (polaridades separadas), com inserto
M3 atrás para o fio; janela do receptor de IR Ø8 em x = 0, z = 16. Na doca: 2 contatos de mola
(passam 4 mm da face: ~2,5 mm de compressão), emissor de IR no mesmo eixo, conector de
alimentação atrás e guias em V (captura lateral ±9,5 mm na entrada; o IR alinha o resto).

## IF-CINTURA (Peça 02 ↔ cintura ↔ tronco)

- 4×M4 num retângulo **70 × 30** centrado no eixo (x ±35, y ±15), **iguais em cima e
  embaixo** (qualquer cartucho entra virado 180°). Embaixo: insertos M4 na Peça 02. Em cima:
  insertos M4 na flange superior da cintura; o tronco parafusa por dentro.
- Passa-cabos Ø25 no eixo. Abertura no piso do tronco Ø56 (cabos + acesso ao anel de ajuste).
- Altura do módulo: **24 mm** (manual e futuro motorizado). Envelope Ø102. Giro ±60°.

## IF-OMBRO (lateral do tronco ↔ módulo do ombro), igual nos dois lados (espelhado)

- Centro do eixo: x = ±92,5 (face externa da lateral), y = −15, z = 239. Eixo do ombro = X.
- Face plana Ø56 na carcaça; 4×M3 com insertos no tronco, raio 20 a 45°/135°/225°/315°.
- Furo central Ø16 (porca do eixo na V1; eixo do servo e cabos na V2).
- Envelope: Ø56 × 40 mm para fora; por dentro 50 (Y) × 60 (Z) × 45 (X) para o servo da V2, **centrado em y = −9, z = 233** (6 mm à frente e 6 abaixo do eixo; centrado no eixo ele furava a casca — `tronco/tronco_traseiro.py:ENV_OMBRO`).

## IF-BRAÇO (módulo do ombro ↔ braço, Peças 05/07)

- Lingueta radial na peça que gira: 24 (tangencial) × 12 (ao longo do eixo), do raio 21 ao 39.
- Em 0° a lingueta aponta para baixo. O braço encaixa por fora (3 lados) e parafusa com
  **2×M3 no sentido do eixo, de fora para dentro**, nos raios 29 e 35 (insertos na lingueta).

## Convenção de giro dos ombros

`ombro/ombro_manual.girar(peça, ângulo, lado)`: 0° = braço para baixo, **+ = para a frente/cima**,
nos dois lados. Cursos: esquerdo 0°…+60° (atrás disso o L e a bandeja batem na base), direito
−30°…+120°. Trava positiva a cada 15°.

## IF-PUNHO (braço ↔ mão / adaptador da bandeja / garra futura)

Face Ø36 na ponta do braço (anel grafite 05C/07C). 3×M3 com insertos no anel, raio 12,5, em
**90°, 200°, 340°** (assimétrico: só monta de um jeito) + ressalto-chave 5×2 a 90° (r 15–18).
Furo de cabos Ø10. O braço direito tem 20×12×25 livres para um conector antes do punho.

## IF-BANDEJA (adaptador ↔ bandeja)

Cubo 06B (Ø50×10) parafusado embaixo da bandeja (3×M3 escareados por cima); no cubo, 2 insertos
M3 a x ±12 e rasgo-chave 14×8×3 deslocado 6 mm (só entra de um jeito). Na V1 o adaptador 05D
deixa a bandeja horizontal com o ombro esquerdo em 0°; na V2 só o adaptador vira nivelador.

## IF-PESCOÇO (topo do tronco ↔ pescoço)

- Face plana Ø66 no topo da traseira, centrada no eixo. 4×M3 (insertos no tronco) em
  **x ±22, y ±15**. Passa-cabos Ø16. Envelope do módulo: 75 × 75 × 80.

## IF-CABEÇA (pescoço ↔ cabeça) — obrigatória no CAD da cabeça

Referencial: o mesmo do robô, girando com o pan/tilt. Em pan 0 / tilt 0:

```
              +Y (frente)
     ┌───────────────────────────┐  60 (X) × 50 (Y), cantos R6, espessura 6
     │  ●(−22,+17)    ○(0,+19)   ●(+22,+17)
     │                            │   ● 4×M3: insertos CURTOS M3×4 na placa, de cima.
     │           ◯ Ø16            │     A cabeça parafusa POR DENTRO, de cima para baixo.
     │                            │   ○ 2 pinos Ø4 × 3 sobem da placa (alinhamento).
     │  ●(−22,−17)    ○(0,−19)   ●(+22,−17)  Furos na cabeça: Ø4,3 nos pinos.
     └───────────────────────────┘
```

- Face de cima da placa em **z = 356** (topo do tronco + 72). Centro de cabos Ø16.
- A cabeça precisa de: furos passantes M3 (Ø3,4) com acesso de chave por dentro, dois furos
  Ø4,3 para os pinos, e furo Ø ≥ 16 no centro.
- Nada macio entre placa e cabeça (câmera). Amortecimento só no suporte interno da câmera.

## Folgas e fixadores comuns

`FOLGA_ENCAIXE` 0,3 por lado · M3 passante 3,4 · inserto M3 Ø4,0 × 5,7 (placa da cabeça:
M3×4) · M4 passante 4,5 · inserto M4 Ø5,6 × 8,1. **Conferir os insertos e porcas reais**
na ficha do lote antes de imprimir (valores de catálogo comum).
