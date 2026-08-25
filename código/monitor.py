import serial
from datetime import datetime
from openpyxl import load_workbook, Workbook
import os

PORTA = 'COM3'
BAUDRATE = 9600
FICHEIRO = 'distrações.xlsx'

distracao_inicio = None
total_distrações = 0

# Cria o ficheiro se não existir
if not os.path.exists(FICHEIRO):
    wb = Workbook()
    ws = wb.active
    ws.title = "Distrações"
    ws.append(['data', 'hora_inicio', 'hora_fim', 'duração_segundos'])
    wb.save(FICHEIRO)

with serial.Serial(PORTA, BAUDRATE, timeout=1) as ser:
    print("A monitorizar... (Ctrl+C para parar)")

    while True:
        linha = ser.readline().decode('utf-8').strip()

        if linha == "DISTRACAO_INICIO":
            distracao_inicio = datetime.now()
            total_distrações += 1
            print(f"[{distracao_inicio.strftime('%H:%M:%S')}] 📵 Distração #{total_distrações} iniciada!")

        elif linha == "DISTRACAO_FIM" and distracao_inicio:
            fim = datetime.now()
            duracao = (fim - distracao_inicio).seconds
            print(f"[{fim.strftime('%H:%M:%S')}] ✅ Voltou a estudar. Duração: {duracao}s")

            wb = load_workbook(FICHEIRO)
            ws = wb.active
            ws.append([
                distracao_inicio.strftime('%Y-%m-%d'),
                distracao_inicio.strftime('%H:%M:%S'),
                fim.strftime('%H:%M:%S'),
                duracao
            ])
            wb.save(FICHEIRO)
            distracao_inicio = None