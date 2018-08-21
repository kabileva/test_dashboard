import plotly.plotly as py
import plotly.graph_objs as go

import MySQLdb
import pandas as pd

conn = MySQLdb.connect(host="localhost", user="root", passwd="Katerina27", db="sample_data")
cursor = conn.cursor()
cursor.execute('select tenant_id, sid, value from data_2');
rows = cursor.fetchall()
df = pd.DataFrame( [[ij for ij in i] for i in rows] )
df.rename(columns={0: 'tenant_id', 1: 'sid', 2: 'value'}, inplace=True);
df = df.sort_values(['value'], ascending=[1]);
trace1 = go.Scatter(
            x=df['value'],
            y=df['sid'],
            text=df['tenant_id'],
            mode='markers'
            )
layout = go.Layout(
            title='Life expectancy vs GNP from MySQL world database',
            xaxis=dict( type='log', title='GNP' ),
            yaxis=dict( title='Life expectancy' )
            )
data = [trace1]
fig = go.Figure(data=data, layout=layout)
py.plot(fig, filename='world GNP vs life expectancy')

