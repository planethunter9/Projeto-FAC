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

// Numeração de figuras e tabelas
#set figure(numbering: "1")

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

// Resumo
#page(numbering: none)[
  #heading(level: 1, numbering: none)[Resumo]

  Este trabalho apresenta o desenvolvimento de um sistema de monitorização de distração durante sessões de estudo, recorrendo ao microcontrolador Arduino Nano RP2040 Connect e ao acelerómetro integrado no dispositivo. O sistema deteta a elevação do telemóvel — interpretada como um momento de distração — e regista automaticamente o evento com data, hora de início, hora de fim e duração. Os dados são armazenados num ficheiro Excel e visualizados através de um dashboard interativo desenvolvido em HTML e JavaScript, que permite filtrar e analisar as distrações por dia, semana e mês. O projeto foi desenvolvido no âmbito da cadeira de Física Aplicada à Computação e procura estabelecer uma ligação clara entre os fundamentos físicos da acelerometria e a sua aplicação prática num contexto do quotidiano.

  #v(0.5em)
  *Palavras-chave:* Arduino, acelerómetro, distração, monitorização, dashboard, Python, Excel, física aplicada.

  #v(2em)
  #heading(level: 1, numbering: none)[Abstract]

  This work presents the development of a distraction monitoring system during study sessions, using the Arduino Nano RP2040 Connect microcontroller and its built-in accelerometer. The system detects when the phone is lifted — interpreted as a moment of distraction — and automatically records the event with date, start time, end time and duration. The data is stored in an Excel file and visualized through an interactive dashboard developed in HTML and JavaScript, which allows filtering and analyzing distractions by day, week and month. The project was developed in the context of the Applied Physics to Computing course and aims to establish a clear connection between the physical foundations of accelerometry and its practical application in an everyday context.

  #v(0.5em)
  *Keywords:* Arduino, accelerometer, distraction, monitoring, dashboard, Python, Excel, applied physics.
]

// Índice
#page(numbering: none)[
  #outline(
    title: "Índice",
    indent: auto,
  )
]

= Introdução

A dificuldade em manter a concentração durante períodos prolongados de estudo é um problema transversal a muitos estudantes, agravado pela omnipresença dos dispositivos móveis. O telemóvel, em particular, constitui uma das principais fontes de distração, dado o seu apelo constante através de notificações, redes sociais e aplicações de entretenimento.

Este projeto propõe o desenvolvimento de um sistema de monitorização de distração durante o estudo, recorrendo ao microcontrolador *Arduino Nano RP2040 Connect* e ao acelerómetro integrado no dispositivo. A ideia central é colocar o Arduino em cima do telemóvel: quando este é levantado, o acelerómetro deteta a variação de aceleração e regista o evento como uma distração. Os dados são enviados para o computador via ligação USB, onde um script em Python os armazena num ficheiro Excel e um dashboard interativo permite visualizá-los de forma clara e detalhada.

O projeto surgiu no âmbito da cadeira de Física Aplicada à Computação e procura ir além de uma mera demonstração técnica, propondo uma ferramenta genuinamente útil que aplica conceitos físicos reais num contexto do quotidiano.

== Objetivos

- Detetar em tempo real a elevação do telemóvel através do acelerómetro integrado no Arduino Nano RP2040 Connect;
- Registar cada evento de distração com data, hora de início, hora de fim e duração;
- Armazenar os dados de forma persistente num ficheiro Excel (`.xlsx`);
- Desenvolver um dashboard interativo em HTML/JavaScript que permita visualizar e filtrar os dados por dia, semana e mês;
- Estabelecer a ligação entre os fundamentos físicos da acelerometria e a aplicação prática desenvolvida.

== Estrutura do Documento

O presente documento está organizado da seguinte forma: o Capítulo 2 apresenta os fundamentos físicos subjacentes ao sistema; o Capítulo 3 descreve o hardware utilizado; o Capítulo 4 detalha o software desenvolvido; o Capítulo 5 apresenta a metodologia e os resultados obtidos; e o Capítulo 6 discute os resultados e apresenta as conclusões.

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

Qualquer sensor físico está sujeito a ruído de medição — flutuações aleatórias nos valores lidos que não correspondem a variações reais na grandeza medida. No caso do acelerómetro LSM6DSOX, estas flutuações são tipicamente da ordem de $plus.minus 0.02g$ em condições estáticas.

Para mitigar o efeito do ruído e evitar falsas deteções, o sistema implementa uma fase de *calibração automática*: nos primeiros segundos de funcionamento, são recolhidas 50 amostras consecutivas em repouso e calculada a média de cada eixo:

$ overline(a)_x = 1/N sum_(i=1)^N a_(x,i), quad overline(a)_y = 1/N sum_(i=1)^N a_(y,i), quad overline(a)_z = 1/N sum_(i=1)^N a_(z,i) $

Estes valores constituem a linha de base do sistema. Uma variação superior a $0.5g$ em qualquer eixo relativamente à linha de base é interpretada como movimento, acionando o registo de uma distração.

= Hardware

== Arduino Nano RP2040 Connect

O *Arduino Nano RP2040 Connect* é um microcontrolador de fator de forma compacto baseado no chip *RP2040* da Raspberry Pi Foundation. A Tabela 3.1 resume as suas principais características.

#figure(
  table(
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
    [Conectividade], [Wi-Fi 802.11 b/g/n e Bluetooth 4.2],
    [LED RGB], [Integrado, controlado via módulo NINA],
    [Interface], [USB Micro-B, I2C, SPI, UART],
  ),
  caption: [Especificações do Arduino Nano RP2040 Connect]
)

== IMU LSM6DSOX

O sensor inercial LSM6DSOX da STMicroelectronics combina um acelerómetro e um giroscópio de 6 eixos num único pacote compacto. As suas principais características são:

- *Gama de medição:* ±2g, ±4g, ±8g ou ±16g (configurável);
- *Resolução:* 16 bits por eixo;
- *Taxa de amostragem:* até 6664 Hz;
- *Interface:* I2C e SPI;
- *Consumo em modo normal:* 0.55 mA.

Neste projeto, a biblioteca `Arduino_LSM6DSOX` é utilizada para comunicar com o sensor via I2C, a uma frequência de amostragem de 10 Hz (uma leitura a cada 100 ms).

== Configuração Física

O sistema não requer hardware adicional além do Arduino Nano RP2040 Connect e do cabo USB. O Arduino é colocado em cima do telemóvel durante as sessões de estudo, ligado ao computador via USB. O LED RGB serve como indicador visual imediato:

#figure(
  table(
    columns: (auto, auto, 1fr),
    inset: 9pt,
    stroke: 0.5pt,
    [*Estado*], [*Cor do LED*], [*Significado*],
    [Em estudo], [Verde], [Nenhum movimento detetado; o utilizador está a estudar],
    [Distração], [Vermelho], [Movimento detetado; o telemóvel foi levantado],
  ),
  caption: [Comportamento do LED RGB em função do estado do sistema]
)

= Software

== Arquitetura do Sistema

O sistema é composto por três componentes de software distintos:

+ *Firmware do Arduino* (C++) — responsável pela leitura do acelerómetro, deteção de movimento e comunicação Serial com o PC;
+ *Script principal* (`main.py`) — corre no PC, recebe os eventos do Arduino via porta Serial, regista-os num ficheiro Excel e gera o dashboard no final de cada sessão;
+ *Dashboard interativo* — ficheiro HTML gerado automaticamente, visualizável em qualquer browser.

O fluxo de dados é o seguinte:

#align(center)[
  *Arduino (IMU)* → *Serial USB* → *Python (main.py)* → *Excel (.xlsx)* → *Dashboard HTML*
]

== Firmware do Arduino

O firmware implementa as seguintes funcionalidades:

*Calibração automática:* no arranque, o sistema recolhe 50 amostras em repouso e calcula a média de cada eixo como linha de base.

*Deteção de movimento:* em cada ciclo de 100 ms, são lidas as acelerações nos três eixos e calculada a diferença relativamente à linha de base. Se qualquer eixo exceder o limiar de $0.5g$, é enviada a mensagem `DISTRACAO_INICIO` via Serial.

*Indicação visual:* o LED RGB muda de cor — verde durante o estudo, vermelho durante uma distração.

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
      }
    } else {
      if (phonePickedUp) {
        phonePickedUp = false;
        Serial.println("DISTRACAO_FIM");
      }
    }
  }
  delay(100);
}
```

== Script Principal (Python)

O script `main.py` deteta automaticamente a porta COM do Arduino, elimina a necessidade de configuração manual, e regista cada evento no ficheiro Excel com os campos: `data`, `hora_inicio`, `hora_fim` e `duracao_segundos`. Quando o utilizador termina a sessão com Ctrl+C, o dashboard é gerado e aberto automaticamente no browser.

== Dashboard Interativo

O dashboard é gerado automaticamente em HTML e inclui:

- *Cards de resumo:* total de distrações, tempo total distraído, duração média e hora mais problemática;
- *Gráfico principal com filtro por período:* permite alternar entre vista diária, semanal e mensal;
- *Gráfico de distribuição horária:* mostra a que horas do dia ocorrem mais distrações;
- *Gráfico de linha:* duração acumulada distraída por dia em minutos;
- *Gráfico semanal com variação percentual:* barras vermelhas indicam semanas piores; verdes indicam melhoria;
- *Tabela detalhada:* com filtro por dia e por tipo (Rápida <30s, Média 30s–2min, Longa >2min);
- *Modo claro/escuro:* botão de alternância no canto superior direito.

== Executável

O projeto foi empacotado num executável Windows (`.exe`) utilizando **PyInstaller**, permitindo que o sistema seja utilizado sem instalação de Python ou de qualquer dependência adicional.

= Metodologia e Resultados

== Recolha de Dados

Os dados foram recolhidos ao longo de aproximadamente um mês, durante sessões de estudo com o Arduino posicionado em cima do telemóvel, ligado ao computador via USB. A recolha decorreu de forma completamente passiva — o script corria em segundo plano e o único indicador visual era o LED do Arduino.

== Resultados Obtidos

Ao longo do período de monitorização foram registadas *159 distrações* distribuídas por 25 dias de estudo, totalizando aproximadamente *4 horas e 44 minutos* de tempo distraído.

#figure(
  table(
    columns: (1fr, auto),
    inset: 9pt,
    stroke: 0.5pt,
    [*Métrica*], [*Valor*],
    [Total de distrações], [159],
    [Dias monitorizados], [25],
    [Média de distrações por dia], [\~6.4],
    [Tempo total distraído], [4h 44min],
    [Duração média por distração], [\~107 segundos],
    [Hora com mais distrações], [19h],
  ),
  caption: [Métricas obtidas durante o período de monitorização]
)

A análise dos dados revela padrões interessantes. As distrações tendem a concentrar-se ao final do dia (entre as 17h e as 20h), o que pode estar relacionado com a fadiga mental acumulada e com o aumento da atividade nas redes sociais nesse período. Os fins de semana apresentam consistentemente menos distrações.

Em termos de duração, a maioria das distrações é relativamente breve — muitas com menos de 30 segundos — o que sugere verificações rápidas do telemóvel. As distrações mais longas (superiores a 2 minutos) contribuem desproporcionalmente para o tempo total distraído.

= Discussão e Conclusão

== Ligação aos Conceitos Físicos

Este projeto ilustra de forma concreta a aplicação de conceitos fundamentais de física no desenvolvimento de sistemas computacionais. A deteção de movimento baseia-se na medição da aceleração gravitacional e na sua variação quando o dispositivo muda de orientação — um conceito clássico da mecânica que aqui encontra uma aplicação prática e inovadora.

A fase de calibração exemplifica um princípio importante em metrologia: qualquer medição é afetada por incertezas sistemáticas e aleatórias, sendo necessário estabelecer uma referência antes de interpretar os resultados. O limiar de deteção ($0.5g$) representa uma escolha de compromisso entre sensibilidade e especificidade, validada empiricamente durante os testes.

== Limitações

- *Dependência do cabo USB:* o Arduino tem de estar permanentemente ligado ao computador, o que limita a mobilidade;
- *Falsos positivos:* vibrações da mesa causadas por batidas ou pela passagem de pessoas podem ser interpretadas como distrações;
- *Contexto limitado:* levantar o telemóvel nem sempre equivale a distração (chamadas, verificar as horas, etc.).

== Trabalho Futuro

Como trabalho futuro, seria interessante:

- Implementar comunicação Wi-Fi para eliminar a dependência do cabo USB, alimentando o Arduino com uma _power bank_;
- Aplicar um filtro de médias móveis para reduzir a sensibilidade ao ruído e aos falsos positivos;
- Adicionar alertas sonoros via _buzzer_ externo após um determinado número de distrações;
- Distinguir automaticamente entre distrações curtas e longas e adaptar os alertas em conformidade.

== Conclusão

Este trabalho demonstrou a viabilidade de desenvolver um sistema de monitorização de comportamento funcional e útil com recurso a hardware de baixo custo e _software_ _open-source_. O Arduino Nano RP2040 Connect, com o seu acelerómetro integrado, revelou-se uma plataforma adequada para a deteção de movimento em tempo real, e a combinação com Python e um dashboard HTML tornou os dados acessíveis e interpretáveis de forma visualmente apelativa.

Do ponto de vista físico, o projeto evidenciou como a medição da aceleração gravitacional pode ser aplicada de forma prática e inovadora no contexto da computação e da monitorização de comportamento. O resultado final é uma ferramenta que, apesar das suas limitações, oferece uma perspetiva genuinamente útil sobre os hábitos de estudo e constitui uma base sólida para desenvolvimentos futuros.

= Referências

#set par(hanging-indent: 1.5em, spacing: 1em)

Arduino. (2024). _Arduino Nano RP2040 Connect — Documentation_. https://docs.arduino.cc/hardware/nano-rp2040-connect/

STMicroelectronics. (2021). _LSM6DSOX — iNEMO inertial module: Always-on 3D accelerometer and 3D gyroscope_. Datasheet DS12451.

Meriam, J. L., & Kraige, L. G. (2012). _Engineering Mechanics: Dynamics_ (7th ed.). Wiley.

McKinney, W. (2022). _Python for Data Analysis_ (3rd ed.). O'Reilly Media.

Chart.js Contributors. (2024). _Chart.js — Simple yet flexible JavaScript charting library_. https://www.chartjs.org
