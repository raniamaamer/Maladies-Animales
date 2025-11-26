import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import os

# ============================================
# CHARGEMENT ET NETTOYAGE DES DONNÉES
# ============================================

def load_and_clean_data():
    """Charge et nettoie le dataset en gérant les erreurs"""
    
    file_path = 'output/animal_diseases_dataset.csv'
    if not os.path.exists(file_path):
        print(f"❌ Fichier introuvable : {file_path}")
        return None
    
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    print(f"✅ {len(df)} entrées chargées")
    
    df_valid = df[df['langue'] != 'N/A'].copy()
    df_errors = df[df['langue'] == 'N/A'].copy()
    
    print(f"✅ Entrées valides : {len(df_valid)}")
    print(f"⚠️  Entrées en erreur : {len(df_errors)}")
    
    if len(df_valid) == 0:
        print("❌ Aucune donnée valide à afficher")
        return None
    
    df_valid['langue'] = df_valid['langue'].fillna('Non détecté')
    df_valid['source_type'] = df_valid['source_type'].fillna('Non classé')
    df_valid['maladie'] = df_valid['maladie'].fillna('Non identifiée')
    df_valid['lieu'] = df_valid['lieu'].fillna('Non spécifié')
    df_valid['nb_mots'] = pd.to_numeric(df_valid['nb_mots'], errors='coerce').fillna(0)
    df_valid['nb_caracteres'] = pd.to_numeric(df_valid['nb_caracteres'], errors='coerce').fillna(0)
    df_valid = df_valid.drop_duplicates(subset=['url'])
    
    print(f"✅ Dataset nettoyé : {len(df_valid)} entrées")
    return df_valid

# ============================================
# APPLICATION DASH
# ============================================

df = load_and_clean_data()

if df is None or len(df) == 0:
    print("\n" + "="*70)
    print("❌ ERREUR : Impossible de démarrer le dashboard")
    print("="*70)
    exit(1)

app = Dash(__name__)

# Ajouter le CSS externe pour le responsive
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            @media (max-width: 768px) {
                .sidebar {
                    position: relative !important;
                    width: 100% !important;
                    height: auto !important;
                    margin-bottom: 20px !important;
                }
                .main-content {
                    margin-left: 0 !important;
                    padding: 10px !important;
                }
                .kpi-box {
                    width: 48% !important;
                    margin: 1% !important;
                    padding: 15px !important;
                    font-size: 12px !important;
                }
                .kpi-box h2 {
                    font-size: 32px !important;
                }
                .kpi-box p {
                    font-size: 12px !important;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Layout RESPONSIVE
app.layout = html.Div([
    
    # Sidebar (Filtres)
    html.Div([
        html.Div([
            html.H2(
                "🔍 Filtres",
                style={
                    'color': '#ffffff',
                    'textAlign': 'center',
                    'marginBottom': '20px',
                    'fontSize': '20px'
                }
            ),
            
            # Filtre Langue
            html.Div([
                html.Label("🌍 Langue", style={'fontWeight': 'bold', 'marginBottom': '8px', 'color': '#ffffff', 'fontSize': '14px'}),
                dcc.Dropdown(
                    id='langue-filter',
                    options=[{'label': '📋 Toutes', 'value': 'all'}] + 
                            [{'label': lang, 'value': lang} for lang in sorted(df['langue'].unique())],
                    value='all',
                    clearable=False,
                    style={'fontSize': '14px'}
                ),
            ], style={'marginBottom': '20px'}),
            
            # Filtre Source
            html.Div([
                html.Label("📰 Source", style={'fontWeight': 'bold', 'marginBottom': '8px', 'color': '#ffffff', 'fontSize': '14px'}),
                dcc.Dropdown(
                    id='source-filter',
                    options=[{'label': '📋 Toutes', 'value': 'all'}] + 
                            [{'label': src, 'value': src} for src in sorted(df['source_type'].unique())],
                    value='all',
                    clearable=False,
                    style={'fontSize': '14px'}
                ),
            ], style={'marginBottom': '20px'}),
            
            # Filtre Lieu
            html.Div([
                html.Label("📍 Lieu", style={'fontWeight': 'bold', 'marginBottom': '8px', 'color': '#ffffff', 'fontSize': '14px'}),
                dcc.Dropdown(
                    id='lieu-filter',
                    options=[{'label': '📋 Tous', 'value': 'all'}] + 
                            [{'label': lieu, 'value': lieu} for lieu in sorted(df['lieu'].unique())],
                    value='all',
                    clearable=False,
                    style={'fontSize': '14px'}
                ),
            ], style={'marginBottom': '20px'}),
            
            # Filtre Maladie
            html.Div([
                html.Label("🦠 Maladie", style={'fontWeight': 'bold', 'marginBottom': '8px', 'color': '#ffffff', 'fontSize': '14px'}),
                dcc.Dropdown(
                    id='maladie-filter',
                    options=[{'label': '📋 Toutes', 'value': 'all'}] + 
                            [{'label': mal, 'value': mal} for mal in sorted(df['maladie'].unique())],
                    value='all',
                    clearable=False,
                    style={'fontSize': '14px'}
                ),
            ], style={'marginBottom': '20px'}),
            
        ], style={'padding': '20px'})
        
    ], className='sidebar', style={
        'position': 'fixed',
        'left': '0',
        'top': '0',
        'width': '280px',
        'height': '100vh',
        'background': 'linear-gradient(180deg, #667eea 0%, #764ba2 100%)',
        'overflowY': 'auto',
        'boxShadow': '2px 0 10px rgba(0,0,0,0.1)',
        'zIndex': '1000'
    }),
    
    # Contenu Principal
    html.Div([
        
        # En-tête
        html.Div([
            html.H1(
                "📊 Dashboard - Maladies Animales",
                style={
                    'textAlign': 'center',
                    'color': '#2c3e50',
                    'padding': '20px',
                    'margin': '0',
                    'fontSize': '24px'
                }
            ),
            html.P(
                f"📈 {len(df)} articles analysés",
                style={
                    'textAlign': 'center',
                    'color': '#7f8c8d',
                    'marginTop': '-10px',
                    'paddingBottom': '15px',
                    'fontSize': '14px'
                }
            )
        ], style={'backgroundColor': '#f8f9fa', 'borderRadius': '0 0 15px 15px', 'marginBottom': '15px'}),
        
        # KPIs
        html.Div(id='kpis', style={'padding': '10px'}),
        
        # Graphiques
        html.Div([dcc.Graph(id='langue-chart')], style={'padding': '10px', 'marginBottom': '15px'}),
        html.Div([dcc.Graph(id='source-chart')], style={'padding': '10px', 'marginBottom': '15px'}),
        html.Div([dcc.Graph(id='maladie-chart')], style={'padding': '10px', 'marginBottom': '15px'}),
        html.Div([dcc.Graph(id='lieu-chart')], style={'padding': '10px', 'marginBottom': '15px'}),
        html.Div([dcc.Graph(id='stats-chart')], style={'padding': '10px'}),
        
        # Footer
        html.Div([
            html.P(
                "🦠 Dashboard Maladies Animales",
                style={'textAlign': 'center', 'color': '#7f8c8d', 'padding': '15px', 'fontSize': '12px'}
            )
        ])
        
    ], className='main-content', style={
        'marginLeft': '280px',
        'padding': '10px',
        'backgroundColor': '#ffffff',
        'minHeight': '100vh'
    })
    
], style={
    'fontFamily': 'Arial, sans-serif',
    'backgroundColor': '#f5f5f5'
})

# ============================================
# CALLBACKS
# ============================================

@app.callback(
    [
        Output('kpis', 'children'),
        Output('langue-chart', 'figure'),
        Output('source-chart', 'figure'),
        Output('maladie-chart', 'figure'),
        Output('lieu-chart', 'figure'),
        Output('stats-chart', 'figure')
    ],
    [
        Input('langue-filter', 'value'),
        Input('source-filter', 'value'),
        Input('lieu-filter', 'value'),
        Input('maladie-filter', 'value')
    ]
)
def update_dashboard(selected_langue, selected_source, selected_lieu, selected_maladie):
    """Met à jour tous les composants du dashboard"""
    
    filtered_df = df.copy()
    
    if selected_langue != 'all':
        filtered_df = filtered_df[filtered_df['langue'] == selected_langue]
    if selected_source != 'all':
        filtered_df = filtered_df[filtered_df['source_type'] == selected_source]
    if selected_lieu != 'all':
        filtered_df = filtered_df[filtered_df['lieu'] == selected_lieu]
    if selected_maladie != 'all':
        filtered_df = filtered_df[filtered_df['maladie'] == selected_maladie]
    
    if len(filtered_df) == 0:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="Aucune donnée",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="gray")
        )
        empty_fig.update_layout(height=300)
        empty_kpis = html.Div([
            html.P("⚠️ Aucune donnée", style={'textAlign': 'center', 'color': '#e74c3c'})
        ])
        return empty_kpis, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig
    
    # KPIs RESPONSIVE
    kpi_style_base = {
        'display': 'inline-block',
        'width': '23%',
        'textAlign': 'center',
        'margin': '5px',
        'padding': '20px',
        'borderRadius': '12px',
        'boxShadow': '0 3px 6px rgba(0,0,0,0.1)',
    }
    
    kpis = html.Div([
        html.Div([
            html.H2(f"{len(filtered_df)}", style={'color': '#fff', 'margin': '0', 'fontSize': '40px'}),
            html.P("Articles", style={'margin': '5px', 'color': '#fff', 'fontSize': '14px'})
        ], className='kpi-box', style={**kpi_style_base, 'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'}),
        
        html.Div([
            html.H2(f"{filtered_df['nb_mots'].mean():.0f}", style={'color': '#fff', 'margin': '0', 'fontSize': '40px'}),
            html.P("Mots moy.", style={'margin': '5px', 'color': '#fff', 'fontSize': '14px'})
        ], className='kpi-box', style={**kpi_style_base, 'background': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'}),
        
        html.Div([
            html.H2(f"{filtered_df['maladie'].nunique()}", style={'color': '#fff', 'margin': '0', 'fontSize': '40px'}),
            html.P("Maladies", style={'margin': '5px', 'color': '#fff', 'fontSize': '14px'})
        ], className='kpi-box', style={**kpi_style_base, 'background': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'}),
        
        html.Div([
            html.H2(f"{filtered_df['lieu'].nunique()}", style={'color': '#fff', 'margin': '0', 'fontSize': '40px'}),
            html.P("Lieux", style={'margin': '5px', 'color': '#fff', 'fontSize': '14px'})
        ], className='kpi-box', style={**kpi_style_base, 'background': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'}),
    ], style={'textAlign': 'center', 'flexWrap': 'wrap'})
    
    # Graphiques avec config mobile-friendly
    config = {'displayModeBar': False, 'responsive': True}
    
    # 1. Langue (Pie)
    langue_counts = filtered_df['langue'].value_counts()
    langue_fig = px.pie(
        values=langue_counts.values,
        names=langue_counts.index,
        title='🌍 Répartition par langue',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    langue_fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=10)
    langue_fig.update_layout(height=400, showlegend=True, title_font_size=16)
    
    # 2. Source (Bar)
    source_counts = filtered_df['source_type'].value_counts()
    source_fig = px.bar(
        x=source_counts.index,
        y=source_counts.values,
        title='📰 Type de source',
        labels={'x': 'Source', 'y': 'Articles'},
        color=source_counts.values,
        color_continuous_scale='Viridis',
        text=source_counts.values
    )
    source_fig.update_traces(textposition='outside')
    source_fig.update_layout(height=350, showlegend=False, xaxis_tickangle=-45, title_font_size=16)
    
    # 3. Maladies (Horizontal Bar)
    maladie_counts = filtered_df['maladie'].value_counts().head(10)
    maladie_fig = px.bar(
        x=maladie_counts.values,
        y=maladie_counts.index,
        orientation='h',
        title='🦠 Top 10 Maladies',
        labels={'x': 'Articles', 'y': 'Maladie'},
        color=maladie_counts.values,
        color_continuous_scale='Reds',
        text=maladie_counts.values
    )
    maladie_fig.update_traces(textposition='outside')
    maladie_fig.update_layout(height=400, showlegend=False, title_font_size=16)
    
    # 4. Lieux (Horizontal Bar)
    lieu_counts = filtered_df['lieu'].value_counts().head(10)
    lieu_fig = px.bar(
        x=lieu_counts.values,
        y=lieu_counts.index,
        orientation='h',
        title='📍 Top 10 Lieux',
        labels={'x': 'Articles', 'y': 'Lieu'},
        color=lieu_counts.values,
        color_continuous_scale='Blues',
        text=lieu_counts.values
    )
    lieu_fig.update_traces(textposition='outside')
    lieu_fig.update_layout(height=400, showlegend=False, title_font_size=16)
    
    # 5. Stats (Box Plot)
    stats_fig = go.Figure()
    stats_fig.add_trace(go.Box(y=filtered_df['nb_mots'], name='Mots', marker_color='#3498db', boxmean='sd'))
    stats_fig.add_trace(go.Box(y=filtered_df['nb_caracteres']/100, name='Chars (÷100)', marker_color='#e74c3c', boxmean='sd'))
    stats_fig.update_layout(title='📊 Distribution', yaxis_title='Valeur', height=350, showlegend=True, title_font_size=16)
    
    return kpis, langue_fig, source_fig, maladie_fig, lieu_fig, stats_fig

# ============================================
# LANCEMENT
# ============================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 DASHBOARD MOBILE-FRIENDLY")
    print("="*70)
    print(f"✅ {len(df)} articles chargés")
    print("\n📊 Accès :")
    print("   PC: http://127.0.0.1:8050/")
    print("   Mobile: http://192.168.1.29:8050/")
    print("\n⌨️  Ctrl+C pour arrêter")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=8050)