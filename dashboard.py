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
    
    # Vérifier l'existence du fichier
    file_path = 'output/animal_diseases_dataset.csv'
    if not os.path.exists(file_path):
        print(f"❌ Fichier introuvable : {file_path}")
        print("💡 Veuillez d'abord exécuter extract.py pour générer les données")
        return None
    
    # Charger les données
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    print(f"✅ {len(df)} entrées chargées")
    
    # Identifier et filtrer les entrées valides (sans erreur)
    df_valid = df[df['langue'] != 'N/A'].copy()
    df_errors = df[df['langue'] == 'N/A'].copy()
    
    print(f"✅ Entrées valides : {len(df_valid)}")
    print(f"⚠️  Entrées en erreur : {len(df_errors)}")
    
    if len(df_valid) == 0:
        print("❌ Aucune donnée valide à afficher")
        return None
    
    # Nettoyer les valeurs manquantes
    df_valid['langue'] = df_valid['langue'].fillna('Non détecté')
    df_valid['source_type'] = df_valid['source_type'].fillna('Non classé')
    df_valid['maladie'] = df_valid['maladie'].fillna('Non identifiée')
    df_valid['lieu'] = df_valid['lieu'].fillna('Non spécifié')
    df_valid['nb_mots'] = pd.to_numeric(df_valid['nb_mots'], errors='coerce').fillna(0)
    df_valid['nb_caracteres'] = pd.to_numeric(df_valid['nb_caracteres'], errors='coerce').fillna(0)
    
    # Supprimer les doublons potentiels
    df_valid = df_valid.drop_duplicates(subset=['url'])
    
    print(f"✅ Dataset nettoyé : {len(df_valid)} entrées")
    
    return df_valid

# ============================================
# APPLICATION DASH
# ============================================

# Charger les données
df = load_and_clean_data()

if df is None or len(df) == 0:
    print("\n" + "="*70)
    print("❌ ERREUR : Impossible de démarrer le dashboard")
    print("="*70)
    print("\n💡 Solutions :")
    print("   1. Exécutez d'abord extract.py pour générer les données")
    print("   2. Vérifiez que le fichier 'output/animal_diseases_dataset.csv' existe")
    print("   3. Assurez-vous qu'il contient au moins une entrée valide\n")
    exit(1)

# Créer l'application Dash
app = Dash(__name__)

# Layout de l'application avec sidebar
app.layout = html.Div([
    
    # Sidebar (Filtres)
    html.Div([
        html.Div([
            html.H2(
                "🔍 Filtres",
                style={
                    'color': '#ffffff',
                    'textAlign': 'center',
                    'marginBottom': '30px',
                    'fontSize': '24px'
                }
            ),
            
            # Filtre Langue
            html.Div([
                html.Label("🌍 Langue", style={'fontWeight': 'bold', 'marginBottom': '10px', 'color': '#ffffff'}),
                dcc.Dropdown(
                    id='langue-filter',
                    options=[{'label': '📋 Toutes', 'value': 'all'}] + 
                            [{'label': lang, 'value': lang} for lang in sorted(df['langue'].unique())],
                    value='all',
                    clearable=False
                ),
            ], style={'marginBottom': '25px'}),
            
            # Filtre Source
            html.Div([
                html.Label("📰 Source", style={'fontWeight': 'bold', 'marginBottom': '10px', 'color': '#ffffff'}),
                dcc.Dropdown(
                    id='source-filter',
                    options=[{'label': '📋 Toutes', 'value': 'all'}] + 
                            [{'label': src, 'value': src} for src in sorted(df['source_type'].unique())],
                    value='all',
                    clearable=False
                ),
            ], style={'marginBottom': '25px'}),
            
            # Filtre Lieu
            html.Div([
                html.Label("📍 Lieu", style={'fontWeight': 'bold', 'marginBottom': '10px', 'color': '#ffffff'}),
                dcc.Dropdown(
                    id='lieu-filter',
                    options=[{'label': '📋 Tous', 'value': 'all'}] + 
                            [{'label': lieu, 'value': lieu} for lieu in sorted(df['lieu'].unique())],
                    value='all',
                    clearable=False
                ),
            ], style={'marginBottom': '25px'}),
            
            # Filtre Maladie
            html.Div([
                html.Label("🦠 Maladie", style={'fontWeight': 'bold', 'marginBottom': '10px', 'color': '#ffffff'}),
                dcc.Dropdown(
                    id='maladie-filter',
                    options=[{'label': '📋 Toutes', 'value': 'all'}] + 
                            [{'label': mal, 'value': mal} for mal in sorted(df['maladie'].unique())],
                    value='all',
                    clearable=False
                ),
            ], style={'marginBottom': '25px'}),
            
        ], style={'padding': '30px'})
        
    ], style={
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
                "📊 Dashboard - Analyse des Maladies Animales",
                style={
                    'textAlign': 'center',
                    'color': '#2c3e50',
                    'padding': '30px',
                    'margin': '0'
                }
            ),
            html.P(
                f"📈 Analyse de {len(df)} articles sur les maladies animales",
                style={
                    'textAlign': 'center',
                    'color': '#7f8c8d',
                    'marginTop': '-15px',
                    'paddingBottom': '20px'
                }
            )
        ], style={'backgroundColor': '#f8f9fa', 'borderRadius': '0 0 20px 20px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '20px'}),
        
        # KPIs
        html.Div(id='kpis', style={'padding': '20px'}),
        
        # Graphique Langue (centré)
        html.Div([
            html.Div([
                dcc.Graph(id='langue-chart')
            ], style={'maxWidth': '800px', 'margin': '0 auto'})
        ], style={'padding': '10px', 'marginBottom': '20px'}),
        
        # Graphique Source (pleine largeur)
        html.Div([
            dcc.Graph(id='source-chart')
        ], style={'padding': '10px'}),
        
        # Graphique Maladies (pleine largeur)
        html.Div([
            dcc.Graph(id='maladie-chart')
        ], style={'padding': '10px'}),
        
        # Graphique Lieux (pleine largeur)
        html.Div([
            dcc.Graph(id='lieu-chart')
        ], style={'padding': '10px'}),
        
        # Graphique statistiques
        html.Div([dcc.Graph(id='stats-chart')], style={'padding': '10px'}),
        
        # Footer
        html.Div([
            html.P(
                "🦠 Dashboard généré à partir des données extraites par extract.py",
                style={'textAlign': 'center', 'color': '#7f8c8d', 'padding': '20px'}
            )
        ])
        
    ], style={
        'marginLeft': '280px',
        'padding': '20px',
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
    """Met à jour tous les composants du dashboard en fonction des filtres"""
    
    # Filtrer les données
    filtered_df = df.copy()
    
    if selected_langue != 'all':
        filtered_df = filtered_df[filtered_df['langue'] == selected_langue]
    
    if selected_source != 'all':
        filtered_df = filtered_df[filtered_df['source_type'] == selected_source]
    
    if selected_lieu != 'all':
        filtered_df = filtered_df[filtered_df['lieu'] == selected_lieu]
    
    if selected_maladie != 'all':
        filtered_df = filtered_df[filtered_df['maladie'] == selected_maladie]
    
    # Gérer le cas où aucune donnée ne correspond aux filtres
    if len(filtered_df) == 0:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="Aucune donnée ne correspond aux filtres sélectionnés",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        empty_fig.update_layout(height=400)
        
        empty_kpis = html.Div([
            html.P("⚠️ Aucune donnée à afficher avec ces filtres", 
                   style={'textAlign': 'center', 'fontSize': '20px', 'color': '#e74c3c', 'padding': '40px'})
        ])
        
        return empty_kpis, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig
    
    # ============================================
    # KPIs
    # ============================================
    
    kpi_style_base = {
        'display': 'inline-block',
        'width': '23%',
        'textAlign': 'center',
        'margin': '5px',
        'padding': '25px',
        'borderRadius': '15px',
        'boxShadow': '0 4px 8px rgba(0,0,0,0.1)',
        'transition': 'transform 0.3s'
    }
    
    kpis = html.Div([
        html.Div([
            html.H2(f"{len(filtered_df)}", style={'color': '#3498db', 'margin': '0', 'fontSize': '48px'}),
            html.P("Articles", style={'margin': '5px', 'color': '#7f8c8d', 'fontSize': '16px'})
        ], style={**kpi_style_base, 'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 'color': 'white'}),
        
        html.Div([
            html.H2(f"{filtered_df['nb_mots'].mean():.0f}", 
                   style={'color': '#e74c3c', 'margin': '0', 'fontSize': '48px'}),
            html.P("Mots (moyenne)", style={'margin': '5px', 'color': '#7f8c8d', 'fontSize': '16px'})
        ], style={**kpi_style_base, 'background': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', 'color': 'white'}),
        
        html.Div([
            html.H2(f"{filtered_df['maladie'].nunique()}", 
                   style={'color': '#2ecc71', 'margin': '0', 'fontSize': '48px'}),
            html.P("Maladies", style={'margin': '5px', 'color': '#7f8c8d', 'fontSize': '16px'})
        ], style={**kpi_style_base, 'background': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', 'color': 'white'}),
        
        html.Div([
            html.H2(f"{filtered_df['lieu'].nunique()}", 
                   style={'color': '#f39c12', 'margin': '0', 'fontSize': '48px'}),
            html.P("Lieux", style={'margin': '5px', 'color': '#7f8c8d', 'fontSize': '16px'})
        ], style={**kpi_style_base, 'background': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', 'color': 'white'}),
    ], style={'textAlign': 'center'})
    
    # ============================================
    # GRAPHIQUES
    # ============================================
    
    # 1. Graphique Langue (Pie) - Centré
    langue_counts = filtered_df['langue'].value_counts()
    langue_fig = px.pie(
        values=langue_counts.values,
        names=langue_counts.index,
        title='🌍 Répartition par langue',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    langue_fig.update_traces(textposition='inside', textinfo='percent+label')
    langue_fig.update_layout(
        height=500,
        showlegend=True,
        title_x=0.5,
        title_font_size=20
    )
    
    # 2. Graphique Source (Bar)
    source_counts = filtered_df['source_type'].value_counts()
    source_fig = px.bar(
        x=source_counts.index,
        y=source_counts.values,
        title='📰 Répartition par type de source',
        labels={'x': 'Type de source', 'y': 'Nombre d\'articles'},
        color=source_counts.values,
        color_continuous_scale='Viridis',
        text=source_counts.values
    )
    source_fig.update_traces(textposition='outside')
    source_fig.update_layout(height=400, showlegend=False, xaxis_tickangle=-45)
    
    # 3. Top 10 Maladies (Horizontal Bar)
    maladie_counts = filtered_df['maladie'].value_counts().head(10)
    maladie_fig = px.bar(
        x=maladie_counts.values,
        y=maladie_counts.index,
        orientation='h',
        title='🦠 Top 10 des maladies détectées',
        labels={'x': 'Nombre d\'articles', 'y': 'Maladie'},
        color=maladie_counts.values,
        color_continuous_scale='Reds',
        text=maladie_counts.values
    )
    maladie_fig.update_traces(textposition='outside')
    maladie_fig.update_layout(height=450, showlegend=False)
    
    # 4. Top 10 Lieux (Horizontal Bar)
    lieu_counts = filtered_df['lieu'].value_counts().head(10)
    lieu_fig = px.bar(
        x=lieu_counts.values,
        y=lieu_counts.index,
        orientation='h',
        title='📍 Top 10 des lieux mentionnés',
        labels={'x': 'Nombre d\'articles', 'y': 'Lieu'},
        color=lieu_counts.values,
        color_continuous_scale='Blues',
        text=lieu_counts.values
    )
    lieu_fig.update_traces(textposition='outside')
    lieu_fig.update_layout(height=450, showlegend=False)
    
    # 5. Statistiques (Box Plot)
    stats_fig = go.Figure()
    
    stats_fig.add_trace(go.Box(
        y=filtered_df['nb_mots'],
        name='Nombre de mots',
        marker_color='#3498db',
        boxmean='sd'
    ))
    
    stats_fig.add_trace(go.Box(
        y=filtered_df['nb_caracteres'] / 100,
        name='Caractères (÷100)',
        marker_color='#e74c3c',
        boxmean='sd'
    ))
    
    stats_fig.update_layout(
        title='📊 Distribution du nombre de mots et caractères',
        yaxis_title='Valeur',
        height=400,
        showlegend=True
    )
    
    return kpis, langue_fig, source_fig, maladie_fig, lieu_fig, stats_fig

# ============================================
# LANCEMENT DU SERVEUR
# ============================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 LANCEMENT DU DASHBOARD - MALADIES ANIMALES")
    print("="*70)
    print(f"\n✅ {len(df)} articles chargés avec succès")
    print(f"🌍 Langues : {', '.join(df['langue'].unique())}")
    print(f"📰 Sources : {', '.join(df['source_type'].unique())}")
    print(f"🦠 Maladies : {df['maladie'].nunique()} différentes")
    print("\n" + "="*70)
    print("📊 Ouvrez votre navigateur à l'adresse :")
    print("👉 http://127.0.0.1:8050/")
    print("\n⌨️  Appuyez sur Ctrl+C pour arrêter le serveur")
    print("="*70 + "\n")
    
    # CORRECTION : Remplacer app.run_server par app.run
    app.run(debug=True)