import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB


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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/<start><br/>"
        f"/api/v1.0/start/end/<start>/<end><br/>"

    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert results to a dictionary using date as the key and precipitation as the value."""
    # Calculate the date 1 year ago from the last data point in the database
    session = Session(engine)
    maxdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    print(maxdate)
    date_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores sorted by date, ascending
    prcpdata = session.query(Measurement.date,Measurement.prcp).\
    filter(Measurement.date >= date_year_ago).\
    order_by(Measurement.date).all()
    precipitationdict = dict(prcpdata)
    
    return (jsonify(precipitationdict))

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset"""
    session = Session(engine)
    active_stations = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    activestationslist = list(np.ravel(active_stations))
    
    return jsonify(activestationslist)      

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of Temperature Observations (tobs) for the previous year."""
    session = Session(engine)
    date_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    temp_obs_data = session.query(Measurement.date, Measurement.station, Measurement.tobs).filter(Measurement.date >=date_year_ago).all()
    temp_obs_datalist = list(temp_obs_data)
    
    return jsonify(temp_obs_datalist)
    
@app.route("/api/v1.0/start/<start>")
def start(start=None):
    # """Return a JSON list of tmin, tmax, tavg, for the dates greater than or equal to the date provided."""
    session = Session(engine)
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date>=start).group_by(Measurement.date).all()
    resultslist = list(results)
    return jsonify(resultslist)

@app.route("/api/v1.0/start/end/<start>/<end>")
def startend(start=None, end=None):
    # """Return a JSON list of tmin, tmax, tavg, in range of start date and end date inclusive."""
    session = Session(engine)
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date>=start, Measurement.date<=end).group_by(Measurement.date).all()
    startendlist = list(results)
    return jsonify (startendlist)


if __name__ == '__main__':
    app.run(debug=True)
