# Robô Mordomo — alinhamento entre as peças

Documento vivo. Cada peça nova que chega (especificação + prancha conceitual) é
cruzada com as anteriores e com o conceito geral. O que está aqui ainda **não é CAD**:
nenhuma peça foi modelada até agora (2026-11-07). As pranchas em `referencias/` são
ilustrações de conceito, não desenhos com medidas.

Legenda: **[DECIDIR]** precisa de escolha do dono · **[PROPOSTA]** minha sugestão, ainda
não aprovada · **[OK]** coerente entre as peças.

## Peças recebidas

| # | Peça | Especificação | Prancha |
|---|---|---|---|
| 00 | Conceito geral (55 cm, ESP32, 2 servos, tela, bandeja) | texto "Versão 1.0" | `00-conceito-geral.png` |
| 01 | Base inferior (verde-petróleo) | 225 × 200 × 25, parede 3, fundo 4, R35 | `01-base-inferior.png` |
| 02 | Base superior (creme) | 225 × 200 × ~45, Ø110 + 4×M4, cabos Ø25 | `02-base-superior.png` |
| 03 | Tronco traseiro (creme) | 185 × 190 × ~65 (tronco total ~105) | `03-tronco-traseiro.png` |
| 04 | Tronco frontal (creme) com tela 3,5" | 185 × 190, profundidade = 105 − traseira | `04-tronco-frontal.png` |
| — | Arquitetura 5 graus de liberdade (V2) | só prancha | `05-arquitetura-5dof.png` |
| — | V1 estático (decorativo) | só prancha | `06-v1-estatico.png` |
| 05–07 | ? | **nunca recebidas** | — |
| 08 | Cintura manual (V1) | ~30 mm, Ø25, M4 em cima e embaixo, giro ±60° com fricção | `08-cintura-manual.png` |

Próximas anunciadas: braços, pescoço, e por último a cabeça.

## 1. Sistema de coordenadas (vale para todas) — [PROPOSTA]

Ainda não existe. Proposta para fixar antes da Peça 01:

- Origem: centro da pegada da base, no plano da mesa (z = 0).
- X = largura (positivo para a direita do robô), Y = profundidade (positivo para a **frente**),
  Z = para cima.
- Eixo vertical do robô (pescoço, passa-cabos Ø25, centro do Ø110) em x = 0, y = 0.
- Um arquivo único `parameters/` com tudo que é compartilhado (contorno da base, torres M3,
  padrão M4, plano de divisão do tronco, folgas). Nenhuma peça redefine esses valores.

## 2. Orçamento de altura (55 cm) — [DECIDIR]

| Item | Fonte | mm |
|---|---|---|
| Base inferior | Peça 01 | 25 |
| Base superior | Peça 02 | 45 |
| Tronco | Peça 03 | 190 |
| Pescoço | não definido | ? |
| Cabeça | conceito geral | ~145 |
| Antena | não definida | ? |
| **Soma conhecida** | | **405** |

Faltam ~145 mm para pescoço + antena chegarem a 550. Na prancha 00 o pescoço é curto
(~20–30 mm) e a antena ~40–60 mm: a soma daria ~470–490 mm, não 550. Ou o robô fica
~48 cm, ou a cabeça/tronco/base crescem. Na prancha 00 a cabeça parece ocupar ~30 % da
altura (≈165 mm), não 145.

## 3. Base inferior × base superior (Peças 01 e 02)

- **[DECIDIR] Direção dos parafusos M3.** A Peça 01 põe insertos nas torres de baixo, então
  o parafuso entra **por cima**, atravessando a Peça 02 inteira (45 mm). Isso pede furo
  fundo ou torre longa na Peça 02 e deixa as cabeças visíveis na tampa creme. A prancha 02
  mostra os furos M3 no canto da tampa, por cima. Alternativa: parafuso **por baixo**,
  atravessando o fundo da Peça 01, inserto na Peça 02. Parafusos escondidos e acessíveis
  virando o robô; muda a Peça 01 (furo passante com rebaixo no fundo em vez de inserto).
- **[PROPOSTA] Contrapeso.** O corte da prancha 01 mostra a placa num rebaixo do fundo. Com
  fundo de 4 mm e placa de 3 mm sobra ~1 mm. Melhor: placa apoiada no fundo, presa por guias
  de canto e presilhas parafusadas. A placa da prancha tem 4 furos, mas as medidas não
  existem; não usar até ter a placa real.
- **[OK] Interferência placa × torres.** Placa 180 × 150 centrada, torres Ø10 nos cantos do
  raio R35: sobram ~2,5 mm entre o canto da placa (com folga) e a torre. Confirmar no CAD.
- **[PROPOSTA] Encaixe.** A aba de ~3 mm da Peça 02 entra **por dentro** da parede da Peça
  01, com folga de 0,3 mm/lado. Como a parede da Peça 01 é inclinada, a aba precisa seguir
  a mesma inclinação (contorno interno no topo da Peça 01, não o externo).
- **[PROPOSTA] Impressão da Peça 02.** De cabeça para baixo, a parte plana de cima apoia na
  mesa, mas as laterais abrem para fora e pedem suporte. Com a abertura para baixo, as
  laterais imprimem sem suporte e o teto precisa de apoio: as nervuras internas descendo até
  a mesa servem de reforço e de suporte ao mesmo tempo (vão entre nervuras ≤ ~40–50 mm).
- **[OK] LED âmbar.** Conceito geral põe o difusor na base; a Peça 02 põe na frente da base
  superior, como alojamento de difusor separado. Coerente com a prancha 00.
- **[OK] Peso e cor.** Inferior verde-petróleo, superior creme, como na prancha 00.

## 4. Base superior × tronco (Peças 02 e 03)

- **[DECIDIR] Os 4 M4 caem no plano de divisão do tronco.** O tronco tem 105 mm de
  profundidade total, 65 na traseira e ~40 na frontal. Se o eixo do robô (centro do Ø110 e
  do Ø25) fica no meio do tronco, o plano de divisão fica ~12,5 mm à frente do centro. Um
  padrão M4 circular centrado (ex.: Ø80) teria os dois furos da frente ~28 mm à frente do
  centro, ou seja, **dentro da carcaça frontal**. A prancha 03 mostra só 2 bosses M4 na
  traseira. Opções: (a) padrão M4 retangular inteiro atrás do plano de divisão;
  (b) deslocar o eixo do robô para trás; (c) flange removível de transição (a Peça 02 já
  fala em "flange removível") que recebe o tronco inteiro.
- **[DECIDIR] Passa-cabos Ø25 no plano de divisão.** Pela mesma conta, o furo Ø25 no
  centro vai de 12,5 mm atrás a 12,5 mm à frente do centro: a borda da frente encosta no
  plano de divisão. Na prancha 03 ele está na traseira, perto da parede de trás.
- **[DECIDIR] Pegada do tronco menor que a plataforma.** A plataforma da Peça 02 tem Ø110
  e o tronco tem 105 mm de profundidade total, ainda mais estreito embaixo ("região inferior
  mais estreita"). Sobra borda da plataforma visível na frente e atrás. Reduzir a plataforma
  ou deixar a borda como degrau proposital.
- **[DECIDIR] Acesso aos M4.** Parafusando de dentro do tronco para baixo, o acesso é pela
  frente aberta, antes da carcaça frontal e com a eletrônica ainda fora. Depois de montado,
  tirar o tronco exige desmontar a frente e a eletrônica. Alternativa: parafuso de baixo para
  cima com a base aberta (outra razão para pensar junto com o item dos M3).

## 5. Tronco traseiro (Peça 03) por dentro

- **[DECIDIR] Ombros cruzam o plano de divisão.** O círculo do ombro na lateral, centrado na
  profundidade do tronco (~52 mm da traseira), com Ø~60 vai de ~22 a ~82 mm: passa do plano
  de divisão (65 mm). A interface do ombro ficaria metade em cada carcaça, fraca para o servo
  do braço direito. Opções: centro do ombro ≤ ~35 mm da traseira, ou plano de divisão mais à
  frente (traseira mais funda).
- **[DECIDIR] Pescoço no plano de divisão.** O eixo do pescoço (centro do tronco) também fica
  perto da divisão; a prateleira do pescoço da prancha 03 está na traseira e precisa avançar
  até o eixo.
- **[DECIDIR] Painel de manutenção: frente ou trás?** A prancha 00 tem a tampa verde-petróleo
  **na frente** (baia do ESP32 com dobradiça). A Peça 03 cria o rebaixo para um painel **atrás**
  (com grade de ventilação). Os trilhos de eletrônica estão na traseira e são acessados pela
  frente aberta. Definir qual é o acesso de manutenção de verdade; dois painéis é mais peça.
- **[PROPOSTA] Rebaixo de 1,5 mm na parede de 3 mm.** Sobra 1,5 mm de parede na área
  inteira do painel. Melhor rebaixar só a moldura (a parede inteira continua com 3 mm) ou o
  painel cobrir uma abertura com reforço em volta.
- **[DECIDIR] Saída de som.** A prancha 03 põe o alto-falante embaixo à esquerda na traseira
  e a grade no painel traseiro; a prancha 00 põe o alto-falante na baia da frente. O som deve
  sair para quem está na frente do robô.
- **[PROPOSTA] Microfone.** Não tem lugar em nenhuma prancha. Precisa ficar longe do
  alto-falante e dos servos, de preferência na cabeça ou no peito, voltado para a frente.
- **[PROPOSTA] Impressão da Peça 03.** Deitada de costas, as costas convexas não apoiam
  plano (suporte em toda a curva). Em pé (fundo na mesa), 190 mm cabe na A1; os ombros e o
  topo arredondado fecham para dentro e a prateleira do pescoço vira ponte. Com a borda de
  união na mesa, as costas viram um teto inteiro sobre a cavidade (suporte em tudo). Avaliar
  no CAD; mesma questão na Peça 04 (seção 8).

## 8. Tronco frontal (Peça 04)

- **[DECIDIR] Agora são duas telas.** Conceito geral: tela grande (4,3"–5") **na cabeça**
  para o rosto. Peça 04: tela de 3,5" **no peito** para Home Assistant (hora, clima, botões).
  Um ESP32-S3 só não alimenta bem as duas (RGB paralela na cabeça + SPI no peito + touch +
  áudio + servos). Linha mais simples: cada tela com sua própria placa S3 integrada (rosto na
  cabeça, painel HA no peito), conversando entre si e com o HA por Wi-Fi; uma delas fica com
  servos e áudio. Isso fecha a pendência "onde fica o controlador" junto com esta.
- **[OK] Profundidade.** 105 − 65 = 40 mm de frontal. Tela 3,5" + moldura + bandeja ocupam
  ~15–25 mm a partir da frente; sobra espaço até os trilhos da traseira. Confirmar com o
  módulo real (placas com pinos/headers chegam a ~20 mm só de módulo).
- **[DECIDIR] Painel inferior não alcança o ESP32.** Na prancha 03 o suporte do ESP32 fica
  no **meio** da traseira, atrás da tela do peito. O painel de manutenção da Peça 04 fica
  **embaixo**. Por ele dá para ver conectores, mas não o ESP32 (a bandeja da tela tampa). A
  prancha 00 pedia USB-C acessível pela frente. Ou o suporte do ESP32 desce para a faixa do
  painel, ou o USB-C sai num cabo/extensão preso perto do painel.
- **[DECIDIR] Três acessos de manutenção.** Moldura da tela (frente), painel inferior
  (frente) e painel traseiro verde-petróleo (Peça 03). Definir quais ficam; cada um é peça,
  furo e parafuso a mais. Cores: o conceito geral pede painéis verde-petróleo; na prancha 04
  o painel inferior é creme.
- **[DECIDIR] Parafusos de união 03 × 04.** A prancha 04 mostra 4 bosses M3 dentro da frontal
  e nenhuma cabeça de parafuso por fora, nem na frente nem atrás (na traseira só os do painel).
  Precisa definir por onde entram: por trás (cabeça aparente nas costas), pela frente
  (escondidos sob a moldura/painel) ou por dentro (inacessível depois de fechado, contra a
  especificação).
- **[DECIDIR] Como a moldura da tela sai pela frente.** "Moldura frontal removível" para
  trocar a tela sem abrir o tronco precisa de fixação que se solta pela frente: parafusos
  aparentes na moldura ou encaixe com pinos e ímãs. Se os parafusos estiverem por dentro,
  trocar a tela exige abrir o tronco.
- **[PROPOSTA] Pilha vertical apertada.** 190 mm de altura para: recorte do pescoço no topo
  + gravata (~25–30 mm) + tela com moldura (~75–80) + painel inferior (~55–60) + bordas. Sobram
  poucos milímetros de parede entre a abertura da tela e a do painel. Painel menor ou tela
  mais alta, com pelo menos ~10 mm de material entre as aberturas.
- **[DECIDIR] Gravata × cabeça.** A gravata fica logo abaixo do pescoço, saliente na frente; a
  cabeça (205 de largura) gira logo acima. Conferir a folga entre a borda inferior da cabeça
  girando e a gravata quando houver pescoço.
- **[PROPOSTA] Impressão da Peça 04.** Opções: (a) frente na mesa, que dá o melhor
  acabamento na face visível se o centro da frente for **plano** (com "levemente convexa", a
  peça balança e pede suporte); (b) em pé, mas a borda de cima da abertura da tela vira uma
  ponte de ~110 mm; (c) borda de união na mesa, mas a frente vira teto. Sugestão: frente com
  região central plana e bordas arredondadas, impressa de frente na mesa.
- **[OK] Ombros.** A prancha 04 não tem nada de ombro na frontal, o que combina com manter as
  interfaces dos ombros inteiras na traseira (seção 5).

## 6. Eletrônica e energia (conceito geral)

- **[DECIDIR] Onde fica o controlador.** Tela 4,3"–5" de cor no ESP32-S3 normalmente é
  painel RGB paralelo (~20 GPIO) e as placas prontas já trazem S3 + tela juntos. Somando
  touch, microfone I²S, amplificador I²S e 2 servos, os GPIO livres acabam. Duas linhas:
  (a) placa S3 com tela integrada **na cabeça**, controlando tudo (o tronco fica com
  alimentação, servos e áudio); (b) S3 no tronco + tela SPI menor na cabeça. Isso muda
  cabeça, pescoço (quantos fios passam) e a baia do tronco.
- **[DECIDIR] Fonte.** A prancha 00 diz 5 V ≥ 2 A. Dois servos "padrão" (tipo MG996R) chegam
  a ~2,5 A cada no travamento; com tela e áudio, 2 A não basta. O conceito geral já pede
  alimentação dos servos separada da lógica. Definir os servos para dimensionar.
- **[OK] Nada de furação de placa inventada.** Todas as pranchas marcam as placas como
  "padrão a definir". Os suportes ficam como peças removíveis com placa de adaptação.

## 7. Estabilidade (verificar quando houver braços)

Base 225 × 200; braços saem do tronco (185) e a bandeja (Ø120) fica para fora, à frente e de
lado. Calcular o momento com bandeja carregada + braço direito estendido contra o peso da
base com contrapeso, antes de fechar o tamanho da placa de aço.

## 9. Pranchas 05 (5 GDL) e 06 (V1 estático) × o que já existe

As pranchas 05 e 06 são "só ideias" (dono), mas divergem do que as especificações pedem:

- **[DECIDIR] Base redonda ou retangular?** As pranchas 05 e 06 mostram base **redonda**
  (Ø~220, cúpula creme sobre anel verde). As especificações 01/02 e o CAD da Peça 01 são
  **retangulares arredondadas** 225 × 200 (R35). Muda a Peça 01 já iniciada e a 02.
- **[DECIDIR] Braços posáveis na V1?** A prancha 06 diz "pose manual com juntas de fricção" e
  mostra braço segmentado (cotovelo, punho). A especificação V1 diz braços fixos com
  adaptadores estáticos e o conceito geral diz "sem cotovelo". Junta de fricção no cotovelo
  é peça a mais, mas não é motor.
- **[OK] Painel do peito falso, LED âmbar falso na base, mão-luva removível no punho**: batem
  com M06, M08 e IF-PUNHO da arquitetura V1/V2.
- **[DECIDIR] Painéis verde-petróleo laterais no tronco (prancha 06)** e "barriga" verde atrás
  não estão em nenhuma especificação (03/04 têm um painel traseiro só).
- **[OK] 5 GDL da prancha 05** = cintura ±60°, ombros −60/+80° (os dois), pan ±90°, tilt ±30°.
  Bate com a V2. Ombros na prancha 05 usam rolamento de apoio além do servo: o envelope do
  IF-OMBRO precisa caber servo + rolamento.
- **[PROPOSTA] Câmera.** Prancha 05 põe a câmera na testa da cabeça (vista externa) e também
  presa no suporte do pan/tilt (vista explodida). Se ficar na cabeça, segue a cabeça (IF-CÂMERA
  na carcaça); se ficar no suporte, o tampão M07 da V1 fica na cabeça do mesmo jeito.

## 10. Peça 08 — cintura manual

- **[OK] Muda o M01 da V1.** Antes era um anel fixo; agora gira à mão (±60°), com fricção
  ajustável e trava. Continua parafusado em cima e embaixo e removível. Registrado na
  arquitetura.
- **[PROPOSTA] Furação igual em cima e embaixo.** A especificação aceita padrões diferentes,
  mas como nem a Peça 02 nem a traseira do tronco existem em CAD, dá para definir **um único
  padrão IF-CINTURA** (4×M4 + Ø25) usado nos dois lados. Assim qualquer cartucho (manual ou
  motorizado) entra virado para qualquer lado e as flanges são a mesma peça.
- **[DECIDIR] M4 do tronco atrás do plano de divisão.** Com a traseira como esqueleto, o
  padrão M4 de cima tem que caber inteiro na traseira; o de baixo pode ser igual (decisão
  acima). Padrão circular centrado no eixo não cabe; vira um padrão deslocado para trás ou
  retangular.
- **[PROPOSTA] Ordem de montagem e acesso.** Flange de baixo parafusa na Peça 02 por cima
  (antes do resto); o conjunto giratório cobre esses parafusos. A flange de cima prende o
  tronco por dentro, com acesso pela frente aberta do tronco. Para tirar a cintura: abrir o
  tronco, soltar o tronco, tirar o conjunto. Registrar no manual.
- **[PROPOSTA] Retenção axial independente da trava.** Eixo central com ressalto preso
  embaixo da flange inferior (o tronco não sai ao levantar) e a trava separada. Como o eixo é
  impresso, a retenção deve usar ressalto largo ou anel parafusado, nunca um encaixe fino.
- **[PROPOSTA] Fricção.** A prancha 08 aperta um anel de atrito com um parafuso radial M4.
  Isso põe toda a fricção numa área pequena (ponta do parafuso). Melhor: pré-carga axial
  em arruelas largas (PTFE/latão, área grande) e o parafuso radial só empurrando uma sapata
  impressa contra o cilindro, como trava. Batentes ±60° por pino num rasgo em arco; centro
  marcado no colar.
- **[DECIDIR] Altura.** 30 mm de cintura entram na pilha: 25 + 45 + 30 + 190 = 290 mm até o
  ombro do tronco; sobram ~260 mm para pescoço (pan/tilt), cabeça e antena até 550.

## Decisões do dono

- **2026-11-07 — Tronco traseiro é o esqueleto.** Cintura (IF-CINTURA), ombros (IF-OMBRO) e
  pescoço (IF-PESCOÇO) ficam **inteiros na carcaça traseira**; a frontal é só capa (tela do
  peito + painel), sem carga. Ombros/pescoço recuam para trás do plano de divisão, ou a
  traseira fica mais funda e a frontal mais fina. Resolve §4 (M4 e Ø25 no plano de divisão)
  e §5 (ombros/pescoço cruzando a divisão).

- **2026-11-07 — V1 estática agora, V2 motorizada depois** (ver `ARQUITETURA_V1_V2.md`, rev. A).
  Imprimir e montar tudo sem comprar motor/tela/eletrônica; nenhuma carcaça grande é
  reimpressa para a V2. Entram: módulo de cintura (giratória na V2), pan/tilt no pescoço,
  ombros motorizados dos dois lados, garra à direita, nivelador da bandeja à esquerda, câmera.

- **2026-11-07 — Tudo modular, porque o projeto vai mudar e demorar.** Regra para todas as
  peças [PROPOSTA de como aplicar]:
  - **Interface fixa, módulo trocável.** Cada carcaça tem uma interface simples e estável
    (placa plana + padrão de furos M3 com insertos, definido no arquivo de parâmetros). O que
    varia (tela, placa, alto-falante, servo, microfone) vai num **adaptador impresso** que
    parafusa nessa interface. Trocar componente = reimprimir só o adaptador.
  - **Telas:** abertura da carcaça dimensionada para o maior candidato; a janela real fica na
    **moldura** e o encaixe da tela na **bandeja**, ambas trocáveis. Vale para o rosto e para
    o peito. Assim a cabeça não precisa ser redesenhada se a tela mudar.
  - **Elétrica com conector em cada fronteira de módulo** (base↔tronco, tronco↔pescoço↔cabeça,
    tronco↔ombro): JST/Dupont travado, nunca fio soldado atravessando duas peças.
  - **Folgas, furos e padrões num só lugar** (`parameters/`); nenhuma peça repete número.
  - **Não fechar medida de componente ainda não comprado**; o adaptador espera a peça real.


- **2026-11-07 — Um ESP32-S3 só para tudo** (rosto, painel do peito, áudio, servos). Não
  usar uma placa por tela.
  Consequências [PROPOSTA, a confirmar]:
  - As duas telas no mesmo barramento SPI (chip-select separado). Tela RGB paralela de
    4,3"–5" na cabeça fica fora: sobra pouco GPIO e ela não divide barramento. Rosto vira
    SPI de até ~4" (480 × 320); o painel do peito, SPI de 3,5" (480 × 320).
  - A placa fica no tronco (perto da tela do peito, do áudio e dos servos). Pelo pescoço passam
    só SPI da cabeça + alimentação (~8 fios) e, se houver, o servo do pescoço.
  - A largura da cabeça (205 mm) e a janela do rosto passam a seguir a tela SPI escolhida.

## 11. Braços e bandeja V2 (pranchas 05/06/07 V2, 07/11)

- **[OK] Numeração fechada:** 05 = braço esquerdo, 06 = bandeja, 07 = braço direito.
- **[MUDOU] Seção redonda Ø40** em 2 metades longitudinais (antes: retangular 32×26 com
  cotovelo fixo). Esquerdo em **L** (altura ~135, alcance 145 até o centro da bandeja, curva
  R30); direito **reto** 155 (antes: cotovelo de 20°). Parâmetros atualizados em globais.py.
- **[MANTIDO] Encaixe no ombro = lingueta IF-BRAÇO** das Peças 09/10. As pranchas desenham um
  disco/flange no ombro; a especificação manda usar a interface existente — o braço abraça a
  lingueta (furação já existente, 2×M3 de fora).
- **[MUDOU] IF-PUNHO** Ø36, 3×M3 em ângulos assimétricos (90/200/340°) + chave: só entra de um
  jeito (mão, adaptador da bandeja e garra futura).
- **[PROPOSTA] Bandeja:** a prancha 06 mostra "estrutura oca" com nervuras embaixo; impressa
  com a superfície útil para cima isso vira teto sobre cavidade (suporte). Fica: fundo maciço
  de 3 mm + boss central (ou módulo aparafusado) com IF-BANDEJA (2×M3 + chave assimétrica);
  adaptador fixo V1 separado, trocado pelo nivelador na V2.
- **[VERIFICAR] Altura da bandeja:** ombro em z 239 e braço de 135 põem o segmento horizontal
  perto de z ~105, só ~35 mm acima da base (z 70) e na frente dela (bandeja até y ~190, base
  até y 100). Conferir no curso −60° do ombro (validador dos braços).

## Decisões tomadas no CAD (07/11 — dono: "resolva os problemas para tudo encaixar")

Escolhas minhas, registradas para revisão; números em `parameters/globais.py`:

- **Traseira do tronco com 75 mm** (era 65) e frontal com 30: o padrão da cintura e o pescoço
  cabem inteiros atrás do plano de divisão (y = +22,5).
- **IF-CINTURA**: 4×M4 em 70 × 30, igual em cima e embaixo; Ø25 de cabos; piso do tronco com
  abertura Ø56 (acesso ao anel de ajuste); módulo de 24 mm (o alvo era ~30; menos altura).
- **IF-OMBRO** em y = −15, z = 239, face Ø56 com 4×M3 a r20; **IF-BRAÇO** = lingueta radial.
- **IF-PESCOÇO** 4×M3 (±22, ±15) e **IF-CABEÇA** placa 60×50 em z = 356 (ver INTERFACES.md).
- **Ombro direito com curso −30°/+120°** (aceno), esquerdo −60°/+60° (bandeja). Mesmo código,
  peças espelhadas.
- **Trava positiva por pino** em ombros e tilt (fricção sozinha não basta com carga).
- **Pescoço rev. B**: eixo = parafuso com ombro ISO 7379 Ø6×65 (um M5×70 comum deixaria rosca
  dentro da bucha), buchas 6×10, calços.
- Ainda **em aberto** e sem decisão minha: base redonda × retangular (fica retangular enquanto
  não houver ordem), braços posáveis no cotovelo (fica sem cotovelo), parafusos entre as
  bases por baixo (proposto, a aplicar quando a Peça 02 for modelada).

## Decisões da rodada com 4 agentes (07/11) — a revisar pelo dono

- Base: torres da união 01↔02 em (±70, ±84) (em (±90, ±75) caíam no canto do contrapeso); 4×M3×25
  por baixo. Rasgo do LED aberto embaixo: o difusor fica preso entre 01 e 02 (troca = tirar a base
  de cima). Peça 02 impressa de cabeça para baixo. 01 tem 225 mm (passa da meta 220, cabe na A1).
- Tronco: costas planas no centro (em vez de levemente convexas) para imprimir sem suporte;
  6×M3×16 de união POR TRÁS (chave Allen 2,5 longa); anéis de sacrifício de 0,8 mm nas aberturas
  (cortar com estilete); frontal não toca a cintura nem o pescoço (alívio de 0,3).
- Cabeça: chanfros de 45° nas bordas frente/trás (imprime sem suporte), 4×M3 de união por trás
  em túneis de 89 mm (Allen longa), M05 com rosto em relevo de 1,2 mm (troca de filamento na
  camada). Massa real 666 g (hipótese era 450): momento no tilt 0,36 N·m, trava com folga 3,6×.
- Braços: braço direito encurtado para **115 mm** (155 da prancha e 125 batiam a luva na base
  com o braço pendurado; 130 é o limite com a base real). Esquerdo com curso 0…+60°.
- Altura: topo da antena em 550 mm.

## Problemas achados pela validação (e corrigidos)

| Peça | Problema | Correção |
|---|---|---|
| 11 rev. A | Pino do batente do tilt saía para dentro do montante (batente não existia) | pino virado para o berço, atravessando arruela + calço |
| 11 rev. A | Arruela PTFE do pan (Ø54) cobria o pino do batente (r 29) | arruela Ø52, pino em r 29,5; comprados entram na checagem de colisão |
| 11 rev. A | Eixo M5 cruzava a janela de cabos no meio | janela 24×22: dois canais de 8 mm ao lado do eixo |
| 11 rev. A | Parafusos da placa da cabeça dentro da janela de cabos | movidos para (±16, ±14) |
| 11 rev. B | M5×70 comum: rosca dentro da bucha | parafuso com ombro Ø6×65 |
| 08 | Critério de impressão por área reprovava pontes curtas | critério pelo vão da ponte (≤ 10–12 mm) |
| render | vistas ortogonais vazias (câmera cortava a cena) | znear/zfar da câmera |
| 09/10 | sinal do rasgo do batente e dos furos de trava invertido: no direito o "+120°" ia para TRÁS | fórmula corrigida + função única `girar()` usada por todos os validadores |
| 08 BOM | M4×10 do tronco na 08B pegava só 5 mm no inserto | M4×12 |
| 09/10 BOM | M3×12 do braço na lingueta | M3×10 (cabeça embutida no soquete) |
| base | torres no canto do contrapeso | (±70, ±84) |
| tronco | envelope do servo do ombro furava a casca | deslocado 6 mm à frente e para baixo |
| braço 07 | luva batia na base com o braço pendurado | braço 115 mm, luva menor |

## Pendências por prioridade

1. ~~Controlador~~ (decidido: um S3). Falta escolher as duas telas SPI reais.
2. Plano de divisão do tronco × eixo do robô (afeta M4, Ø25, ombros, pescoço).
3. Direção dos parafusos M3 e M4 entre base e tronco.
4. Orçamento de altura (550 mm).
5. Acessos de manutenção (moldura, painel inferior, painel traseiro), USB-C e alto-falante.
6. Por onde entram os parafusos de união 03 × 04 e da moldura da tela.
7. Servos e fonte.
