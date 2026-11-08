# Robô Mordomo DIY (55 cm) — CAD paramétrico (CadQuery)

Robô mordomo de mesa, 100% impresso em 3D (Bambu Lab A1, PETG), projetado em código (CadQuery)
e validado automaticamente (encaixes, colisões, cursos, momentos, estabilidade, imprimibilidade).

**[Abrir o visualizador 3D interativo](https://joefreire.github.io/robo-mordomo-diy/)** — gire as
juntas dentro dos limites reais, explode, corte e clique nas peças.

> Estado: **CAD completo e validado; nada foi impresso nem testado fisicamente ainda.** Medidas de
> componentes comprados (insertos, porcas, parafusos) são de catálogo — conferir com o seu lote.

*EN: tabletop butler robot (550 mm), fully 3D-printable, parametric CAD in CadQuery with automated
validation. V1 is static (no electronics); V2 swaps modules for servos, screens, ESP32-S3, wheels and
self-charging without reprinting the main shells. Docs are in Portuguese.*

V1 estática (imprime e monta agora, sem eletrônica) preparada para virar V2 motorizada
trocando só módulos. Ver `documentation/ARQUITETURA_V1_V2.md`, `documentation/INTERFACES.md`
e `documentation/ALINHAMENTO.md` (decisões e pendências).

## Estado das peças (07/11)

| Peça | Pasta | Peças impressas | Validação |
|---|---|---|---|
| 01 Base inferior + 02 base superior | `base/` | 01, 4 presilhas, 02, difusor cego | `exports/p01_p02_base/RELATORIO.md` — aprovado |
| 03 Tronco traseiro (esqueleto) + 04 frontal | `tronco/` | 03A, 03B painel; 04A, 04B moldura, 04C bandeja da tela, 04D tampa, 04E painel M06 | `exports/p03_p04_tronco/RELATORIO.md` — aprovado |
| 05 Braço esquerdo (L) + 06 bandeja + 07 braço direito | `braco/` | 05A/B metades, 05C anel, 05D adaptador V1; 06A bandeja, 06B cubo, 06C anel; 07A/B, 07C, 07E luva, 07F friso | `exports/p05_p06_p07_bracos/RELATORIO.md` — aprovado |
| 08 Cintura manual | `cintura/` | 5 | `exports/p08_cintura/RELATORIO.md` — aprovado |
| 09 / 10 Ombros (mesmo código) | `ombro/` | 4 + 4 | `exports/p09_*/`, `exports/p10_*/` — aprovados |
| 11 Pescoço pan/tilt rev. B | `pescoco/` | 7 (rev. A congelada) | `exports/p11_pescoco/RELATORIO.md` — aprovado |
| Cabeça | `cabeca/` | C05 frente, C06 traseira, M05 tampa facial, M07 tampão, antena, 2 orelhas | `exports/p_cabeca/RELATORIO.md` — aprovado |
| Gravata | `acessorios/` | gravata + tampa do nó | `exports/acessorios/RELATORIO_gravata.md` |
| 01R Base com rodas (V2) + doca de carga | `base/base_rodas.py`, `base/doca_carga.py` | 01R, doca | `exports/p01R_base_rodas/RELATORIO.md` — aprovado |
| **Robô montado** | `assembly/montagem_v1.py` | — | `exports/montagem/RELATORIO.md` |
| Visualizador 3D | `tools/visualizador.py` | — | `docs/index.html` (GitHub Pages) |

## Rodar

```bash
cd robo-mordomo-diy
python3 -m venv .venv && .venv/bin/pip install cadquery trimesh manifold3d pyrender Pillow
PY=.venv/bin/python                      # CadQuery 2.8 (Python 3.10–3.12)
$PY cintura/cintura_manual.py   && $PY cintura/validar_cintura.py
$PY ombro/ombro_manual.py       && $PY ombro/validar_ombro.py        # gera 09 e 10
$PY pescoco/pescoco_manual.py   && $PY pescoco/validar_pescoco.py
$PY base/validar_base.py && $PY tronco/validar_tronco.py && $PY braco/validar_bracos.py && $PY cabeca/validar_cabeca.py
$PY acessorios/gravata.py
$PY base/base_rodas.py && $PY base/doca_carga.py && $PY base/validar_base_rodas.py   # V2: rodas + doca
$PY assembly/montagem_v1.py                                        # robô inteiro: colisões, massa, CG, tombamento
$PY tools/visualizador.py && cp exports/visualizador_robo.html docs/index.html
```

Cada validador sai com código 1 se houver falha e grava `RELATORIO.md` + PNGs em `exports/`.

## Impressão (A1, PETG, bico 0,4, camada 0,2)

| Peça | Orientação | Paredes / preenchimento |
|---|---|---|
| 08A, 08B, 09/10A, 09/10B, 11A, 11B | fundo na mesa | 4 paredes, 40% giroide (mancais e insertos) |
| 08C, 09/10C, 11C, 11E | deitadas (face plana na mesa) | 4 paredes, 30% |
| 08D colar, manípulos | de cabeça para baixo | 3 paredes, 15% |
| 11D berço | fundo na mesa | 4 paredes, 40% |

Sem suporte em nenhuma: as maiores pontes são de 5–12 mm (rasgos de batente, alojamentos de
porca/cabeça). Insertos térmicos depois da impressão.

## Decisões de engenharia tomadas no CAD (resumo)

- Retenção axial sempre separada da trava: anel parafusado no cubo (cintura, pan) e eixo com
  porca autotravante (ombros, tilt). Travas só seguram giro.
- Fricção com área grande (arruelas PTFE/silicone/borracha compradas), compressão limitada por
  batente: o aperto não esmaga a arruela.
- Ombros e tilt com **trava positiva** (pino do manípulo em furos a cada 15°/10°): a fricção
  sozinha não segura bandeja com 300 g nem a cabeça (pêndulo invertido) — ver relatórios.
- Pescoço rev. B: eixo = parafuso com ombro ISO 7379 Ø6×65 em buchas 6×10 nos dois montantes,
  calços para folga axial.

## Licença

Código: MIT. Modelos, imagens e documentação: CC BY-NC-SA 4.0. Ver `LICENSE`.
