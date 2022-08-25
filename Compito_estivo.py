from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)
#  pip install flask pandas contextily geopandas matplotlib folium lxml openpyxl
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import folium
import contextily
import geopandas as gpd
import pandas as pd
import io
from flask import Flask, render_template, send_file, make_response, url_for, Response, request, redirect
app = Flask(__name__)
import re


laghi = gpd.read_file('Laghi.zip')
province = gpd.read_file('Province.zip').to_crs(epsg=4326)
regioni = gpd.read_file('Regioni.zip').to_crs(epsg=4326)
quartieri = gpd.read_file('quartieri_milano.zip')
data = pd.read_excel('GdL_GV_2021.xlsx')
data = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data.longitude, data.latitude))
data['latitude'] = data['geometry'].x
data['longitude'] = data['geometry'].y
regionic = regioni[regioni['DEN_REG']== 'Lombardia']
datac = pd.DataFrame(data[data.intersects(regionic.unary_union)])
laghi1 = laghi[laghi.intersects(regioni.unary_union)]

@app.route('/', methods=['GET'])
def home():
    
    return render_template('home.html', data = data.to_html())

@app.route('/risp', methods=['GET'])
def risp():
  if request.args['sel'] == 'nluoghigiud':
    return redirect(url_for("nluoghigiudizio"))
  if request.args['sel'] == 'nluoghigiudper':
    return redirect(url_for("nluoghigiudizioper"))
  if request.args['sel'] == 'nluoghigiudgrafico':
    return redirect(url_for("nluoghigiudiziografico"))
  if request.args['sel'] == 'luoghispiaggia':
    return redirect(url_for("luoghispiaggia"))
  if request.args['sel'] == 'mappalombpunti':
    return redirect(url_for("mappa"))
  if request.args['sel'] == 'mappalombpuntigiud':
    return redirect(url_for("mappagiudizio"))
  if request.args['sel'] == 'mappauser':
    return redirect(url_for("mappauser"))
  if request.args['sel'] == 'laghiuser':
    return redirect(url_for("laghiuser"))
  return render_template(home.html)



@app.route('/nluoghigiudizio', methods=['GET'])
def nluoghigiudizio():
  data2 = pd.DataFrame(data.groupby("giudizio")["punto"].count().sort_values(ascending = False))
  return render_template('result.html' , data2=data2.to_html())


@app.route('/nluoghigiudizioper', methods=['GET'])
def nluoghigiudizioper():
  data2 = pd.DataFrame(data.groupby("giudizio")["punto"].count().sort_values(ascending = False))
  data2 = pd.DataFrame(100 * data2['punto'].count() / data2.groupby('giudizio')['punto'].transform('sum'))
  return render_template('result.html' , data2=data2.to_html())

@app.route('/luoghispiaggia', methods=['GET'])
def luoghispiaggia():
  data2 = pd.DataFrame(data[data['punto'].str.contains('spiaggia', flags=re.IGNORECASE, regex=True)]['punto'])
  return render_template('result.html' , data2=data2.to_html())

@app.route('/mappa', methods=['GET'])
def mappa():
  m = folium.Map(location=[45.46220047218434, 9.191121737490482],zoom_start=8, tiles='openstreetmap')  
  
  for _, row in datac.iterrows():
            folium.Marker(
                location=[row["longitude"], row["latitude"]],
                popup=row['punto'],
                icon=folium.map.Icon(color='green')
            ).add_to(m)
  for _, r in regioni[regioni['DEN_REG']=='Lombardia'].iterrows():
    sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
    geo_j = sim_geo.to_json()
    geo_j = folium.GeoJson(data=geo_j, style_function=lambda x: {'fillColor': 'blue'})
    folium.Popup(r['DEN_REG']).add_to(geo_j)
    geo_j.add_to(m)
  return render_template('result.html',  map=m._repr_html_())

@app.route('/mappagiudizio', methods=['GET'])
def mappagiudizio():
  m = folium.Map(location=[45.46220047218434, 9.191121737490482],zoom_start=8, tiles='openstreetmap')  
  
  for _, row in datac.iterrows():
            folium.Marker(
                location=[row["longitude"], row["latitude"]],
                popup=row['giudizio'],
                icon=folium.map.Icon(color='green')
            ).add_to(m)
  for _, r in regioni[regioni['DEN_REG']=='Lombardia'].iterrows():
    sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
    geo_j = sim_geo.to_json()
    geo_j = folium.GeoJson(data=geo_j, style_function=lambda x: {'fillColor': 'blue'})
    folium.Popup(r['DEN_REG']).add_to(geo_j)
    geo_j.add_to(m)
  return render_template('result.html',  map=m._repr_html_())

@app.route('/mappauser', methods=['GET'])
def mappauser():
  
  return render_template('mappauser.html', regioni=regioni['DEN_REG'])

@app.route('/resmappauser', methods=['GET'])
def resmappauser():
  m = folium.Map(location=[43.049849, 12.452571],zoom_start=6, tiles='openstreetmap')  
  regioniu = regioni[regioni['DEN_REG']== request.args['regione']]
  datac = pd.DataFrame(data[data.intersects(regioniu.unary_union)])
  for _, row in datac.iterrows():
            folium.Marker(
                location=[row["longitude"], row["latitude"]],
                popup=row['giudizio'],
                icon=folium.map.Icon(color='green')
            ).add_to(m)
  for _, r in regioniu.iterrows():
    sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
    geo_j = sim_geo.to_json()
    geo_j = folium.GeoJson(data=geo_j, style_function=lambda x: {'fillColor': 'blue'})
    folium.Popup(r['DEN_REG']).add_to(geo_j)
    geo_j.add_to(m)
  return render_template('result.html', map=m._repr_html_())


@app.route('/laghiuser', methods=['GET'])
def laghiuser():
  
  return render_template('laghiuser.html', laghi1=laghi1['LAKE_NAME'])

@app.route('/reslaghiutente', methods=['GET'])
def reslaghiutente():

  m = folium.Map(location=[43.049849, 12.452571],zoom_start=6, tiles='openstreetmap')  

  laghi1 = laghi[laghi.intersects(regioni.unary_union)]
  laghi1 = laghi1[laghi1['LAKE_NAME']== request.args['lago']]
  
  for _, r in laghi1.iterrows():
    sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
    geo_j = sim_geo.to_json()
    geo_j = folium.GeoJson(data=geo_j, style_function=lambda x: {'fillColor': 'blue'})
    folium.Popup(r['LAKE_NAME']).add_to(geo_j)
    geo_j.add_to(m)
  puntilaghi = pd.DataFrame(data[data.intersects(laghi1.unary_union)])
  for _, row in puntilaghi.iterrows():
            folium.Marker(
                location=[row["longitude"], row["latitude"]],
                popup=row['giudizio'],
                icon=folium.map.Icon(color='green')
            ).add_to(m)
  return render_template('result.html', map=m._repr_html_())

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3245, debug=True)