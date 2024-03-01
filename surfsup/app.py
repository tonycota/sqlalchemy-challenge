# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import pandas as pd
import numpy as np
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# home page
@app.route("/")
def home():
    """List all available api routes"""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

# precipitation page
@app.route("/api/v1.0/precipitation")
def precipitation():
    # create the session link to the database(remember to close each one)
    session = Session(engine)
    
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    # find the targeted year from the last date in the data
    year_ago_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # query the data using a premade variable which value holds the data
    sel = [Measurement.date, Measurement.prcp]
    data_for_twelve_months = session.query(*sel).filter(Measurement.date >= year_ago_date).all()
    # convert the data into a pandas dataframe
    measurements_df = pd.DataFrame(data_for_twelve_months, columns=['Date','Prcp'])
    measurements_df.set_index('Date', inplace=True)
    # sort the dataframe by date
    measurements_df.sort_values(by='Date')
    # convert to dictionaries 
    prcp_dict = measurements_df.to_dict()
    # close the session
    session.close()
    return jsonify(prcp_dict)

# stations page
@app.route("/api/v1.0/stations")
def stations():
    # start the session link!
    session = Session(engine)
    # query the data
    results = session.query(Measurement.station).distinct().all()
    session.close()
    
    # use list of dictionaries to show the names of the stations
    station_data = []
    for station in results:
        station_dict = {}
        station_dict["Name of Station"] = station[0]
        station_data.append(station_dict)

    # jsonify and print the data
    return jsonify(station_data)

# tobs page
@app.route("/api/v1.0/tobs")
def route():
    # start the session link
    session = Session(engine)
    end_date = '2016-08-23'
    result = session.query(Measurement.date, Measurement.tobs).filter((Measurement.station == 'USC00519281') & (Measurement.date > end_date)).all()
    session.close()

    # similar concept to the stations data, create a list of dictionaries
    tobs_info = []
    for date, tobs in result:
        t_dict = {}
        t_dict["Date"] = date
        t_dict["Observed Temperature"] = tobs
        tobs_info.append(t_dict)
    return jsonify(tobs_info)

# start page
@app.route("/api/v1.0/start")
def start():
    # start the session link
    session = Session(engine)
    start_date = dt.date(2016, 12, 19)
    # query the data
    start = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    session.close()
    jsonify_start = list(np.ravel(start))
    return jsonify(jsonify_start)

@app.route("/api/v1.0/start/end")
def start_end():
    # start the session link
    session = Session(engine)
    # implement start and end dates
    start_date = dt.date(2016, 12, 19)
    end_date = dt.date(2017, 1, 28)
    #query the data
    start_end = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()
    jsonify_start_end = list(np.ravel(start_end))
    return jsonify(jsonify_start_end)


# remember to implement this otherwise the flask app won't run tony!
if __name__ == '__main__':
    app.run(debug=True)
