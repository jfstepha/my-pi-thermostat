#!/usr/bin/python3

import yfinance as yf
import os
import time
import datetime
from influxdb import InfluxDBClient

class MyStock:

    def __init__(self):
        print("initializing")
        self.influxdbClient = InfluxDBClient( host="localhost", port="8086", database="stock", username="grafana", password="QREs_rule")

    def run(self):
        print("running")
        while True:
            ticker = yf.Ticker( "INTC" )
            history = ticker.history()
            if history.empty:
                print( nowstr + "Got an empty dataframe from yahoo" )
            else:
                last_quote = (history.tail(1)['Close'].iloc[0])
                today_high = (history.tail(1)['High'].iloc[0])
                today_low = (history.tail(1)['Low'].iloc[0])
                yesterday_close =  (history.tail(2)['Close'].iloc[0])

                json_body = [{ "measurement": "intc", "fields": { "price": last_quote, "high": today_high, "low": today_low, "yesterday_close": yesterday_close } } ]
                now=datetime.datetime.now()
                nowstr =  now.strftime( "[%Y-%m-%d %H:%M:%S] " )
                print( nowstr + "Got last intc quote: %0.2f (%0.2f-%0.2f) yesterday:%0.2f " % (last_quote, today_high, today_low, yesterday_close))
                print( nowstr + "Writing to DB:")
                self.influxdbClient.write_points(json_body)
            print( nowstr + "Sleeping...")
            today9am = now.replace(hour=9, minute=0, second=0)
            today4pm = now.replace(hour=16,minute=0, second=0)
            print( nowstr + "today4pm=" + today4pm.strftime( "%Y-%m-%d %H:%M:%S") )
            if datetime.datetime.weekday( now ) > 4: 
                print( nowstr + "Weekend, sleeping 4 hours")
                time.sleep( 60 * 60 * 4)
            elif now < today9am or now > today4pm:
                print( nowstr + "After hours, sleeping 15 min")
                time.sleep( 60 * 15)
            else:
                time.sleep(60)
if __name__ == "__main__":
    print("Starting up yahoo finance influx script...")
    mystock = MyStock()
    mystock.run()
