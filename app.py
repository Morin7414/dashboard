import psycopg2
from dash import Dash, dcc, html, dash_table
import plotly.graph_objs as go
from collections import Counter
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve database credentials
DB_HOST = os.getenv('DB_HOST')
DB_DATABASE = os.getenv('DB_DATABASE')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')


# Connect to PostgreSQL database
conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_DATABASE,
    user=DB_USER,
    password=DB_PASSWORD
)

cursor = conn.cursor()

# Query data from PostgreSQL database for treemap
cursor.execute("SELECT status FROM public.workorder_workorder;")
work_orders_data = cursor.fetchall()

# Query data from PostgreSQL database for table
cursor.execute("SELECT status, location, asset_number, model, reason_for_repair, date_created, date_closed FROM public.workorder_workorder;")
table_data = cursor.fetchall()

# Process data for treemap
status_counter = Counter(str(status[0]) for status in work_orders_data)

# Define column names for the table
column_names = ['Status', 'Location', 'Asset Number', 'Model', 'Reason for Repair', 'Date Created', 'Date Closed']

# Convert table_data to list of dictionaries
table_data_dicts = []
for row in table_data:
    table_data_dicts.append(dict(zip(column_names, row)))

# Close cursor and connection
cursor.close()
conn.close()

# Create Dash app
app = Dash(__name__, external_stylesheets=['/static/css/style.css'])

# Define layout
app.layout = html.Div([
    dcc.Graph(
        id='work-order-status-treemap',
        figure={
            'data': [
                go.Treemap(
                    labels=list(status_counter.keys()),
                    parents=[''] * len(status_counter),
                    values=list(status_counter.values()),
                    text=list(status_counter.values()),  # Text to display (counts)
                    textinfo='label+value',  # Display label and value on hover
                    textposition='middle center',  # Position the text in the center
                    textfont=dict(size=28),  # Set the text font size
                    hoverinfo='label+value',  # Display label and value on hover
                )
            ],
            'layout': go.Layout(
                title='Work Order Status TreeMap',
                font=dict(size=18),  # Set the title font size
            )
        }
    ),
    html.Div([
        dash_table.DataTable(
            id='table',
            columns=[{"name": column, "id": column} for column in column_names],
            data=table_data_dicts,
        )
    ])
])

if __name__ == '__main__':
    app.run_server(debug=False)