import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output

# Inicializa o aplicativo Dash com um tema Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Carrega os dados do CSV
data = pd.read_csv('dados_vendas_assinaturas.csv')
data['data_compra'] = pd.to_datetime(data['data_compra'])

# Layout do Dashboard
app.layout = dbc.Container(
    children=[
        dbc.Row(dbc.Col(html.H1("Dashboard PetisCo", className="text-center mt-3 mb-4"))),

        dbc.Row(dbc.Col(html.H2("Selecione o Período", className="text-center"))),

        dbc.Row(
            dbc.Col(
                dcc.DatePickerRange(
                    id='date-picker-range',
                    start_date=data['data_compra'].min().date(),
                    end_date=data['data_compra'].max().date(),
                    display_format='YYYY-MM-DD',
                    className="d-flex justify-content-center mb-4"
                )
            )
        ),

        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Total de Novos Clientes"),
                            dbc.CardBody(html.P(id='total-novos-clientes', className="card-text"))
                        ], className="mb-4"
                    )
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Total de Renovações"),
                            dbc.CardBody(html.P(id='total-renovacoes', className="card-text"))
                        ], className="mb-4"
                    )
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Receita Total"),
                            dbc.CardBody(html.P(id='receita-total', className="card-text"))
                        ], className="mb-4"
                    )
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Total de Assinaturas"),
                            dbc.CardBody(html.P(id='total-assinaturas', className="card-text"))
                        ], className="mb-4"
                    )
                )
            ]
        ),

        dbc.Row(dbc.Col(html.H2("Vendas por Categoria", className="text-center"))),

        dbc.Row(dbc.Col(dcc.Graph(id='vendas-categoria'))),

        dbc.Row(dbc.Col(html.H2("Distribuição de Tipos de Plano", className="text-center"))),

        dbc.Row(dbc.Col(dcc.Graph(id='distribuicao-plano'))),

        dbc.Row(dbc.Col(html.H2("Vendas por Origem", className="text-center"))),

        dbc.Row(dbc.Col(dcc.Graph(id='vendas-origem')))
    ],
    fluid=True
)

@app.callback(
    [
        Output('total-novos-clientes', 'children'),
        Output('total-renovacoes', 'children'),
        Output('receita-total', 'children'),
        Output('total-assinaturas', 'children'),
        Output('vendas-categoria', 'figure'),
        Output('distribuicao-plano', 'figure'),
        Output('vendas-origem', 'figure')
    ],
    [
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date')
    ]
)
def update_metrics(start_date, end_date):
    # Filtrando os dados pelo período selecionado
    mask = (data['data_compra'] >= start_date) & (data['data_compra'] <= end_date)
    filtered_data = data.loc[mask]

    # Contagem de novos clientes versus renovações
    total_novos_clientes = filtered_data[filtered_data['is_renovacao'] == False]['id_cliente'].nunique()
    total_renovacoes = filtered_data[filtered_data['is_renovacao'] == True]['id_cliente'].nunique()

    # Receita total
    receita_total = filtered_data['preco_venda'].sum()

    # Total de assinaturas
    total_assinaturas = filtered_data['id_cliente'].nunique()

    # Vendas por categoria
    vendas_por_categoria = filtered_data.groupby('categoria')['preco_venda'].sum().reset_index()
    vendas_categoria_fig = px.bar(vendas_por_categoria, x='categoria', y='preco_venda', title='Vendas por Categoria')

    # Distribuição de tipos de plano
    distribuicao_plano = filtered_data['plano'].value_counts().reset_index()
    distribuicao_plano.columns = ['plano', 'count']
    distribuicao_plano_fig = px.pie(distribuicao_plano, names='plano', values='count', title='Distribuição de Tipos de Plano')

    # Vendas por origem
    vendas_por_origem = filtered_data.groupby('origem')['preco_venda'].sum().reset_index()
    vendas_origem_fig = px.bar(vendas_por_origem, x='origem', y='preco_venda', title='Vendas por Origem')

    return (
        f'Total de Novos Clientes: {total_novos_clientes}',
        f'Total de Renovações: {total_renovacoes}',
        f'Receita Total: R${receita_total:.2f}',
        f'Total de Assinaturas: {total_assinaturas}',
        vendas_categoria_fig,
        distribuicao_plano_fig,
        vendas_origem_fig
    )

if __name__ == '__main__':
    app.run_server(debug=True)
