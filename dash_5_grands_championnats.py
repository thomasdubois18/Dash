import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd

df = pd.read_csv("data/BIG FIVE 1995-2019.csv", sep=",")



#--------------------------------
#
#               DASH
#
#--------------------------------

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output

def donne_classement(pays,annee,df):
    
    df_use  = df.loc[df['Country']==pays]
    df_use  = df_use.set_index("Year")
    df_use  = df_use.loc[annee]
    df_use = df_use.reset_index()
    
    
    GGD_1 = []
    GGD_2 = []
    for i in range(len(df_use)):
        temp = df_use.loc[i]
        if (temp[13] ==3): #indice 13 = Team 1 (pts)
            GGD_1.append(temp[12]) #indice 12 = GGD
            GGD_2.append(-temp[12])
        elif(temp[14] ==3): 
            GGD_1.append(-temp[12])
            GGD_2.append(temp[12])
        else:
            GGD_1.append(temp[12])
            GGD_2.append(temp[12])
    df_use['GGD Team 1']=GGD_1
    df_use['GGD Team 2']=GGD_2

    
    
    classement = df_use[["Team 1", "Team 1 (pts)","GGD Team 1",'FT Team 1']].groupby(["Team 1"]).sum()
    class_ext = df_use[["Team 2", "Team 2 (pts)",'GGD Team 2','FT Team 2']].groupby(["Team 2"]).sum()
    classement['Team 2 (pts)'] = class_ext["Team 2 (pts)"]
    classement['FT Team 2']    = class_ext['FT Team 2']
    classement['GGD Team 2']   = class_ext['GGD Team 2']

    classement['final']        = classement['Team 1 (pts)']+ classement['Team 2 (pts)']
    classement['GGD final']    = classement['GGD Team 1']  + classement['GGD Team 1']
    classement['Goal final']   = classement['FT Team 1']   + classement['FT Team 1']

    classement_final = classement[['final','GGD final','Goal final']].sort_values(['final','GGD final','Goal final'],ascending=False)
    position = range(1,len(classement_final)+1)
    classement_final['Position'] = position
    classement_final = classement_final.reset_index()
    classement_final = classement_final.sort_values('Position')
    classement_final.rename(columns={'Team 1': 'Equipe', 'final': 'Points','GGD final': 'Goal Average','Goal final':'Nombre de buts marqués'}, inplace=True)
    classement_final = classement_final[['Position','Equipe','Points','Goal Average','Nombre de buts marqués']]
    
    return classement_final

def found_releg(champ,annee,df):
    df_year1 = donne_classement('FR',annee,df)
    df_year2 = donne_classement('FR',annee+1,df)
    tab1 = []
    for i in range(len(df_year1)):
        tab1.append(df_year1.loc[i]['Equipe'])
    tab2 = []
    for i in range(len(df_year2)):
        tab2.append(df_year2.loc[i]['Equipe'])
    tab = []
    for i in tab1:
        res = True
        for j in tab2:
            if i == j:
                res = False
                break
        if res:
            tab.append(df_year1['Position'].loc[df_year1['Equipe']==i].values.tolist()[0]-1)
    return(tab)   

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Label('Pays :'),
    dcc.Dropdown(
        id = 'pays',
        options=[
            {'label': 'France', 'value': 'FR'},
            {'label': 'Allemagne', 'value': 'GER'},
            {'label': 'Espagne', 'value': 'ESP'},
            {'label': 'Angleterre', 'value': 'ENG'},
            {'label': 'Italie', 'value': 'IT'}
        ],
        value = 'FR'
    ),

    
    html.Label('Année :'),
    dcc.RangeSlider(
        id = 'year',
        min=min(df['Year']),
        max=max(df['Year']),
        marks={i : str(i) for i in range(min(df['Year']), max(df['Year'])+1)},
        value=[min(df['Year']),max(df['Year'])+1]
    ),


    
    dash_table.DataTable(
    id='DF',
    columns=[{"name": i, "id": i,"deletable": True} for i in df.columns],
    data=df.to_dict('records'),
    fixed_rows={'headers': True},
    style_table={'height': 400},  # defaults to 500
    sort_action="native",
    sort_mode="multi"),


    html.Label('Choix du graph à afficher :'),
    dcc.Dropdown(
        id = 'choice graph',
        options=[
            {'label': 'Classement', 'value': 'CLSMT'},
            {'label': 'Buts (to do)', 'value': 'GOALS'}
        ],
        value=['CLSMT']
    ),


    html.Div(id='notre plot evolutif')#plot
    ])

@app.callback(
    Output('DF', 'data'),
    Input('pays', "value"),
    Input('year', "value"))
def update_table(pays,year):
    range_year = range(year[0],year[-1]+1)

    temp_df = pd.DataFrame()
    for y in range_year:
        temp_df = pd.concat([temp_df , df[df['Year']==y]])

    temp_df2 = pd.DataFrame()
    temp_df2 = pd.concat([temp_df2 , temp_df[temp_df['Country']==pays]])

    return temp_df2.to_dict('records')





@app.callback(
    Output('notre plot evolutif', "children"),
    Input('choice graph', "value"),
    Input('pays', "value"),
    Input('year', "value")
    )
def update_graphs(choice,pays,year):

    if choice == 'CLSMT':
        new_year = year[0]
        new_pays = pays

        
        df_res = donne_classement(new_pays, new_year,df)    


        
        return [
            dash_table.DataTable(
                id='notre plot evolutif',
                columns=[{"name": i, "id": i} for i in df_res.columns],
                data=df_res.to_dict('records'),
                editable=True,
                style_data_conditional=[
                    {
                        'if': {
                            'row_index': 0,
                            },
                        'backgroundColor': 'gold',
                        'color': 'white'
                        },
                    {
                        'if': {
                            'row_index': 1,
                            },
                        'backgroundColor': 'silver',
                        'color': 'white'
                        },
                    {
                        'if': {
                            'row_index': 2,
                            },
                        'backgroundColor': 'rgb(196, 156, 72)',
                        'color': 'white'
                        },
                    {
                        'if': {
                            'row_index': found_releg(new_pays,new_year,df),
                            },
                        'backgroundColor': 'red',
                        'color': 'white'  
                        }
                        
                    
                    ]
                )
            ]






if __name__ == '__main__':
    app.run_server()
