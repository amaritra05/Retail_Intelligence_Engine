import pandas as pd

def preprocess(df):
    df = df[df['Order-Status'] != 'Cancelled']
    df = df[df['Quantity'] > 0]
    df['Revenue'] = df['Selling Price'] * df['Quantity']
    df['Order-Date'] = pd.to_datetime(df['Order-Date'])
    return df

def daily_metrics(df):
    return df.groupby(['Order-Date', 'Ship-State', 'Category']).agg({
        'Revenue': 'sum',
        'SKU': 'count'
    }).reset_index()

def top_skus(df, month, metric="Revenue", top_n=10):
    df['Order-Date'] = pd.to_datetime(df['Order-Date'])
    df['Month'] = df['Order-Date'].dt.to_period('M')
    month_df = df[df['Month'] == month]
    return month_df.groupby('SKU')[metric].sum().sort_values(ascending=False).head(top_n)

def category_performance(df):
    return df.groupby(['Category', 'Ship-State'])['Revenue'].sum().reset_index()