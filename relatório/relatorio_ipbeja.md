# Resumo

## Sistema de Deteção de Distração no Estudo com Arduino {#resumo .unnumbered}

Este trabalho apresenta o desenvolvimento de um sistema de monitorização de distração durante sessões de estudo, recorrendo ao microcontrolador Arduino Nano RP2040 Connect e ao acelerómetro integrado no dispositivo. O sistema deteta a elevação do telemóvel — interpretada como um momento de distração — e regista automaticamente o evento com data, hora de início, hora de fim e duração. Os dados são armazenados num ficheiro Excel e visualizados através de um dashboard interativo desenvolvido em HTML e JavaScript, que permite filtrar e analisar as distrações por dia, semana e mês. O projeto foi desenvolvido no âmbito da cadeira de Física Aplicada à Computação e procura estabelecer uma ligação clara entre os fundamentos físicos da acelerometria e a sua aplicação prática num contexto do quotidiano.

**Palavras-chave**: Arduino, acelerómetro, distração, monitorização, machine learning embebido, dashboard, Python, Excel.

# Abstract

## Distraction Detection System During Study with Arduino {#abstract .unnumbered}

This work presents the development of a distraction monitoring system during study sessions, using the Arduino Nano RP2040 Connect microcontroller and its built-in accelerometer. The system detects when the phone is lifted — interpreted as a moment of distraction — and automatically records the event with date, start time, end time and duration. The data is stored in an Excel file and visualized through an interactive dashboard developed in HTML and JavaScript, which allows filtering and analyzing distractions by day, week and month. The project was developed in the context of the Applied Physics to Computing course and aims to establish a clear connection between the physical foundations of accelerometry and its practical application in an everyday context.

**Keywords**: Arduino, accelerometer, distraction, monitoring, embedded machine learning, dashboard, Python, Excel.

# Introdução {#intro}

A dificuldade em manter a concentração durante períodos prolongados de estudo é um problema transversal a muitos estudantes, agravado pela omnipresença dos dispositivos móveis. O telemóvel, em particular, constitui uma das principais fontes de distração, dado o seu apelo constante através de notificações, redes sociais e aplicações de entretenimento.

Este projeto propõe o desenvolvimento de um sistema de monitorização de distração durante o estudo, recorrendo ao microcontrolador **Arduino Nano RP2040 Connect** e ao acelerómetro integrado no dispositivo. A ideia central é colocar o Arduino em cima do telemóvel: quando este é levantado, o acelerómetro deteta a variação de aceleração e regista o evento como uma distração. Os dados são enviados para o computador via ligação USB, onde um script em Python os armazena num ficheiro Excel e um dashboard interativo permite visualizá-los de forma clara e detalhada.

O projeto surgiu no âmbito da cadeira de Física Aplicada à Computação e procura ir além de uma mera demonstração técnica, propondo uma ferramenta genuinamente útil que aplica conceitos físicos reais num contexto do quotidiano.

## Objetivos

Os objetivos principais deste projeto são:

- Detetar em tempo real a elevação do telemóvel através do acelerómetro integrado no Arduino Nano RP2040 Connect;
- Registar cada evento de distração com data, hora de início, hora de fim e duração;
- Armazenar os dados de forma persistente num ficheiro Excel (`.xlsx`);
- Desenvolver um dashboard interativo em HTML/JavaScript que permita visualizar e filtrar os dados por dia, semana e mês;
- Estabelecer a ligação entre os fundamentos físicos da acelerometria e a aplicação prática desenvolvida.

## Estrutura do Documento

O presente documento está organizado da seguinte forma: o Capítulo 2 apresenta os fundamentos físicos subjacentes ao sistema; o Capítulo 3 descreve o hardware utilizado; o Capítulo 4 detalha o software desenvolvido; o Capítulo 5 apresenta a metodologia e os resultados obtidos; e o Capítulo 6 discute os resultados e apresenta as conclusões.

# Fundamentos Físicos {#fundamentos}

## Aceleração e Força

A aceleração é uma grandeza física vetorial que descreve a taxa de variação da velocidade de um corpo em função do tempo. De acordo com a segunda lei de Newton:

$$F = m \cdot a$$

onde $F$ representa a força resultante aplicada ao corpo (em Newtons), $m$ a sua massa (em quilogramas) e $a$ a aceleração resultante (em metros por segundo ao quadrado). Esta relação é fundamental para compreender o funcionamento dos acelerómetros: ao medir as forças que atuam sobre uma massa de prova interna, é possível inferir a aceleração do dispositivo.

## Acelerómetros MEMS

Os acelerómetros modernos, como o **LSM6DSOX** presente no Arduino Nano RP2040 Connect, são fabricados com tecnologia **MEMS** (Micro-Electro-Mechanical Systems). Estes dispositivos consistem numa estrutura microscópica com uma massa suspensa por molas, cujo deslocamento é medido eletricamente quando sujeita a uma força de aceleração.

A sensibilidade de um acelerómetro MEMS é expressa em $g$, onde $1g \approx 9.81 \, \text{m/s}^2$ corresponde à aceleração gravítica terrestre. Em repouso sobre uma superfície plana, o eixo perpendicular à superfície regista aproximadamente $1g$, enquanto os eixos horizontais registam valores próximos de zero.

## A Gravidade como Referência

Uma propriedade fundamental que torna os acelerómetros especialmente úteis é o facto de medirem não apenas acelerações dinâmicas, mas também a aceleração estática devida à gravidade. Quando o dispositivo está completamente em repouso, o vetor de aceleração medido corresponde ao vetor gravitacional:

$$\vec{a}_{\text{repouso}} = -\vec{g}$$

Esta propriedade permite distinguir dois estados do sistema:

- **Repouso**: o telemóvel está pousado na mesa; os valores de aceleração são estáveis e próximos dos valores de calibração;
- **Movimento**: o telemóvel é levantado; a reorientação do dispositivo em relação ao vetor gravitacional provoca variações significativas nos três eixos.

## Ruído e Calibração

Qualquer sensor físico está sujeito a ruído de medição — flutuações aleatórias nos valores lidos que não correspondem a variações reais na grandeza medida. No caso do acelerómetro LSM6DSOX, estas flutuações são tipicamente da ordem de $\pm 0.02g$ em condições estáticas.

Para mitigar o efeito do ruído e evitar falsas deteções, o sistema implementa uma fase de **calibração automática**: nos primeiros segundos de funcionamento, são recolhidas 50 amostras consecutivas em repouso e calculada a média de cada eixo:

$$\bar{a}_x = \frac{1}{N} \sum_{i=1}^N a_{x,i}, \quad \bar{a}_y = \frac{1}{N} \sum_{i=1}^N a_{y,i}, \quad \bar{a}_z = \frac{1}{N} \sum_{i=1}^N a_{z,i}$$

Estes valores constituem a linha de base do sistema. Uma variação superior a $0.5g$ em qualquer eixo relativamente à linha de base é interpretada como movimento, acionando o registo de uma distração.

# Hardware {#hardware}

## Arduino Nano RP2040 Connect

O **Arduino Nano RP2040 Connect** é um microcontrolador de fator de forma compacto baseado no chip **RP2040** da Raspberry Pi Foundation. A Tabela 3.1 resume as suas principais características.

::: {#tab:arduino}
  Componente       Especificação
  ---------------- -------------------------------------------
  Processador      Dual-core ARM Cortex-M0+ a 133 MHz
  Memória RAM      264 KB SRAM
  Memória Flash    16 MB
  IMU              LSM6DSOX (acelerómetro + giroscópio 6 eixos)
  Microfone        MP34DT05 (PDM, integrado)
  Conectividade    Wi-Fi 802.11 b/g/n e Bluetooth 4.2
  LED RGB          Integrado, controlado via módulo NINA
  Interface        USB Micro-B, I2C, SPI, UART

  : Tabela 3.1 — Especificações do Arduino Nano RP2040 Connect
:::

Para este projeto, os componentes relevantes são o **IMU LSM6DSOX**, utilizado para detetar o movimento do telemóvel, e o **LED RGB**, utilizado como indicador visual do estado do sistema.

## IMU LSM6DSOX

O sensor inercial LSM6DSOX da STMicroelectronics combina um acelerómetro e um giroscópio de 6 eixos num único pacote compacto. As suas principais características são:

- **Gama de medição do acelerómetro**: ±2g, ±4g, ±8g ou ±16g (configurável);
- **Resolução**: 16 bits por eixo;
- **Taxa de amostragem**: até 6664 Hz;
- **Interface**: I2C e SPI;
- **Consumo em modo normal**: 0.55 mA.

## Configuração Física

O sistema não requer hardware adicional além do Arduino Nano RP2040 Connect e do cabo USB. O Arduino é colocado em cima do telemóvel durante as sessões de estudo, ligado ao computador via USB. A Tabela 3.2 descreve o comportamento do LED RGB em função do estado do sistema.

::: {#tab:led}
  Estado       Cor do LED   Significado
  ------------ ------------ ------------------------------------------
  Em estudo    Verde        Nenhum movimento detetado
  Distração    Vermelho     Movimento detetado; telemóvel levantado

  : Tabela 3.2 — Comportamento do LED RGB
:::

# Software {#software}

## Arquitetura do Sistema

O sistema é composto por três componentes de software distintos:

1. **Firmware do Arduino** (C++) — responsável pela leitura do acelerómetro, deteção de movimento e comunicação Serial com o PC;
2. **Script de monitorização** (`main.py`) — corre no PC, recebe os eventos do Arduino via porta Serial e regista-os num ficheiro Excel;
3. **Dashboard interativo** — gerado automaticamente em HTML/JavaScript, permite visualizar e analisar os dados.

O fluxo de dados é o seguinte:

**Arduino (IMU)** → **Serial USB** → **Python (main.py)** → **Excel (.xlsx)** → **Dashboard HTML**

## Firmware do Arduino

O firmware implementa as seguintes funcionalidades:

**Calibração automática**: no arranque, o sistema recolhe 50 amostras em repouso e calcula a média de cada eixo como linha de base.

**Deteção de movimento**: em cada ciclo de 100 ms, são lidas as acelerações nos três eixos e calculada a diferença relativamente à linha de base. Se qualquer eixo exceder o limiar de $0.5g$, é enviada a mensagem `DISTRACAO_INICIO` via Serial. Quando os valores regressam abaixo do limiar, é enviado `DISTRACAO_FIM`.

A Listagem 4.1 apresenta o núcleo do ciclo de deteção implementado no Arduino.

::: tcolorbox
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
        digitalWrite(LEDR, LOW);
        digitalWrite(LEDG, HIGH);
        digitalWrite(LEDB, HIGH);
      }
    } else {
      if (phonePickedUp) {
        phonePickedUp = false;
        Serial.println("DISTRACAO_FIM");
        // LED verde
        digitalWrite(LEDR, HIGH);
        digitalWrite(LEDG, LOW);
        digitalWrite(LEDB, HIGH);
      }
    }
  }
  delay(100);
}
```
:::

## Script de Monitorização (Python)

O script `main.py` corre continuamente no PC enquanto o Arduino está ligado. Ao receber `DISTRACAO_INICIO`, regista a hora de início. Ao receber `DISTRACAO_FIM`, calcula a duração e escreve uma nova linha no ficheiro Excel com os seguintes campos:

- `data` — data do evento (formato YYYY-MM-DD);
- `hora_inicio` — hora em que o telemóvel foi levantado;
- `hora_fim` — hora em que o telemóvel foi pousado;
- `duracao_segundos` — duração da distração em segundos.

O script deteta automaticamente a porta COM do Arduino, elimina a necessidade de configuração manual. Quando o utilizador termina a sessão (Ctrl+C), o dashboard é gerado e aberto automaticamente no browser.

## Dashboard Interativo

O dashboard é gerado automaticamente em HTML e inclui:

- **Cards de resumo**: total de distrações, tempo total distraído, duração média e hora mais problemática;
- **Gráfico principal com filtro por período**: permite alternar entre vista diária, semanal e mensal;
- **Gráfico de distribuição horária**: mostra a que horas do dia ocorrem mais distrações;
- **Gráfico de linha com duração acumulada por dia**;
- **Gráfico semanal com percentagem de variação**: barras vermelhas indicam semanas com mais distrações que a anterior; verdes indicam melhoria;
- **Tabela detalhada**: lista todos os eventos com filtro por dia e tipo (Rápida <30s, Média 30s–2min, Longa >2min);
- **Modo claro/escuro**: botão de alternância no canto superior direito.

## Executável

O projeto foi empacotado num executável Windows (`.exe`) utilizando a ferramenta **PyInstaller**, permitindo que o sistema seja utilizado sem instalação de Python ou de qualquer dependência.

# Metodologia e Resultados {#resultados}

## Recolha de Dados

Os dados foram recolhidos ao longo de aproximadamente um mês, durante sessões de estudo com o Arduino posicionado em cima do telemóvel, ligado ao computador via USB. Sempre que o telemóvel era levantado, o sistema registava o evento automaticamente de forma completamente passiva.

## Resultados Obtidos

Ao longo do período de monitorização foram registadas **159 distrações** distribuídas por **25 dias** de estudo, totalizando aproximadamente **4 horas e 44 minutos** de tempo distraído. A Tabela 5.1 resume as principais métricas obtidas.

::: {#tab:resultados}
  Métrica                          Valor
  -------------------------------- ---------------------
  Total de distrações              159
  Dias monitorizados               25
  Média de distrações por dia      ~6.4
  Tempo total distraído            4h 44min
  Duração média por distração      ~107 segundos
  Hora com mais distrações         19h

  : Tabela 5.1 — Métricas obtidas durante o período de monitorização
:::

A análise dos dados revela alguns padrões interessantes. As distrações tendem a concentrar-se ao final do dia (entre as 17h e as 20h), o que pode estar relacionado com a fadiga mental acumulada e com o aumento da atividade nas redes sociais nesse período. Os fins de semana apresentam consistentemente menos distrações, não necessariamente por maior disciplina, mas por sessões de estudo mais curtas ou inexistentes.

Em termos de duração, a maioria das distrações é relativamente breve — muitas com menos de 30 segundos — o que sugere que se tratam frequentemente de verificações rápidas do telemóvel. Ainda assim, as distrações mais longas (superiores a 2 minutos) contribuem desproporcionalmente para o tempo total distraído.

# Discussão e Conclusão {#conclusao}

## Ligação aos Conceitos Físicos

Este projeto ilustra de forma concreta a aplicação de conceitos fundamentais de física no desenvolvimento de sistemas computacionais. A deteção de movimento baseia-se na medição da aceleração gravitacional e na sua variação quando o dispositivo muda de orientação.

A fase de calibração exemplifica um princípio importante em metrologia: qualquer medição é afetada por incertezas sistemáticas e aleatórias, e é necessário estabelecer uma referência antes de interpretar os resultados. O limiar de deteção ($0.5g$) representa uma escolha de compromisso entre sensibilidade e especificidade, validada empiricamente durante os testes.

## Limitações

- **Dependência do cabo USB**: o Arduino tem de estar permanentemente ligado ao computador;
- **Falsos positivos**: vibrações da mesa podem ser interpretadas como distrações;
- **Contexto limitado**: levantar o telemóvel nem sempre equivale a distração (chamadas, verificar as horas, etc.).

## Trabalho Futuro

- Implementar comunicação Wi-Fi para eliminar a dependência do cabo USB;
- Aplicar um filtro de médias móveis para reduzir falsos positivos;
- Adicionar alertas sonoros via buzzer externo;
- Distinguir automaticamente entre distrações curtas e longas e adaptar os alertas.

## Conclusão

Este trabalho demonstrou a viabilidade de desenvolver um sistema de monitorização de comportamento funcional e útil com recurso a hardware de baixo custo e software open-source. O Arduino Nano RP2040 Connect, com o seu acelerómetro integrado, revelou-se uma plataforma adequada para a deteção de movimento em tempo real, e a combinação com Python e um dashboard HTML tornou os dados acessíveis e interpretáveis.

Do ponto de vista físico, o projeto evidenciou como a medição da aceleração gravitacional pode ser aplicada de forma prática e inovadora no contexto da computação e da monitorização de comportamento. O resultado final é uma ferramenta que, apesar das suas limitações, oferece uma perspetiva genuinamente útil sobre os hábitos de estudo.

# Referências {#referencias .unnumbered}

Arduino. (2024). *Arduino Nano RP2040 Connect — Documentation*. https://docs.arduino.cc/hardware/nano-rp2040-connect/

STMicroelectronics. (2021). *LSM6DSOX — iNEMO inertial module: Always-on 3D accelerometer and 3D gyroscope*. Datasheet DS12451.

Meriam, J. L., & Kraige, L. G. (2012). *Engineering Mechanics: Dynamics* (7th ed.). Wiley.

McKinney, W. (2022). *Python for Data Analysis* (3rd ed.). O'Reilly Media.

Chart.js Contributors. (2024). *Chart.js — Simple yet flexible JavaScript charting library*. https://www.chartjs.org
