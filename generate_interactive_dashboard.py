"""
Generate a unified interactive HTML dashboard with Plotly for:
1. Interactive 3D Chart (Quality vs Latency vs Cost) - full mouse rotation
2. Interactive 2D Chart: Quality vs Execution Latency
3. Interactive 2D Chart: Quality vs Financial Cost

Data: resac2026/clean_suite_master.csv (the clean suite, built by
scripts/build_clean_suite_report.py), chart-eligible configs only. Before
2026-09-22 this read the frozen 31-model grok/minimax panel
(dss_benchmark_31models_13tasks.csv), now archived with its charts.
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def assign_provider(model_name: str) -> str:
    m = model_name.lower()
    if 'anthropic' in m or 'claude' in m:
        return 'Anthropic'
    elif 'google' in m or 'gemini' in m or 'gemma' in m:
        return 'Google'
    elif 'openai' in m or 'gpt' in m:
        return 'OpenAI'
    elif 'x-ai' in m or 'grok' in m:
        return 'xAI'
    elif 'deepseek' in m:
        return 'DeepSeek'
    elif 'meta' in m or 'llama' in m:
        return 'Meta'
    elif 'qwen' in m:
        return 'Qwen'
    elif 'mistral' in m:
        return 'Mistral'
    else:
        return 'Other Open-Weights'

provider_colors = {
    'Anthropic': '#7c3aed',
    'Google': '#2563eb',
    'OpenAI': '#059669',
    'xAI': '#dc2626',
    'DeepSeek': '#0891b2',
    'Meta': '#ea580c',
    'Qwen': '#d97706',
    'Mistral': '#4f46e5',
    'Other Open-Weights': '#64748b'
}

def clean_model_label(model: str) -> str:
    m = model.split('/')[-1]
    return m.replace('-preview', '').replace('-thinking', ' (th)')

master = pd.read_csv("resac2026/clean_suite_master.csv")
master = master[master["included"]]          # same coverage/replay gates as the PNG charts
df = pd.DataFrame({
    "Model": master["config"],                 # model + effort: one point per config
    "Consensus Avg Score": master["quality"],
    "Avg Latency / Task (s)": master["avg_latency_s"],
    "Avg Cost / Task ($)": master["avg_cost_usd"],
    "Total Latency (s)": master["total_latency_s"],
    "Total Cost ($)": master["total_cost_usd"],
})
N = len(df)
df['Provider'] = df['Model'].apply(assign_provider)
df['Color'] = df['Provider'].map(provider_colors)
df['Label'] = df['Model'].apply(clean_model_label)

# Filter dataframe for charts where latency is plotted
df_valid_lat = df.dropna(subset=['Avg Latency / Task (s)']).copy()
df_valid_lat = df_valid_lat[df_valid_lat['Avg Latency / Task (s)'] > 0]

# 1. 3D Plot
fig3d = go.Figure()
for provider in df_valid_lat['Provider'].unique():
    sub = df_valid_lat[df_valid_lat['Provider'] == provider]
    custom_data = np.stack((
        sub['Model'],
        sub['Consensus Avg Score'],
        sub['Avg Latency / Task (s)'],
        sub['Avg Cost / Task ($)'],
        sub['Total Latency (s)'],
        sub['Total Cost ($)']
    ), axis=-1)
    
    fig3d.add_trace(go.Scatter3d(
        x=sub['Avg Latency / Task (s)'],
        y=sub['Avg Cost / Task ($)'],
        z=sub['Consensus Avg Score'],
        mode='markers+text',
        name=provider,
        text=sub['Label'],
        textposition='top center',
        textfont=dict(size=9, color="#1e293b"),
        marker=dict(
            size=7,
            color=provider_colors.get(provider, '#64748b'),
            opacity=0.9,
            line=dict(width=1, color='white')
        ),
        customdata=custom_data,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br><br>"
            "🏆 <b>Quality Score:</b> %{customdata[1]:.1f} / 100<br>"
            "⏱️ <b>Avg Latency:</b> %{customdata[2]:.1f} s / task<br>"
            "💰 <b>Avg Cost:</b> $%{customdata[3]:.4f} / task<br>"
            "📊 <b>Total Benchmark Cost:</b> $%{customdata[5]:.3f}<br>"
            "<extra></extra>"
        )
    ))

fig3d.update_layout(
    title=dict(
        text=f"<b>Interactive 3D Pareto Frontier: Score vs. Latency vs. Cost ({N} configs)</b><br><span style='font-size:12px; color:#64748b;'>Rotate with mouse (left-click drag) · Pan (right-click drag) · Zoom (scroll)</span>",
        x=0.02, y=0.96
    ),
    scene=dict(
        xaxis=dict(title='Avg Latency (s)', backgroundcolor="#f8fafc", gridcolor="#e2e8f0"),
        yaxis=dict(title='Avg Cost ($ / Task)', backgroundcolor="#f8fafc", gridcolor="#e2e8f0"),
        zaxis=dict(title='Consensus Score (0-100)', backgroundcolor="#f8fafc", gridcolor="#e2e8f0"),
        camera=dict(eye=dict(x=-1.7, y=-1.7, z=1.3))
    ),
    margin=dict(l=0, r=0, b=0, t=55),
    legend=dict(x=0.85, y=0.88, bgcolor="rgba(255, 255, 255, 0.85)"),
    paper_bgcolor="#ffffff",
    font=dict(family="system-ui, -apple-system, sans-serif"),
    height=620
)

# 2. 2D Quality vs Latency
fig2d_time = go.Figure()
for provider in df_valid_lat['Provider'].unique():
    sub = df_valid_lat[df_valid_lat['Provider'] == provider]
    custom_data = np.stack((
        sub['Model'], sub['Consensus Avg Score'], sub['Avg Latency / Task (s)'], sub['Avg Cost / Task ($)']
    ), axis=-1)
    
    fig2d_time.add_trace(go.Scatter(
        x=sub['Avg Latency / Task (s)'],
        y=sub['Consensus Avg Score'],
        mode='markers+text',
        name=provider,
        text=sub['Label'],
        textposition='top right',
        textfont=dict(size=10, color="#1e293b"),
        marker=dict(
            size=12,
            color=provider_colors.get(provider, '#64748b'),
            opacity=0.85,
            line=dict(width=1.5, color='white')
        ),
        customdata=custom_data,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br><br>"
            "🏆 <b>Quality Score:</b> %{customdata[1]:.1f} / 100<br>"
            "⏱️ <b>Avg Latency:</b> %{customdata[2]:.1f} s<br>"
            "💰 <b>Avg Cost:</b> $%{customdata[3]:.4f}<br>"
            "<extra></extra>"
        )
    ))

fig2d_time.update_layout(
    title=dict(text=f"<b>Quality Score vs. Execution Latency ({N} configs)</b>", x=0.02, y=0.96),
    xaxis=dict(title='<b>Average Latency per Task (Seconds)</b> — Lower is Faster', gridcolor="#e2e8f0"),
    yaxis=dict(title='<b>Consensus Score (0–100)</b> — Higher is Better', gridcolor="#e2e8f0", range=[40, 90]),
    margin=dict(l=50, r=20, b=50, t=55),
    legend=dict(x=0.85, y=0.15, bgcolor="rgba(255, 255, 255, 0.85)"),
    paper_bgcolor="#ffffff",
    plot_bgcolor="#f8fafc",
    font=dict(family="system-ui, -apple-system, sans-serif"),
    height=550
)

# 3. 2D Quality vs Cost
fig2d_cost = go.Figure()
for provider in df['Provider'].unique():
    sub = df[df['Provider'] == provider]
    custom_data = np.stack((
        sub['Model'], sub['Consensus Avg Score'], sub['Avg Latency / Task (s)'], sub['Avg Cost / Task ($)']
    ), axis=-1)
    
    fig2d_cost.add_trace(go.Scatter(
        x=sub['Avg Cost / Task ($)'],
        y=sub['Consensus Avg Score'],
        mode='markers+text',
        name=provider,
        text=sub['Label'],
        textposition='top right',
        textfont=dict(size=10, color="#1e293b"),
        marker=dict(
            size=12,
            color=provider_colors.get(provider, '#64748b'),
            opacity=0.85,
            line=dict(width=1.5, color='white')
        ),
        customdata=custom_data,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br><br>"
            "🏆 <b>Quality Score:</b> %{customdata[1]:.1f} / 100<br>"
            "💰 <b>Avg Cost:</b> $%{customdata[3]:.4f} / task<br>"
            "⏱️ <b>Avg Latency:</b> %{customdata[2]:.1f} s<br>"
            "<extra></extra>"
        )
    ))

fig2d_cost.update_layout(
    title=dict(text=f"<b>Quality Score vs. Financial Cost ({N} configs, Log Scale)</b>", x=0.02, y=0.96),
    xaxis=dict(title='<b>Average Cost per Task (USD, Log Scale)</b> — Lower is Cheaper', type='log', gridcolor="#e2e8f0"),
    yaxis=dict(title='<b>Consensus Score (0–100)</b> — Higher is Better', gridcolor="#e2e8f0", range=[40, 90]),
    margin=dict(l=50, r=20, b=50, t=55),
    legend=dict(x=0.85, y=0.15, bgcolor="rgba(255, 255, 255, 0.85)"),
    paper_bgcolor="#ffffff",
    plot_bgcolor="#f8fafc",
    font=dict(family="system-ui, -apple-system, sans-serif"),
    height=550
)

# Convert all three to embeddable HTML divs
div_3d = fig3d.to_html(include_plotlyjs=False, full_html=False)
div_2d_time = fig2d_time.to_html(include_plotlyjs=False, full_html=False)
div_2d_cost = fig2d_cost.to_html(include_plotlyjs=False, full_html=False)

full_dashboard = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Scholarly Editing Benchmark - Interactive Charts</title>
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <style>
        body {{
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f1f5f9;
            color: #0f172a;
        }}
        .dashboard-container {{
            max-width: 1200px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            padding: 24px;
        }}
        .tab-nav {{
            display: flex;
            gap: 12px;
            border-bottom: 2px solid #e2e8f0;
            margin-bottom: 20px;
            padding-bottom: 8px;
        }}
        .tab-btn {{
            background: none;
            border: none;
            padding: 10px 18px;
            font-size: 15px;
            font-weight: 600;
            color: #64748b;
            cursor: pointer;
            border-radius: 8px;
            transition: all 0.2s ease;
        }}
        .tab-btn:hover {{
            background: #f8fafc;
            color: #0f172a;
        }}
        .tab-btn.active {{
            background: #eff6ff;
            color: #2563eb;
            border-bottom: 3px solid #2563eb;
        }}
        .chart-tab {{
            display: none;
        }}
        .chart-tab.active {{
            display: block;
        }}
        .chart-caption {{
            margin-top: 14px;
            font-size: 13.5px;
            color: #475569;
            background: #f8fafc;
            padding: 12px 16px;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
        }}
    </style>
</head>
<body>
    <div class="dashboard-container">
        <h2 style="margin-top:0; color:#1e293b;">Digital Scholarly Editing AI Benchmark — Interactive Explorer</h2>
        <div class="tab-nav">
            <button class="tab-btn active" onclick="switchTab('tab-3d', this)">🌐 Interactive 3D Chart (Mouse Orbit)</button>
            <button class="tab-btn" onclick="switchTab('tab-time', this)">⏱️ Quality vs. Execution Latency (2D)</button>
            <button class="tab-btn" onclick="switchTab('tab-cost', this)">💰 Quality vs. Financial Cost (2D)</button>
        </div>

        <div id="tab-3d" class="chart-tab active">
            {div_3d}
            <div class="chart-caption">
                <strong>How to interact:</strong> Left-click and drag to rotate the 3D space. Right-click and drag to pan across the axes. Scroll up/down to zoom in on clusters. Hover over any point to view exact score, latency, and cost statistics.
            </div>
        </div>

        <div id="tab-time" class="chart-tab">
            {div_2d_time}
            <div class="chart-caption">
                <strong>Data:</strong> clean suite (<code>resac2026/clean_suite_master.csv</code>), chart-eligible configs only; one point per model × reasoning effort. Hover a point for details; Pareto frontiers are in <code>clean_chart_pareto_*.png</code>.
            </div>
        </div>

        <div id="tab-cost" class="chart-tab">
            {div_2d_cost}
            <div class="chart-caption">
                <strong>Data:</strong> clean suite (<code>resac2026/clean_suite_master.csv</code>), chart-eligible configs only; one point per model × reasoning effort. Hover a point for details; Pareto frontiers are in <code>clean_chart_pareto_*.png</code>.
            </div>
        </div>
    </div>

    <script>
        function switchTab(tabId, btn) {{
            document.querySelectorAll('.chart-tab').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            btn.classList.add('active');
            window.dispatchEvent(new Event('resize'));
        }}
    </script>
</body>
</html>
"""

with open("resac2026/interactive_charts_dashboard.html", "w", encoding="utf-8") as f:
    f.write(full_dashboard)

print("Saved: resac2026/interactive_charts_dashboard.html")
