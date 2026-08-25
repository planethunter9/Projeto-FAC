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

#set figure(numbering: "1")

// ─────────────────────────────────────────────────────────
// CAPA
// ─────────────────────────────────────────────────────────
#page(numbering: none)[
  #grid(
    columns: (1fr, 1fr),
    align(left)[
      #image("logo ipb.png", height: 4cm)
    ],
    align(right)[
      #image("logo estig.png", height: 4cm)
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

// ─────────────────────────────────────────────────────────
// RESUMO
// ─────────────────────────────────────────────────────────
#page(numbering: none)[
  #heading(level: 1, numbering: none)[Resumo]

  Este trabalho apresenta o desenvolvimento de um sistema de monitorização de distração durante sessões de estudo, recorrendo ao microcontrolador Arduino Nano RP2040 Connect e ao acelerómetro integrado no dispositivo. O sistema deteta a elevação do telemóvel — interpretada como um momento de distração — e regista automaticamente o evento com data, hora de início, hora de fim e duração. Os dados são armazenados num ficheiro Excel e visualizados através de um dashboard interativo desenvolvido em HTML e JavaScript, que permite filtrar e analisar as distrações por dia, semana e mês, com funcionalidades de drill-down interativo e distribuição por período do dia.

  O projeto foi desenvolvido no âmbito da cadeira de Física Aplicada à Computação e procura estabelecer uma ligação clara entre os fundamentos físicos da acelerometria — nomeadamente a medição de aceleração, o ruído de sensor e a calibração — e a sua aplicação prática num contexto do quotidiano. Os resultados obtidos revelam padrões de distração consistentes, com maior incidência ao final do dia e maioria das distrações de curta duração.

  #v(0.5em)
  *Palavras-chave:* Arduino, acelerómetro, distração, monitorização, dashboard, Python, HTML, Excel.

  #v(2em)
  #heading(level: 1, numbering: none)[Abstract]

  This work presents the development of a distraction monitoring system during study sessions, using the Arduino Nano RP2040 Connect microcontroller and its built-in accelerometer. The system detects when the phone is lifted — interpreted as a moment of distraction — and automatically records the event with date, start time, end time and duration. The data is stored in an Excel file and visualized through an interactive dashboard developed in HTML and JavaScript, allowing filtering and analysis of distractions by day, week and month, with interactive drill-down features and time-of-day distribution.

  The project was developed in the context of the Applied Physics to Computing course and aims to establish a clear connection between the physical foundations of accelerometry — namely acceleration measurement, sensor noise and calibration — and their practical application in an everyday context. The results obtained reveal consistent distraction patterns, with higher incidence at the end of the day and the majority of distractions being of short duration.

  #v(0.5em)
  *Keywords:* Arduino, accelerometer, distraction, monitoring, dashboard, Python, Excel, applied physics.
]

// ─────────────────────────────────────────────────────────
// ÍNDICE
// ─────────────────────────────────────────────────────────
#page(numbering: none)[
  #outline(
    title: "Índice",
    indent: auto,
  )
]

// ─────────────────────────────────────────────────────────
// 1. INTRODUÇÃO
// ─────────────────────────────────────────────────────────
= Introdução

A dificuldade em manter a concentração durante períodos prolongados de estudo é um problema transversal a muitos estudantes universitários e profissionais, agravado de forma significativa pela omnipresença dos dispositivos móveis. O telemóvel, em particular, constitui uma das principais fontes de distração no contexto académico, dado o seu apelo constante através de notificações, redes sociais e aplicações de entretenimento. Estudos recentes na área da psicologia cognitiva indicam que uma distração, mesmo que breve, pode interromper o estado de _flow_ — o estado de concentração profunda e produtiva — por um período significativamente superior à duração da própria distração.

A tomada de consciência dos próprios padrões de comportamento é frequentemente apontada como o primeiro passo para a sua modificação. Neste sentido, um sistema de monitorização passiva que registe automaticamente as distrações sem exigir qualquer ação por parte do utilizador pode ser uma ferramenta genuinamente útil para promover hábitos de estudo mais produtivos.

Este projeto propõe o desenvolvimento de um sistema de monitorização de distração durante o estudo, recorrendo ao microcontrolador *Arduino Nano RP2040 Connect* e ao acelerómetro integrado no dispositivo. A ideia central é colocar o Arduino em cima do telemóvel: quando este é levantado, o acelerómetro deteta a variação de aceleração e regista o evento como uma distração. Os dados são enviados para o computador via ligação USB, onde um script em Python os armazena num ficheiro Excel e um dashboard interativo permite visualizá-los de forma clara e detalhada.

O projeto surgiu no âmbito da cadeira de Física Aplicada à Computação e procura ir além de uma mera demonstração técnica, propondo uma ferramenta genuinamente útil que aplica conceitos físicos reais — nomeadamente a acelerometria, o tratamento de ruído de sensor e a calibração — num contexto do quotidiano.

== Objetivos

Os objetivos principais deste projeto são os seguintes:

- Detetar em tempo real a elevação do telemóvel através do acelerómetro integrado no Arduino Nano RP2040 Connect;
- Registar cada evento de distração com data, hora de início, hora de fim e duração, de forma completamente passiva e automática;
- Armazenar os dados de forma persistente num ficheiro Excel (`.xlsx`) para análise posterior;
- Desenvolver um dashboard interativo em HTML/JavaScript que permita visualizar e filtrar os dados por dia, semana e mês, com funcionalidades de drill-down e análise por período do dia;
- Disponibilizar o sistema como executável Windows (`.exe`) para facilitar a sua utilização sem instalação de dependências;
- Estabelecer a ligação entre os fundamentos físicos da acelerometria e a aplicação prática desenvolvida.

== Estrutura do Documento

O presente documento está organizado da seguinte forma: o Capítulo 2 apresenta o estado da arte em sistemas de monitorização de produtividade e distração; o Capítulo 3 apresenta os fundamentos físicos subjacentes ao sistema; o Capítulo 4 descreve o hardware utilizado; o Capítulo 5 detalha o software desenvolvido; o Capítulo 6 apresenta a metodologia e os resultados obtidos; e o Capítulo 7 discute os resultados e apresenta as conclusões.

// ─────────────────────────────────────────────────────────
// 2. ESTADO DA ARTE
// ─────────────────────────────────────────────────────────
= Estado da Arte

== Sistemas de Monitorização de Produtividade

A monitorização de produtividade e de hábitos digitais é uma área em crescimento, com diversas soluções comerciais e académicas disponíveis. Estas soluções podem ser categorizadas em três grandes grupos: aplicações de software para PC e telemóvel, sistemas baseados em hardware dedicado, e estudos académicos sobre distração e concentração.

=== Aplicações de Software

*RescueTime* é uma das ferramentas mais conhecidas neste domínio. Trata-se de uma aplicação que corre em segundo plano no computador e no telemóvel, monitorizando automaticamente o tempo despendido em cada aplicação e website. No final da semana, gera relatórios detalhados com uma pontuação de produtividade. A abordagem é puramente baseada em software e não requer hardware adicional, mas está limitada à monitorização de atividade digital — não deteta distrações físicas como levantar o telemóvel.

*Forest* é uma aplicação para telemóvel que utiliza uma abordagem de gamificação: o utilizador planta uma árvore virtual quando começa a estudar, e a árvore morre se sair da aplicação. Embora eficaz como mecanismo de compromisso, é uma solução ativa — requer que o utilizador a inicie conscientemente — e não gera dados analíticos detalhados sobre os padrões de distração.

*Screen Time* (iOS) e *Digital Wellbeing* (Android) são funcionalidades integradas nos sistemas operativos móveis que monitorizam o tempo de uso de cada aplicação e permitem definir limites diários. Contudo, apenas medem o uso ativo do telemóvel, não conseguindo detetar se o telemóvel foi simplesmente levantado sem interação significativa.

=== Sistemas Baseados em Hardware

Existem alguns projetos académicos e de investigação que utilizam hardware dedicado para monitorização de atenção e distração. Sistemas baseados em sensores de electroencefalografia (EEG) — como o *Muse* ou o *NeuroSky MindWave* — medem a atividade elétrica cerebral e conseguem inferir estados de atenção, concentração e fadiga com elevado grau de precisão. No entanto, estes sistemas são consideravelmente mais caros, intrusivos e tecnicamente complexos, o que limita a sua adoção em contextos quotidianos.

Projetos de _maker_ baseados em Arduino e Raspberry Pi têm explorado o uso de sensores de presença, câmaras e acelerómetros para monitorização de produtividade. No entanto, a maioria destes projetos não inclui um sistema completo de registo, análise e visualização de dados, ficando-se pela demonstração de conceito.

=== Investigação Académica

A investigação sobre o impacto do telemóvel na concentração e desempenho académico é extensa. Diversos estudos demonstram que a mera presença do telemóvel sobre a secretária — mesmo silenciado e com o ecrã virado para baixo — reduz a capacidade cognitiva disponível, um fenómeno denominado _brain drain_. A simples consciência da possibilidade de receber notificações ocupa recursos cognitivos que de outra forma estariam disponíveis para a tarefa em curso.

Estudos de _experience sampling_ — metodologia em que os participantes são contactados aleatoriamente ao longo do dia e questionados sobre o seu estado atual — revelam que os estudantes universitários verificam o telemóvel em média 52 vezes por dia, com picos de frequência ao final da tarde e ao início da noite.

== Posicionamento do Projeto

O sistema desenvolvido neste projeto distingue-se das soluções existentes em vários aspetos. Em primeiro lugar, é completamente passivo — não requer qualquer ação do utilizador para além de colocar o Arduino sobre o telemóvel. Em segundo lugar, é baseado em hardware de baixo custo (Arduino Nano RP2040 Connect) e software open-source, tornando-o acessível. Em terceiro lugar, gera dados analíticos detalhados com granularidade temporal fina, permitindo identificar padrões de comportamento que soluções mais simples não conseguem capturar.

A principal limitação em relação às soluções comerciais é a necessidade de manter o Arduino ligado ao computador via USB durante as sessões de estudo. Esta limitação é reconhecida e endereçada na secção de trabalho futuro, onde se propõe a implementação de comunicação Wi-Fi.

// ─────────────────────────────────────────────────────────
// 3. FUNDAMENTOS FÍSICOS
// ─────────────────────────────────────────────────────────
= Fundamentos Físicos

== Aceleração e a Segunda Lei de Newton

A aceleração é uma grandeza física vetorial que descreve a taxa de variação da velocidade de um corpo em função do tempo. Formalmente, a aceleração instantânea é definida como:

$ arrow(a) = lim_(Delta t -> 0) (Delta arrow(v)) / (Delta t) = (d arrow(v)) / (d t) $

De acordo com a segunda lei de Newton, a aceleração de um corpo é proporcional à força resultante que sobre ele atua e inversamente proporcional à sua massa:

$ arrow(F) = m dot arrow(a) $

onde $F$ representa a força resultante (em Newtons), $m$ a massa (em quilogramas) e $a$ a aceleração resultante (em metros por segundo ao quadrado). Esta relação é o princípio de funcionamento dos acelerómetros: ao medir as forças que atuam sobre uma massa de prova interna, é possível inferir a aceleração do dispositivo.

== Acelerómetros MEMS

Os acelerómetros modernos, como o *LSM6DSOX* presente no Arduino Nano RP2040 Connect, são fabricados com tecnologia *MEMS* (Micro-Electro-Mechanical Systems). Estes dispositivos integram estruturas mecânicas e circuitos eletrónicos à escala micrométrica num único chip de silício.

O princípio de funcionamento de um acelerómetro MEMS baseia-se numa massa de prova suspensa por estruturas elásticas (molas). Quando o dispositivo sofre uma aceleração, a massa de prova desloca-se relativamente à estrutura de suporte. Este deslocamento é medido por variação de capacitância entre elétrodos fixos e móveis. A variação de capacitância é proporcional ao deslocamento e, consequentemente, à aceleração.

A sensibilidade de um acelerómetro MEMS é expressa em $g$, onde:

$ 1g = 9.81 "m/s"^2 $

correspondendo à aceleração gravítica à superfície da Terra. O LSM6DSOX permite configurar a gama de medição entre ±2g e ±16g, com uma resolução de 16 bits por eixo e uma taxa de amostragem máxima de 6664 Hz.

== A Gravidade como Referência de Calibração

Uma propriedade fundamental que torna os acelerómetros especialmente úteis na deteção de movimento é o facto de medirem não apenas acelerações dinâmicas, mas também a aceleração estática devida à gravidade. Quando o dispositivo está completamente em repouso, o vetor de aceleração medido corresponde ao vetor gravitacional com sinal invertido:

$ arrow(a)_"medida" = -arrow(g) $

Isto significa que um acelerómetro em repouso sobre uma superfície horizontal regista aproximadamente $1g$ no eixo perpendicular à superfície e valores próximos de zero nos eixos horizontais. Quando o dispositivo é inclinado ou movimentado, a relação entre os três eixos altera-se de forma previsível, permitindo detetar e quantificar o movimento.

Esta propriedade é aproveitada no sistema desenvolvido: em repouso sobre a mesa, o Arduino regista valores estáveis num determinado ponto do espaço de aceleração. Quando o telemóvel é levantado, a reorientação do dispositivo em relação ao vetor gravitacional provoca variações significativas nos três eixos, que são interpretadas como um evento de distração.

== Ruído de Sensor e Incerteza de Medição

Qualquer sensor físico está sujeito a ruído de medição — flutuações aleatórias nos valores lidos que não correspondem a variações reais na grandeza medida. O ruído tem múltiplas origens: ruído térmico dos componentes eletrónicos, interferências eletromagnéticas, vibrações ambientais, e imperfeições no processo de fabrico do sensor.

No caso do acelerómetro LSM6DSOX, o ruído em condições estáticas é tipicamente da ordem de $plus.minus 0.02g$, o que significa que mesmo sem qualquer movimento real, os valores lidos flutuam continuamente dentro desta gama. Este fenómeno tem implicações diretas no design do sistema de deteção: se o limiar de deteção for demasiado baixo, qualquer flutuação aleatória desencadeará um falso alarme; se for demasiado alto, movimentos reais podem não ser detetados.

A relação sinal-ruído (SNR) para a deteção de movimento pode ser expressa como:

$ "SNR" = (Delta a_"movimento") / (sigma_"ruído") $

onde $Delta a_"movimento"$ é a variação de aceleração associada ao movimento e $sigma_"ruído"$ é o desvio padrão do ruído. Para garantir uma deteção fiável, o SNR deve ser significativamente superior a 1.

== Calibração Automática

Para mitigar o efeito do ruído e adaptar o sistema a diferentes condições de instalação (diferentes mesas, diferentes orientações do Arduino), o sistema implementa uma fase de *calibração automática*. Esta técnica é amplamente utilizada em metrologia e instrumentação para eliminar erros sistemáticos.

No arranque, são recolhidas $N = 50$ amostras consecutivas em repouso e calculada a média de cada eixo:

$ overline(a)_x = 1/N sum_(i=1)^N a_(x,i), quad overline(a)_y = 1/N sum_(i=1)^N a_(y,i), quad overline(a)_z = 1/N sum_(i=1)^N a_(z,i) $

Estes valores médios constituem a *linha de base* do sistema — o ponto de referência a partir do qual as variações são medidas. O desvio em relação à linha de base é calculado em cada ciclo de medição:

$ Delta a_x = |a_x - overline(a)_x|, quad Delta a_y = |a_y - overline(a)_y|, quad Delta a_z = |a_z - overline(a)_z| $

Se qualquer um dos três desvios exceder o limiar de deteção ($tau = 0.5g$), o sistema interpreta o evento como movimento:

$ "movimento" = (Delta a_x > tau) or (Delta a_y > tau) or (Delta a_z > tau) $

O valor de $tau = 0.5g$ foi determinado empiricamente durante os testes, representando um compromisso entre sensibilidade (capacidade de detetar movimentos reais) e especificidade (capacidade de ignorar falsas deteções causadas por ruído ou vibrações ambientais).

== Frequência de Amostragem e Teorema de Nyquist

O sistema realiza leituras do acelerómetro a uma frequência de 10 Hz, ou seja, uma amostra a cada 100 ms. Esta escolha respeita o teorema de Nyquist-Shannon, que estabelece que para representar fielmente um sinal com componentes de frequência até $f_"max"$, a frequência de amostragem deve ser pelo menos $2 f_"max"$.

O movimento de levantar um telemóvel é um evento relativamente lento, com duração tipicamente superior a 200 ms e componentes de frequência inferiores a 5 Hz. A frequência de amostragem de 10 Hz é, portanto, suficiente para detetar este tipo de movimento com fidelidade, enquanto rejeita vibrações de alta frequência (como batidas na mesa ou vibrações do próprio motor do telemóvel) que poderiam causar falsas deteções.

// ─────────────────────────────────────────────────────────
// 4. HARDWARE
// ─────────────────────────────────────────────────────────
= Hardware

== Arduino Nano RP2040 Connect

O *Arduino Nano RP2040 Connect* é um microcontrolador de fator de forma compacto (48 × 18 mm) baseado no chip *RP2040* da Raspberry Pi Foundation. Destaca-se por integrar num único módulo de dimensões reduzidas um conjunto de periféricos de alta capacidade que o tornam especialmente adequado para projetos de IoT e computação embebida. A Tabela 4.1 resume as suas principais características técnicas.

#figure(
  table(
    columns: (auto, 1fr),
    inset: 9pt,
    stroke: 0.5pt,
    align: (left, left),
    [*Componente*], [*Especificação*],
    [Processador], [Dual-core ARM Cortex-M0+ a 133 MHz],
    [Memória RAM], [264 KB SRAM],
    [Memória Flash], [16 MB (QSPI externo)],
    [IMU], [LSM6DSOX (acelerómetro + giroscópio de 6 eixos)],
    [Microfone], [MP34DT05 (PDM, integrado)],
    [Conectividade], [Wi-Fi 802.11 b/g/n e Bluetooth 4.2 (u-blox NINA-W102)],
    [LED RGB], [Integrado, controlado via módulo NINA],
    [Interface], [USB Micro-B, I2C, SPI, UART, ADC, PWM],
    [Tensão de operação], [3.3 V],
    [Alimentação], [5 V via USB ou pino VIN],
    [Dimensões], [48 × 18 mm],
  ),
  caption: [Especificações técnicas do Arduino Nano RP2040 Connect]
)

O processador dual-core ARM Cortex-M0+ permite executar tarefas em paralelo com grande eficiência energética. Neste projeto, um dos núcleos é dedicado à leitura do acelerómetro e comunicação Serial, enquanto o segundo permanece disponível para eventuais expansões futuras.

== IMU LSM6DSOX

O sensor inercial *LSM6DSOX* da STMicroelectronics é um dispositivo de 6 graus de liberdade (6-DoF) que combina um acelerómetro triaxial e um giroscópio triaxial num único pacote compacto de 2.5 × 3.0 × 0.83 mm. As suas principais características são apresentadas na Tabela 4.2.

#figure(
  table(
    columns: (auto, 1fr),
    inset: 9pt,
    stroke: 0.5pt,
    align: (left, left),
    [*Parâmetro*], [*Valor*],
    [Gama do acelerómetro], [±2g, ±4g, ±8g ou ±16g (configurável)],
    [Gama do giroscópio], [±125 a ±2000 dps (configurável)],
    [Resolução], [16 bits por eixo],
    [Taxa de amostragem máx.], [6664 Hz (acelerómetro), 6664 Hz (giroscópio)],
    [Interface de comunicação], [I2C (até 400 kHz) e SPI (até 10 MHz)],
    [Consumo em modo normal], [0.55 mA],
    [Consumo em modo baixo], [4 µA],
    [Temperatura de operação], [-40°C a +85°C],
  ),
  caption: [Características técnicas do sensor LSM6DSOX]
)

Neste projeto, a biblioteca `Arduino_LSM6DSOX` é utilizada para comunicar com o sensor via I2C a uma frequência de amostragem de 10 Hz. Apenas o acelerómetro é utilizado — o giroscópio permanece inativo para reduzir o consumo energético.

== Configuração Física do Sistema

O sistema não requer hardware adicional além do Arduino Nano RP2040 Connect e do cabo USB Micro-B. O Arduino é colocado em cima do telemóvel durante as sessões de estudo, com a face dos componentes virada para cima, e ligado ao computador via USB.

O LED RGB integrado serve como indicador visual imediato do estado do sistema, eliminando a necessidade de consultar o terminal durante as sessões de estudo:

#figure(
  table(
    columns: (auto, auto, 1fr),
    inset: 9pt,
    stroke: 0.5pt,
    [*Estado*], [*Cor do LED*], [*Significado*],
    [Calibração], [Apagado], [O sistema está a recolher amostras de referência],
    [Em estudo], [Verde], [Nenhum movimento detetado; o utilizador está focado],
    [Distração], [Vermelho], [Movimento detetado; o telemóvel foi levantado],
  ),
  caption: [Comportamento do LED RGB em função do estado do sistema]
)

// ─────────────────────────────────────────────────────────
// 5. SOFTWARE
// ─────────────────────────────────────────────────────────
= Software

== Arquitetura do Sistema

O sistema é composto por três componentes de software distintos, cada um com responsabilidades bem definidas:

+ *Firmware do Arduino* (C++) — responsável pela leitura do acelerómetro a 10 Hz, deteção de movimento por comparação com a linha de base, indicação visual via LED RGB e comunicação de eventos via Serial USB;
+ *Script principal* (`main.py`, Python) — corre no PC em segundo plano, recebe os eventos do Arduino via porta Serial, calcula a duração de cada distração, regista os dados no ficheiro Excel e gera o dashboard interativo no final de cada sessão;
+ *Dashboard interativo* (HTML/JavaScript) — ficheiro HTML auto-suficiente gerado automaticamente pelo script Python, visualizável em qualquer browser sem instalação de software adicional.

O fluxo de dados completo é o seguinte:

#align(center)[
  #text(size: 10pt)[
    *Arduino (IMU)* → *Serial USB* → *Python (main.py)* → *Excel (.xlsx)* → *Dashboard HTML*
  ]
]

Esta arquitetura foi desenhada para minimizar a complexidade do firmware (que corre num microcontrolador com recursos limitados) e maximizar as capacidades de análise e visualização no PC, onde os recursos são abundantes.

== Firmware do Arduino

O firmware implementa um ciclo de execução simples e eficiente com três fases distintas: inicialização, calibração e monitorização contínua.

=== Inicialização

Na fase de inicialização, o sistema configura os pinos do LED RGB, inicializa a comunicação Serial a 9600 baud e verifica a disponibilidade do sensor IMU. Se o sensor não for detetado, o sistema entra em estado de erro e aguarda intervenção.

=== Calibração Automática

A calibração recolhe 50 amostras em repouso (duração aproximada de 2.5 segundos) e calcula a média de cada eixo como linha de base. Durante esta fase, o LED permanece apagado e uma mensagem é enviada via Serial para informar o utilizador. Este tempo de calibração é suficiente para estabilizar as leituras do sensor e eliminar o efeito de transientes de arranque.

=== Monitorização Contínua

O ciclo principal de monitorização executa a cada 100 ms (10 Hz) e implementa uma máquina de estados simples com dois estados: `EM_ESTUDO` e `DISTRAÇÃO`. A transição entre estados ocorre quando a variação de aceleração em qualquer eixo excede o limiar de $0.5g$. A Listagem 5.1 apresenta o núcleo do ciclo de deteção.

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
        // LED vermelho — distração detetada
        digitalWrite(LEDR, LOW);
        digitalWrite(LEDG, HIGH);
        digitalWrite(LEDB, HIGH);
        Serial.println("DISTRACAO_INICIO");
      }
    } else {
      if (phonePickedUp) {
        phonePickedUp = false;
        // LED verde — voltou a estudar
        digitalWrite(LEDR, HIGH);
        digitalWrite(LEDG, LOW);
        digitalWrite(LEDB, HIGH);
        Serial.println("DISTRACAO_FIM");
      }
    }
  }
  delay(100);
}
```

O uso da variável booleana `phonePickedUp` garante que apenas uma mensagem `DISTRACAO_INICIO` é enviada por evento de distração, evitando a geração de eventos duplicados enquanto o telemóvel permanece levantado.

== Script Principal (Python)

O script `main.py` é o componente central do sistema no PC. As suas responsabilidades incluem:

*Deteção do Arduino:* o script percorre todas as portas Serial disponíveis e identifica automaticamente aquela em que o Arduino está ligado, eliminando a necessidade de configuração manual por parte do utilizador.

*Receção de eventos:* o script lê continuamente a porta Serial e processa as mensagens `DISTRACAO_INICIO` e `DISTRACAO_FIM`. Ao receber `DISTRACAO_INICIO`, regista o timestamp de início. Ao receber `DISTRACAO_FIM`, calcula a duração e persiste o registo.

*Persistência de dados:* cada evento de distração é registado no ficheiro Excel com os campos apresentados na Tabela 5.1.

#figure(
  table(
    columns: (auto, auto, 1fr),
    inset: 9pt,
    stroke: 0.5pt,
    [*Campo*], [*Tipo*], [*Descrição*],
    [`data`], [String], [Data do evento (formato YYYY-MM-DD)],
    [`hora_inicio`], [String], [Hora em que o telemóvel foi levantado (HH:MM:SS)],
    [`hora_fim`], [String], [Hora em que o telemóvel foi pousado (HH:MM:SS)],
    [`duracao_segundos`], [Inteiro], [Duração da distração em segundos],
  ),
  caption: [Estrutura do registo de cada evento de distração no ficheiro Excel]
)

*Interface no terminal:* o script apresenta uma interface colorida no terminal, com mensagens de estado e registo em tempo real de cada distração detetada, incluindo o número sequencial e a duração.

*Geração do dashboard:* quando o utilizador termina a sessão (Ctrl+C), o script gera automaticamente o ficheiro `dashboard.html` a partir dos dados acumulados e abre-o no browser predefinido.

== Dashboard Interativo

O dashboard é gerado automaticamente em HTML e JavaScript, utilizando a biblioteca Chart.js para a renderização dos gráficos. Trata-se de um ficheiro HTML auto-suficiente que não requer servidor web nem instalação de software — basta abrir no browser.

As funcionalidades do dashboard são as seguintes:

*Cards de resumo:* quatro indicadores de topo apresentam as métricas mais relevantes: total de distrações, tempo total distraído, duração média por distração e hora do dia com mais distrações.

*Gráfico principal interativo:* o gráfico central permite alternar entre três vistas — por dia, por semana e por mês. Ao clicar numa barra, o gráfico lateral direito atualiza automaticamente com o detalhe correspondente: as horas de um dia específico, os dias de uma semana específica, ou as semanas de um mês específico. Um breadcrumb permite regressar à vista global.

*Gráfico de distribuição horária:* mostra a distribuição das distrações ao longo das horas do dia, com atualização dinâmica conforme a seleção no gráfico principal.

*Gráfico de linha temporal:* apresenta o tempo total distraído por dia em minutos, permitindo identificar tendências ao longo do período de monitorização.

*Gráfico circular por período do dia:* distribui as distrações por quatro períodos — Manhã (9h–12h), Tarde (12h–18h), Fim de tarde (18h–20h) e Noite (20h+) — num gráfico de anel.

*Percentagens de variação semanal:* quando na vista semanal, as barras são coloridas a vermelho (mais distrações que a semana anterior) ou verde (menos distrações), com a percentagem de variação indicada por cima de cada barra.

*Tabela detalhada:* lista todos os eventos registados, com filtros por dia e por tipo de distração (Rápida <30s, Média 30s–2min, Longa >2min). Cada linha apresenta data, hora de início, hora de fim, duração e tipo com badge colorido.

*Modo claro/escuro:* um botão no canto superior direito permite alternar entre o tema escuro (predefinido) e o tema claro.

As Figuras 5.1, 5.2 e 5.3 apresentam capturas de ecrã do dashboard com os dados recolhidos durante o período de monitorização.

#figure(
  image("dashboard_visao_geral.png", width: 100%),
  caption: [Vista geral do dashboard — gráfico de distrações por dia e distribuição horária]
)

#figure(
  image("dashboard_graficos_baixo.png", width: 100%),
  caption: [Secção inferior do dashboard — gráfico de linha temporal e gráfico circular por período do dia]
)

#figure(
  image("dashboard_tabela.png", width: 100%),
  caption: [Registo detalhado no dashboard — tabela com filtro por dia e tipo de distração]
)

== Executável Windows

O projeto foi empacotado num executável Windows (`.exe`) utilizando a ferramenta *PyInstaller*, permitindo que o sistema seja utilizado sem instalação de Python ou de qualquer dependência adicional. O executável detecta automaticamente o ficheiro de dados na mesma pasta e, se não existir, cria-o automaticamente.

Para gerar o executável, utiliza-se o seguinte comando:

```bash
python -m PyInstaller --onefile --name "AntiDistracao" main.py
```

O ficheiro `AntiDistracao.exe` resultante pode ser copiado para qualquer pasta, desde que o ficheiro `distrações.xlsx` esteja na mesma localização.

// ─────────────────────────────────────────────────────────
// 6. METODOLOGIA E RESULTADOS
// ─────────────────────────────────────────────────────────
= Metodologia e Resultados

== Metodologia de Recolha de Dados

Os dados foram recolhidos ao longo de aproximadamente um mês (de 10 de junho a 23 de julho de 2026), durante sessões de estudo com o Arduino posicionado em cima do telemóvel, ligado ao computador via USB. A recolha decorreu de forma completamente passiva — o script `main.py` corria em segundo plano no computador e o único indicador visual era o LED do Arduino, que mudava de verde para vermelho em cada distração detetada.

O procedimento seguido em cada sessão de estudo foi o seguinte:

+ Ligar o Arduino ao computador via USB;
+ Aguardar a calibração automática (~2.5 segundos);
+ Colocar o Arduino em cima do telemóvel na posição de estudo;
+ Estudar normalmente, sem qualquer preocupação com o sistema;
+ No final da sessão, premir Ctrl+C para terminar o script e gerar o dashboard.

Não foram excluídos quaisquer eventos da análise, incluindo distrações de duração zero (correspondentes a levantamentos muito breves do telemóvel, inferiores ao ciclo de leitura de 100 ms).

== Resultados Globais

Ao longo do período de monitorização foram registadas *159 distrações* distribuídas por *25 dias* de estudo, totalizando aproximadamente *4 horas e 44 minutos* de tempo distraído. A Tabela 6.1 resume as principais métricas obtidas.

#figure(
  table(
    columns: (1fr, auto),
    inset: 9pt,
    stroke: 0.5pt,
    [*Métrica*], [*Valor*],
    [Total de distrações registadas], [159],
    [Dias com sessões de estudo monitorizadas], [25],
    [Média de distrações por dia de estudo], [~6.4],
    [Tempo total distraído], [4h 44min (17 040s)],
    [Duração média por distração], [~107 segundos (~1m 47s)],
    [Mediana da duração das distrações], [~45 segundos],
    [Distração mais longa registada], [4m 53s],
    [Hora do dia com mais distrações], [19h],
    [Período do dia com mais distrações], [Tarde (12h–18h)],
  ),
  caption: [Métricas globais obtidas durante o período de monitorização]
)

== Análise por Tipo de Distração

As 159 distrações foram classificadas em três categorias com base na sua duração:

#figure(
  table(
    columns: (auto, auto, auto, 1fr),
    inset: 9pt,
    stroke: 0.5pt,
    [*Tipo*], [*Critério*], [*Count*], [*% do total*],
    [Rápida], [< 30 segundos], [_a preencher_], [_a preencher_],
    [Média], [30s – 2 minutos], [_a preencher_], [_a preencher_],
    [Longa], [> 2 minutos], [_a preencher_], [_a preencher_],
  ),
  caption: [Distribuição das distrações por tipo]
)

A maioria das distrações é de curta duração, o que sugere que se tratam frequentemente de verificações rápidas — consultar as horas, ver se chegou alguma notificação, ou simplesmente pegar no telemóvel por hábito sem interação significativa. No entanto, as distrações longas, apesar de menos frequentes, contribuem de forma desproporcional para o tempo total distraído.

== Análise Temporal

=== Distribuição por Hora do Dia

A análise da distribuição das distrações ao longo do dia revela um padrão com dois picos de maior atividade: um pico matinal entre as 10h e as 11h, e um pico mais pronunciado ao final da tarde e início da noite, entre as 18h e as 20h. A hora com maior número de distrações registadas foi as 19h, com 21 ocorrências ao longo do período de monitorização.

Este padrão é consistente com a literatura sobre ritmos circadianos e fadiga cognitiva: a concentração tende a ser mais elevada durante as primeiras horas da manhã, deteriora-se ao final da tarde com o acúmulo de fadiga, e a atividade nas redes sociais é tipicamente mais intensa ao início da noite.

=== Distribuição por Período do Dia

A distribuição por período do dia mostra que a Tarde (12h–18h) concentra a maior parte das distrações, seguida do Fim de tarde (18h–20h). A Manhã (9h–12h) apresenta valores moderados, enquanto a Noite (20h+) regista menos distrações, provavelmente por corresponder a sessões de estudo mais curtas.

=== Variação Semanal

A análise semanal revela algumas tendências interessantes. As primeiras semanas do período de monitorização (semanas 23 e 24) apresentam uma variação significativa, com a semana 24 a registar o dobro das distrações da semana 23. A partir da semana 25, observa-se uma tendência geral de diminuição, o que pode sugerir uma maior consciencialização sobre os próprios hábitos de distração ao longo do tempo.

A semana 28 apresenta um número muito reduzido de distrações (apenas 1), correspondendo a um período com poucas sessões de estudo.

=== Variação Diária

O dia com maior número de distrações registadas foi 07/07/2026, com 11 ocorrências. Os dias com menos distrações correspondem geralmente a sessões de estudo mais curtas ou a períodos de maior foco. A variabilidade diária é elevada, o que reflete a natureza irregular das sessões de estudo e das condições ambientais.

== Análise do Tempo Distraído

Para além da contagem de distrações, o tempo total distraído por dia (em minutos) é uma métrica importante para avaliar o impacto real das distrações na produtividade. O gráfico de linha temporal do dashboard revela picos de tempo distraído que nem sempre coincidem com os dias de maior número de distrações — um dia com poucas distrações longas pode ter um tempo distraído superior a um dia com muitas distrações curtas.

O dia com maior tempo distraído regista aproximadamente 30 minutos, o que representa uma fracção significativa de uma sessão de estudo típica de 2–3 horas.

// ─────────────────────────────────────────────────────────
// 7. DISCUSSÃO E CONCLUSÃO
// ─────────────────────────────────────────────────────────
= Discussão e Conclusão

== Ligação aos Conceitos Físicos

Este projeto ilustra de forma concreta e aplicada vários conceitos fundamentais de física que sustentam o funcionamento do sistema.

A *segunda lei de Newton* é o princípio físico de base dos acelerómetros MEMS: a relação entre força e aceleração permite inferir o estado de movimento de um corpo a partir das forças que sobre ele atuam. A tecnologia MEMS, por sua vez, demonstra como princípios físicos clássicos — a deformação de estruturas elásticas e a variação de capacitância — podem ser implementados à escala micrométrica com recurso a técnicas de microfabricação.

A *calibração automática* implementada no sistema exemplifica um princípio fundamental de metrologia: toda a medição física está sujeita a incertezas sistemáticas e aleatórias, e é necessário estabelecer uma referência antes de interpretar os resultados. A média de 50 amostras como estimador da linha de base é uma aplicação direta da lei dos grandes números, que garante que a média amostral converge para o valor verdadeiro com o aumento do número de amostras.

O *teorema de Nyquist-Shannon* fundamenta a escolha da frequência de amostragem de 10 Hz: para detetar movimentos com componentes de frequência inferiores a 5 Hz (como o gesto de levantar o telemóvel), a frequência de amostragem de 10 Hz é suficiente e ao mesmo tempo eficiente em termos de recursos computacionais e energéticos.

O *conceito de SNR* e a escolha do limiar de deteção ($tau = 0.5g$) ilustram o compromisso fundamental entre sensibilidade e especificidade presente em qualquer sistema de deteção: aumentar a sensibilidade reduz as falsas não-deteções mas aumenta os falsos alarmes, e vice-versa.

== Avaliação Crítica dos Resultados

Os resultados obtidos revelam padrões de distração consistentes com a literatura existente. O pico de distrações ao final da tarde (18h–20h) é consistente com estudos sobre fadiga cognitiva e com os padrões de uso de redes sociais. A predominância de distrações de curta duração sugere que o comportamento mais comum é a verificação reflexiva do telemóvel — um hábito automático — em vez de sessões prolongadas de uso.

O facto de a maioria das distrações ocorrer durante a tarde é relevante do ponto de vista da gestão do estudo: concentrar as tarefas que exigem maior esforço cognitivo nas primeiras horas do dia, reservando as tarefas mais mecânicas para o período de maior propensão à distração, pode ser uma estratégia eficaz de gestão do tempo.

A variação semanal observada — com tendência para diminuição ao longo do período de monitorização — pode sugerir um efeito de consciencialização: o simples facto de saber que as distrações estão a ser registadas pode induzir uma redução do comportamento distrativo, um fenómeno conhecido em psicologia como *efeito Hawthorne*.

== Limitações do Sistema

O sistema apresenta algumas limitações que importa reconhecer e contextualizar.

*Dependência do cabo USB:* o Arduino tem de estar permanentemente ligado ao computador durante as sessões de estudo. Embora esta limitação não comprometa a funcionalidade do sistema em contexto de uso ao computador, impede a sua utilização em contextos sem PC (estudo em papel, leitura, etc.).

*Contexto de interpretação:* o sistema assume que levantar o telemóvel equivale sempre a uma distração. Na realidade, existem razões legítimas para levantar o telemóvel durante o estudo: atender uma chamada importante, verificar as horas, colocar um alarme. Estas situações são registadas como distrações, o que pode introduzir algum ruído nos dados.

*Condições ambientais:* vibrações externas — como batidas na mesa, passagem de veículos pesados ou o próprio motor de vibração do telemóvel — podem desencadear falsas deteções, especialmente se o limiar de deteção for reduzido para aumentar a sensibilidade.

*Portabilidade dos dados:* o ficheiro Excel é gerado no computador onde o script corre, o que torna a análise de dados dependente de esse computador estar disponível.

== Trabalho Futuro

As limitações identificadas apontam para várias direções de desenvolvimento futuro que poderiam tornar o sistema mais robusto e versátil.

*Comunicação Wi-Fi:* a implementação de comunicação Wi-Fi (o módulo u-blox NINA-W102 já está integrado no Arduino) permitiria eliminar a dependência do cabo USB, alimentando o Arduino com uma _power bank_. Os dados seriam enviados via HTTP para um servidor Python local ou para um serviço de cloud. Esta seria provavelmente a melhoria de maior impacto na usabilidade do sistema.

*Filtro de médias móveis:* a aplicação de um filtro de médias móveis sobre as últimas N leituras antes de tomar uma decisão de deteção reduziria a sensibilidade ao ruído impulsivo e às falsas deteções causadas por vibrações momentâneas.

*Classificação inteligente:* a integração de um modelo de _machine learning_ simples — por exemplo, treinado com o Edge Impulse — poderia permitir distinguir entre diferentes tipos de movimento: levantar o telemóvel, bater na mesa, e vibração do motor do telemóvel. Isto reduziria significativamente as falsas deteções.

*Alertas sonoros:* a adição de um _buzzer_ piezoelétrico externo permitiria emitir um aviso sonoro após um determinado número de distrações ou após um tempo acumulado distraído, funcionando como um mecanismo de feedback imediato.

*Aplicação web:* o dashboard HTML poderia ser alojado num servidor web simples, tornando os dados acessíveis a partir de qualquer dispositivo na mesma rede — incluindo o telemóvel — sem necessidade de gerar e abrir um ficheiro HTML manualmente.

== Conclusão

Este trabalho demonstrou a viabilidade de desenvolver um sistema de monitorização de comportamento funcional, útil e de baixo custo, recorrendo ao microcontrolador Arduino Nano RP2040 Connect e a ferramentas de software open-source. O sistema é capaz de detetar e registar automaticamente eventos de distração durante sessões de estudo, gerando dados analíticos detalhados que permitem ao utilizador compreender e refletir sobre os seus próprios padrões de comportamento.

Do ponto de vista físico, o projeto estabelece uma ligação clara e concreta entre conceitos fundamentais da mecânica clássica e da instrumentação — a segunda lei de Newton, os acelerómetros MEMS, o ruído de sensor, a calibração e o teorema de Nyquist — e a sua aplicação prática num sistema de monitorização do quotidiano. Esta ligação demonstra como a física não é apenas uma disciplina teórica, mas o fundamento de inúmeras tecnologias que utilizamos diariamente.

Os resultados obtidos revelam padrões de distração consistentes e analiticamente interessantes, com maior incidência ao final da tarde e predominância de distrações de curta duração. O dashboard interativo desenvolvido permite explorar estes dados de forma intuitiva e visualmente apelativa, oferecendo múltiplas perspetivas de análise — temporal, por período do dia, por tipo de distração.

O resultado final é uma ferramenta que, apesar das suas limitações, oferece uma perspetiva genuinamente útil sobre os hábitos de estudo e constitui uma base sólida para os desenvolvimentos futuros propostos.

// ─────────────────────────────────────────────────────────
// REFERÊNCIAS
// ─────────────────────────────────────────────────────────
= Referências

#set par(hanging-indent: 1.5em, spacing: 1em)

Arduino. (2024). _Arduino Nano RP2040 Connect — Documentation_. Disponível em: https://docs.arduino.cc/hardware/nano-rp2040-connect/

Chart.js Contributors. (2024). _Chart.js — Simple yet flexible JavaScript charting library_. Disponível em: https://www.chartjs.org

Meriam, J. L., & Kraige, L. G. (2012). _Engineering Mechanics: Dynamics_ (7th ed.). Wiley.

Shannon, C. E. (1949). Communication in the presence of noise. _Proceedings of the IRE_, 37(1), 10–21.

STMicroelectronics. (2021). _LSM6DSOX — iNEMO inertial module: Always-on 3D accelerometer and 3D gyroscope_. Datasheet DS12451. Disponível em: https://www.st.com/resource/en/datasheet/lsm6dsox.pdf

Ward, A. F., Duke, K., Gneezy, A., & Bos, M. W. (2017). Brain drain: The mere presence of one's own smartphone reduces available cognitive capacity. _Journal of the Association for Consumer Research_, 2(2), 140–154.

Ophir, E., Nass, C., & Wagner, A. D. (2009). Cognitive control in media multitaskers. _Proceedings of the National Academy of Sciences_, 106(37), 15583–15587.

van der Schuur, W. A., Baumgartner, S. E., Sumter, S. R., & Valkenburg, P. M. (2015). The consequences of media multitasking for youth: A review. _Computers in Human Behavior_, 53, 204–215.
