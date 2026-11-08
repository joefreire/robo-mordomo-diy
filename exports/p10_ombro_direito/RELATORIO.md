# Peça 10 — ombro direito: relatório

Resultado: **APROVADO** (0 falhas)

## 1. Sólidos
OK  10A_flange_tronco: válido e 1 corpo
OK  10B_rotor_braco: válido e 1 corpo
OK  10C_tampa_pressao: válido e 1 corpo
OK  10D_manipulo: válido e 1 corpo

## 2. Interface com o tronco (Peça 03, IF-OMBRO)
OK  face Ø56 em y=-15 inteira na traseira (até y=+22.5)
OK  face termina 17 mm abaixo do topo do tronco
OK  flange Ø52 cabe na face plana Ø56

## 3, 6–7. Curso -30° a +120°: colisões a cada 15° (tronco = caixa 185×105×190)
OK    -30°: livre
OK    -15°: livre
OK     +0°: livre
OK    +15°: livre
OK    +30°: livre
OK    +45°: livre
OK    +60°: livre
OK    +75°: livre
OK    +90°: livre
OK   +105°: livre
OK   +120°: livre
OK  batente segura em -33° (pino entra no rotor: 5.9 mm³)
OK  batente segura em +123° (pino entra no rotor: 5.9 mm³)

## 4. Retenção axial
OK  eixo M6 + porca autotravante presa na A: o rotor B não sai mesmo com o manípulo solto
OK  tampa C apoia na arruela de fricção antes do cubo: compressão máx. 0.6 mm (o aperto do M6 não esmaga a arruela além disso)

## 5. Trava (manípulo com pino de indexação a cada 15°)
OK  ponta Ø4 entra no furo nas 11 posições (-30° a +120°, passo 15°)
OK  entre posições a ponta encosta na face (sem furo) = só fricção

## 8. Momento no ombro (hipóteses, sem ensaio)
- braço (casca oca PETG): 180 g a 110 mm do eixo
- mão-luva: 50 g a 200 mm do eixo
- garra futura V2 (estimativa): 120 g a 220 mm do eixo
- objeto na garra (estimativa): 100 g a 230 mm do eixo
- momento máximo (braço a 90° da vertical): **0.78 N·m**
- fricção com pré-carga 150 N (μ borracha 0,5, PTFE 0,1): 1.29 N·m
- fricção com pré-carga 400 N (μ borracha 0,5, PTFE 0,1): 3.43 N·m
- trava positiva (pino Ø4 apoiado 2.5 mm no PETG, 30% de 40 MPa): ~2.6 N·m
OK  pino de indexação ≥ 1,5 × momento máximo (2.6 vs 0.78 N·m)
- Recomendação: **usar a posição travada (pino) com carga**; a fricção sozinha só para o braço vazio. Ensaiar com 300 g antes de confiar.

## 9. Acesso
OK  parafusos do braço (de fora, na lingueta) fora da tampa C
OK  manípulo e cabeça do M6 na face de fora; 4×M3 da A ficam sob o rotor: montar A antes (ordem no relatório)

## 10. Imprimibilidade
OK  10A_flange_tronco: maior ponte 11.8 mm; 52×52×20 mm
OK  10B_rotor_braco: maior ponte 5.6 mm; 52×65×12 mm
OK  10C_tampa_pressao: maior ponte 11.0 mm; 50×50×6 mm
OK  10D_manipulo: maior ponte 7.4 mm; 21×19×12 mm

## Volumes

- 10A_flange_tronco: 15.8 cm³
- 10B_rotor_braco: 23.9 cm³
- 10C_tampa_pressao: 10.7 cm³
- 10D_manipulo: 3.4 cm³

## Fixadores e comprados (por ombro)

- 1 × Parafuso M6 × 30 cabeça cilíndrica (eixo)
- 1 × Porca M6 autotravante (presa na 09A)
- 4 × Parafuso M3 × 10 (09A -> tronco)
- 4 × Inserto térmico M3 no tronco (IF-OMBRO)
- 2 × Parafuso M3 × 10 (braço -> lingueta, de fora; cabeça embutida no soquete)
- 2 × Inserto térmico M3 na lingueta (09B)
- 1 × Parafuso M4 × 25 (manípulo; ponta entra no furo de indexação)
- 1 × Inserto térmico M4 na tampa 09C
- 1 × Arruela PTFE Ø20.5×Ø40×1
- 1 × Arruela de borracha/cortiça Ø20.5×Ø36×2 (fricção)
