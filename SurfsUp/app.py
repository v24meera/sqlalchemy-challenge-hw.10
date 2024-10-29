# Import the dependencies.

import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt
from dateutil.relativedelta import relativedelta #adding this to use months instead of days

########################################
# Database Setup
########################################
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
sesh = Session(engine)

#########################################
# Flask Setup
#########################################
app = Flask(__name__)

#########################################
# Flask Routes
########################################
########################################
@app.route("/")
def splash():
     """List all the available routes"""
     return (
          f"<title>Hawaii Weather App</title>"
          f"<h1>Hawaii Weather App</h1>"
          f"<h2>Available Routes:</h2>"
          f"<li><b> / </b><<< You are here! </li>"
          f"<ul><i> Navigate thusly to receive thy data </i></ul>"
          f"<li><b> /api/v1.0/precipitation </b></li>"
          f"<ul><i> Will provide the final year's worth of precipitation data by date and station </i></ul>"
          f"<li><b> /api/v1.0/stations </b></li>"
          f"<ul><i> Will provide a list of all stations used </i></ul>"
          f"<li><b> /api/v1.0/tobs </b></li>"
          f"<ul><i> Will provide the final year's worth of temperature data by date for station USC00519281 </i></ul>"
          f"<li><b> /api/v1.0/'start' </b></li>"
          f"<ul><i> Will provide min, max, and avg temps from 'start' to 2017-08-23 (use format YYYY-MM-DD) </i></ul>"
          f"<li><b> /api/v1.0/'start'/'end' </b></li>"
          f"<ul><i> Will provide min, max, and avg temps from 'start' to 'end' (use format YYYY-MM-DD) </i></ul>"

     )
#################################################
#################################################
@app.route("/api/v1.0/precipitation")
def precip_dic():

     last_date = sesh.query(measurement.date).order_by(measurement.date.desc()).first()

     year_ago = dt.datetime.strptime(last_date.date, '%Y-%m-%d') - relativedelta(months=12)

     precip_query = sesh.query(measurement.station, measurement.date, measurement.prcp).filter(measurement.date >= year_ago).all()

     #precipitation = list(np.ravel(precip_query))
     app_list = []
     
     for station, date, prcp in precip_query:
          step_dict = {}
          step_dict["Station"] = station
          step_dict["Date"] = date
          step_dict["Prcp"] = prcp
          app_list.append(step_dict)
    
     return jsonify(app_list)
#################################################
#################################################
@app.route("/api/v1.0/stations")
def stat_stats():
     
     stations = sesh.query(station.name).all()

     station_list = list(np.ravel(stations))

     return jsonify(station_list)
#################################################
#################################################
@app.route("/api/v1.0/tobs")

def stat_temp():

     last_date = sesh.query(measurement.date).order_by(measurement.date.desc()).first()

     year_ago = dt.datetime.strptime(last_date.date, '%Y-%m-%d') - relativedelta(months=12)

     active_stat = sesh.query(measurement.station, func.count(measurement.station))\
            .group_by(measurement.station).order_by(func.count(measurement.station).desc()).first()

     temp_query = sesh.query(measurement.date, measurement.tobs)\
            .filter(measurement.date >= year_ago, measurement.station == active_stat.station).all()
     
     #final_result = list(np.ravel(temp_query))
     app_list = []
     
     for date, tobs in temp_query:
          step_dict = {}
          step_dict["Date"] = date
          step_dict["Temp"] = tobs
          app_list.append(step_dict)

     return jsonify(app_list)
#################################################
#################################################
@app.route("/api/v1.0/<start>")
def start(start):
     
     start_date = dt.datetime.strptime(start, '%Y-%m-%d')

     station_deets = sesh.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs))\
                .filter(measurement.date >= start_date).all()
     
     #final_result = list(np.ravel(station_deets))
     app_list = []
     
     for min, max, avg in station_deets:
          step_dict = {}
          step_dict["Min Temp"] = min
          step_dict["Max Temp"] = max
          step_dict["Avg Temp"] = avg
          app_list.append(step_dict)

     return jsonify(app_list)
#################################################
#################################################
@app.route("/api/v1.0/<start>/<end>")
def end(start, end):

     start_date = dt.datetime.strptime(start, '%Y-%m-%d')
     end_date = dt.datetime.strptime(end, '%Y-%m-%d')

     station_deets = sesh.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs))\
                .filter(measurement.date >= start_date, measurement.date <= end_date).all()
     
     #final_result = list(np.ravel(station_deets))
     app_list = []
     
     for min, max, avg in station_deets:
          step_dict = {}
          step_dict["Min Temp"] = min
          step_dict["Max Temp"] = max
          step_dict["Avg Temp"] = avg
          app_list.append(step_dict)

     return jsonify(app_list)
#################################################
#################################################
if __name__ == '__main__':
    app.run(debug=True)
