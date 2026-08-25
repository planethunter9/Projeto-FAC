# Sistema de Deteção de Distração no Estudo

Sistema de monitorização de distração durante sessões de estudo, desenvolvido com **Arduino Nano RP2040 Connect** e **Python**.

O Arduino deteta quando o telemóvel é levantado através do acelerómetro integrado, regista o evento com data e hora, e gera automaticamente um dashboard interativo com a análise das distrações.

---

## Hardware Necessário

- Arduino Nano RP2040 Connect
- Cabo USB Micro-B

---

## Estrutura do Projeto

```
projeto
├── main.py              # Script principal (monitorização + geração do dashboard)
├── distrações.xlsx      # Ficheiro de dados (criado automaticamente)
├── dashboard.html       # Dashboard gerado automaticamente
├── AntiDistracao.exe    # Executável Windows (opcional)
└── sketch/
    └── main.ino         # Firmware do Arduino
```

---

## Como Instalar e Correr

### 1. Instalar dependências Python

```bash
pip install pyserial openpyxl
```

### 2. Carregar o firmware no Arduino

- Abre o ficheiro `sketch/main.ino` no Arduino IDE
- Seleciona a board **Arduino Nano RP2040 Connect**
- Faz upload para o Arduino

### 3. Correr o sistema

```bash
python main.py
```

O programa deteta automaticamente a porta COM do Arduino, inicia a monitorização e, quando terminares (Ctrl+C), gera o dashboard e abre-o no browser.

### Alternativa — Executável Windows

Faz duplo clique em `AntiDistracao.exe`. Não requer instalação de Python.

---

## Dashboard

O dashboard interativo inclui:

- **Cards** com total de distrações, tempo distraído, duração média e hora mais problemática
- **Gráfico principal** com filtro por dia, semana e mês — clica numa barra para ver o detalhe
- **Gráfico de horas** com atualização dinâmica ao clicar
- **Gráfico de linha** com tempo distraído por dia
- **Gráfico circular** com distribuição por período do dia (manhã, tarde, fim de tarde, noite)
- **Tabela detalhada** com filtro por dia e tipo (Rápida, Média, Longa)
- **Modo claro/escuro**

---

## Como Funciona

1. O Arduino é colocado em cima do telemóvel
2. O acelerómetro deteta quando o telemóvel é levantado
3. O LED muda de **verde** (a estudar) para **vermelho** (distração)
4. O evento é enviado via Serial para o PC e guardado no Excel
5. No final da sessão, o dashboard é gerado automaticamente

---

## Compilar o Executável (opcional)

```bash
pip install pyinstaller
python -m PyInstaller --onefile --name "AntiDistracao" main.py
```

O executável fica em `dist/AntiDistracao.exe`. Copia o `distrações.xlsx` para a mesma pasta.

---
