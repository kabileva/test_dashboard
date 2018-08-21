from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
import os
from flask import make_response
import requests
from sqlalchemy.orm import sessionmaker
from tabledef import *

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

from datetime import datetime as dt

import plotly.plotly as py
import plotly.graph_objs as go

import MySQLdb
import pandas as pd

engine = create_engine('sqlite:///tutorial.db', echo=True)
 
app = Flask(__name__)


 
@app.route('/', methods = ['GET'])
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        # req = requests.get('http://192.168.1.182:8088/login/', data = {'HTTP_X_PROXY_REMOTE_USER': 'kate_multitenancy'})
        # req = requests.post('http://192.168.1.182:8088/login/', data = {'HTTP_X_PROXY_REMOTE_USER': 'kate_multitenancy'})
        # req = requests.get('http://192.168.1.182:8088/', data = {'HTTP_X_PROXY_REMOTE_USER': 'kate_multitenancy'})
        # req = requests.post('http://192.168.1.182:8088/', data = {'HTTP_X_PROXY_REMOTE_USER': 'kate_multitenancy'})
        return render_template('index.html')

 
@app.route('/login', methods=['POST'])
def do_admin_login():
 
    POST_USERNAME = str(request.form['username'])
    POST_PASSWORD = str(request.form['password'])
 
    Session = sessionmaker(bind=engine)
    s = Session()
    query = s.query(User).filter(User.username.in_([POST_USERNAME]), User.password.in_([POST_PASSWORD]) )
    result = query.first()
    if result:
        session['logged_in'] = True
        session['username'] = POST_USERNAME
        #add username to cookie
        resp = make_response(render_template('index.html'))
        resp.set_cookie('username', POST_USERNAME)
        return resp 
        
        # req = requests.get('http://192.168.1.182:8088/login/', data = {'H                                      TTP_X_PROXY_REMOTE_USER': 'kate_multitenancy'})
        # req = requests.post('http://192.168.1.182:8088/login/', data = {'HTTP_X_PROXY_REMOTE_USER': 'kate_multitenancy'})
        # req = requests.get('http://192.168.1.182:8088/', data = {'HTTP_X_PROXY_REMOTE_USER': 'kate_multitenancy'})
        # req = requests.post('http://192.168.1.182:8088/',  data = {'HTTP_X_PROXY_REMOTE_USER': 'kate_multitenancy'})

    else:
        flash('wrong password or username!')
        return render_template('login.html')
    # return home()
 
@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()

@app.route("/superset")
def superset_dashboard():
    return render_template("superset.html",url_base_pathname='/dummy')

chart = dash.Dash(__name__, server=app)

#The general layout
chart.layout = html.Div([
    dcc.Graph(
            id='my-graph',
        ),
    dcc.Interval(
        id='interval-component',
        interval=1*1000, # in milliseconds
        n_intervals=0
    )
], style={'width': '500'})

#Responsive output

@chart.callback(
    dash.dependencies.Output('my-graph','figure'),
    [dash.dependencies.Input('interval-component', 'n_intervals')])
def update_graph_live(n): #arguments correspond to the input values
    #connect to database
    conn = MySQLdb.connect(host="localhost", user="root", passwd="Katerina27", db="sample_data")
    cursor = conn.cursor()
    cursor.execute('select tenant_id, sid, value, time from data_2');

    rows = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()

    #add data to pandas table
    df = pd.DataFrame( [[ij for ij in i] for i in rows] )
    df.rename(columns={0: 'tenant_id', 1: 'sid', 2: 'value', 3:'time'}, inplace=True);
    df = df.sort_values(['value'], ascending=[1]);
    #Group by sid and get keys
    keys = df.groupby('sid').groups.keys()
    #get username from cookies
    username = request.cookies.get('username')

    #Filter by username
    df_new = df[(df.tenant_id==username)]
    #Return data grouped by sid
    return {
        'data': 
            [{'y': df_new[(df_new.sid==sid)]['value'],
                'x': df_new[(df_new.sid==sid)]['time'],
                'mode': 'markers',
                'marker': {'size': 12}, 
                'name': sid
            } for sid in keys],
            'layout': {
                'title': "{}'s data".format(username)
            }
    }



@app.route("/plotly-dash")
def plotly_dash():
    return chart.index()


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=4000)