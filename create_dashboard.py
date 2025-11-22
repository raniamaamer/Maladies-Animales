import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

# Charger les données
df = pd.read_csv('output/animal_diseases_dataset.csv')

# Créer l'application Dash
app = Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1(
        "📊 Dashboard - Maladies Animales",
        style={
            'textAlign': 'center',
            'color': '#2c3e50',
            'padding': '20px',
            'backgroundColor': '#ecf0f1',
            'marginBottom': '30px'
        }
    ),
    
    # Filtres
    html.Div([
        html.Div([
            html.Label("🌍 Filtrer par langue:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='langue-filter',
                options=[{'label': 'Toutes les langues', 'value': 'all'}] +
                        [{'label': lang, 'value': lang} for lang in df['langue'].dropna().unique()],
                value='all',
                style={'width': '100%'}
            ),
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '20px'}),
        
        html.Div([
            html.Label("📰 Filtrer par source:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='source-filter',
                options=[{'label': 'Toutes les sources', 'value': 'all'}] +
                        [{'label': src, 'value': src} for src in df['source_type'].dropna().unique()],
                value='all',
                style={'width': '100%'}
            ),
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '20px'}),
    ]),
    
    # KPIs
    html.Div(id='kpis', style={'padding': '20px'}),
    
    # Graphiques
    html.Div([
        html.Div([dcc.Graph(id='langue-chart')], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(id='source-chart')], style={'width': '50%', 'display': 'inline-block'}),
    ]),
    
    html.Div([dcc.Graph(id='maladie-chart')]),
    html.Div([dcc.Graph(id='stats-chart')]),
], style={'fontFamily': 'Arial, sans-serif'})


# Callback
@app.callback(
    [
        Output('kpis', 'children'),
        Output('langue-chart', 'figure'),
        Output('source-chart', 'figure'),
        Output('maladie-chart', 'figure'),
        Output('stats-chart', 'figure')
    ],
    [Input('langue-filter', 'value'),
     Input('source-filter', 'value')]
)
def update_dashboard(selected_langue, selected_source):
    # Filtrer les données
    filtered_df = df.copy()
    if selected_langue != 'all':
        filtered_df = filtered_df[filtered_df['langue'] == selected_langue]
    if selected_source != 'all':
        filtered_df = filtered_df[filtered_df['source_type'] == selected_source]
    
    # KPIs
    kpis = html.Div([
        html.Div([
            html.H2(f"{len(filtered_df)}", style={'color': '#3498db', 'margin': '0'}),
            html.P("Total News", style={'margin': '5px'})
        ], style={'display': 'inline-block', 'width': '23%', 'textAlign': 'center',
                  'backgroundColor': '#ecf0f1', 'margin': '5px', 'padding': '20px',
                  'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        
        html.Div([
            html.H2(f"{filtered_df['nb_mots'].mean():.0f}" if not filtered_df.empty else "0", 
                    style={'color': '#e74c3c', 'margin': '0'}),
            html.P("Mots moyens", style={'margin': '5px'})
        ], style={'display': 'inline-block', 'width': '23%', 'textAlign': 'center',
                  'backgroundColor': '#ecf0f1', 'margin': '5px', 'padding': '20px',
                  'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        
        html.Div([
            html.H2(f"{filtered_df['maladie'].nunique()}", style={'color': '#2ecc71', 'margin': '0'}),
            html.P("Maladies", style={'margin': '5px'})
        ], style={'display': 'inline-block', 'width': '23%', 'textAlign': 'center',
                  'backgroundColor': '#ecf0f1', 'margin': '5px', 'padding': '20px',
                  'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        
        html.Div([
            html.H2(f"{filtered_df['lieu'].nunique()}", style={'color': '#f39c12', 'margin': '0'}),
            html.P("Pays", style={'margin': '5px'})
        ], style={'display': 'inline-block', 'width': '23%', 'textAlign': 'center',
                  'backgroundColor': '#ecf0f1', 'margin': '5px', 'padding': '20px',
                  'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
    ])
    
    # Graphique langue
    langue_counts = filtered_df['langue'].value_counts()
    langue_fig = px.pie(
        values=langue_counts.values,
        names=langue_counts.index,
        title='🌍 Répartition par langue',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    langue_fig.update_layout(height=400)
    
    # Graphique source
    source_counts = filtered_df['source_type'].value_counts()
    source_fig = px.bar(
        x=source_counts.index,
        y=source_counts.values,
        title='📰 Répartition par type de source',
        labels={'x': 'Type de source', 'y': 'Nombre de news'},
        color=source_counts.values,
        color_continuous_scale='Blues'
    )
    source_fig.update_layout(height=400, showlegend=False)
    
    # Top maladies
    maladie_counts = filtered_df['maladie'].value_counts().head(10)
    maladie_fig = px.bar(
        x=maladie_counts.values,
        y=maladie_counts.index,
        orientation='h',
        title='🦠 Top 10 des maladies détectées',
        labels={'x': 'Nombre de news', 'y': 'Maladie'},
        color=maladie_counts.values,
        color_continuous_scale='Reds'
    )
    maladie_fig.update_layout(height=500, showlegend=False)
    
    # Statistiques mots/caractères
    stats_fig = go.Figure()
    stats_fig.add_trace(go.Box(
        y=filtered_df['nb_mots'],
        name='Nombre de mots',
        marker_color='lightblue'
    ))
    stats_fig.add_trace(go.Box(
        y=filtered_df['nb_caracteres']/100,
        name='Nombre de caractères (x100)',
        marker_color='lightcoral'
    ))
    stats_fig.update_layout(
        title='📊 Distribution du nombre de mots et caractères',
        yaxis_title='Valeur',
        height=400
    )
    
    return kpis, langue_fig, source_fig, maladie_fig, stats_fig


# Lancer le serveur
if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 Lancement du Dashboard")
    print("="*70)
    print("\n📊 Ouvrez votre navigateur à l'adresse :")
    print("👉 http://127.0.0.1:8050/")
    print("\n⌨️  Appuyez sur Ctrl+C pour arrêter le serveur\n")
    
    app.run_server(debug=True)
