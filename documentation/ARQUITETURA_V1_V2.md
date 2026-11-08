# Robô Mordomo — Arquitetura V1 (estática) → V2 (motorizada) · Revisão A

2026-11-07. Substitui a ideia de "robô com 2 servos desde o início". Não apaga nada:
`ALINHAMENTO.md` continua valendo para as pendências de geometria; esta revisão muda a
estratégia de fabricação.

**Regra principal (dono):** imprimir e montar o robô inteiro agora, sem comprar nenhum
motor, tela ou eletrônica, e nunca reimprimir uma carcaça grande para instalar algo depois.
Reimprimir adaptador, suporte e tampa pequena é aceitável.

**Como cumprir:** toda carcaça grande só tem **interfaces padronizadas** (seção 3). O que
muda entre V1 e V2 é um **módulo** que parafusa nessa interface. Na V1 o módulo é
provisório e rígido; na V2 é o módulo real com servo/tela/placa.

## 0. Estado real dos arquivos (o que existe para revisar)

| Peça | Situação em 2026-11-07 |
|---|---|
| 01 Base inferior | CAD fase 1 (só forma) em `base/base_inferior.py` |
| 02 Base superior | só especificação + prancha |
| 03 Tronco traseiro | só especificação + prancha |
| 04 Tronco frontal | só especificação + prancha |
| 05, 06, 07 | **nunca recebidas** (o pedido cita 01–07). Não sei quais são. |

Então "alterações nos arquivos existentes" (item 5) vale hoje para a Peça 01 e para as
especificações 02–04.

## 1. Lista de peças — V1 estática

Carcaças (fixas, iguais na V1 e na V2):

| ID | Peça | Cor | Observação |
|---|---|---|---|
| C01 | Base inferior | verde-petróleo | contrapeso + pés |
| C02 | Base superior | creme | recebe IF-CINTURA |
| C03 | Tronco traseiro | creme | IF-OMBRO ×2, IF-PESCOÇO, trilhos |
| C04 | Tronco frontal | creme | abertura IF-TELA-PEITO, painel de manutenção |
| C05 | Cabeça frente | creme | abertura IF-TELA-ROSTO, reserva IF-CÂMERA |
| C06 | Cabeça traseira | creme | acesso aos parafusos |
| C07 | Braço esquerdo (sup. + antebraço) | creme/grafite | casca oca, IF-OMBRO-BRAÇO + IF-PUNHO |
| C08 | Braço direito (sup. + antebraço) | creme/grafite | idem |

Módulos provisórios V1 (rígidos, baratos, reimprimíveis):

| ID | Módulo V1 | Ocupa | Vira na V2 |
|---|---|---|---|
| M01 | Cintura manual (Peça 08): gira à mão ±60°, fricção ajustável + trava | IF-CINTURA | M01-V2 cintura motorizada |
| M02 | Pescoço fixo (coluna) | IF-PESCOÇO + IF-CABEÇA | M02-V2 pan/tilt |
| M03 E/D | Ombro fixo com indexação de ângulo | IF-OMBRO | M03-V2 ombro com servo |
| M04 E | Mão-bandeja fixa | IF-PUNHO esq. | M04-V2 nivelador da bandeja |
| M04 D | Mão simples | IF-PUNHO dir. | M04-V2 garra |
| M05 | Tampa facial decorativa (olhos/boca) | IF-TELA-ROSTO | moldura + bandeja da tela real |
| M06 | Painel decorativo do peito | IF-TELA-PEITO | moldura + bandeja da tela real |
| M07 | Tampão da câmera | IF-CÂMERA | suporte da câmera |
| M08 | Difusor cego da barra de LED | IF-LED (base) | difusor + régua de LED |
| — | Bandeja Ø120, gravata, antena, orelhas | encaixes próprios | iguais |

Sem eletrônica: as grades de som e ventilação já saem impressas nas carcaças (não muda
na V2). Trilhos, canais e alojamentos de conector ficam vazios.

## 2. Módulos de expansão — V2

| Módulo | Interface | O que entra (a escolher) |
|---|---|---|
| Cintura giratória | IF-CINTURA (mesma furação embaixo e em cima) | rolamento tipo "lazy susan" + servo/motor; anel coletor ou folga de cabo |
| Ombro esquerdo | IF-OMBRO | servo + suporte; eixo de saída no padrão IF-OMBRO-BRAÇO |
| Ombro direito | IF-OMBRO | idem |
| Pan/tilt da cabeça | IF-PESCOÇO + IF-CABEÇA | 2 servos (giro e inclinação) |
| Garra | IF-PUNHO direito | micro servo + dedos |
| Nivelador da bandeja | IF-PUNHO esquerdo | micro servo no punho |
| Tela do peito | IF-TELA-PEITO | SPI ~3,5" (decisão: um ESP32-S3 só) |
| Tela do rosto | IF-TELA-ROSTO | SPI até ~4" |
| Câmera | IF-CÂMERA | módulo de câmera + cabo |
| ESP32-S3, áudio, drivers | IF-ELETRÔNICA (trilhos) | bandejas removíveis |
| LEDs | IF-LED | régua âmbar atrás do difusor |

## 3. Interfaces mecânicas compartilhadas (o contrato)

Todas no `parameters/globais.py`, com nome fixo. Valores abaixo são **propostas iniciais**;
os que dependem de peça comprada ficam como **envelope** (espaço máximo reservado), não
como furação.

| Interface | Liga | Contrato proposto |
|---|---|---|
| IF-CINTURA | C02 ↔ M01 ↔ tronco | Plataforma plana Ø110 em C02 e na base do tronco. 4×M4 num quadrado (posição a decidir, ver §6). Furo central Ø25. Altura do módulo entre as duas faces = constante `CINTURA_ALTURA` (a mesma para M01 e M01-V2). |
| IF-OMBRO | tronco ↔ M03 | Flange plana na lateral do tronco traseiro: furo central (cabos/eixo) + círculo de parafusos M3. Envelope interno reservado para um servo padrão + suporte. |
| IF-OMBRO-BRAÇO | M03 ↔ braço | Cubo do braço com o mesmo padrão nos dois lados. V1: M03 tem dentes/furos de indexação a cada 15° para escolher a pose. V2: o cubo prende no braço do servo por um adaptador. |
| IF-PUNHO | antebraço ↔ mão | Flange de ferramenta igual nos dois braços (mão, bandeja, garra, nivelador). Furo para cabos. |
| IF-PESCOÇO | tronco ↔ M02 | Prateleira estrutural no topo do tronco, furação M3 + furo de cabos. Envelope reservado para pan/tilt. |
| IF-CABEÇA | M02 ↔ cabeça | Flange no fundo da cabeça, mesmo padrão. |
| IF-TELA-ROSTO / PEITO | carcaça ↔ moldura + bandeja | Abertura para o maior candidato. A moldura define a janela; a bandeja define o encaixe da tela. Na V1, a tampa decorativa usa os mesmos furos da moldura. |
| IF-CÂMERA | cabeça ↔ suporte | Furo pequeno na testa + pontos M2/M3 internos; tampão na V1. |
| IF-ELETRÔNICA | tronco ↔ bandejas | 2 trilhos verticais com furos M3 a passo fixo (proposta 10 mm). |
| IF-LED | C02 ↔ difusor | Rasgo frontal com moldura; difusor cego na V1. |
| IF-CABO | todas as fronteiras | Furo/canal com raio nas bordas e espaço para conector travado. |

## 4. Adaptadores provisórios necessários (V1)

M01 cintura fixa · M02 pescoço fixo · M03 ombro fixo (×2, com indexação) · M04 mão-bandeja e
mão simples · M05 tampa facial · M06 painel do peito · M07 tampão da câmera · M08 difusor
cego. Todos parafusados, nenhum colado.

## 5. Alterações nas peças existentes

| Peça | O que muda |
|---|---|
| 01 Base inferior | Nada na forma. Mantém torres, contrapeso e pés. O contrapeso ganha peso com a V2 (servos lá em cima): reservar placa maior ou empilhável. |
| 02 Base superior | O topo deixa de "receber o tronco" e passa a receber **M01**. A plataforma Ø110 + 4×M4 + Ø25 vira IF-CINTURA. Alojamento do LED vira IF-LED. |
| 03 Tronco traseiro | A base do tronco vira IF-CINTURA (lado de cima). Ombros viram IF-OMBRO com envelope de servo. Topo vira IF-PESCOÇO com envelope **de pan/tilt** (maior que o "um servo de giro" anterior). Trilhos = IF-ELETRÔNICA. |
| 04 Tronco frontal | Abertura da tela = IF-TELA-PEITO; painel decorativo M06 na V1. |
| Cabeça (ainda não especificada) | Precisa de IF-CABEÇA embaixo, IF-TELA-ROSTO, IF-CÂMERA na testa e espaço para o tilt. |
| Braços (ainda não especificados) | Esquerdo também precisa de IF-PUNHO: o nivelador da bandeja na V2 fica no punho. |

## 6. Conflitos e pendências desta revisão

- **[DECIDIDO 07/11: traseira = esqueleto] Divisão do tronco.** IF-CINTURA, IF-OMBRO e
  IF-PESCOÇO são os pontos de maior esforço e ficam todos perto do plano entre traseira e
  frontal (65/40 mm). Se cada interface ficar metade em cada carcaça, o módulo da V2 não tem
  onde se apoiar sozinho. Proposta: as três interfaces inteiras na **carcaça traseira**
  (estrutural), e a frontal só como capa.
- **[DECIDIR] Altura com a cintura.** O módulo da cintura entra na pilha: 25 + 45 +
  **cintura** + 190 + **pescoço** + cabeça + antena. Isso ajuda a fechar os 550 mm (faltavam
  ~80–145 mm). O pescoço precisa caber num pan/tilt (mais alto que um giro simples).
- **[PROPOSTA] Envelopes, não furos.** Para servo, tela, câmera e placa, a carcaça reserva um
  volume livre (envelope) e a furação real fica no adaptador. Tamanho do envelope: o maior
  candidato realista de cada tipo, a confirmar antes de modelar a carcaça.
- **[DECIDIR] Rosto decorativo na V1.** Olhos e boca na tampa facial: em relevo/cor única
  (pintado) ou em outra cor? A A1 tem AMS lite? Isso muda como a tampa é feita.
- **[PROPOSTA] Estabilidade V2.** Servos, pan/tilt e garra somam peso no alto. Conferir o
  tombamento com a bandeja carregada antes de fechar o contrapeso.
- **[PROPOSTA] Pose na V1.** Ombros com indexação a cada 15° deixam escolher a pose dos braços
  sem motor; o pescoço fixo pode ter 2–3 posições de inclinação da cabeça.

## 7. Ordem de impressão proposta (V1)

1. Testes de encaixe pequenos: anel IF-CINTURA, flange IF-OMBRO, flange IF-PUNHO, cantos da
   base (folgas reais na A1 com PETG).
2. C01 base inferior → C02 base superior → M01 cintura (valida o empilhamento).
3. C03 tronco traseiro → C04 tronco frontal → M06 painel do peito.
4. M02 pescoço → C05/C06 cabeça → M05 tampa facial → M07 tampão.
5. M03 ombros → C07/C08 braços → M04 mãos → bandeja.
6. Acabamentos: gravata, antena, orelhas, M08 difusor.

## 8. Montagem virtual

Ainda não dá: só a Peça 01 (forma) existe em CAD. Plano: `assembly/v1.py` monta tudo que
existir, com os módulos V1; `assembly/v2_envelopes.py` mostra os módulos V2 como volumes
transparentes (envelopes) dentro das mesmas carcaças, para provar que cabem.


## Revisão B (08/11) — rodas, auto-carregamento e cotovelos

- **Base trocável (IF-BASE):** a Peça 01 vira um módulo. V1 = pés + contrapeso; V2 = **01R** com 2
  rodas de tração, 4 rodízios, bateria embaixo (substitui o aço), driver e placa de carga. Peça 02 e
  tudo acima não mudam; altura do robô não muda. Estabilidade V2 (hipóteses de massa dos servos e
  telas): tomba com ~18° vazio, ~13° com 300 g na bandeja, ~11° com o braço a +60° e 300 g.
- **Auto-carregamento:** contatos de cobre e IR na traseira da 01R + **doca de carga** com contatos
  de mola e guias em V. Robô entra de ré. Firmware: achar o farol IR, dar ré, detectar a carga.
- **Cotovelos (futuro, "V3 braços"):** recomendação — não colocar agora. Braço é peça barata de
  reimprimir (~100–220 g de PETG); o que não dá para reimprimir fácil (tronco e interface do ombro)
  já aguenta: os 4×M3 do IF-OMBRO seguram muito mais do que o torque de um braço carregando, e o
  envelope interno do servo (50×60×45) cabe servos de 25–35 kg·cm. **Para carregar objetos, o servo
  do ombro da V2 deve ter ≥ 25 kg·cm** (300 g na mão a ~250 mm + braço com cotovelo + garra ≈ 1,3 N·m
  parado, mais aceleração). O braço V3 terá: servo do cotovelo dentro do braço superior, mesmo IF-BRAÇO
  (a lingueta pode ser reforçada trocando só o rotor do ombro, peça pequena) e o mesmo IF-PUNHO.
