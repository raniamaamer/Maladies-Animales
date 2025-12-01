import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output
import os
from pathlib import Path

# ============================================
# CONFIGURATION
# ============================================

# Chemins des fichiers
OUTPUT_FILE = "data/output/output_dataset.csv"

# ============================================
# CHARGEMENT ET NETTOYAGE DES DONNÉES
# ============================================

def load_and_clean_data():
    """Charge et nettoie le dataset en gérant les erreurs"""
    
    # Essayer les deux chemins possibles
    file_path = OUTPUT_FILE if os.path.exists(OUTPUT_FILE) else FALLBACK_FILE
    
    if not os.path.exists(file_path):
        print(f"❌ Fichier introuvable : {file_path}")
        print(f"   Assurez-vous d'avoir lancé le scraping avec : python main.py")
        return None
    
    print(f"📂 Chargement de : {file_path}")
    
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        print(f"✅ {len(df)} entrées chargées")
    except Exception as e:
        print(f"❌ Erreur lors du chargement : {e}")
        return None
    
    # Filtrer les erreurs
    df_valid = df[
        (df['langue'] != 'N/A') & 
        (df['langue'].notna()) & 
        (df['contenu'] != 'Erreur lors du scraping')
    ].copy()
    
    df_errors = df[
        (df['langue'] == 'N/A') | 
        (df['langue'].isna()) | 
        (df['contenu'] == 'Erreur lors du scraping')
    ].copy()
    
    print(f"✅ Entrées valides : {len(df_valid)}")
    print(f"⚠️  Entrées en erreur : {len(df_errors)}")
    
    if len(df_valid) == 0:
        print("❌ Aucune donnée valide à afficher")
        return None
    
    # Nettoyage et standardisation
    df_valid['langue'] = df_valid['langue'].fillna('Non détecté')
    df_valid['source_publication'] = df_valid['source_publication'].fillna('Non classé')
    df_valid['maladie'] = df_valid['maladie'].fillna('Non identifiée')
    df_valid['animal'] = df_valid['animal'].fillna('Non spécifié')
    df_valid['lieu'] = df_valid['lieu'].fillna('Non spécifié')
    df_valid['date_publication'] = df_valid['date_publication'].fillna('inconnue')
    
    # Convertir les nombres
    df_valid['nb_mots'] = pd.to_numeric(df_valid['nb_mots'], errors='coerce').fillna(0).astype(int)
    df_valid['nb_caracteres'] = pd.to_numeric(df_valid['nb_caracteres'], errors='coerce').fillna(0).astype(int)
    
    # Supprimer les doublons
    df_valid = df_valid.drop_duplicates(subset=['url'])
    
    print(f"✅ Dataset nettoyé : {len(df_valid)} entrées uniques")
    return df_valid

# ============================================
# CHARGEMENT DES DONNÉES
# ============================================

df = load_and_clean_data()

if df is None or len(df) == 0:
    print("\n" + "="*70)
    print("❌ ERREUR : Impossible de démarrer le dashboard")
    print("="*70)
    print("\n💡 SOLUTION :")
    print("   1. Lancez d'abord le scraping : python main.py")
    print("   2. Vérifiez que le fichier existe : data/output/output_dataset.csv")
    print("="*70 + "\n")
    exit(1)

# ============================================
# APPLICATION DASH
# ============================================

app = Dash(__name__)
app.title = "Dashboard Maladies Animales"

# CSS personnalisé pour le responsive
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            * {
                box-sizing: border-box;
            }
            body {
                margin: 0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
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
                }
                .kpi-box h2 {
                    font-size: 28px !important;
                }
                .kpi-box p {
                    font-size: 11px !important;
                }
            }
            @media (max-width: 480px) {
                .kpi-box {
                    width: 100% !important;
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

# ============================================
# LAYOUT
# ============================================

app.layout = html.Div([
    
    # Sidebar (Filtres)
    html.Div([
        html.Div([
            html.H2(
                "🔍 Filtres",
                style={
                    'color': '#ffffff',
                    'textAlign': 'center',
                    'marginBottom': '25px',
                    'fontSize': '22px',
                    'fontWeight': 'bold'
                }
            ),
            
            # Filtre Langue
            html.Div([
                html.Label("🌍 Langue", style={
                    'fontWeight': 'bold',
                    'marginBottom': '8px',
                    'color': '#ffffff',
                    'fontSize': '14px',
                    'display': 'block'
                }),
                dcc.Dropdown(
                    id='langue-filter',
                    options=[{'label': '📋 Toutes les langues', 'value': 'all'}] + 
                            [{'label': f"{lang} ({len(df[df['langue']==lang])})", 'value': lang} 
                             for lang in sorted(df['langue'].unique())],
                    value='all',
                    clearable=False,
                    style={'fontSize': '14px'}
                ),
            ], style={'marginBottom': '20px'}),
            
            # Filtre Source
            html.Div([
                html.Label("📰 Type de source", style={
                    'fontWeight': 'bold',
                    'marginBottom': '8px',
                    'color': '#ffffff',
                    'fontSize': '14px',
                    'display': 'block'
                }),
                dcc.Dropdown(
                    id='source-filter',
                    options=[{'label': '📋 Toutes les sources', 'value': 'all'}] + 
                            [{'label': f"{src} ({len(df[df['source_publication']==src])})", 'value': src} 
                             for src in sorted(df['source_publication'].unique())],
                    value='all',
                    clearable=False,
                    style={'fontSize': '14px'}
                ),
            ], style={'marginBottom': '20px'}),
            
            # Filtre Lieu
            html.Div([
                html.Label("📍 Lieu", style={
                    'fontWeight': 'bold',
                    'marginBottom': '8px',
                    'color': '#ffffff',
                    'fontSize': '14px',
                    'display': 'block'
                }),
                dcc.Dropdown(
                    id='lieu-filter',
                    options=[{'label': '📋 Tous les lieux', 'value': 'all'}] + 
                            [{'label': f"{lieu} ({len(df[df['lieu']==lieu])})", 'value': lieu} 
                             for lieu in sorted(df['lieu'].unique())],
                    value='all',
                    clearable=False,
                    style={'fontSize': '14px'}
                ),
            ], style={'marginBottom': '20px'}),
            
            # Filtre Maladie
            html.Div([
                html.Label("🦠 Maladie", style={
                    'fontWeight': 'bold',
                    'marginBottom': '8px',
                    'color': '#ffffff',
                    'fontSize': '14px',
                    'display': 'block'
                }),
                dcc.Dropdown(
                    id='maladie-filter',
                    options=[{'label': '📋 Toutes les maladies', 'value': 'all'}] + 
                            [{'label': f"{mal} ({len(df[df['maladie']==mal])})", 'value': mal} 
                             for mal in sorted(df['maladie'].unique())],
                    value='all',
                    clearable=False,
                    style={'fontSize': '14px'}
                ),
            ], style={'marginBottom': '20px'}),
            
            # Filtre Animal
            html.Div([
                html.Label("🐾 Animal", style={
                    'fontWeight': 'bold',
                    'marginBottom': '8px',
                    'color': '#ffffff',
                    'fontSize': '14px',
                    'display': 'block'
                }),
                dcc.Dropdown(
                    id='animal-filter',
                    options=[{'label': '📋 Tous les animaux', 'value': 'all'}] + 
                            [{'label': f"{animal} ({len(df[df['animal']==animal])})", 'value': animal} 
                             for animal in sorted(df['animal'].unique())],
                    value='all',
                    clearable=False,
                    style={'fontSize': '14px'}
                ),
            ], style={'marginBottom': '20px'}),
            
            # Bouton Reset
            html.Button(
                '🔄 Réinitialiser tous les filtres',
                id='reset-button',
                n_clicks=0,
                style={
                    'width': '100%',
                    'padding': '12px',
                    'backgroundColor': '#e74c3c',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '8px',
                    'cursor': 'pointer',
                    'fontSize': '14px',
                    'fontWeight': 'bold',
                    'marginTop': '10px'
                }
            ),
            
        ], style={'padding': '20px'})
        
    ], className='sidebar', style={
        'position': 'fixed',
        'left': '0',
        'top': '0',
        'width': '300px',
        'height': '100vh',
        'background': 'linear-gradient(180deg, #667eea 0%, #764ba2 100%)',
        'overflowY': 'auto',
        'boxShadow': '3px 0 15px rgba(0,0,0,0.2)',
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
                    'padding': '25px',
                    'margin': '0',
                    'fontSize': '28px',
                    'fontWeight': 'bold'
                }
            ),
            html.P(
                f"📈 Base de données : {len(df)} articles analysés",
                style={
                    'textAlign': 'center',
                    'color': '#7f8c8d',
                    'marginTop': '-15px',
                    'paddingBottom': '20px',
                    'fontSize': '16px'
                }
            )
        ], style={
            'backgroundColor': '#f8f9fa',
            'borderRadius': '0 0 15px 15px',
            'marginBottom': '20px',
            'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'
        }),
        
        # KPIs
        html.Div(id='kpis', style={'padding': '15px'}),
        
        # Graphiques
        html.Div([
            dcc.Graph(id='langue-chart')
        ], style={'padding': '15px', 'marginBottom': '20px'}),
        
        html.Div([
            dcc.Graph(id='source-chart')
        ], style={'padding': '15px', 'marginBottom': '20px'}),
        
        html.Div([
            dcc.Graph(id='maladie-chart')
        ], style={'padding': '15px', 'marginBottom': '20px'}),
        
        html.Div([
            dcc.Graph(id='animal-chart')
        ], style={'padding': '15px', 'marginBottom': '20px'}),
        
        html.Div([
            dcc.Graph(id='lieu-chart')
        ], style={'padding': '15px', 'marginBottom': '20px'}),
        
        html.Div([
            dcc.Graph(id='stats-chart')
        ], style={'padding': '15px', 'marginBottom': '20px'}),
        
        # Tableau de données
        html.Div([
            html.H3("📋 Détails des articles", style={
                'textAlign': 'center',
                'color': '#2c3e50',
                'marginBottom': '20px'
            }),
            html.Div(id='data-table')
        ], style={'padding': '15px'}),
        
        # Footer
        html.Div([
            html.P(
                "🦠 Dashboard Maladies Animales - Analyse automatisée d'articles",
                style={
                    'textAlign': 'center',
                    'color': '#7f8c8d',
                    'padding': '20px',
                    'fontSize': '13px',
                    'borderTop': '1px solid #ecf0f1'
                }
            )
        ])
        
    ], className='main-content', style={
        'marginLeft': '300px',
        'padding': '15px',
        'backgroundColor': '#ffffff',
        'minHeight': '100vh'
    })
    
], style={
    'fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    'backgroundColor': '#f5f7fa'
})

# ============================================
# CALLBACKS
# ============================================

@app.callback(
    [
        Output('langue-filter', 'value'),
        Output('source-filter', 'value'),
        Output('lieu-filter', 'value'),
        Output('maladie-filter', 'value'),
        Output('animal-filter', 'value'),
    ],
    [Input('reset-button', 'n_clicks')]
)
def reset_filters(n_clicks):
    """Réinitialise tous les filtres"""
    if n_clicks > 0:
        return 'all', 'all', 'all', 'all', 'all'
    return 'all', 'all', 'all', 'all', 'all'

@app.callback(
    [
        Output('kpis', 'children'),
        Output('langue-chart', 'figure'),
        Output('source-chart', 'figure'),
        Output('maladie-chart', 'figure'),
        Output('animal-chart', 'figure'),
        Output('lieu-chart', 'figure'),
        Output('stats-chart', 'figure'),
        Output('data-table', 'children')
    ],
    [
        Input('langue-filter', 'value'),
        Input('source-filter', 'value'),
        Input('lieu-filter', 'value'),
        Input('maladie-filter', 'value'),
        Input('animal-filter', 'value')
    ]
)
def update_dashboard(selected_langue, selected_source, selected_lieu, selected_maladie, selected_animal):
    """Met à jour tous les composants du dashboard"""
    
    filtered_df = df.copy()
    
    # Appliquer les filtres
    if selected_langue != 'all':
        filtered_df = filtered_df[filtered_df['langue'] == selected_langue]
    if selected_source != 'all':
        filtered_df = filtered_df[filtered_df['source_publication'] == selected_source]
    if selected_lieu != 'all':
        filtered_df = filtered_df[filtered_df['lieu'] == selected_lieu]
    if selected_maladie != 'all':
        filtered_df = filtered_df[filtered_df['maladie'] == selected_maladie]
    if selected_animal != 'all':
        filtered_df = filtered_df[filtered_df['animal'] == selected_animal]
    
    # Gestion du cas vide
    if len(filtered_df) == 0:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="Aucune donnée pour ces filtres",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        empty_fig.update_layout(height=350)
        empty_kpis = html.Div([
            html.P("⚠️ Aucune donnée disponible avec ces filtres", 
                   style={'textAlign': 'center', 'color': '#e74c3c', 'fontSize': '18px'})
        ])
        empty_table = html.P("Aucune donnée", style={'textAlign': 'center', 'color': '#95a5a6'})
        return empty_kpis, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_table
    
    # === KPIs ===
    kpi_style_base = {
        'display': 'inline-block',
        'width': '19%',
        'textAlign': 'center',
        'margin': '5px',
        'padding': '25px',
        'borderRadius': '12px',
        'boxShadow': '0 4px 8px rgba(0,0,0,0.15)',
    }
    
    kpis = html.Div([
        html.Div([
            html.H2(f"{len(filtered_df)}", style={'color': '#fff', 'margin': '0', 'fontSize': '42px', 'fontWeight': 'bold'}),
            html.P("Articles", style={'margin': '8px 0 0 0', 'color': '#fff', 'fontSize': '14px'})
        ], className='kpi-box', style={**kpi_style_base, 'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'}),
        
        html.Div([
            html.H2(f"{int(filtered_df['nb_mots'].mean())}", style={'color': '#fff', 'margin': '0', 'fontSize': '42px', 'fontWeight': 'bold'}),
            html.P("Mots moy.", style={'margin': '8px 0 0 0', 'color': '#fff', 'fontSize': '14px'})
        ], className='kpi-box', style={**kpi_style_base, 'background': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'}),
        
        html.Div([
            html.H2(f"{filtered_df['maladie'].nunique()}", style={'color': '#fff', 'margin': '0', 'fontSize': '42px', 'fontWeight': 'bold'}),
            html.P("Maladies", style={'margin': '8px 0 0 0', 'color': '#fff', 'fontSize': '14px'})
        ], className='kpi-box', style={**kpi_style_base, 'background': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'}),
        
        html.Div([
            html.H2(f"{filtered_df['animal'].nunique()}", style={'color': '#fff', 'margin': '0', 'fontSize': '42px', 'fontWeight': 'bold'}),
            html.P("Animaux", style={'margin': '8px 0 0 0', 'color': '#fff', 'fontSize': '14px'})
        ], className='kpi-box', style={**kpi_style_base, 'background': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'}),
        
        html.Div([
            html.H2(f"{filtered_df['lieu'].nunique()}", style={'color': '#fff', 'margin': '0', 'fontSize': '42px', 'fontWeight': 'bold'}),
            html.P("Lieux", style={'margin': '8px 0 0 0', 'color': '#fff', 'fontSize': '14px'})
        ], className='kpi-box', style={**kpi_style_base, 'background': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'}),
    ], style={'textAlign': 'center', 'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-around'})
    
    # Config graphiques
    config = {'displayModeBar': True, 'responsive': True, 'displaylogo': False}
    
    # === GRAPHIQUES ===
    
    # 1. Langue (Donut)
    langue_counts = filtered_df['langue'].value_counts()
    langue_fig = px.pie(
        values=langue_counts.values,
        names=langue_counts.index,
        title='🌍 Répartition par langue',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    langue_fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12)
    langue_fig.update_layout(height=450, showlegend=True, title_font_size=18, title_x=0.5)
    
    # 2. Source (Bar)
    source_counts = filtered_df['source_publication'].value_counts()
    source_fig = px.bar(
        x=source_counts.index,
        y=source_counts.values,
        title='📰 Répartition par type de source',
        labels={'x': 'Source', 'y': 'Nombre d\'articles'},
        color=source_counts.values,
        color_continuous_scale='Viridis',
        text=source_counts.values
    )
    source_fig.update_traces(textposition='outside', textfont_size=12)
    source_fig.update_layout(height=400, showlegend=False, xaxis_tickangle=-45, title_font_size=18, title_x=0.5)
    
    # 3. Maladies (Horizontal Bar - Top 15)
    maladie_counts = filtered_df['maladie'].value_counts().head(15)
    maladie_fig = px.bar(
        x=maladie_counts.values,
        y=maladie_counts.index,
        orientation='h',
        title='🦠 Top 15 des maladies les plus mentionnées',
        labels={'x': 'Nombre d\'articles', 'y': ''},
        color=maladie_counts.values,
        color_continuous_scale='Reds',
        text=maladie_counts.values
    )
    maladie_fig.update_traces(textposition='outside', textfont_size=11)
    maladie_fig.update_layout(height=500, showlegend=False, title_font_size=18, title_x=0.5)
    
    # 4. Animaux (Horizontal Bar - Top 15)
    animal_counts = filtered_df['animal'].value_counts().head(15)
    animal_fig = px.bar(
        x=animal_counts.values,
        y=animal_counts.index,
        orientation='h',
        title='🐾 Top 15 des animaux les plus mentionnés',
        labels={'x': 'Nombre d\'articles', 'y': ''},
        color=animal_counts.values,
        color_continuous_scale='Greens',
        text=animal_counts.values
    )
    animal_fig.update_traces(textposition='outside', textfont_size=11)
    animal_fig.update_layout(height=500, showlegend=False, title_font_size=18, title_x=0.5)
    
    # 5. Lieux (Horizontal Bar - Top 15)
    lieu_counts = filtered_df['lieu'].value_counts().head(15)
    lieu_fig = px.bar(
        x=lieu_counts.values,
        y=lieu_counts.index,
        orientation='h',
        title='📍 Top 15 des lieux les plus mentionnés',
        labels={'x': 'Nombre d\'articles', 'y': ''},
        color=lieu_counts.values,
        color_continuous_scale='Blues',
        text=lieu_counts.values
    )
    lieu_fig.update_traces(textposition='outside', textfont_size=11)
    lieu_fig.update_layout(height=500, showlegend=False, title_font_size=18, title_x=0.5)
    
    # 6. Stats (Box Plot)
    stats_fig = go.Figure()
    stats_fig.add_trace(go.Box(
        y=filtered_df['nb_mots'],
        name='Nombre de mots',
        marker_color='#3498db',
        boxmean='sd'
    ))
    stats_fig.add_trace(go.Box(
        y=filtered_df['nb_caracteres']/100,
        name='Nb caractères (÷100)',
        marker_color='#e74c3c',
        boxmean='sd'
    ))
    stats_fig.update_layout(
        title='📊 Distribution statistique du contenu',
        yaxis_title='Valeur',
        height=400,
        showlegend=True,
        title_font_size=18,
        title_x=0.5
    )
    
    # === TABLEAU ===
    table_df = filtered_df[['code', 'titre', 'maladie', 'animal', 'lieu', 'langue', 'nb_mots', 'date_publication']].head(50)
    
    data_table = dash_table.DataTable(
        data=table_df.to_dict('records'),
        columns=[
            {'name': 'Code', 'id': 'code'},
            {'name': 'Titre', 'id': 'titre'},
            {'name': 'Maladie', 'id': 'maladie'},
            {'name': 'Animal', 'id': 'animal'},
            {'name': 'Lieu', 'id': 'lieu'},
            {'name': 'Langue', 'id': 'langue'},
            {'name': 'Mots', 'id': 'nb_mots'},
            {'name': 'Date', 'id': 'date_publication'}
        ],
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'fontSize': '13px'
        },
        style_header={
            'backgroundColor': '#667eea',
            'color': 'white',
            'fontWeight': 'bold',
            'textAlign': 'center'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f8f9fa'
            }
        ],
        page_size=10
    )
    
    return kpis, langue_fig, source_fig, maladie_fig, animal_fig, lieu_fig, stats_fig, data_table

# ============================================
# LANCEMENT
# ============================================

if __name__ == '__main__':
    import socket
    
    # Obtenir l'IP locale
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "votre-ip-locale"
    
    print("\n" + "="*70)
    print("🚀 LANCEMENT DU DASHBOARD - Maladies Animales")
    print("="*70)
    print(f"✅ {len(df)} articles chargés et prêts à être analysés")
    print("\n📊 ACCÈS AU DASHBOARD :")
    print(f"   🖥️  Local (PC)     : http://127.0.0.1:8050/")
    print(f"   📱 Mobile/Réseau : http://{local_ip}:8050/")
    print("\n⌨️  Appuyez sur Ctrl+C pour arrêter le serveur")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=8050)