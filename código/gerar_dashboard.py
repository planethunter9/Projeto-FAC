import json
from openpyxl import load_workbook
from datetime import datetime, timedelta
from collections import defaultdict

FICHEIRO = 'C:/Users/Inês/Desktop/uni/projeto de FAC/código/distrações.xlsx'

# Ler dados
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

# Organizar por dia
por_dia = defaultdict(list)
for d in dados:
    por_dia[d['data']].append(d)

# Organizar por semana
por_semana = defaultdict(list)
for d in dados:
    dt = datetime.strptime(d['data'], '%Y-%m-%d')
    semana = dt.strftime('%Y-W%W')
    por_semana[semana].append(d)

# Organizar por mes
por_mes = defaultdict(list)
for d in dados:
    mes = d['data'][:7]
    por_mes[mes].append(d)

# Dados para os graficos
dias = sorted(por_dia.keys())
semanas = sorted(por_semana.keys())
meses = sorted(por_mes.keys())

dados_por_dia = {d: len(por_dia[d]) for d in dias}
duracao_por_dia = {d: sum(x['duracao'] for x in por_dia[d]) for d in dias}

dados_por_semana = {s: len(por_semana[s]) for s in semanas}
dados_por_mes = {m: len(por_mes[m]) for m in meses}

# Por hora global
por_hora = defaultdict(int)
for d in dados:
    hora = int(d['hora_inicio'].split(':')[0])
    por_hora[hora] += 1

# Detalhes por dia para tabela
detalhes_json = json.dumps(por_dia)
dados_por_dia_json = json.dumps(dados_por_dia)
duracao_por_dia_json = json.dumps(duracao_por_dia)
dados_por_semana_json = json.dumps(dados_por_semana)
dados_por_mes_json = json.dumps(dados_por_mes)
por_hora_json = json.dumps(dict(sorted(por_hora.items())))

total = len(dados)
total_seg = sum(d['duracao'] for d in dados)
media = total_seg / total if total > 0 else 0
hora_pior = max(por_hora, key=por_hora.get) if por_hora else 0

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
  
  /* Cards */
  .cards {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }}
  .card {{ background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; }}
  .card .valor {{ font-size: 28px; font-weight: 700; margin-bottom: 4px; }}
  .card .label {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }}
  .card.red .valor {{ color: #f87171; }}
  .card.yellow .valor {{ color: #fbbf24; }}
  .card.blue .valor {{ color: #60a5fa; }}
  .card.purple .valor {{ color: #a78bfa; }}
  
  /* Filtros */
  .filtros {{ display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap; align-items: center; }}
  .filtros span {{ color: #94a3b8; font-size: 13px; margin-right: 4px; }}
  .btn {{ padding: 8px 16px; border-radius: 8px; border: 1px solid #334155; background: #1e293b;
          color: #94a3b8; cursor: pointer; font-size: 13px; transition: all 0.2s; }}
  .btn:hover {{ border-color: #60a5fa; color: #60a5fa; }}
  .btn.active {{ background: #2563eb; border-color: #2563eb; color: white; }}
  
  /* Graficos */
  .graficos-grid {{ display: grid; grid-template-columns: 2fr 1fr; gap: 16px; margin-bottom: 16px; }}
  .grafico-box {{ background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; }}
  .grafico-box h3 {{ font-size: 14px; color: #94a3b8; margin-bottom: 16px; text-transform: uppercase; letter-spacing: 0.05em; }}
  .grafico-box canvas {{ width: 100% !important; }}
  
  .graficos-grid2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }}
  
  /* Tabela */
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

  .semana-delta {{ font-size: 11px; margin-top: 4px; }}
  .semana-delta.up {{ color: #f87171; }}
  .semana-delta.down {{ color: #6ee7b7; }}
  .semana-delta.igual {{ color: #94a3b8; }}
</style>
</head>
<body>
<button class="toggle-theme" onclick="toggleTheme()">☀️ Light Mode</button>
<header>
  <h1>Dashboard de Distrações no Estudo</h1>
  <p>Sistema de monitorização com Arduino Nano RP2040 Connect</p>
</header>

<div class="container">

  <!-- Cards -->
  <div class="cards">
    <div class="card red">
      <div class="valor" id="card-total">{total}</div>
      <div class="label">Total de Distrações</div>
    </div>
    <div class="card yellow">
      <div class="valor" id="card-tempo">{total_seg // 3600}h {(total_seg % 3600) // 60}min</div>
      <div class="label">Tempo Total Distraído</div>
    </div>
    <div class="card blue">
      <div class="valor" id="card-media">{media:.0f}s</div>
      <div class="label">Duração Média</div>
    </div>
    <div class="card purple">
      <div class="valor">{hora_pior}h</div>
      <div class="label">Hora com mais distrações</div>
    </div>
  </div>

  <!-- Filtros de periodo -->
  <div class="filtros">
    <span>Ver por:</span>
    <button class="btn active" onclick="setVista('dia', this)">Dia</button>
    <button class="btn" onclick="setVista('semana', this)">Semana</button>
    <button class="btn" onclick="setVista('mes', this)">Mês</button>
  </div>

  <!-- Grafico principal + horas -->
  <div class="graficos-grid">
    <div class="grafico-box">
      <h3 id="titulo-principal">Distrações por Dia</h3>
      <canvas id="grafico-principal" height="120"></canvas>
    </div>
    <div class="grafico-box">
      <h3>A Que Horas Ocorrem?</h3>
      <canvas id="grafico-horas" height="120"></canvas>
    </div>
  </div>

  <!-- Grafico duracoes + semanas -->
  <div class="graficos-grid2">
    <div class="grafico-box">
      <h3>Tempo Total Distraído por Dia (minutos)</h3>
      <canvas id="grafico-duracao" height="120"></canvas>
    </div>
    <div class="grafico-box">
      <h3>Distrações por Semana</h3>
      <canvas id="grafico-semana" height="120"></canvas>
    </div>
  </div>

  <!-- Tabela detalhada -->
  <div class="tabela-box">
    <h3>Registo Detalhado</h3>
    <div class="filtro-dia">
      <select id="select-dia" onchange="atualizarTabela()">
        <option value="">-- Todos os dias --</option>
      </select>
      <select id="select-tipo" onchange="atualizarTabela()">
        <option value="">-- Todos os tipos --</option>
        <option value="curta">Rápida (&lt;30s)</option>
        <option value="media">Média (30s–2min)</option>
        <option value="longa">Longa (&gt;2min)</option>
      </select>
    </div>
    </div>
    <table>
      <thead>
        <tr>
          <th>Data</th>
          <th>Hora Início</th>
          <th>Hora Fim</th>
          <th>Duração</th>
          <th>Tipo</th>
        </tr>
      </thead>
      <tbody id="tabela-body"></tbody>
    </table>
  </div>

</div>

<script>
const dadosDia = {dados_por_dia_json};
const duracaoDia = {duracao_por_dia_json};
const dadosSemana = {dados_por_semana_json};
const dadosMes = {dados_por_mes_json};
const dadosHora = {por_hora_json};
const detalhes = {detalhes_json};

const CHART_OPTS = {{
  responsive: true,
  plugins: {{ legend: {{ display: false }} }},
  scales: {{
    x: {{ ticks: {{ color: '#94a3b8', font: {{ size: 11 }} }}, grid: {{ display: false }} }},
    y: {{ ticks: {{ color: '#94a3b8', font: {{ size: 11 }} }}, grid: {{ color: '#334155' }} }}
  }}
}};

// Grafico principal
const ctxP = document.getElementById('grafico-principal').getContext('2d');
let graficoPrincipal = new Chart(ctxP, {{
  type: 'bar',
  data: {{
    labels: Object.keys(dadosDia).map(d => formatarData(d)),
    datasets: [{{ data: Object.values(dadosDia), backgroundColor: '#3b82f6', borderRadius: 6 }}]
  }},
  options: CHART_OPTS
}});

// Grafico horas
const ctxH = document.getElementById('grafico-horas').getContext('2d');
new Chart(ctxH, {{
  type: 'bar',
  data: {{
    labels: Object.keys(dadosHora).map(h => h + 'h'),
    datasets: [{{ data: Object.values(dadosHora), backgroundColor: '#a78bfa', borderRadius: 6 }}]
  }},
  options: CHART_OPTS
}});

// Grafico duracoes
const ctxD = document.getElementById('grafico-duracao').getContext('2d');
new Chart(ctxD, {{
  type: 'line',
  data: {{
    labels: Object.keys(duracaoDia).map(d => formatarData(d)),
    datasets: [{{ 
      data: Object.values(duracaoDia).map(s => Math.round(s/60*10)/10),
      borderColor: '#f59e0b', backgroundColor: '#f59e0b22',
      fill: true, tension: 0.4, pointRadius: 4
    }}]
  }},
  options: CHART_OPTS
}});

// Grafico semana
const ctxS = document.getElementById('grafico-semana').getContext('2d');
const semanaVals = Object.values(dadosSemana);
const semanaKeys = Object.keys(dadosSemana);

const semanaColors = semanaVals.map((val, i) => {{
  if (i === 0) return '#10b981';
  return val > semanaVals[i-1] ? '#f87171' : '#10b981';
}});

const pluginDelta = {{
  id: 'deltaPlugin',
  afterDatasetsDraw(chart) {{
    const ctx = chart.ctx;
    ctx.save();
    ctx.font = 'bold 11px Segoe UI';
    ctx.textAlign = 'center';
    semanaVals.forEach((val, i) => {{
      if (i === 0) return;
      const anterior = semanaVals[i-1];
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

new Chart(ctxS, {{
  type: 'bar',
  data: {{
    labels: semanaKeys.map(s => 'Sem ' + s.split('W')[1]),
    datasets: [{{ data: semanaVals, backgroundColor: semanaColors, borderRadius: 6 }}]
  }},
  options: CHART_OPTS,
  plugins: [pluginDelta]
}});

// Vista dia/semana/mes
let vistaAtual = 'dia';
function setVista(vista, btn) {{
  vistaAtual = vista;
  document.querySelectorAll('.btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  
  let labels, valores, titulo;
  if (vista === 'dia') {{
    labels = Object.keys(dadosDia).map(d => formatarData(d));
    valores = Object.values(dadosDia);
    titulo = 'Distracoes por Dia';
  }} else if (vista === 'semana') {{
    labels = Object.keys(dadosSemana).map(s => 'Sem ' + s.split('W')[1]);
    valores = Object.values(dadosSemana);
    titulo = 'Distracoes por Semana';
  }} else {{
    labels = Object.keys(dadosMes);
    valores = Object.values(dadosMes);
    titulo = 'Distracoes por Mes';
  }}
  
  document.getElementById('titulo-principal').textContent = titulo;
  graficoPrincipal.data.labels = labels;
  graficoPrincipal.data.datasets[0].data = valores;
  graficoPrincipal.update();
}}

// Tabela
const select = document.getElementById('select-dia');
Object.keys(detalhes).sort().forEach(dia => {{
  const opt = document.createElement('option');
  opt.value = dia;
  opt.textContent = formatarData(dia);
  select.appendChild(opt);
}});

function toggleTheme() {{
  const isLight = document.body.classList.toggle('light');
  document.querySelector('.toggle-theme').textContent = isLight ? '🌙 Dark Mode' : '☀️ Light Mode';
}}

function atualizarTabela() {{
  const diaFiltro = document.getElementById('select-dia').value;
  const tipoFiltro = document.getElementById('select-tipo').value;
  const tbody = document.getElementById('tabela-body');
  tbody.innerHTML = '';
  
  let registos = [];
  if (diaFiltro) {{
    registos = detalhes[diaFiltro] || [];
  }} else {{
    Object.values(detalhes).forEach(arr => registos.push(...arr));
    registos.sort((a, b) => a.data.localeCompare(b.data) || a.hora_inicio.localeCompare(b.hora_inicio));
  }} 

   if (tipoFiltro) {{
    registos = registos.filter(r => {{
      const dur = r.duracao;
      if (tipoFiltro === 'curta') return dur < 30;
      if (tipoFiltro === 'media') return dur >= 30 && dur < 120;
      if (tipoFiltro === 'longa') return dur >= 120;
    }});
  }}
  
  registos.slice(0, 100).forEach(r => {{
    const dur = r.duracao;
    let badge, tipo;
    if (dur < 30) {{ badge = 'curta'; tipo = 'Rápida'; }}
    else if (dur < 120) {{ badge = 'media'; tipo = 'Média'; }}
    else {{ badge = 'longa'; tipo = 'Longa'; }}
    
    const mins = Math.floor(dur / 60);
    const segs = dur % 60;
    const durStr = mins > 0 ? `${{mins}}m ${{segs}}s` : `${{segs}}s`;
    
    tbody.innerHTML += `
      <tr>
        <td>${{formatarData(r.data)}}</td>
        <td>${{r.hora_inicio}}</td>
        <td>${{r.hora_fim}}</td>
        <td>${{durStr}}</td>
        <td><span class="badge ${{badge}}">${{tipo}}</span></td>
      </tr>`;
  }});
}}

function formatarData(d) {{
  const [ano, mes, dia] = d.split('-');
  return `${{dia}}/${{mes}}/${{ano}}`;
}}

atualizarTabela();
</script>
</body>
</html>"""

with open('dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Dashboard gerado: dashboard.html")
print(f"Total de registos: {total}")
