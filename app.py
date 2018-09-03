from schema import schema

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

from flask_graphql import GraphQLView


engine = create_engine('sqlite:///tutorial.db', echo=True)
 
app = Flask(__name__)

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True # for having the GraphiQL interface
    )
)

 
@app.route('/', methods = ['GET'])
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
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
    ),
    html.Button('Click Me', id='my-button'),
    dcc.Graph(
        id='bar-graph',
    )
], style={'width': '500'})

#Responsive output

@chart.callback(
    dash.dependencies.Output('my-graph','figure'),
    [dash.dependencies.Input('interval-component', 'n_intervals')])
def update_graph_live(n): #arguments correspond to the input values
    #get username from cookies
    username = request.cookies.get('username')
    query = '{ \
            dataByTenantName(tenantName: "%s", last: 50) {\
                id\
                value\
                time\
                tenant {\
                    id\
                    name\
                    }\
                sensor {\
                    id\
                    name\
                    }\
                }\
            }'%(username)

    result = schema.execute(query)
    if result and result.data:
        data = result.data['dataByTenantName']
        #add data to pandas table
        df = pd.DataFrame( [[i['tenant']['name'], i['sensor']['name'], i['value'], i['time']] for i in data])
        df.rename(columns={0: 'tenant_id', 1: 'sid', 2: 'value', 3:'time'}, inplace=True);
        #Group by sid and get keys
        keys = df.groupby('sid').groups.keys()

        #Return data grouped by sid
        return {
                'data': [{
                        'y': df[(df.sid==sid)]['value'],
                        #'x': df_tenant[(df_tenant.sid==sid)]['time'],
                        'x': range(len(df[(df.sid==sid)])),
                        #'mode': 'markers',
                        #'marker': {'size': 12}, 
                        'type':'line',
                        'name': sid
                        } for sid in keys],
                        'layout': {
                            'title': "{}'s data".format(username)
                        }
                }

@chart.callback(
    dash.dependencies.Output('bar-graph','figure'),
    [dash.dependencies.Input('my-button', 'n_clicks')],
    [dash.dependencies.State('interval-component', 'n_intervals')])
def update_bar_graph(n,n_intervals): #arguments correspond to the input values
    #connect to database
    if n:
        #get username from cookies
        username = request.cookies.get('username')
        query = '{ \
                dataByTenantName(tenantName: "%s") {\
                    id\
                    value\
                    time\
                    tenant {\
                        id\
                        name\
                        }\
                    sensor {\
                        id\
                        name\
                        }\
                    }\
                }'%(username)
        result = schema.execute(query)
        if result and result.data:
            data = result.data['dataByTenantName']
            #add data to pandas table
            df = pd.DataFrame( [[i['tenant']['name'], i['sensor']['name'], i['value'], i['time']] for i in data])
            df.rename(columns={0: 'tenant_id', 1: 'sid', 2: 'value', 3:'time'}, inplace=True);
            #Group by sid and get keys
            keys = df.groupby('sid').groups.keys()

            if n%2 == 0:

                #Return data grouped by sid
                return {
                    'data': [{
                            'y': df[(df.sid==sid)]['value'],
                            #'x': df_tenant[(df_tenant.sid==sid)]['time'],
                            'x': range(len(df[(df.sid==sid)])),
                            'type':'bar',
                            'name': sid
                            } for sid in keys],
                            'layout': {
                                'title': "{}'s data".format(username)
                            }
                        }
            else:
                return {
                    'data': [{
                            'y': df[(df.sid==sid)]['value'],
                            #'x': df_tenant[(df_tenant.sid==sid)]['time'],
                            'x': range(len(df[(df.sid==sid)])),
                            'mode': 'markers',
                            'marker': {'size': 12}, 
                            'name': sid
                            } for sid in keys],
                            'layout': {
                                'title': "{}'s data".format(username)
                            }
                        }
    #return some fake data to avoid null error
    return  {
            'data': {
                    'y':[0],
                    'x': [0],
                    'type':'line'
                }
            }       


@app.route("/plotly-dash")
def plotly_dash():
    return chart.index()


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=4000)
