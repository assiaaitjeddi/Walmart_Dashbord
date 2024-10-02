import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Charger les données
@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)
    return data

st.set_page_config(
    page_title="Walmart Sales Dashboard",
    page_icon=":money_with_wings:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar
st.sidebar.title("Walmart Dashboard")  # Add title to the sidebar


file_path = st.sidebar.file_uploader("Choose a CSV file")

if file_path is not None:
    data = load_data(file_path)

    # Parse the 'Date' column as datetime
    data['Date'] = pd.to_datetime(data['Date'])

    # Sort the DataFrame by the 'Date' column
    data.sort_values(by='Date', inplace=True)

    def calculate_total_sales(filtered_data):
        total_sales = filtered_data['sales_forec'].sum()
        return total_sales
    
    st.sidebar.title("Options")
    selected_option = st.sidebar.radio("Select an option", ["Dataset", "Dashboard"])
    store_list = ['ALL'] + sorted(data['Store'].unique())
    selected_store = st.sidebar.selectbox("Select Store", store_list)

    year_list = ['ALL'] + sorted(data['Year'].unique())
    selected_year = st.sidebar.selectbox("Select Year", year_list)

    week_list = ['ALL'] + sorted(data['Week'].unique())
    selected_week = st.sidebar.selectbox("Select Week", week_list)

    # Filter data by selected store and year
    filtered_data = data.copy()
    if selected_store != 'ALL':
        filtered_data = filtered_data[filtered_data['Store'] == selected_store]
    if selected_year != 'ALL':
        filtered_data = filtered_data[filtered_data['Year'] == selected_year]
    if selected_week != 'ALL':
        filtered_data = filtered_data[filtered_data['Week'] == selected_week]

    # Sidebar options

    if selected_option == "Dataset":
        # Display dataset
        st.write(filtered_data)

    elif selected_option == "Dashboard":
        total_sales = calculate_total_sales(filtered_data)
        # Format total sales
        total_sales_str = format(total_sales, ",.0f")

        sales_by_store = data.groupby('Store')['Weekly_Sales'].sum().reset_index()
        sales_by_store_sorted = sales_by_store.sort_values(by='Weekly_Sales', ascending=False)
        top_5_stores = sales_by_store_sorted.head(5)
        # Sélectionner uniquement les colonnes 'Store' et 'Weekly_Sales'
        top_5_df = top_5_stores[['Store', 'Weekly_Sales']]

        #**********************************
        top_5_stores_with_size = data.loc[data['Store'].isin(top_5_stores['Store']), ['Store', 'Size','Type']].drop_duplicates()
    
        # Affichage des informations sur les ventes totales
        st.markdown(f'<div class="total-sales-container">\
                        <div class="total-sales" style="align:center;">\
                            <span style="color: #1F618D; font-size: 40px;">🛒</span>\
                            <span style="font-size: 20px;">Total Sales:</span>\
                            <span style="font-size: 24px; font-weight: bold;">{total_sales_str}</span>\
                        </div>\
                    </div>', unsafe_allow_html=True)

        # Affichage des top 5 magasins avec leurs ventes
        c9, C_ = st.columns(2)
        with c9:
            st.write("### Top 5 Sales Stores")
            st.write(top_5_df)
        with C_:
            st.write("### Top Stores Size")
            st.write(top_5_stores_with_size)

        sales_by_type = filtered_data.groupby('Type')['Weekly_Sales'].sum().reset_index()
        fig_sales_by_type = go.Figure(go.Pie(labels=sales_by_type['Type'], values=sales_by_type['Weekly_Sales'],
                                            hole=.3, marker_colors=['#85C1E9', '#2E86C1', '#1F618D']))
        fig_sales_by_type.update_layout(title='Predicted Sales by Type')

        if not filtered_data.empty:
            sales_by_holiday = filtered_data.groupby('IsHoliday')['Weekly_Sales'].sum().reset_index()
            fig_sales_by_holiday = go.Figure(go.Pie(labels=sales_by_holiday['IsHoliday'], values=sales_by_holiday['Weekly_Sales'],
                                                    hole=.3, marker_colors=['#1F618D ', '#228FD4']))
            fig_sales_by_holiday.update_layout(title='Predicted Sales by Holiday')

        weekly_data = filtered_data.groupby('Week').agg({'Weekly_Sales': 'mean'}).reset_index()
        fig_sales_rop_stock = go.Figure()
        fig_sales_rop_stock.add_trace(go.Scatter(x=weekly_data['Week'], y=weekly_data['Weekly_Sales'],
                                                mode='lines', name='Average Predicted Sales'))
        fig_sales_rop_stock.update_layout(title='Average Predicted Sales per Week',
                                        xaxis_title='Week', yaxis_title='Value')

        # Create Plotly histogram for sales by store
        sales_by_store = filtered_data.groupby('Store')['Weekly_Sales'].sum().reset_index()
        fig_sales_by_store = go.Figure(go.Bar(x=sales_by_store['Store'], y=sales_by_store['Weekly_Sales']))
        fig_sales_by_store.update_layout(title='Total Sales Predicted by Store',
                                        xaxis_title='Store', yaxis_title='Total Sales')

        # Create Plotly histogram for total sales by month
        monthly_sales = filtered_data.groupby('Month')['Weekly_Sales'].sum().reset_index()
        fig_sales_by_month = go.Figure(go.Bar(x=monthly_sales['Month'], y=monthly_sales['Weekly_Sales']))
        fig_sales_by_month.update_layout(
            title='Total Sales Predicted by Month',
            xaxis_title='Month',
            yaxis_title='Total Sales'
        )

        # Affichage des graphiques dans des colonnes
        col1, col2, col3 = st.columns(3)

        with col1:
            if not filtered_data.empty:
                st.plotly_chart(fig_sales_by_type, use_container_width=True)

        with col2:
            if not filtered_data.empty:
                st.plotly_chart(fig_sales_by_holiday, use_container_width=True)

        with col3:
            if not filtered_data.empty:
                st.plotly_chart(fig_sales_rop_stock, use_container_width=True)

        c2, c3 = st.columns(2)
        with c2:
            if not filtered_data.empty:
                st.plotly_chart(fig_sales_by_store, use_container_width=True)
        with c3:
            if not filtered_data.empty:
                st.plotly_chart(fig_sales_by_month, use_container_width=True)
