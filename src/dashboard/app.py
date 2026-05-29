import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import clickhouse_connect
from datetime import datetime
import sys
import os

# Adicionar o diretório src ao path para importar as configurações
sys.path.append(os.path.join(os.getcwd(), 'src'))
from common.config import config

# Configuração da Página
st.set_page_config(
    page_title="Northwind Data Pipeline - Executive Intelligence",
    page_icon="📊",
    layout="wide"
)

# Estilo customizado
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# Conexão com ClickHouse
@st.cache_resource
def get_ch_client():
    try:
        return clickhouse_connect.get_client(
            host=config.CH_HOST,
            port=config.CH_PORT,
            username=config.CH_USER,
            password=config.CH_PASSWORD
        )
    except Exception as e:
        st.error(f"Erro ao conectar ao ClickHouse: {e}")
        return None

@st.cache_data(ttl=60)
def query_clickhouse(query):
    client = get_ch_client()
    if client:
        return client.query_df(query)
    return pd.DataFrame()

def format_metric(value):
    """Formata valores grandes para escala de mil (k)."""
    if value >= 1000:
        return f"${value/1000:,.1f}k"
    return f"${value:,.2f}"

# --- SIDEBAR ---
st.sidebar.title("Northwind Analytics")
st.sidebar.image("https://www.streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png", width=150)

st.sidebar.divider()
st.sidebar.subheader("Filtros")

# Filtro de Países
countries_df = query_clickhouse("SELECT DISTINCT ship_country FROM northwind.gold_revenue_monthly ORDER BY ship_country")
countries = ["Todos"] + countries_df['ship_country'].tolist() if not countries_df.empty else ["Todos"]
selected_country = st.sidebar.selectbox("País de Destino", countries)

# Filtro de Data
date_range = query_clickhouse("SELECT min(month), max(month) FROM northwind.gold_revenue_monthly")
if not date_range.empty and date_range.iloc[0, 0] is not None:
    min_date = pd.to_datetime(date_range.iloc[0, 0])
    max_date = pd.to_datetime(date_range.iloc[0, 1])
else:
    min_date = datetime(1996, 1, 1)
    max_date = datetime.now()

start_date, end_date = st.sidebar.date_input(
    "Período",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Opção de Escala Logarítmica
use_log = st.sidebar.checkbox("Usar Escala Logarítmica", help="Melhora a visibilidade de dados menores comparados ao líder.")

# --- MAIN CONTENT ---
st.title("🚀 Northwind Business Intelligence")
st.markdown(f"**Contexto:** {selected_country} | **Período:** {start_date} a {end_date}")

# Cláusulas WHERE dinâmicas
where_gold = f"WHERE month >= '{start_date}' AND month <= '{end_date}'"
where_silver = f"WHERE order_date >= '{start_date}' AND order_date <= '{end_date}'"

if selected_country != "Todos":
    where_gold += f" AND ship_country = '{selected_country}'"
    where_silver += f" AND ship_country = '{selected_country}'"

# 1. KPI Cards
st.subheader("Indicadores de Desempenho (KPIs)")
cols = st.columns(5)

rev_query = f"SELECT sum(total_revenue) as rev, sum(order_count) as orders FROM northwind.gold_revenue_monthly {where_gold}"
rev_data = query_clickhouse(rev_query)
total_revenue = rev_data['rev'].iloc[0] if not rev_data.empty and rev_data['rev'].iloc[0] is not None else 0
total_orders = rev_data['orders'].iloc[0] if not rev_data.empty and rev_data['orders'].iloc[0] is not None else 0

sla_where = "" if selected_country == "Todos" else f"WHERE ship_country = '{selected_country}'"
sla_query = f"SELECT avg(on_time_rate) * 100 as sla FROM northwind.gold_logistics_performance {sla_where}"
sla_data = query_clickhouse(sla_query)
on_time_rate = sla_data['sla'].iloc[0] if not sla_data.empty and sla_data['sla'].iloc[0] is not None else 0

retention_query = "SELECT rebuy_rate * 100 as rate FROM northwind.gold_customer_retention ORDER BY loaded_at DESC LIMIT 1"
retention_data = query_clickhouse(retention_query)
rebuy_rate = retention_data['rate'].iloc[0] if not retention_data.empty else 0
avg_ticket = total_revenue / total_orders if total_orders > 0 else 0

with cols[0]:
    st.metric("Receita Líquida", format_metric(total_revenue))
with cols[1]:
    st.metric("Total de Pedidos", f"{total_orders:,}")
with cols[2]:
    st.metric("SLA (On-Time %)", f"{on_time_rate:.1f}%")
with cols[3]:
    st.metric("Taxa de Recompra %", f"{rebuy_rate:.1f}%")
with cols[4]:
    st.metric("Ticket Médio", f"${avg_ticket:.2f}")

st.divider()

# 2. SEÇÃO: EVOLUÇÃO DE PRODUTOS
st.subheader("📊 Evolução Mensal dos Top 10 Produtos")

# Identificar Top 10 de forma robusta
top_ids_query = f"""
    SELECT product_id, sum(total_price) as total_rev 
    FROM northwind.silver_orders_unified 
    {where_silver}
    GROUP BY product_id 
    ORDER BY total_rev DESC LIMIT 10
"""
df_top_ids = query_clickhouse(top_ids_query)

if not df_top_ids.empty:
    top_ids = df_top_ids['product_id'].tolist()
    
    evolution_query = f"""
        SELECT 
            toStartOfMonth(order_date) as month,
            product_id,
            sum(total_price) as monthly_revenue
        FROM northwind.silver_orders_unified
        WHERE product_id IN ({','.join(map(str, top_ids))})
        AND order_date >= '{start_date}' AND order_date <= '{end_date}'
        GROUP BY month, product_id
        ORDER BY month, monthly_revenue DESC
    """
    df_evolution = query_clickhouse(evolution_query)
    
    if not df_evolution.empty:
        df_evolution['product_id'] = "Prod " + df_evolution['product_id'].astype(str)
        fig_evo = px.line(df_evolution, x='month', y='monthly_revenue', color='product_id',
                          labels={'monthly_revenue': 'Receita ($)', 'month': 'Mês', 'product_id': 'Produto'},
                          markers=True)
        if use_log:
            fig_evo.update_yaxes(type="log")
        st.plotly_chart(fig_evo, use_container_width=True)

    st.divider()

    # 3. Segunda Linha: Ranking e Geografia
    col_e, col_f = st.columns(2)

    with col_e:
        st.subheader("🏆 Ranking Top 10 Produtos")
        df_ranking = df_top_ids.copy()
        df_ranking['product_id'] = "Prod " + df_ranking['product_id'].astype(str)
        df_ranking = df_ranking.sort_values('total_rev', ascending=True)
        
        fig_prod = px.bar(df_ranking, x='total_rev', y='product_id', orientation='h',
                           labels={'total_rev': 'Receita Total ($)', 'product_id': 'Produto'},
                           color='total_rev', color_continuous_scale='Reds',
                           text='total_rev')
        fig_prod.update_traces(texttemplate='$%{text:.3s}', textposition='outside', cliponaxis=False)
        fig_prod.update_yaxes(type='category')
        if use_log:
            fig_prod.update_xaxes(type="log")
        fig_prod.update_layout(bargap=0.2, margin=dict(r=50))
        st.plotly_chart(fig_prod, use_container_width=True)

    with col_f:
        st.subheader("👨‍💼 Performance por Vendedor")
        # GARANTIA: Agrupar por ID para evitar empilhamento caso existam duplicados históricos
        seller_query = """
            SELECT employee_id, sum(total_revenue) as total_rev 
            FROM northwind.gold_seller_performance 
            GROUP BY employee_id 
            ORDER BY total_rev DESC LIMIT 10
        """
        df_seller = query_clickhouse(seller_query)
        if not df_seller.empty:
            df_seller['employee_id'] = "Vend " + df_seller['employee_id'].astype(str)
            df_seller = df_seller.sort_values('total_rev', ascending=True)
            
            fig_seller = px.bar(df_seller, x='total_rev', y='employee_id', orientation='h',
                                 labels={'total_rev': 'Receita Total ($)', 'employee_id': 'Vendedor'},
                                 color='total_rev', color_continuous_scale='Blues',
                                 text='total_rev')
            fig_seller.update_traces(texttemplate='$%{text:.3s}', textposition='outside', cliponaxis=False)
            fig_seller.update_yaxes(type='category')
            fig_seller.update_layout(bargap=0.2, margin=dict(r=50))
            st.plotly_chart(fig_seller, use_container_width=True)

# 4. Terceira Linha: Países e Status
st.divider()
col_g, col_h = st.columns(2)

with col_g:
    st.subheader("🌍 Receita por País")
    geo_rev_query = f"SELECT ship_country, sum(total_revenue) as revenue FROM northwind.gold_revenue_monthly {where_gold} GROUP BY ship_country ORDER BY revenue DESC LIMIT 10"
    df_geo = query_clickhouse(geo_rev_query)
    if not df_geo.empty:
        df_geo = df_geo.sort_values('revenue', ascending=True)
        fig_geo = px.bar(df_geo, x='revenue', y='ship_country', orientation='h',
                          labels={'revenue': 'Receita ($)', 'ship_country': 'País'},
                          color='revenue', color_continuous_scale='Viridis',
                          text='revenue')
        fig_geo.update_traces(texttemplate='$%{text:.3s}', textposition='outside', cliponaxis=False)
        fig_geo.update_layout(bargap=0.2, margin=dict(r=50))
        st.plotly_chart(fig_geo, use_container_width=True)

with col_h:
    st.subheader("📊 Distribuição de Status")
    status_query = "SELECT status, sum(order_count) as total_orders FROM northwind.gold_order_status GROUP BY status"
    df_status = query_clickhouse(status_query)
    if not df_status.empty:
        fig_status = px.pie(df_status, values='total_orders', names='status', 
                            color='status', color_discrete_map={'Shipped': '#00CC96', 'Pending': '#EF553B'},
                            hole=.4)
        fig_status.update_layout(showlegend=True)
        st.plotly_chart(fig_status, use_container_width=True)

# 5. Detalhamento Geográfico
st.divider()
st.subheader("📍 Concentração por Cidade")
geo_dist_query = f"""
    SELECT ship_country, ship_city, toFloat64(sum(total_revenue)) as total_revenue, sum(unique_customers) as unique_customers 
    FROM northwind.gold_geographic_distribution 
    { "WHERE ship_country = '" + selected_country + "'" if selected_country != "Todos" else "" }
    GROUP BY ship_country, ship_city
    ORDER BY total_revenue DESC LIMIT 20
"""
df_geo_dist = query_clickhouse(geo_dist_query)
if not df_geo_dist.empty:
    st.dataframe(df_geo_dist.style.format({"total_revenue": "${:,.2f}"}), use_container_width=True)

# Footer
st.sidebar.divider()
st.sidebar.caption(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.sidebar.info("Northwind Intelligence v1.7")
