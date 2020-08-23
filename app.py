import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt


# Database Setup

engine = create_engine("sqlite:///Resources/hawaii.sqlite") 

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Flask Setup
app = Flask(__name__)



# Flask Routes


@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date(in Y-m-d)<br/>"
        f"/api/v1.0/start_date(Y-m-d)/end_date(Y-m-d)"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    """Return date and prcp values for last 12 months as that was specified from the Data Analysis"""
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date_string = str(latest_date[0])
    latest_date = dt.datetime.strptime(latest_date[0], "%Y-%m-%d")


    query_date = dt.date(int(latest_date.strftime("%Y")), 
                     int(latest_date.strftime("%m")), 
                     int(latest_date.strftime("%d"))) - dt.timedelta(days=365)
    last_year_string = str(query_date)
    data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year_string).all()
    session.close()
    return_dict = {}
    for prec in data:
        return_dict[prec[0]] = prec[1]
    return jsonify(return_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    """Return each station and their count just like in Data Analysis"""
    station_count = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()
    session.close()
    return_list = []
    for station in station_count:
        return_list.append([station[0], station[1]])
    return jsonify(return_list)

@app.route("/api/v1.0/tobs")
def temperatureobservations():
    session = Session(engine)
    """Return Date and Observation for the most active station for the last year"""
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date_string = str(latest_date[0])
    latest_date = dt.datetime.strptime(latest_date[0], "%Y-%m-%d")

    query_date = dt.date(int(latest_date.strftime("%Y")), 
                     int(latest_date.strftime("%m")), 
                     int(latest_date.strftime("%d"))) - dt.timedelta(days=365)
    last_year_string = str(query_date)
    station_count = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()
    most_active = station_count[0][0]
    print(most_active)
    temperature_obs = (session.query( Measurement.date, Measurement.tobs)
                  .filter(Measurement.date >= last_year_string)
                   .filter(Measurement.station == most_active)
                   .all())
    session.close()
    tobs_return_list = []
    for observation in temperature_obs:
        tobs_return_list.append([observation[0], observation[1]])
    return jsonify(tobs_return_list)

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    """Returns the min, max and average temperature of the start date specified to the end date"""
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date_string = str(latest_date[0])
    latest_date = dt.datetime.strptime(latest_date[0], "%Y-%m-%d")
    start_date = start
    print(start_date)
    statistics = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                 filter(Measurement.date >= start).\
                 filter(Measurement.date <= last_date_string).all()
    session.close()
    return jsonify([statistics[0][0], statistics[0][1], statistics[0][2]])

@app.route("/api/v1.0/<start>/<end>")
def startEnd(start, end):
    session = Session(engine)
    """Returns the min, max and average temperature of the start date specified to the end date specified"""
    start_date = start
    end_date = end
    print(start_date)
    print(end_date)
    statistics = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                 filter(Measurement.date >= start_date).\
                 filter(Measurement.date <= end_date).all()
    session.close()
    return jsonify([statistics[0][0], statistics[0][1], statistics[0][2]])


if __name__ == '__main__':
    app.run(debug=True)
