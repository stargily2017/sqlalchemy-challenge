#################################################
# Dependencies Setup
#################################################

import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# create engine using the `hawaii.sqlite` database file
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

#save references to the tables
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# --- Flask Routes ---
#################################################
    #1.List all the available routes.
@app.route("/")
def homepage():
    print("Server returns climate app home page...")
    return (
        f"Welcome to the Hawaii Climate App!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f" /api/v1.0/<start>/<end><br/>"
        f"Format of <start> and <end> date for querying is 'YYYY-MM-DD'"
    )
    
    #-------------------------------------------------
    #2.Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) 
    # to a dictionary using date as the key and prcp as the value.Return the JSON representation of your dictionary.
 
 
@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server returns Hawaii climate app precipitation page")

    # create a session from Python to the db.
    session = Session(engine)

      
    #retrieve only the last 12 months of data) 
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    print("Query Date: ", query_date) 
    
    sel = [measurement.date, measurement.prcp]
    precipitation = session.query(*sel).\
            filter(measurement.date >= query_date).\
                       order_by(measurement.date).all()
   

    #close the session
    session.close()

    #convert the query results to a dictionary using date as the key and prcp as the value
    precipitation_dict = {} 
    for date, prcp in precipitation:
        precipitation_dict[date] = prcp
    
    # Return the JSON representation of your dictionary.
    return jsonify(precipitation_dict)

    #--------------------------------------------
    #3.Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    print("Server returns Hawaii climate app station data")

    # create a session from Python to the database ---
    session = Session(engine)
    
    # perform a query to retrieve all the station data ---
    total_data = session.query(station.id, station.station, station.name, station.latitude,
                               station.longitude, station.elevation).all()

    # close the session
    session.close()

    # create a list of dictionaries with station info using for loop---
    list_stations = []

    for stn in total_data:
        station_dict = {}

        station_dict["id"] = stn[0]
        station_dict["station"] = stn[1]
        station_dict["name"] = stn[2]
        station_dict["latitude"] = stn[3]
        station_dict["longitude"] = stn[4]
        station_dict["elevation"] = stn[5]
        
        list_stations.append(station_dict)

    # Return a JSON list of stations from the dataset.
    return jsonify(list_stations)

    #-------------------------------------------------
    #4.Query the dates and temperature observations of the most-active station for the previous year of data.

@app.route("/api/v1.0/tobs")
def active_station_temps():

    print("Server returns Hawaii temperature app station data")
    # create a session from Python to the database ---
    session = Session(engine)
    # Calculate the date 1 year ago from the last data point in the database
    
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)


    #find the station with the highest number of temp observations
    most_active_station = session.query(measurement.station, func.count(measurement.tobs))\
                                .group_by(measurement.station)\
                                .order_by(func.count(measurement.tobs).desc())\
                                .first()[0]
    

    #query the last 12 months of temp observation data for this station
    active_station = session.query(measurement.date, measurement.tobs).\
                    filter(measurement.date >= query_date).\
                    filter(measurement.station == most_active_station).\
                    order_by(measurement.date).all()

    temp_bin = []
    for sts in active_station: 
        list_temp_dict = {}
        list_temp_dict["Station ID"] = sts[0]
        list_temp_dict["Temperature"] = sts[1]
        temp_bin.append(list_temp_dict)

    return jsonify(temp_bin)

    #---------------------------------------------
    #5.For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.

@app.route("/api/v1.0/<start>")
def temps_start(start):
    
    """returns min,max,avg,temperature from start date"""
     # create a session from Python to the database ---
    session = Session(engine)
    temperature_start = session.query(func.min(measurement.tobs), 
                                                       func.max(measurement.tobs),
                                                       func.avg(measurement.tobs)).\
                                            filter(measurement.date >= start).all()
    print(temperature_start)

    #all temparature range put in the bin
    all_temps = []
    
    all_temp_dict = {}
    for min, max, avg in temperature_start:
        all_temp_dict["TMIN"] = min
        all_temp_dict["TMAX"] = max
        all_temp_dict["TAVG"] = avg
        #from the bin to each dict   
        all_temps.append(all_temp_dict)
        
        
    return jsonify(all_temps)

    #-----------------------------------------------
    #5.For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
    
@app.route("/api/v1.0/<start>/<end>")
def temps_start_end(start,end):
    
    """returns min,max,avg,temperature from start date"""
     # create a session from Python to the database ---
    session = Session(engine)
    temperature_start = session.query(func.min(measurement.tobs), 
                                                       func.max(measurement.tobs),
                                                       func.avg(measurement.tobs)).\
                                            filter(measurement.date >= start).\
                                            filter(measurement.date <= end).all()
    print(temperature_start)

    #all temparature range put in the bin
    all_temps = []
    
    all_temp_dict = {}
    for min, max, avg in temperature_start:
        all_temp_dict["TMIN"] = min
        all_temp_dict["TMAX"] = max
        all_temp_dict["TAVG"] = avg
        #from the bin to each dict   
        all_temps.append(all_temp_dict)
        
        
    return jsonify(all_temps)
    #run all the routes for temperature, precipitation, active station.
    
if __name__ == "__main__":
    app.run(debug=True)