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
  .graficos-grid2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; align-items: stretch; }}
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
    background: #1e293b; color: #e2e8f0; cursor: pointer; font-size: 13px; }}
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
</style>
</head>
<body>
<button class="toggle-theme" onclick="toggleTheme()">☀️ Light Mode</button>
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
  <div class="filtros">
    <span>Ver por:</span>
    <button class="btn active" onclick="setVista('dia', this)">Dia</button>
    <button class="btn" onclick="setVista('semana', this)">Semana</button>
    <button class="btn" onclick="setVista('mes', this)">Mês</button>
  </div>
  <div class="graficos-grid">
    <div class="grafico-box">
      <h3 id="titulo-principal">Distrações por Dia</h3>
      <div class="grafico-hint" id="hint-principal">💡 Clica numa barra para ver o detalhe</div>
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
    <div class="grafico-box"><h3>Tempo Total Distraído por Dia (minutos)</h3><canvas id="grafico-duracao" height="120"></canvas></div>
    <div class="grafico-box" style="display:flex; flex-direction:column; justify-content:center;"><h3>Distribuição por Período do Dia</h3><div style="height: 250px;"><canvas id="grafico-periodos"></canvas></div></div>
      </div>
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

let vistaAtual = 'dia';
let selecaoAtual = null;

const CHART_OPTS = {{
  responsive: true,
  plugins: {{ legend: {{ display: false }} }},
  scales: {{
    x: {{ offset: true, ticks: {{ color: '#94a3b8', font: {{ size: 11 }} }}, grid: {{ display: false }} }},
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
new Chart(ctxDur, {{
  type: 'line',
  data: {{ labels: Object.keys(duracaoDia).map(d => formatarData(d)), datasets: [{{ data: Object.values(duracaoDia).map(s => Math.round(s/60*10)/10), borderColor: '#f59e0b', backgroundColor: '#f59e0b22', fill: true, tension: 0.4, pointRadius: 4 }}] }},
  options: CHART_OPTS
}});

// ── Gráfico circular períodos ──────────────────────────────
const ctxPer = document.getElementById('grafico-periodos').getContext('2d');
new Chart(ctxPer, {{
  type: 'doughnut',
  data: {{
    labels: Object.keys(periodos),
    datasets: [{{ data: Object.values(periodos), backgroundColor: ['#60a5fa','#f59e0b','#f87171','#a78bfa'], borderWidth: 0 }}]
  }},
  options: {{
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{
      legend: {{ display: true, position: 'bottom', labels: {{ color: '#94a3b8', font: {{ size: 11 }}, padding: 12 }} }},
      tooltip: {{ callbacks: {{ label: (ctx) => ` ${{ctx.label.replace('\\n',' ')}}: ${{ctx.raw}} distrações` }} }}
    }}
  }}
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

function toggleTheme() {{
  const isLight = document.body.classList.toggle('light');
  document.querySelector('.toggle-theme').textContent = isLight ? '🌙 Dark Mode' : '☀️ Light Mode';
}}

atualizarTabela();
</script>
</body>
</html>"""

    with open(DASHBOARD, 'w', encoding='utf-8') as f:
        f.write(html)
    return True

def monitorizar(porta):
    distracao_inicio = None
    total = 0
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
                    print(verde(f"  [{fim.strftime('%H:%M:%S')}] Voltou a estudar. Duração: {duracao}s"))
                    wb = load_workbook(FICHEIRO)
                    ws = wb.active
                    ws.append([distracao_inicio.strftime('%Y-%m-%d'), distracao_inicio.strftime('%H:%M:%S'), fim.strftime('%H:%M:%S'), duracao])
                    wb.save(FICHEIRO)
                    distracao_inicio = None
    except KeyboardInterrupt:
        pass

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
