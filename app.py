# Import dependencies
import matplotlib.pyplot as plt
# %matplotlib inline
import datetime
from datetime import date
import pandas as pd
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text, Date, Float, func
from flask import Flask, jsonify

# Create engine
engine = create_engine('sqlite:///hawaii.sqlite')

Base=automap_base()

Base.prepare(engine, reflect=True)

#check to see if it works... OMG it works again! Codes are magical.
Base.classes.keys()

#let's save these reflections into variables
Stations = Base.classes.station
Measurement = Base.classes.measurement

# Precipitation Analysis
session = Session(engine)
#retrieve the last 12 months of precipitation data
measurement = pd.read_sql_query("SELECT * FROM Measurement", engine)
measurement['date'] = measurement['date'].astype('datetime64[ns]')
#retrieve the data from the past 12 months
# the pandas way: 
oneYr = measurement[(measurement['date'] > '2016-08-23') & (measurement['date'] < '2017-08-23')]

# the sqlalchemy way:
# prcp1yr = session.query(Measurement.date, Measurement.prcp)\
# .filter(Measurement.date.between('2016-08-23','2017-08-23')).order_by(Measurement.date.asc()).all()

#select only the prcp and date column, and set date as index
# the pandas way: 
prcp1yr = oneYr[['date','prcp']].set_index('date')

# the sqlalchemy way:
# date = [i[0] for i in prcp1yr]
# precipitation = [i[1] for i in prcp1yr]
# prcp1yr = pd.DataFrame(prcp1yr, columns=['date', 'precipitation']).set_index('date')

#plot a graph
prcp1yr.plot()

#summary statistic
prcp1yr.describe()

# Station Analysis

#let's check out what the station data looks like...
station = pd.read_sql_query("SELECT * FROM station", engine).set_index('id')
station

# to calculate the total number of stations
pd.read_sql_query("SELECT COUNT(station) FROM station", engine)

# to calculate the most active station
stationCount = pd.read_sql_query("SELECT *, COUNT(tobs) FROM measurement GROUP BY station ORDER BY COUNT(tobs) DESC", engine)
print(stationCount)
print("")
print("The most active station is %s, id %s, with a tobs count of %s" % (stationCount['station'][0], stationCount['id'][0], stationCount['COUNT(tobs)'][0]))

# Temperature Analysis

#get the data from the most observed station within the last year
tobs1yr = pd.read_sql_query("SELECT * FROM measurement WHERE station = 'USC00519281'", engine)
#doing the pandas way because it's 
tobs1yr = tobs1yr[(tobs1yr['date'] > '2016-08-23') & (tobs1yr['date'] < '2017-08-23')]

tobs1yr = tobs1yr[['date','tobs']].set_index('date')

tobs1yr.plot.hist()

calcTemp = measurement[['date','tobs']]
def calc_temp(start_date, end_date):
    start_date = start_date - pd.offsets.DateOffset(years=1)
    end_date = end_date - pd.offsets.DateOffset(years=1)
    return calcTemp[(calcTemp['date'] > start_date) & (calcTemp['date'] < '2017-08-23')].describe()

tempStats = calc_temp(pd.to_datetime('2018-07-01'), pd.to_datetime('2018-07-10'))

tmin = tempStats.loc["min"].values
tmax = tempStats.loc["max"].values
tmean = tempStats.loc["mean"].values

tmean = pd.DataFrame(tmean)
tmean.plot(kind='bar', yerr=[tmin-tmax], title = "Trip Avg Temp", figsize = (2, 5), legend=False)

#Flask API
app = Flask(__name__)
localhost:5000

@app.route("/")
def welcome():
    return (
        f"All routes"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )
    
@app.route("/api/v1.0/precipitation")
def prcp():
    prcpQuery = session.query(Measurement.date, Measurement.tobs)\
    .filter(Measurement.date.between('2016-08-23','2017-08-23')).order_by(Measurement.date.asc()).all()
    prcpDate = [row[0] for row in prcpQuery]
    prcpTobs = [row[1] for row in prcpQuery]
    prcpDict = dict(zip(prcpDate, prcpTobs))
    return jsonify(prcpDict)

@app.route("/api/v1.0/stations")
def stations():
    stationQuery = session.query(Stations.station).order_by(Stations.station.asc()).all()
    return jsonify(stationQuery)
    
@app.route("/api/v1.0/tobs")
def tobs():
    tobsQuery = session.query(Measurement.tobs)\
   .filter(Measurement.date.between('2016-08-23','2017-08-23')).order_by(Measurement.station.asc()).all()
    return jsonify(tobsQuery)
    
@app.route("/api/v1.0/<start>")
def start(start_date):
    tempQuery = session.query(func.max(Measurement.tobs).label("max"),\
                        func.min(Measurement.tobs).label("min"),\
                        func.avg(Measurement.tobs).label("avg"))\
                       .filter(Measurement.date>=start_date)\
                       .all()
    tempStats = ('Max', 'Min', 'Avg')
    tempNums = (tempQuery[0][0],tempQuery[0][1],tempQuery[0][2])
    tempDict = dict(zip(tempStats,tempNums))
    return jsonify(tempDict)
                                 
@app.route("/api/v1.0/<start>/<end>")
def startEnd(start_date, end_date):
    tempQuery = session.query(func.max(Measurement.tobs).label("max"),\
                        func.min(Measurement.tobs).label("min"),\
                        func.avg(Measurement.tobs).label("avg"))\
                       .filter(Measurement.date>=start_date)\
                       .filter(Measurement.date<=end_date)\
                       .all()
    tempStats = ('Max', 'Min', 'Avg')
    tempNums = (tempQuery[0][0],tempQuery[0][1],tempQuery[0][2])
    tempDict = dict(zip(tempStats,tempNums))
    return jsonify(tempDict)
                                 
if __name__ == "__main__":
    app.run(debug=True)

