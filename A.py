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

# Define custom CSS styles
st.markdown(
    """
    <style>
    .sidebar .sidebar-content {
        background-image: linear-gradient(to bottom, #f2f2f2, #ffffff);
    }
    .sidebar .sidebar-content .block-container {
        color: #1F618D;
    }
    .sidebar .sidebar-content .block-container .block-title {
        color: #1F618D;
    }
    .sidebar .sidebar-content .block-container .stSelectbox {
        color: #1F618D;
        background-color: #ffffff;
    }
    .sidebar .sidebar-content .stButton {
        color: #ffffff;
        background-color: #1F618D;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.title("Walmart Sales Dashboard")  # Add title to the sidebar
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

    # Sidebar
    st.sidebar.title("Options")
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

    # Calculate total sales based on filtered data
    total_sales = calculate_total_sales(filtered_data)
    # Format total sales
    total_sales_str = format(total_sales, ",.0f")

    # Group data by store and calculate total sales for each store
    sales_by_store = filtered_data.groupby('Store')['Weekly_Sales'].sum().reset_index()

    # Sort stores by total sales in descending order
    sales_by_store_sorted = sales_by_store.sort_values(by='Weekly_Sales', ascending=False)

    # Select top 5 stores
    top_5_stores = sales_by_store_sorted.head(5)
    # Sélectionner uniquement les colonnes 'Store' et 'Weekly_Sales'
    top_5_df = top_5_stores[['Store', 'Weekly_Sales']]


    #**********************************
    top_5_stores_with_size = filtered_data.loc[filtered_data['Store'].isin(top_5_stores['Store']), ['Store', 'Size','Type']].drop_duplicates()
    
    
    st.markdown(f'<div style="border: 2px solid #1F618D; border-radius: 5px; padding: 10px; background-color: #f2f2f2; color: black; width: 300px;">\
                     <span style="color: #1F618D; font-size: 20px;">💰</span>\
                     <span style="font-size: 20px;">Total Sales:</span>\
                     <span style="font-size: 24px; font-weight: bold;">{total_sales_str}</span>\
                 </div>', unsafe_allow_html=True)


    c9, C_ = st.columns(2)
    with c9 :
        st.write("### Top 5 Sales Stores")
        st.write(top_5_df)
    with C_ :
        st.write("### Top Stores Size")
        st.write(top_5_stores_with_size)


    # Create Plotly figure for donut chart (sales by type)
    sales_by_type = filtered_data.groupby('Type')['Weekly_Sales'].sum().reset_index()
    fig_sales_by_type = go.Figure(go.Pie(labels=sales_by_type['Type'], values=sales_by_type['Weekly_Sales'],
                                         hole=.3, marker_colors=['#85C1E9', '#2E86C1', '#1F618D']))
    fig_sales_by_type.update_layout(title='Predicted Sales by Type')

    # Create Plotly figure for donut chart (sales by holidays)
    if not filtered_data.empty:
        sales_by_holiday = filtered_data.groupby('IsHoliday')['Weekly_Sales'].sum().reset_index()
        fig_sales_by_holiday = go.Figure(go.Pie(labels=sales_by_holiday['IsHoliday'], values=sales_by_holiday['Weekly_Sales'],
                                                hole=.3, marker_colors=['#1F618D ', '#228FD4']))
        fig_sales_by_holiday.update_layout(title='Predicted Sales by Holiday')

    # Display the donut charts using st.columns(2)
    col1, col2 = st.columns(2)

    with col1:
        if not filtered_data.empty:
            st.plotly_chart(fig_sales_by_type, use_container_width=True)

    with col2:
        if not filtered_data.empty:
            st.plotly_chart(fig_sales_by_holiday, use_container_width=True)

    # Group data by week and calculate average sales, ROP, and safety stock
    weekly_data = filtered_data.groupby('Week').agg({'Weekly_Sales': 'mean'}).reset_index()

    # Create Plotly figure for sales, ROP, and safety stock
    fig_sales_rop_stock = go.Figure()

    # Add trace for average sales
    fig_sales_rop_stock.add_trace(go.Scatter(x=weekly_data['Week'], y=weekly_data['Weekly_Sales'],
                                              mode='lines', name='Average Predicted Sales'))
    # Add annotations for holidays
    holidays = filtered_data[filtered_data['IsHoliday'] == 1]['Week'].unique()
    for holiday in holidays:
        fig_sales_rop_stock.add_annotation(x=holiday, y=weekly_data.loc[weekly_data['Week'] == holiday, 'Weekly_Sales'].values[0],
                                           text="Holiday", showarrow=True, arrowhead=1)

    # Update layout for sales, ROP, and safety stock
    fig_sales_rop_stock.update_layout(title='Average Predicted Sales per Week',
                                       xaxis_title='Week', yaxis_title='Value')

    # Display the plot for sales, ROP, and safety stock
    st.plotly_chart(fig_sales_rop_stock)

    # Group data by store and calculate total sales for each store
    sales_by_store = filtered_data.groupby('Store')['Weekly_Sales'].sum().reset_index()

    # Create Plotly histogram for sales by store
    fig_sales_by_store = go.Figure(go.Bar(x=sales_by_store['Store'], y=sales_by_store['Weekly_Sales']))

    # Update layout for sales by store
    fig_sales_by_store.update_layout(title='Total Sales Predicted by Store',
                                      xaxis_title='Store', yaxis_title='Total Sales')

    # Display the histogram for sales by store
    st.plotly_chart(fig_sales_by_store)

    # Group data by month and calculate total sales for each month
    monthly_sales = filtered_data.groupby('Month')['Weekly_Sales'].sum().reset_index()

    # Create Plotly histogram for total sales by month
    fig_sales_by_month = go.Figure(go.Bar(x=monthly_sales['Month'], y=monthly_sales['Weekly_Sales']))

    # Add holidays as annotations
    holidays = filtered_data[filtered_data['IsHoliday'] == 1].groupby('Month')['Weekly_Sales'].sum().reset_index()
    for i, row in holidays.iterrows():
        fig_sales_by_month.add_annotation(x=row['Month'], y=row['Weekly_Sales'],
                                          text="Holiday",
                                          showarrow=True,
                                          arrowhead=1,
                                          ax=0,
                                          ay=-40)

    # Update layout for total sales by month
    fig_sales_by_month.update_layout(
        title='Total Sales Predicted by Month',
        xaxis_title='Month',
        yaxis_title='Total Sales'
    )

    # Display the histogram for total sales by month
    st.plotly_chart(fig_sales_by_month)


    # Afficher le DataFrame filtré
    st.write("Filtered Data:")
    st.write(filtered_data)
