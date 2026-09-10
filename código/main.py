import os
import sys
import webbrowser
import serial
import serial.tools.list_ports
from datetime import datetime
from openpyxl import load_workbook, Workbook

# ── Caminhos ──────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FICHEIRO = os.path.join(BASE_DIR, 'distrações.xlsx')
DASHBOARD = os.path.join(BASE_DIR, 'dashboard.html')
BAUDRATE = 9600

def verde(t):    return f"\033[92m{t}\033[0m"
def vermelho(t): return f"\033[91m{t}\033[0m"
def amarelo(t):  return f"\033[93m{t}\033[0m"
def azul(t):     return f"\033[94m{t}\033[0m"
def bold(t):     return f"\033[1m{t}\033[0m"

def detetar_porta():
    portas = list(serial.tools.list_ports.comports())
    for p in portas:
        if 'Arduino' in p.description or 'RP2040' in p.description or 'USB Serial' in p.description:
            return p.device
    if portas:
        return portas[0].device
    return None

def inicializar_excel():
    if not os.path.exists(FICHEIRO):
        wb = Workbook()
        ws = wb.active
        ws.title = "Distrações"
        ws.append(['data', 'hora_inicio', 'hora_fim', 'duracao_segundos'])
        wb.save(FICHEIRO)
        print(verde("Ficheiro Excel criado."))
    else:
        print(verde(f"Ficheiro Excel encontrado: {FICHEIRO}"))

def gerar_dashboard():
    import json
    from collections import defaultdict

    wb = load_workbook(FICHEIRO)
    ws = wb.active
    dados = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] and row[3] is not None:
            dados.append({
                'data': str(row[0]),
                'hora_inicio': str(row[1]),
                'hora_fim': str(row[2]),
                'duracao': int(row[3])
            })

    if not dados:
        print(amarelo("Sem dados para gerar dashboard."))
        return False

    por_dia = defaultdict(list)
    for d in dados:
        por_dia[d['data']].append(d)

    por_semana = defaultdict(list)
    for d in dados:
        dt = datetime.strptime(d['data'], '%Y-%m-%d')
        por_semana[dt.strftime('%Y-W%W')].append(d)

    por_mes = defaultdict(list)
    for d in dados:
        por_mes[d['data'][:7]].append(d)

    dias = sorted(por_dia.keys())
    semanas = sorted(por_semana.keys())
    meses = sorted(por_mes.keys())

    dados_por_dia = {d: len(por_dia[d]) for d in dias}
    duracao_por_dia = {d: sum(x['duracao'] for x in por_dia[d]) for d in dias}
    dados_por_semana = {s: len(por_semana[s]) for s in semanas}
    dados_por_mes = {m: len(por_mes[m]) for m in meses}

    # Horas por dia (para detalhe ao clicar)
    horas_por_dia = {}
    for dia in dias:
        h = defaultdict(int)
        for d in por_dia[dia]:
            h[int(d['hora_inicio'].split(':')[0])] += 1
        horas_por_dia[dia] = dict(sorted(h.items()))

    # Dias por semana (para detalhe ao clicar)
    dias_por_semana = {}
    for s in semanas:
        dp = defaultdict(int)
        for d in por_semana[s]:
            dp[d['data']] += 1
        dias_por_semana[s] = dict(sorted(dp.items()))

    # Semanas por mes (para detalhe ao clicar)
    semanas_por_mes = {}
    for m in meses:
        sp = defaultdict(int)
        for d in por_mes[m]:
            dt = datetime.strptime(d['data'], '%Y-%m-%d')
            sem = dt.strftime('%Y-W%W')
            sp[sem] += 1
        semanas_por_mes[m] = dict(sorted(sp.items()))

    # Distribuição por periodo do dia (global)
    periodos = {'Manhã\n(9h-12h)': 0, 'Tarde\n(12h-18h)': 0, 'Fim de tarde\n(18h-20h)': 0, 'Noite\n(20h+)': 0}
    for d in dados:
        h = int(d['hora_inicio'].split(':')[0])
        if 9 <= h < 12:
            periodos['Manhã\n(9h-12h)'] += 1
        elif 12 <= h < 18:
            periodos['Tarde\n(12h-18h)'] += 1
        elif 18 <= h < 20:
            periodos['Fim de tarde\n(18h-20h)'] += 1
        else:
            periodos['Noite\n(20h+)'] += 1

    por_hora = defaultdict(int)
    for d in dados:
        por_hora[int(d['hora_inicio'].split(':')[0])] += 1

    total = len(dados)
    total_seg = sum(d['duracao'] for d in dados)
    media = total_seg / total if total > 0 else 0
    hora_pior = max(por_hora, key=por_hora.get) if por_hora else 0

    # ── INSIGHTS AUTOMÁTICOS ──────────────────────────────
    insights = []

    # Insight 1: hora mais problemática
    if por_hora:
        insights.append(f"A tua hora mais crítica é às <b>{hora_pior}h</b> — é quando te distrais mais.")

    # Insight 2: período do dia dominante
    periodo_top = max(periodos, key=periodos.get)
    periodo_nome = periodo_top.split('\n')[0]
    total_periodo = sum(periodos.values())
    if total_periodo > 0:
        pct_periodo = round(periodos[periodo_top] / total_periodo * 100)
        insights.append(f"Concentras <b>{pct_periodo}%</b> das distrações no período da <b>{periodo_nome.lower()}</b>.")

    # Insight 3: melhor vs pior dia da semana
    dow_pt = ['segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado', 'domingo']
    por_dow = defaultdict(list)
    for dia in dias:
        dt = datetime.strptime(dia, '%Y-%m-%d')
        por_dow[dt.weekday()].append(len(por_dia[dia]))
    media_dow = {d: sum(v)/len(v) for d, v in por_dow.items() if v}
    if media_dow:
        melhor_dow = min(media_dow, key=media_dow.get)
        pior_dow = max(media_dow, key=media_dow.get)
        insights.append(f"<b>{dow_pt[melhor_dow].capitalize()}</b> é o teu dia mais focado; <b>{dow_pt[pior_dow]}</b> o mais distraído.")

    # Insight 4: duração típica
    curtas = sum(1 for d in dados if d['duracao'] < 30)
    pct_curtas = round(curtas / total * 100) if total > 0 else 0
    insights.append(f"<b>{pct_curtas}%</b> das tuas distrações são rápidas (menos de 30 segundos) — verificações reflexas do telemóvel.")

    # ── COMPARAÇÃO SEMANA ATUAL vs ANTERIOR ───────────────
    comparacao = None
    if len(semanas) >= 2:
        sem_atual = semanas[-1]
        sem_anterior = semanas[-2]
        n_atual = len(por_semana[sem_atual])
        n_anterior = len(por_semana[sem_anterior])
        seg_atual = sum(d['duracao'] for d in por_semana[sem_atual])
        seg_anterior = sum(d['duracao'] for d in por_semana[sem_anterior])
        if n_anterior > 0:
            delta_n = round((n_atual - n_anterior) / n_anterior * 100)
        else:
            delta_n = 0
        if seg_anterior > 0:
            delta_seg = round((seg_atual - seg_anterior) / seg_anterior * 100)
        else:
            delta_seg = 0

        # Intervalo de datas de cada semana
        meses_pt = {1:'jan',2:'fev',3:'mar',4:'abr',5:'mai',6:'jun',
                    7:'jul',8:'ago',9:'set',10:'out',11:'nov',12:'dez'}
        def intervalo_semana(dados_sem):
            datas = sorted(datetime.strptime(d['data'], '%Y-%m-%d') for d in dados_sem)
            ini, fim = datas[0], datas[-1]
            if ini.month == fim.month:
                return f"{ini.day}–{fim.day} {meses_pt[ini.month]}"
            return f"{ini.day} {meses_pt[ini.month]} – {fim.day} {meses_pt[fim.month]}"

        label_atual = intervalo_semana(por_semana[sem_atual])
        label_anterior = intervalo_semana(por_semana[sem_anterior])

        comparacao = {
            'n_atual': n_atual, 'n_anterior': n_anterior, 'delta_n': delta_n,
            'min_atual': round(seg_atual/60), 'min_anterior': round(seg_anterior/60), 'delta_seg': delta_seg,
            'label_atual': label_atual, 'label_anterior': label_anterior
        }

    insights_json = json.dumps(insights)
    comparacao_json = json.dumps(comparacao)

    detalhes_json = json.dumps(por_dia)
    dados_por_dia_json = json.dumps(dados_por_dia)
    duracao_por_dia_json = json.dumps(duracao_por_dia)
    dados_por_semana_json = json.dumps(dados_por_semana)
    dados_por_mes_json = json.dumps(dados_por_mes)
    horas_por_dia_json = json.dumps(horas_por_dia)
    dias_por_semana_json = json.dumps(dias_por_semana)
    semanas_por_mes_json = json.dumps(semanas_por_mes)
    periodos_json = json.dumps(periodos)

    html = f"""<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="UTF-8">
<title>Dashboard de Distrações</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; }}
  header {{ background: #1e293b; padding: 20px 30px; border-bottom: 1px solid #334155; }}
  header h1 {{ font-size: 22px; color: #f8fafc; }}
  header p {{ color: #94a3b8; font-size: 13px; margin-top: 4px; }}
  .container {{ padding: 24px 30px; }}
  .cards {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }}
  .card {{ background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; }}
  .card .valor {{ font-size: 28px; font-weight: 700; margin-bottom: 4px; }}
  .card .label {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }}
  .card.red .valor {{ color: #f87171; }}
  .card.yellow .valor {{ color: #fbbf24; }}
  .card.blue .valor {{ color: #60a5fa; }}
  .card.purple .valor {{ color: #a78bfa; }}
  .filtros {{ display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap; align-items: center; }}
  .filtros span {{ color: #94a3b8; font-size: 13px; margin-right: 4px; }}
  .btn {{ padding: 8px 16px; border-radius: 8px; border: 1px solid #334155; background: #1e293b;
          color: #94a3b8; cursor: pointer; font-size: 13px; transition: all 0.2s; }}
  .btn:hover {{ border-color: #60a5fa; color: #60a5fa; }}
  .btn.active {{ background: #2563eb; border-color: #2563eb; color: white; }}
  .graficos-grid {{ display: grid; grid-template-columns: 2fr 1fr; gap: 16px; margin-bottom: 16px; }}
  .grafico-box {{ background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; }}
  .grafico-box h3 {{ font-size: 14px; color: #94a3b8; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.05em; }}
  .grafico-hint {{ font-size: 11px; color: #475569; margin-bottom: 12px; }}
  .graficos-grid2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }}
  .tabela-box {{ background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; margin-bottom: 16px; }}
  .tabela-box h3 {{ font-size: 14px; color: #94a3b8; margin-bottom: 16px; text-transform: uppercase; letter-spacing: 0.05em; }}
  .filtro-dia {{ display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }}
  .filtro-dia select {{ background: #0f172a; color: #e2e8f0; border: 1px solid #334155;
                        padding: 6px 12px; border-radius: 8px; font-size: 13px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{ text-align: left; padding: 10px 12px; color: #64748b; border-bottom: 1px solid #334155; font-weight: 500; }}
  td {{ padding: 10px 12px; border-bottom: 1px solid #1e293b; color: #cbd5e1; }}
  tr:hover td {{ background: #0f172a; }}
  .badge {{ padding: 2px 8px; border-radius: 20px; font-size: 11px; font-weight: 600; }}
  .badge.curta {{ background: #064e3b; color: #6ee7b7; }}
  .badge.media {{ background: #78350f; color: #fcd34d; }}
  .badge.longa {{ background: #7f1d1d; color: #fca5a5; }}
  .toggle-theme {{ position: fixed; top: 20px; right: 20px; z-index: 999;
    padding: 8px 16px; border-radius: 8px; border: 1px solid #334155;
    background: #1e293b; color: #e2e8f0; cursor: pointer; font-size: 13px;
    display: inline-flex; align-items: center; gap: 6px; }}
  .toggle-theme #theme-icon {{ display: inline-flex; align-items: center; }}
  .btn-pdf {{ display: inline-flex; align-items: center; }}
  .breadcrumb {{ font-size: 12px; color: #475569; margin-bottom: 8px; }}
  .breadcrumb span {{ color: #60a5fa; cursor: pointer; }}
  .breadcrumb span:hover {{ text-decoration: underline; }}
  body.light {{ background: #f1f5f9; color: #0f172a; }}
  body.light header {{ background: #ffffff; border-color: #e2e8f0; }}
  body.light header h1 {{ color: #0f172a; }}
  body.light header p {{ color: #64748b; }}
  body.light .card {{ background: #ffffff; border-color: #e2e8f0; }}
  body.light .btn {{ background: #ffffff; border-color: #e2e8f0; color: #64748b; }}
  body.light .btn.active {{ background: #2563eb; color: white; }}
  body.light .grafico-box {{ background: #ffffff; border-color: #e2e8f0; }}
  body.light .grafico-box h3 {{ color: #64748b; }}
  body.light .tabela-box {{ background: #ffffff; border-color: #e2e8f0; }}
  body.light .tabela-box h3 {{ color: #64748b; }}
  body.light .filtro-dia select {{ background: #f8fafc; color: #0f172a; border-color: #e2e8f0; }}
  body.light td {{ color: #334155; }}
  body.light tr:hover td {{ background: #f8fafc; }}
  body.light .toggle-theme {{ background: #ffffff; border-color: #e2e8f0; color: #0f172a; }}
  body.light .grafico-hint {{ color: #94a3b8; }}
  body.light .breadcrumb {{ color: #94a3b8; }}

  /* Tabs */
  .tabs {{ display: flex; gap: 4px; margin-bottom: 20px; border-bottom: 1px solid #334155; }}
  .tab {{ padding: 10px 20px; border: none; background: none; color: #94a3b8;
    cursor: pointer; font-size: 14px; font-weight: 500; border-bottom: 2px solid transparent;
    margin-bottom: -1px; transition: all 0.2s; }}
  .tab:hover {{ color: #60a5fa; }}
  .tab.active {{ color: #60a5fa; border-bottom-color: #60a5fa; }}
  .tab-panel {{ display: none; }}
  .tab-panel.active {{ display: block; }}
  body.light .tabs {{ border-color: #e2e8f0; }}
  body.light .tab {{ color: #64748b; }}
  body.light .tab.active {{ color: #2563eb; border-bottom-color: #2563eb; }}

  /* Insights */
  .insights-meta-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; align-items: stretch; }}
  .insights {{ background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; }}
  .insights h3 {{ font-size: 14px; color: #94a3b8; margin-bottom: 14px; text-transform: uppercase; letter-spacing: 0.05em; }}
  .insight-item {{ display: flex; align-items: flex-start; gap: 10px; padding: 10px 0; border-bottom: 1px solid #0f172a; font-size: 14px; color: #cbd5e1; }}
  .insight-item:last-child {{ border-bottom: none; }}
  .insight-item .ico {{ font-size: 18px; }}
  .insight-item b {{ color: #60a5fa; }}
  body.light .insights {{ background: #ffffff; border-color: #e2e8f0; }}
  body.light .insights h3 {{ color: #64748b; }}
  body.light .insight-item {{ color: #334155; border-color: #f1f5f9; }}

  /* Comparação semanal */
  .comparacao {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }}
  .comp-card {{ background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; }}
  .comp-card .label {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; }}
  .comp-card .valor {{ font-size: 24px; font-weight: 700; color: #f8fafc; }}
  .comp-card .delta {{ font-size: 14px; font-weight: 600; margin-top: 4px; }}
  .comp-card .delta.up {{ color: #f87171; }}
  .comp-card .delta.down {{ color: #6ee7b7; }}
  .comp-card .sub {{ font-size: 12px; color: #64748b; margin-top: 2px; }}
  body.light .comp-card {{ background: #ffffff; border-color: #e2e8f0; }}
  body.light .comp-card .valor {{ color: #0f172a; }}

  /* Meta */
  .meta-box {{ background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; }}
  .meta-box h3 {{ font-size: 14px; color: #94a3b8; margin-bottom: 14px; text-transform: uppercase; letter-spacing: 0.05em; }}
  .meta-controls {{ display: flex; align-items: center; gap: 12px; margin-bottom: 14px; flex-wrap: wrap; }}
  .meta-controls input {{ background: #0f172a; color: #e2e8f0; border: 1px solid #334155; padding: 6px 12px; border-radius: 8px; font-size: 13px; width: 70px; }}
  .meta-controls label {{ font-size: 13px; color: #94a3b8; }}
  .meta-barra {{ height: 24px; background: #0f172a; border-radius: 12px; overflow: hidden; position: relative; }}
  .meta-fill {{ height: 100%; border-radius: 12px; transition: width 0.4s, background 0.4s; }}
  .meta-texto {{ font-size: 13px; margin-top: 8px; color: #cbd5e1; }}
  body.light .meta-box {{ background: #ffffff; border-color: #e2e8f0; }}
  body.light .meta-box h3 {{ color: #64748b; }}
  body.light .meta-controls input {{ background: #f8fafc; color: #0f172a; border-color: #e2e8f0; }}
  body.light .meta-barra {{ background: #f1f5f9; }}
  body.light .meta-texto {{ color: #334155; }}

  /* Botão PDF */
  .btn-pdf {{ position: fixed; top: 20px; right: 170px; z-index: 999;
    padding: 8px 16px; border-radius: 8px; border: 1px solid #334155;
    background: #2563eb; color: white; cursor: pointer; font-size: 13px; }}
  .btn-pdf:hover {{ background: #1d4ed8; }}

  @media print {{
    .toggle-theme, .btn-pdf, .filtros, .meta-controls {{ display: none !important; }}
    body {{ background: white !important; color: black !important; }}
    .card, .grafico-box, .insights, .comp-card, .meta-box, .tabela-box {{ 
      background: white !important; border: 1px solid #ccc !important; 
      page-break-inside: avoid; }}
  }}
</style>
</head>
<body>
<button class="btn-pdf" onclick="window.print()"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px;margin-right:6px"><path d="M6 9V2h12v7"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>Exportar PDF</button>
<button class="toggle-theme" onclick="toggleTheme()"><span id="theme-icon"></span><span id="theme-label">Light Mode</span></button>
<header>
  <h1>Dashboard de Distrações no Estudo</h1>
  <p>Sistema de monitorização com Arduino Nano RP2040 Connect</p>
</header>
<div class="container">
  <div class="cards">
    <div class="card red"><div class="valor">{total}</div><div class="label">Total de Distrações</div></div>
    <div class="card yellow"><div class="valor">{total_seg // 3600}h {(total_seg % 3600) // 60}min</div><div class="label">Tempo Total Distraído</div></div>
    <div class="card blue"><div class="valor">{media:.0f}s</div><div class="label">Duração Média</div></div>
    <div class="card purple"><div class="valor">{hora_pior}h</div><div class="label">Hora com mais Distrações</div></div>
  </div>

  <div class="tabs">
    <button class="tab active" onclick="mostrarTab('visao', this)">Visão Geral</button>
    <button class="tab" onclick="mostrarTab('analise', this)">Análise</button>
    <button class="tab" onclick="mostrarTab('registo', this)">Registo</button>
  </div>

  <div class="tab-panel active" id="tab-visao">
  <div class="insights-meta-grid">
    <div class="insights">
      <h3><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px;margin-right:6px"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5.76.76 1.23 1.52 1.41 2.5"/></svg>Insights</h3>
      <div id="insights-lista"></div>
    </div>

    <div class="meta-box">
      <h3><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-2px;margin-right:6px"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>Meta Diária</h3>
      <div class="meta-controls">
        <label>Objetivo máximo de distrações por dia:</label>
        <input type="number" id="meta-input" value="5" min="1" max="50" onchange="atualizarMeta()">
      </div>
      <div class="meta-barra"><div class="meta-fill" id="meta-fill"></div></div>
      <div class="meta-texto" id="meta-texto"></div>
    </div>
  </div>

  <div class="comparacao" id="comparacao-box"></div>
  </div>

  <div class="tab-panel" id="tab-analise">
  <div class="filtros">
    <span>Ver por:</span>
    <button class="btn active" onclick="setVista('dia', this)">Dia</button>
    <button class="btn" onclick="setVista('semana', this)">Semana</button>
    <button class="btn" onclick="setVista('mes', this)">Mês</button>
  </div>
  <div class="graficos-grid">
    <div class="grafico-box">
      <h3 id="titulo-principal">Distrações por Dia</h3>
      <div class="grafico-hint" id="hint-principal"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-1px;margin-right:4px"><path d="m9 9 5 12 1.8-5.2L21 14Z"/><path d="M7.2 2.2 8 5.1"/><path d="m5.1 8-2.9-.8"/><path d="M14 4.1 12 6"/><path d="m6 12-1.9 2"/></svg>Clica numa barra para ver o detalhe</div>
      <div class="breadcrumb" id="breadcrumb" style="display:none"></div>
      <canvas id="grafico-principal" height="120"></canvas>
    </div>
    <div class="grafico-box" style="display:flex; flex-direction:column;">
      <h3 id="titulo-detalhe">A Que Horas Ocorrem?</h3>
      <p class="grafico-hint" id="hint-detalhe">Todas as distrações</p>
      <div style="flex:1; min-height:200px;"><canvas id="grafico-detalhe"></canvas></div>
    </div>
  </div>
  <div class="graficos-grid2">
    <div class="grafico-box"><h3>Tempo Total Distraído por Dia (minutos)</h3><div style="height:260px;"><canvas id="grafico-duracao"></canvas></div></div>
    <div class="grafico-box"><h3>Distribuição por Período do Dia</h3><div style="height:260px;"><canvas id="grafico-periodos"></canvas></div></div>
  </div>
  </div>

  <div class="tab-panel" id="tab-registo">
  <div class="tabela-box">
    <h3>Registo Detalhado</h3>
    <div class="filtro-dia">
      <select id="select-dia" onchange="atualizarTabela()"><option value="">-- Todos os dias --</option></select>
      <select id="select-tipo" onchange="atualizarTabela()">
        <option value="">-- Todos os tipos --</option>
        <option value="curta">Rápida (&lt;30s)</option>
        <option value="media">Média (30s–2min)</option>
        <option value="longa">Longa (&gt;2min)</option>
      </select>
    </div>
    <table>
      <thead><tr><th>Data</th><th>Hora Início</th><th>Hora Fim</th><th>Duração</th><th>Tipo</th></tr></thead>
      <tbody id="tabela-body"></tbody>
    </table>
  </div>
  </div>
</div>
<script>
const dadosDia = {dados_por_dia_json};
const duracaoDia = {duracao_por_dia_json};
const dadosSemana = {dados_por_semana_json};
const dadosMes = {dados_por_mes_json};
const detalhes = {detalhes_json};
const horasPorDia = {horas_por_dia_json};
const diasPorSemana = {dias_por_semana_json};
const semanasPorMes = {semanas_por_mes_json};
const periodos = {periodos_json};
const insights = {insights_json};
const comparacao = {comparacao_json};
const dadosDiaMeta = {dados_por_dia_json};

let vistaAtual = 'dia';
let selecaoAtual = null;

const CHART_OPTS = {{
  responsive: true,
  plugins: {{ legend: {{ display: false }} }},
  scales: {{
    x: {{ ticks: {{ color: '#94a3b8', font: {{ size: 11 }} }}, grid: {{ display: false }} }},
    y: {{ min: 0, ticks: {{ color: '#94a3b8', font: {{ size: 11 }} }}, grid: {{ color: '#334155' }} }}
  }}
}};

// ── Gráfico principal ──────────────────────────────────────
const ctxP = document.getElementById('grafico-principal').getContext('2d');
let graficoPrincipal = new Chart(ctxP, {{
  type: 'bar',
  data: {{ labels: Object.keys(dadosDia).map(d => formatarData(d)), datasets: [{{ data: Object.values(dadosDia), backgroundColor: '#3b82f6', borderRadius: 6 }}] }},
  options: {{
    ...CHART_OPTS,
    onClick: (e, elements) => {{
      if (elements.length > 0) {{
        const idx = elements[0].index;
        const chave = Object.keys(graficoPrincipal.data.labelsRaw || {{}})[idx];
        clicarBarra(idx);
      }}
    }},
    onHover: (e, elements) => {{
      e.native.target.style.cursor = elements.length > 0 ? 'pointer' : 'default';
    }}
  }}
}});
graficoPrincipal.data.labelsRaw = dadosDia;

// ── Gráfico detalhe (direita) ──────────────────────────────
const ctxD2 = document.getElementById('grafico-detalhe').getContext('2d');
let graficoDetalhe;

function renderDetalhe(labels, valores, titulo, hint) {{
  document.getElementById('titulo-detalhe').textContent = titulo;
  document.getElementById('hint-detalhe').textContent = hint;
  if (graficoDetalhe) graficoDetalhe.destroy();
  graficoDetalhe = new Chart(ctxD2, {{
    type: 'bar',
    data: {{ labels, datasets: [{{ data: valores, backgroundColor: '#a78bfa', borderRadius: 6 }}] }},
    options: {{ ...CHART_OPTS, maintainAspectRatio: false }}
  }});
}}

// Detalhe global: horas globais
const horasGlobal = {{}};
Object.values(horasPorDia).forEach(h => {{
  Object.entries(h).forEach(([hr, cnt]) => {{
    horasGlobal[hr] = (horasGlobal[hr] || 0) + cnt;
  }});
}});
const horasGlobalSorted = Object.keys(horasGlobal).sort((a,b)=>+a-+b);
renderDetalhe(horasGlobalSorted.map(h => h+'h'), horasGlobalSorted.map(h => horasGlobal[h]), 'A Que Horas Ocorrem?', 'Todas as distrações');

// ── Clique numa barra ──────────────────────────────────────
function clicarBarra(idx) {{
  selecaoAtual = idx;
  const keys = Object.keys(graficoPrincipal.data.labelsRaw || {{}});
  const chave = keys[idx];
  if (!chave) return;

  // Destacar barra selecionada
  const cores = keys.map((_, i) => i === idx ? '#f59e0b' : '#3b82f6');
  graficoPrincipal.data.datasets[0].backgroundColor = cores;
  graficoPrincipal.update();

  const bc = document.getElementById('breadcrumb');
  bc.style.display = 'block';

  if (vistaAtual === 'dia') {{
    const horas = horasPorDia[chave] || {{}};
    const hs = Object.keys(horas).sort((a,b)=>+a-+b);
    renderDetalhe(hs.map(h=>h+'h'), hs.map(h=>horas[h]), `Horas — ${{formatarData(chave)}}`, `${{Object.values(horas).reduce((a,b)=>a+b,0)}} distrações`);
    bc.innerHTML = `<span onclick="voltarGlobal()">← Todos os dias</span> › ${{formatarData(chave)}}`;
    // Filtrar tabela
    document.getElementById('select-dia').value = chave;
    atualizarTabela();
  }} else if (vistaAtual === 'semana') {{
    const dias = diasPorSemana[chave] || {{}};
    const ds = Object.keys(dias).sort();
    renderDetalhe(ds.map(d=>formatarData(d)), ds.map(d=>dias[d]), `Dias — Sem ${{chave.split('W')[1]}}`, `${{Object.values(dias).reduce((a,b)=>a+b,0)}} distrações`);
    bc.innerHTML = `<span onclick="voltarGlobal()">← Todas as semanas</span> › Sem ${{chave.split('W')[1]}}`;
  }} else {{
    const sems = semanasPorMes[chave] || {{}};
    const ss = Object.keys(sems).sort();
    renderDetalhe(ss.map(s=>'Sem '+s.split('W')[1]), ss.map(s=>sems[s]), `Semanas — ${{chave}}`, `${{Object.values(sems).reduce((a,b)=>a+b,0)}} distrações`);
    bc.innerHTML = `<span onclick="voltarGlobal()">← Todos os meses</span> › ${{chave}}`;
  }}
}}

function voltarGlobal() {{
  selecaoAtual = null;
  document.getElementById('breadcrumb').style.display = 'none';
  // Repor cores
  const n = graficoPrincipal.data.datasets[0].data.length;
  graficoPrincipal.data.datasets[0].backgroundColor = Array(n).fill('#3b82f6');
  graficoPrincipal.update();
  // Repor detalhe global
  renderDetalhe(horasGlobalSorted.map(h=>h+'h'), horasGlobalSorted.map(h=>horasGlobal[h]), 'A Que Horas Ocorrem?', 'Todas as distrações');
  document.getElementById('select-dia').value = '';
  atualizarTabela();
}}

// ── Gráfico linha duração ──────────────────────────────────
const ctxDur = document.getElementById('grafico-duracao').getContext('2d');
let graficoDuracao = new Chart(ctxDur, {{
  type: 'line',
  data: {{ labels: Object.keys(duracaoDia).map(d => formatarData(d)), datasets: [{{ data: Object.values(duracaoDia).map(s => Math.round(s/60*10)/10), borderColor: '#f59e0b', backgroundColor: '#f59e0b22', fill: true, tension: 0.4, pointRadius: 4 }}] }},
  options: {{ ...CHART_OPTS, maintainAspectRatio: false }}
}});

// ── Gráfico circular períodos ──────────────────────────────
const ctxPer = document.getElementById('grafico-periodos').getContext('2d');
const periodoVals = Object.values(periodos);
const periodoTotal = periodoVals.reduce((a, b) => a + b, 0);

const pluginPctDonut = {{
  id: 'pctDonut',
  afterDatasetsDraw(chart) {{
    const ctx = chart.ctx;
    const meta = chart.getDatasetMeta(0);
    ctx.save();
    ctx.font = 'bold 13px Segoe UI';
    ctx.fillStyle = '#fff';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    meta.data.forEach((arc, i) => {{
      const val = periodoVals[i];
      if (val === 0 || periodoTotal === 0) return;
      const pct = Math.round(val / periodoTotal * 100);
      const pos = arc.tooltipPosition();
      ctx.fillText(pct + '%', pos.x, pos.y);
    }});
    ctx.restore();
  }}
}};

let graficoPeriodos = new Chart(ctxPer, {{
  type: 'doughnut',
  data: {{
    labels: Object.keys(periodos),
    datasets: [{{ data: periodoVals, backgroundColor: ['#60a5fa','#f59e0b','#f87171','#a78bfa'], borderWidth: 0 }}]
  }},
  options: {{
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{
      legend: {{ display: true, position: 'bottom', labels: {{ color: '#94a3b8', font: {{ size: 11 }}, padding: 12 }} }},
      tooltip: {{ callbacks: {{ label: (ctx) => ` ${{ctx.label.replace('\\n',' ')}}: ${{ctx.raw}} distrações` }} }}
    }}
  }},
  plugins: [pluginPctDonut]
}});

// ── Vista ──────────────────────────────────────────────────
function setVista(vista, btn) {{
  vistaAtual = vista;
  selecaoAtual = null;
  document.getElementById('breadcrumb').style.display = 'none';
  document.querySelectorAll('.btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');

  let labelsRaw, labels, valores, titulo;
  const pluginsSemana = [];

  if (vista === 'dia') {{
    labelsRaw = dadosDia;
    labels = Object.keys(dadosDia).map(d => formatarData(d));
    valores = Object.values(dadosDia);
    titulo = 'Distrações por Dia';
    graficoPrincipal.data.datasets[0].backgroundColor = Array(valores.length).fill('#3b82f6');
  }} else if (vista === 'semana') {{
    labelsRaw = dadosSemana;
    const semanaVals = Object.values(dadosSemana);
    const semanaKeys = Object.keys(dadosSemana);
    labels = semanaKeys.map(s => 'Sem ' + s.split('W')[1]);
    valores = semanaVals;
    titulo = 'Distrações por Semana';
    const cores = semanaVals.map((val, i) => i === 0 ? '#10b981' : val > semanaVals[i-1] ? '#f87171' : '#10b981');
    graficoPrincipal.data.datasets[0].backgroundColor = cores;
    pluginsSemana.push(pluginDelta);
  }} else {{
    labelsRaw = dadosMes;
    labels = Object.keys(dadosMes);
    valores = Object.values(dadosMes);
    titulo = 'Distrações por Mês';
    graficoPrincipal.data.datasets[0].backgroundColor = Array(valores.length).fill('#3b82f6');
  }}

  document.getElementById('titulo-principal').textContent = titulo;
  graficoPrincipal.data.labelsRaw = labelsRaw;
  graficoPrincipal.data.labels = labels;
  graficoPrincipal.data.datasets[0].data = valores;
  graficoPrincipal.options.plugins.tooltip = {{ enabled: true }};
  graficoPrincipal.update();

  // Repor detalhe global
  renderDetalhe(horasGlobalSorted.map(h=>h+'h'), horasGlobalSorted.map(h=>horasGlobal[h]), 'A Que Horas Ocorrem?', 'Todas as distrações');
  document.getElementById('select-dia').value = '';
  atualizarTabela();
}}

// Plugin delta semanas
const pluginDelta = {{
  id: 'deltaPlugin',
  afterDatasetsDraw(chart) {{
    if (vistaAtual !== 'semana') return;
    const ctx = chart.ctx;
    ctx.save();
    ctx.font = 'bold 11px Segoe UI';
    ctx.textAlign = 'center';
    const vals = chart.data.datasets[0].data;
    vals.forEach((val, i) => {{
      if (i === 0) return;
      const anterior = vals[i-1];
      if (anterior === 0) return;
      const pct = Math.round((val - anterior) / anterior * 100);
      const texto = pct > 0 ? '+' + pct + '%' : pct + '%';
      ctx.fillStyle = pct > 0 ? '#f87171' : '#6ee7b7';
      const meta = chart.getDatasetMeta(0).data[i];
      ctx.fillText(texto, meta.x, meta.y - 8);
    }});
    ctx.restore();
  }}
}};
Chart.register(pluginDelta);

// ── Tabela ──────────────────────────────────────────────────
const select = document.getElementById('select-dia');
Object.keys(detalhes).sort().forEach(dia => {{
  const opt = document.createElement('option');
  opt.value = dia; opt.textContent = formatarData(dia);
  select.appendChild(opt);
}});

function atualizarTabela() {{
  const diaFiltro = document.getElementById('select-dia').value;
  const tipoFiltro = document.getElementById('select-tipo').value;
  const tbody = document.getElementById('tabela-body');
  tbody.innerHTML = '';
  let registos = [];
  if (diaFiltro) {{ registos = detalhes[diaFiltro] || []; }}
  else {{ Object.values(detalhes).forEach(arr => registos.push(...arr)); registos.sort((a,b) => a.data.localeCompare(b.data) || a.hora_inicio.localeCompare(b.hora_inicio)); }}
  if (tipoFiltro) {{ registos = registos.filter(r => {{ const dur = r.duracao; if (tipoFiltro==='curta') return dur<30; if (tipoFiltro==='media') return dur>=30&&dur<120; if (tipoFiltro==='longa') return dur>=120; }}); }}
  registos.slice(0, 100).forEach(r => {{
    const dur = r.duracao;
    let badge, tipo;
    if (dur<30) {{ badge='curta'; tipo='Rápida'; }}
    else if (dur<120) {{ badge='media'; tipo='Média'; }}
    else {{ badge='longa'; tipo='Longa'; }}
    const mins = Math.floor(dur/60), segs = dur%60;
    const durStr = mins > 0 ? `${{mins}}m ${{segs}}s` : `${{segs}}s`;
    tbody.innerHTML += `<tr><td>${{formatarData(r.data)}}</td><td>${{r.hora_inicio}}</td><td>${{r.hora_fim}}</td><td>${{durStr}}</td><td><span class="badge ${{badge}}">${{tipo}}</span></td></tr>`;
  }});
}}

function formatarData(d) {{
  const [ano, mes, dia] = d.split('-');
  return `${{dia}}/${{mes}}/${{ano}}`;
}}

const svgSun = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>';
const svgMoon = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>';
document.getElementById('theme-icon').innerHTML = svgSun;

function toggleTheme() {{
  const isLight = document.body.classList.toggle('light');
  document.getElementById('theme-icon').innerHTML = isLight ? svgMoon : svgSun;
  document.getElementById('theme-label').textContent = isLight ? 'Dark Mode' : 'Light Mode';
}}

atualizarTabela();

// ── Insights ───────────────────────────────────────────────
const listaInsights = document.getElementById('insights-lista');
const svgClock = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>';
const svgChart = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>';
const svgCalendar = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>';
const svgBolt = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>';
const icones = [svgClock, svgChart, svgCalendar, svgBolt];
insights.forEach((txt, i) => {{
  const div = document.createElement('div');
  div.className = 'insight-item';
  div.innerHTML = `<span class="ico">${{icones[i % icones.length]}}</span><span>${{txt}}</span>`;
  listaInsights.appendChild(div);
}});

// ── Comparação semanal ─────────────────────────────────────
if (comparacao) {{
  const box = document.getElementById('comparacao-box');
  const setaN = comparacao.delta_n > 0 ? '↑' : comparacao.delta_n < 0 ? '↓' : '→';
  const classeN = comparacao.delta_n > 0 ? 'up' : 'down';
  const setaS = comparacao.delta_seg > 0 ? '↑' : comparacao.delta_seg < 0 ? '↓' : '→';
  const classeS = comparacao.delta_seg > 0 ? 'up' : 'down';
  box.innerHTML = `
    <div class="comp-card">
      <div class="label">Distrações na última semana registada</div>
      <div class="valor">${{comparacao.n_atual}}</div>
      <div class="delta ${{classeN}}">${{setaN}} ${{Math.abs(comparacao.delta_n)}}% face à semana anterior</div>
      <div class="sub">${{comparacao.label_atual}} · anterior (${{comparacao.label_anterior}}): ${{comparacao.n_anterior}} distrações</div>
    </div>
    <div class="comp-card">
      <div class="label">Tempo distraído na última semana registada</div>
      <div class="valor">${{comparacao.min_atual}} min</div>
      <div class="delta ${{classeS}}">${{setaS}} ${{Math.abs(comparacao.delta_seg)}}% face à semana anterior</div>
      <div class="sub">${{comparacao.label_atual}} · anterior (${{comparacao.label_anterior}}): ${{comparacao.min_anterior}} min</div>
    </div>`;
}}

// ── Meta diária ────────────────────────────────────────────
function atualizarMeta() {{
  const meta = parseInt(document.getElementById('meta-input').value) || 5;
  const valores = Object.values(dadosDiaMeta);
  const diasOk = valores.filter(v => v <= meta).length;
  const totalDias = valores.length;
  const pct = totalDias > 0 ? Math.round(diasOk / totalDias * 100) : 0;

  const fill = document.getElementById('meta-fill');
  fill.style.width = pct + '%';
  if (pct >= 70) fill.style.background = '#10b981';
  else if (pct >= 40) fill.style.background = '#f59e0b';
  else fill.style.background = '#f87171';

  document.getElementById('meta-texto').innerHTML =
    `Cumpriste a meta em <b>${{diasOk}} de ${{totalDias}} dias</b> (${{pct}}%). ` +
    (pct >= 70 ? 'Bom trabalho!' : pct >= 40 ? 'Vais no bom caminho.' : 'Há margem para melhorar.');
}}
atualizarMeta();

// ── Tabs ───────────────────────────────────────────────────
function mostrarTab(nome, btn) {{
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('tab-' + nome).classList.add('active');
  // Redimensionar gráficos (Chart.js não desenha bem se o painel estava escondido)
  setTimeout(() => {{
    if (nome === 'analise') {{
      graficoPrincipal.resize();
      if (graficoDetalhe) graficoDetalhe.resize();
      graficoDuracao.resize();
      graficoPeriodos.resize();
    }}
  }}, 50);
}}
</script>
</body>
</html>"""

    with open(DASHBOARD, 'w', encoding='utf-8') as f:
        f.write(html)
    return True

def monitorizar(porta):
    distracao_inicio = None
    total = 0
    inicio_sessao = datetime.now()
    duracoes_sessao = []
    print(verde(f"\nArduino detetado em {porta}"))
    print(bold("\n┌─────────────────────────────────────────┐"))
    print(bold("│   Sistema de Monitorização Ativo        │"))
    print(bold("│   Coloca o Arduino em cima do telemóvel │"))
    print(bold("│   Prima Ctrl+C para parar e ver o       │"))
    print(bold("│   dashboard                             │"))
    print(bold("└─────────────────────────────────────────┘\n"))
    try:
        with serial.Serial(porta, BAUDRATE, timeout=1) as ser:
            while True:
                linha = ser.readline().decode('utf-8').strip()
                if linha == "DISTRACAO_INICIO":
                    distracao_inicio = datetime.now()
                    total += 1
                    print(vermelho(f"  [{distracao_inicio.strftime('%H:%M:%S')}] Distração #{total} iniciada!"))
                elif linha == "DISTRACAO_FIM" and distracao_inicio:
                    fim = datetime.now()
                    duracao = (fim - distracao_inicio).seconds
                    duracoes_sessao.append(duracao)
                    print(verde(f"  [{fim.strftime('%H:%M:%S')}] Voltou a estudar. Duração: {duracao}s"))
                    wb = load_workbook(FICHEIRO)
                    ws = wb.active
                    ws.append([distracao_inicio.strftime('%Y-%m-%d'), distracao_inicio.strftime('%H:%M:%S'), fim.strftime('%H:%M:%S'), duracao])
                    wb.save(FICHEIRO)
                    distracao_inicio = None
    except KeyboardInterrupt:
        pass

    # ── Resumo da sessão ──────────────────────────────────
    fim_sessao = datetime.now()
    dur_sessao = int((fim_sessao - inicio_sessao).total_seconds())
    h_sessao = dur_sessao // 3600
    m_sessao = (dur_sessao % 3600) // 60
    total_distraido = sum(duracoes_sessao)
    media_sessao = total_distraido / len(duracoes_sessao) if duracoes_sessao else 0

    print(bold(azul("\n╔══════════════════════════════════════════════╗")))
    print(bold(azul("║             RESUMO DA SESSÃO                 ║")))
    print(bold(azul("╚══════════════════════════════════════════════╝")))
    print(f"  Duração da sessão:      {h_sessao}h {m_sessao}min")
    print(f"  Distrações detetadas:   {total}")
    print(f"  Tempo distraído:        {total_distraido // 60}min {total_distraido % 60}s")
    if duracoes_sessao:
        print(f"  Duração média:          {media_sessao:.0f}s")
        print(f"  Distração mais longa:   {max(duracoes_sessao)}s")
    if dur_sessao > 0:
        pct_focado = round((1 - total_distraido / dur_sessao) * 100)
        print(f"  Tempo focada:           {pct_focado}%")
        if pct_focado >= 90:
            print(verde("  Excelente sessão de estudo!"))
        elif pct_focado >= 75:
            print(amarelo("  Boa sessão, mas há margem para melhorar."))
        else:
            print(vermelho("  Sessão com muitas distrações."))
    print()

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(bold(azul("""
  ╔══════════════════════════════════════════════╗
  ║   Sistema de Deteção de Distração no Estudo  ║
  ║   Arduino Nano RP2040 Connect                ║
  ╚══════════════════════════════════════════════╝
""")))
    inicializar_excel()
    print(amarelo("\nÀ procura do Arduino..."))
    porta = detetar_porta()
    if not porta:
        print(vermelho("Arduino não encontrado. Verifica a ligação USB."))
        input("\nPrime Enter para sair...")
        sys.exit(1)
    try:
        monitorizar(porta)
    except Exception as e:
        print(vermelho(f"\nErro na monitorização: {e}"))
    print(amarelo("\nA gerar dashboard..."))
    if gerar_dashboard():
        print(verde("Dashboard gerado com sucesso!"))
        webbrowser.open(f"file:///{DASHBOARD.replace(os.sep, '/')}")
    else:
        print(vermelho("Não foi possível gerar o dashboard (sem dados)."))
    input("\nPrime Enter para sair...")

if __name__ == '__main__':
    main()
