# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///../Resources/hawaii.sqlite?check_same_thread=False")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of precipitation for last 12 months"""

    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    prcp = {date: prcp for date, prcp in precipitation}

    return jsonify(prcp)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all stations"""
    results = session.query(Station.station).all()

    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of observed temperatures for the last year for the most active station"""
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results_2 = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago).\
        filter(Measurement.station == "USC00519281").all()

    most_active_temps = {date: most_active_temps for date, most_active_temps in results_2}

    return jsonify(most_active_temps)

@app.route("/api/v1.0/<start>")
def start_date(start):
    """Return list of min, avg and max temps for specified start date"""
    start = dt.datetime.strptime(start, '%Y-%m-%d')
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    temperatures = list(np.ravel(results))
    return jsonify(temperatures)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Return list of min, avg and max temps for specified start and end date"""
    start = dt.datetime.strptime(start, '%Y-%m-%d')
    end = dt.datetime.strptime(end, '%Y-%m-%d')
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temperatures = list(np.ravel(results))
    return jsonify(temperatures)

if __name__ == "__main__":
    app.run(debug=True)