#set document(
  title: "Sistema de Deteção de Distração no Estudo com Arduino",
  author: "Inês Nascimento",
)

#set page(
  paper: "a4",
  margin: (top: 2.5cm, bottom: 2.5cm, left: 2.5cm, right: 2.5cm),
  numbering: "1",
  number-align: center,
)

#set text(
  font: "New Computer Modern",
  size: 11pt,
  lang: "pt",
)

#set par(
  justify: true,
  leading: 0.72em,
  spacing: 1.2em,
)

#set heading(numbering: "1.")

#show heading: it => {
  v(0.8em)
  it
  v(0.5em)
}

// Capa
#page(numbering: none)[
  #grid(
    columns: (1fr, 1fr),
    align(left)[
      #image("logo ipb.png", height: 2cm)
    ],
    align(right)[
      #image("logo estig.png", height: 2cm)
    ],
  )

  #align(center)[
    #v(2.5cm)
    #text(size: 13pt)[Instituto Politécnico de Beja] \
    #text(size: 12pt)[Escola Superior de Tecnologia e Gestão] \
    #v(0.2cm)
    #text(size: 12pt)[Licenciatura em Engenharia Informática] \
    #v(0.3cm)
    #text(size: 12pt)[Física Aplicada à Computação]

    #v(2.8cm)

    #line(length: 100%)
    #v(0.5cm)
    #text(size: 19pt, weight: "bold")[
      Sistema de Deteção de Distração \
      no Estudo com Arduino
    ]
    #v(0.3cm)
    #text(size: 13pt, style: "italic")[
      Monitorização de comportamento com acelerómetro \
      e análise de dados em Python
    ]
    #v(0.5cm)
    #line(length: 100%)

    #v(3cm)

    #text(size: 12pt)[
      *Autora:* Inês Nascimento \
      *Número:* 24481 \
      #v(0.3cm)
      *Docente:* Nuno Pereira
    ]

    #v(3cm)
    #text(size: 11pt)[Beja, julho de 2026]
  ]
]

// Índice
#page(numbering: none)[
  #outline(
    title: "Índice",
    indent: auto,
  )
]

// Início do conteúdo
= Introdução

A dificuldade em manter a concentração durante períodos prolongados de estudo é um problema transversal a muitos estudantes, agravado pela omnipresença dos dispositivos móveis. O telemóvel, em particular, constitui uma das principais fontes de distração, dado o seu apelo constante através de notificações, redes sociais e aplicações de entretenimento.

Este projeto propõe o desenvolvimento de um sistema de monitorização de distração durante o estudo, recorrendo ao microcontrolador *Arduino Nano RP2040 Connect* e ao acelerómetro integrado no dispositivo. A ideia central é colocar o Arduino em cima do telemóvel: quando este é levantado, o acelerómetro deteta a variação de aceleração e regista o evento como uma distração. Os dados são enviados para o computador via ligação USB, onde um script em Python os armazena num ficheiro Excel e um dashboard interativo permite visualizá-los de forma clara e detalhada.

O projeto surgiu no âmbito da cadeira de Física Aplicada à Computação e procura ir além de uma mera demonstração técnica, propondo uma ferramenta genuinamente útil que aplica conceitos físicos reais — nomeadamente a medição de aceleração, a análise de sinais e a filtragem de dados — num contexto do quotidiano.

== Objetivos

- Detetar em tempo real a elevação do telemóvel através do acelerómetro integrado no Arduino Nano RP2040 Connect;
- Registar cada evento de distração com data, hora de início, hora de fim e duração;
- Armazenar os dados de forma persistente num ficheiro Excel (`.xlsx`);
- Desenvolver um dashboard interativo em HTML/JavaScript que permita visualizar e filtrar os dados por dia, semana e mês;
- Estabelecer a ligação entre os fundamentos físicos da acelerometria e a aplicação prática desenvolvida.

= Fundamentos Físicos

== Aceleração e Força

A aceleração é uma grandeza física vetorial que descreve a taxa de variação da velocidade de um corpo em função do tempo. De acordo com a segunda lei de Newton:

$ F = m dot a $

onde $F$ representa a força resultante aplicada ao corpo (em Newtons), $m$ a sua massa (em quilogramas) e $a$ a aceleração resultante (em metros por segundo ao quadrado). Esta relação é fundamental para compreender o funcionamento dos acelerómetros: ao medir as forças que atuam sobre uma massa de prova interna, é possível inferir a aceleração do dispositivo.

== Acelerómetros MEMS

Os acelerómetros modernos, como o *LSM6DSOX* presente no Arduino Nano RP2040 Connect, são fabricados com tecnologia *MEMS* (Micro-Electro-Mechanical Systems). Estes dispositivos consistem numa estrutura microscópica com uma massa suspensa por molas, cujo deslocamento é medido eletricamente quando sujeita a uma força de aceleração.

A sensibilidade de um acelerómetro MEMS é expressa em $g$, onde $1g approx 9.81 "m/s"^2$ corresponde à aceleração gravítica terrestre. Em repouso sobre uma superfície plana, o eixo perpendicular à superfície regista aproximadamente $1g$, enquanto os eixos horizontais registam valores próximos de zero.

== A Gravidade como Referência

Uma propriedade fundamental que torna os acelerómetros especialmente úteis é o facto de medirem não apenas acelerações dinâmicas, mas também a aceleração estática devida à gravidade. Quando o dispositivo está completamente em repouso, o vetor de aceleração medido corresponde ao vetor gravitacional:

$ arrow(a)_"repouso" = -arrow(g) $

Esta propriedade permite distinguir dois estados do sistema:

- *Repouso:* o telemóvel está pousado na mesa; os valores de aceleração são estáveis e próximos dos valores de calibração;
- *Movimento:* o telemóvel é levantado; a reorientação do dispositivo em relação ao vetor gravitacional provoca variações significativas nos três eixos.

== Ruído e Calibração

Qualquer sensor físico está sujeito a ruído de medição — flutuações aleatórias nos valores lidos que não correspondem a variações reais na grandeza medida. No caso do acelerómetro LSM6DSOX, estas flutuações são tipicamente da ordem de $pm 0.02g$ em condições estáticas.

Para mitigar o efeito do ruído e evitar falsas deteções, o sistema implementa uma fase de *calibração automática*: nos primeiros segundos de funcionamento, são recolhidas 50 amostras consecutivas em repouso e calculada a média de cada eixo:

$ overline(a)_x = 1/N sum_(i=1)^N a_(x,i), quad overline(a)_y = 1/N sum_(i=1)^N a_(y,i), quad overline(a)_z = 1/N sum_(i=1)^N a_(z,i) $

Estes valores constituem a linha de base do sistema. Uma variação superior a $0.5g$ em qualquer eixo relativamente à linha de base é interpretada como movimento, acionando o registo de uma distração.

= Hardware

== Arduino Nano RP2040 Connect

O *Arduino Nano RP2040 Connect* é um microcontrolador de fator de forma compacto baseado no chip *RP2040* da Raspberry Pi Foundation. As suas características principais incluem:

#table(
  columns: (auto, 1fr),
  inset: 9pt,
  stroke: 0.5pt,
  align: (left, left),
  [*Componente*], [*Especificação*],
  [Processador], [Dual-core ARM Cortex-M0+ a 133 MHz],
  [Memória RAM], [264 KB SRAM],
  [Memória Flash], [16 MB],
  [IMU], [LSM6DSOX (acelerómetro + giroscópio de 6 eixos)],
  [Microfone], [MP34DT05 (PDM, integrado)],
  [Conectividade], [Wi-Fi 802.11 b/g/n e Bluetooth 4.2 (módulo u-blox NINA-W102)],
  [LED RGB], [Integrado, controlado via módulo NINA],
  [Interface], [USB Micro-B, I2C, SPI, UART],
)

Para este projeto, os componentes relevantes são o *IMU LSM6DSOX*, utilizado para detetar o movimento do telemóvel, e o *LED RGB*, utilizado como indicador visual do estado do sistema.

== IMU LSM6DSOX

O sensor inercial LSM6DSOX da STMicroelectronics combina um acelerómetro e um giroscópio de 6 eixos num único pacote compacto. As suas principais características são:

- *Gama de medição do acelerómetro:* ±2g, ±4g, ±8g ou ±16g (configurável);
- *Resolução:* 16 bits por eixo;
- *Taxa de amostragem:* até 6664 Hz;
- *Interface:* I2C e SPI;
- *Consumo em modo normal:* 0.55 mA.

Neste projeto, a biblioteca `Arduino_LSM6DSOX` é utilizada para comunicar com o sensor via I2C, a uma frequência de amostragem de 10 Hz (uma leitura a cada 100 ms).

== Configuração Física

O sistema não requer hardware adicional além do Arduino Nano RP2040 Connect e do cabo USB. O Arduino é colocado em cima do telemóvel durante as sessões de estudo, ligado ao computador via USB. O LED RGB do Arduino serve como indicador visual imediato:

#table(
  columns: (auto, auto, 1fr),
  inset: 9pt,
  stroke: 0.5pt,
  [*Estado*], [*Cor do LED*], [*Significado*],
  [Em estudo], [Verde], [Nenhum movimento detetado; o utilizador está a estudar],
  [Distração], [Vermelho], [Movimento detetado; o telemóvel foi levantado],
)

= Software

== Arquitetura do Sistema

O sistema é composto por três componentes de software distintos:

+ *Firmware do Arduino* (C++) — responsável pela leitura do acelerómetro, deteção de movimento e comunicação Serial com o PC;
+ *Script de monitorização* (`monitor.py`) — corre no PC, recebe os eventos do Arduino via porta Serial e regista-os num ficheiro Excel;
+ *Script de dashboard* (`gerar_dashboard.py`) — lê o ficheiro Excel e gera um ficheiro HTML com um dashboard interativo.

O fluxo de dados é o seguinte:

#align(center)[
  *Arduino (IMU)* → *Serial USB* → *Python (monitor.py)* → *Excel (.xlsx)* → *Python (gerar_dashboard.py)* → *Dashboard HTML*
]

== Firmware do Arduino

O firmware implementa as seguintes funcionalidades:

*Calibração automática:* no arranque, o sistema aguarda que o utilizador não mexa no Arduino durante a fase de calibração (50 amostras, ~2.5 segundos). A média de cada eixo é calculada e armazenada como linha de base.

*Deteção de movimento:* em cada ciclo de 100 ms, são lidas as acelerações nos três eixos e calculada a diferença relativamente à linha de base. Se qualquer eixo exceder o limiar de $0.5g$, é enviada a mensagem `DISTRACAO_INICIO` via Serial. Quando os valores regressam abaixo do limiar, é enviado `DISTRACAO_FIM`.

*Indicação visual:* o LED RGB muda de cor em função do estado — verde durante o estudo, vermelho durante uma distração.

```cpp
void loop() {
  float x, y, z;
  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(x, y, z);
    float diffX = abs(x - baseX);
    float diffY = abs(y - baseY);
    float diffZ = abs(z - baseZ);

    if (diffX > THRESHOLD || diffY > THRESHOLD || diffZ > THRESHOLD) {
      if (!phonePickedUp) {
        phonePickedUp = true;
        Serial.println("DISTRACAO_INICIO");
        // LED vermelho
      }
    } else {
      if (phonePickedUp) {
        phonePickedUp = false;
        Serial.println("DISTRACAO_FIM");
        // LED verde
      }
    }
  }
  delay(100);
}
```

== Script de Monitorização (Python)

O script `monitor.py` corre continuamente no PC enquanto o Arduino está ligado. Ao receber `DISTRACAO_INICIO`, regista a hora de início. Ao receber `DISTRACAO_FIM`, calcula a duração e escreve uma nova linha no ficheiro Excel com os seguintes campos:

- `data` — data do evento (formato YYYY-MM-DD);
- `hora_inicio` — hora em que o telemóvel foi levantado;
- `hora_fim` — hora em que o telemóvel foi pousado;
- `duracao_segundos` — duração da distração em segundos.

A biblioteca `openpyxl` é utilizada para leitura e escrita do ficheiro `.xlsx`, garantindo compatibilidade com o Microsoft Excel e o Power BI.

== Dashboard Interativo

O script `gerar_dashboard.py` lê o ficheiro Excel e gera um ficheiro HTML auto-suficiente que pode ser aberto em qualquer browser sem instalação de software adicional. O dashboard inclui:

- *Cards de resumo:* total de distrações, tempo total distraído, duração média e hora mais problemática;
- *Gráfico principal com filtro por período:* permite alternar entre vista diária, semanal e mensal com um clique;
- *Gráfico de distribuição horária:* mostra a que horas do dia ocorrem mais distrações;
- *Gráfico de linha com duração acumulada por dia:* permite identificar dias com distrações mais prolongadas;
- *Gráfico semanal:* visão agregada por semana;
- *Tabela detalhada:* lista todos os eventos com filtro por dia e classificação automática em "Rápida" (<30s), "Média" (30s–2min) e "Longa" (>2min).

O dashboard é gerado com recurso à biblioteca *Chart.js*, carregada via CDN, e não requer qualquer servidor web.

= Metodologia e Resultados

== Processo de Recolha de Dados

Os dados foram recolhidos ao longo de um período de aproximadamente um mês, durante sessões de estudo com o Arduino posicionado em cima do telemóvel. Sempre que o telemóvel era levantado — para consultar notificações, redes sociais ou simplesmente por hábito — o sistema registava o evento automaticamente.

A recolha decorreu de forma completamente passiva: o script `monitor.py` corria em segundo plano no computador e o único indicador visual era o LED do Arduino, que mudava de verde para vermelho em cada distração detetada.

== Análise dos Dados Recolhidos

Ao longo do período de monitorização foram registadas *154 distrações* distribuídas por 24 dias de estudo, totalizando aproximadamente *1h 32 minutos* de tempo distraído.

#table(
  columns: (1fr, auto),
  inset: 9pt,
  stroke: 0.5pt,
  [*Métrica*], [*Valor*],
  [Total de distrações], [154],
  [Dias monitorizados], [24],
  [Média de distrações por dia], [~6.4],
  [Tempo total distraído], [1h 32min],
  [Duração média por distração], [~36 segundos],
  [Hora mais problemática], [17h],
)

A análise dos dados revela alguns padrões interessantes. As distrações tendem a concentrar-se ao final da tarde (entre as 15h e as 18h), o que pode estar relacionado com a fadiga mental acumulada ao longo do dia e com o aumento da atividade nas redes sociais nesse período. Os fins de semana apresentam consistentemente menos distrações, não necessariamente por maior disciplina, mas por sessões de estudo mais curtas ou inexistentes.

Em termos de duração, a maioria das distrações é relativamente breve — muitas com menos de 30 segundos — o que sugere que se tratam frequentemente de verificações rápidas do telemóvel e não de períodos prolongados de distração. Ainda assim, as distrações mais longas (superiores a 2 minutos) contribuem desproporcionalmente para o tempo total distraído.

== Dashboard — Visualização dos Resultados

O dashboard gerado permite explorar os dados de forma interativa. A funcionalidade de filtro por dia permite identificar quais foram os dias mais problemáticos, enquanto a vista semanal e mensal oferece uma perspetiva de evolução ao longo do tempo.

#align(center)[
  _[Inserir capturas de ecrã do dashboard aqui]_
]

= Discussão

== Ligação aos Conceitos Físicos

Este projeto ilustra de forma concreta a aplicação de conceitos fundamentais de física no desenvolvimento de sistemas computacionais. A deteção de movimento baseia-se na medição da aceleração gravitacional — um conceito estudado na mecânica clássica — e na sua variação quando o dispositivo muda de orientação ou sofre uma aceleração dinâmica.

A fase de calibração exemplifica um princípio importante em metrologia: qualquer medição é afetada por incertezas sistemáticas e aleatórias, e é necessário estabelecer uma referência antes de interpretar os resultados. O valor médio calculado durante a calibração funciona como essa referência, tornando o sistema independente das condições específicas de cada mesa ou posição.

O limiar de deteção ($0.5g$) representa uma escolha de compromisso entre sensibilidade e especificidade: um valor demasiado baixo geraria falsas deteções (qualquer vibração seria interpretada como distração); um valor demasiado alto deixaria passar movimentos reais. Esta escolha foi validada empiricamente durante os testes.

== Limitações

Apesar dos resultados satisfatórios, o sistema apresenta algumas limitações que importa reconhecer:

- *Dependência do cabo USB:* o Arduino tem de estar permanentemente ligado ao computador para transmitir os dados, o que limita a mobilidade e obriga a ter o telemóvel perto do PC;
- *Falsos positivos:* vibrações da mesa causadas por batidas ou pela passagem de pessoas podem ser interpretadas como distrações;
- *Contexto de uso limitado:* o sistema assume que levantar o telemóvel equivale sempre a distração, quando por vezes pode tratar-se de uma necessidade legítima (receber uma chamada, verificar as horas, etc.);
- *Ausência de conectividade sem fios:* a versão atual não utiliza o módulo Wi-Fi do Arduino, o que poderia eliminar a necessidade do cabo USB numa versão futura.

== Trabalho Futuro

As limitações identificadas apontam para várias direções de desenvolvimento futuro:

- *Comunicação Wi-Fi:* implementar o envio de dados via HTTP para um servidor local, eliminando a dependência do cabo USB e permitindo alimentar o Arduino com uma power bank;
- *Filtro de médias móveis:* aplicar uma média sobre as últimas N leituras antes de tomar uma decisão, reduzindo a sensibilidade ao ruído e aos falsos positivos;
- *Classificação de distrações:* distinguir automaticamente entre distrações curtas (verificação rápida) e longas (uso prolongado), e adaptar os alertas em conformidade;
- *Alertas sonoros:* adicionar um buzzer que emita um sinal após um determinado número de distrações, incentivando o utilizador a manter o foco.

= Conclusão

Este trabalho demonstrou a viabilidade de desenvolver um sistema de monitorização de comportamento funcional e útil com recurso a hardware de baixo custo e software open-source. O Arduino Nano RP2040 Connect, com o seu acelerómetro integrado, revelou-se uma plataforma adequada para a deteção de movimento em tempo real, e a combinação com Python e um dashboard HTML tornou os dados acessíveis e interpretáveis.

Do ponto de vista físico, o projeto evidenciou como a medição da aceleração gravitacional — um conceito clássico da mecânica — pode ser aplicada de forma prática e inovadora no contexto da computação e da monitorização de comportamento. A fase de calibração, o tratamento do ruído e a definição do limiar de deteção refletem desafios reais que qualquer sistema de medição enfrenta, independentemente da sua escala ou complexidade.

O resultado final é uma ferramenta que, apesar das suas limitações, oferece uma perspetiva genuinamente útil sobre os hábitos de estudo e constitui uma base sólida para desenvolvimentos futuros.

= Referências

#set par(hanging-indent: 1.5em, spacing: 1em)

Arduino. (2024). _Arduino Nano RP2040 Connect — Documentation_. https://docs.arduino.cc/hardware/nano-rp2040-connect/

STMicroelectronics. (2021). _LSM6DSOX — iNEMO inertial module: Always-on 3D accelerometer and 3D gyroscope_. Datasheet DS12451.

Meriam, J. L., & Kraige, L. G. (2012). _Engineering Mechanics: Dynamics_ (7th ed.). Wiley.

McKinney, W. (2022). _Python for Data Analysis_ (3rd ed.). O'Reilly Media.

Plotly Technologies Inc. (2015). _Collaborative data science_. https://plotly.com

Chart.js Contributors. (2024). _Chart.js — Simple yet flexible JavaScript charting library_. https://www.chartjs.org
