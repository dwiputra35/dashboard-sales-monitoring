import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import category_encoders as ce
from config import settings
import calendar

st.set_page_config(page_title="Ecommerce Dashboard", page_icon=":bar_chart:", layout="wide")

st.title("""Retail Sales/Ecommerce Monitoring Dashboard
         """)
st.write('Created by: [Dwi Putra Satria Utama](https://www.linkedin.com/in/dwiputra3500/)')

# Function to load data
def load_dataframe(sheet_id, sheet_name, date_column=None, date_format=None):
    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={sheet_name}'
    df = pd.read_csv(url)

    # Convert the specified date column to datetime with the given format
    if date_column and date_format:
        df[date_column] = pd.to_datetime(df[date_column], format=date_format)

    return df

@st.cache_data
def daily_sales_trend(transaksi_selected_month):
    transaksi_selected_month.set_index('DATE', inplace=True)
    df_daily = transaksi_selected_month.groupby(transaksi_selected_month.index)['QUANTITY'].sum()
    df_daily = df_daily.rename('TOTAL_QUANTITY').to_frame()

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df_daily.index,
                             y=df_daily['TOTAL_QUANTITY'],
                             mode='lines+markers',
                             name='JUMLAH PENJUALAN',
                             text=df_daily.index.strftime('%b %d, %Y') + '<br>Quantity = ' + df_daily['TOTAL_QUANTITY'].astype(int).astype(str),
                             hoverinfo='text',
                             line=dict(color='#2E86AB')))

    fig.update_layout(title='TREN PENJUALAN HARIAN',
                      xaxis_title='TAHUN',
                      yaxis_title='JUMLAH PENJUALAN',
                      height=300,
                      width=500)

    st.plotly_chart(fig, use_container_width=True)

@st.cache_data
def distribusi_pelanggan(transaksi_selected_month):
    pembelian_user= (transaksi_selected_month.groupby(['USER_ID', 'STATUS'])[['QUANTITY', 'NILAI_TRANSAKSI']].sum()
                 .sort_values('NILAI_TRANSAKSI', ascending=False)
                 .reset_index())
    
    # Menggunakan Category Encoder untuk mengubah 'USER_ID' menjadi kategori
    encoder = ce.OrdinalEncoder(cols=['USER_ID'])
    pembelian_user = encoder.fit_transform(pembelian_user)
    # Membuat bar chart
    fig = px.bar(pembelian_user, 
                x='USER_ID', 
                y='NILAI_TRANSAKSI',  
                color='STATUS', 
                hover_data=['QUANTITY'],
                title='DISTRIBUSI PELANGGAN BERDASARKAN STATUS',
                color_discrete_map={'premium': '#2E86AB', 'basic': '#F39237'}
                )

    # Menyesuaikan label sumbu x dan y
    fig.update_layout(
        xaxis_title='USER ID',
        yaxis_title='NILAI TRANSAKSI',
        height=400,
        width=500
        )

    st.plotly_chart(fig, use_container_width=True)


@st.cache_data
def ketersediaan_produk():
    produk = load_dataframe(settings.sheet_id, settings.sheet_produk)

    fig = px.bar(produk, 
             x=produk['PRODUCT_ID'], 
             y='HARUS_RESTOCK_BILA_JUMLAH_GUDANG_TERSISA', 
             color='PRODUCT_ID',
             labels={'HARUS_RESTOCK_BILA_JUMLAH_GUDANG_TERSISA': 'Batas Restock'},
             title='KETERSEDIAAN PRODUK DI GUDANG',
             color_discrete_map={ 'a': '#F39237', 'b': '#F39237', 'c': '#F39237', 'd': '#F39237', 'e': '#F39237'}
             )
    
    
    # Menambahkan bar tambahan
    fig.add_bar(x=produk['PRODUCT_ID'], 
                y=produk['JUMLAH_DIGUDANG'],
                name='Tersedia',
                marker_color='#2E86AB')

    fig.update_layout(xaxis_title='PRODUCT ID', 
                      yaxis_title='JUMLAH',
                      height=400,
                      width=500)
        
    st.plotly_chart(fig, use_container_width=True)


@st.cache_data
def performa_produk(transaksi_selected_month):
    produk_terjual = (transaksi_selected_month
                      .groupby('PRODUCT_ID')['QUANTITY']
                      .sum()
                      .reset_index()
                      .sort_values('QUANTITY', ascending=False)
                      .reset_index()
                      .drop(columns=['index']))

    # Use a modern minimalist color palette
    colors = ['#2E86AB', '#F39237', '#F35B04', '#333333', '#D9BF77']

    fig = go.Figure(data=[go.Pie(labels=produk_terjual['PRODUCT_ID'],
                                 values=produk_terjual['QUANTITY'],
                                 hole=.6,
                                 marker=dict(colors=colors))])  # hole parameter creates the donut shape

    fig.update_layout(title_text='PERFORMA PRODUK',
                      height=400,
                      width=400)

    st.plotly_chart(fig, use_container_width=True)



@st.cache_data
def transaksi_perbulan(transaksi_selected_month):
    # Modify the function to use the selected month
    perbulan = transaksi_selected_month.groupby(transaksi_selected_month['DATE'].dt.to_period("M"))['NILAI_TRANSAKSI'].sum().reset_index()

    # # Visualize Total Nilai Transaksi
    fig = go.Figure()

    value = perbulan['NILAI_TRANSAKSI'].iloc[-1] if not perbulan.empty else 0
    fig.add_trace(go.Indicator(
        mode='number',
        value=value,
        # title={'text': 'NILAI TRANSAKSI', 'font': {'size': 10}},
        delta=dict(reference=0),
        ))
    
    fig.update_layout(
    height=250,  
    width=250,
    title={
            'text': 'NILAI TRANSAKSI',
            'y':0.65,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 17}  
        },
    )  

    # Display the figures separately
    st.plotly_chart(fig, use_container_width=True)


@st.cache_data
def delta_pct(perbulan_selected_month):
    # perbulan
    fig = go.Figure()
    
    value_pct = perbulan_selected_month['PERUBAHAN_PCT'].iloc[0]

    if value_pct > 0:
        title = 'KENAIKAN (%) vs BULAN SEBELUMNYA'
    elif value_pct < 0:
        title = 'PENURUNAN (%) vs BULAN SEBELUMNYA'
    else:
        title = 'TIDAK ADA PERUBAHAN'


    fig.add_trace(go.Indicator(
        mode='delta',
        value=value_pct,
        # title=title,
        delta=dict(reference=0),
    ))

    fig.update_layout(
    height=250,  
    width=250,
    title={
            'text': title,
            'y':0.65,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 17}  # Menyesuaikan ukuran font judul
        },
    )   


    # Display the figures separately
    st.plotly_chart(fig, use_container_width=True)

@st.cache_data
def delta_value(perbulan_selected_month):
    # perbulan

    fig = go.Figure()
    
    value = perbulan_selected_month['PERUBAHAN'].iloc[0]

    if value > 0:
        title = 'KENAIKAN TRANSAKSI vs BULAN SEBELUMNYA'
    elif value < 0:
        title = 'PENURUNAN TRANSAKSI vs BULAN SEBELUMNYA'
    else:
        title = 'TIDAK ADA PERUBAHAN'


    fig.add_trace(go.Indicator(
        mode='delta',
        value=value,
        # title=title,
        delta=dict(reference=0),
    ))

    fig.update_layout(
    height=250,  
    width=250,
    title={
            'text': title,
            'y':0.65,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 17}  # Menyesuaikan ukuran font judul
        },
    )  
    # Display the figures separately
    st.plotly_chart(fig, use_container_width=True)

def main():
    transaksi = load_dataframe(settings.sheet_id, settings.sheet_transaksi, date_column='DATE', date_format='%Y-%m-%d')

    transaksi['MONTH'] = pd.to_datetime(transaksi['DATE']).dt.strftime('%Y-%m')

    transaksi['PERUBAHAN'] = transaksi['NILAI_TRANSAKSI'] - transaksi['NILAI_TRANSAKSI'].shift(1)
    transaksi['PERUBAHAN_PCT'] = transaksi['NILAI_TRANSAKSI'].pct_change() * 100
    
    perbulan = transaksi.groupby('MONTH')['NILAI_TRANSAKSI'].sum().reset_index()
    perbulan['PERUBAHAN'] = perbulan['NILAI_TRANSAKSI'] - perbulan['NILAI_TRANSAKSI'].shift(1)
    perbulan['PERUBAHAN_PCT'] = perbulan['NILAI_TRANSAKSI'].pct_change() * 100  
    

    with st.sidebar:
        # Get unique months in the sidebar  
        perbulan_grouped = transaksi.groupby('MONTH')['NILAI_TRANSAKSI'].sum().reset_index()
        month_list = list(transaksi['MONTH'].unique())
        selected_month = st.selectbox('Select a month', month_list)

    transaksi_selected_month = transaksi[transaksi['MONTH'] == selected_month]
    perbulan_selected_month = perbulan[perbulan['MONTH'] == selected_month]

    # transaksi_selected_month

    # Call the daily_sales_trend function outside of the sidebar
    # transaksi_perbulan(transaksi_selected_month)
    # delta_pct(perbulan_selected_month)
    # delta_value(perbulan_selected_month)
    # daily_sales_trend(transaksi_selected_month)
    # distribusi_pelanggan(transaksi_selected_month)
    # performa_produk(transaksi_selected_month)
    # ketersediaan_produk()

    grid = st.columns([1, 1, 1])
    with grid[0]:
        transaksi_perbulan(transaksi_selected_month)

    with grid[1]:
        delta_value(perbulan_selected_month)

    with grid[2]:
        delta_pct(perbulan_selected_month)

    grid2 = st.columns([4, 2])

    with grid2[0]:
        daily_sales_trend(transaksi_selected_month)

    with grid2[1]:
        performa_produk(transaksi_selected_month)    

    grid3 = st.columns([2, 2])

    with grid3[0]:
        distribusi_pelanggan(transaksi_selected_month)

    with grid3[1]:
        ketersediaan_produk() 
        
if __name__ == '__main__':
    main()