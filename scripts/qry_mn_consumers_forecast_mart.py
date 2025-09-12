import duckdb
import pandas

def fetch_mn_consumers_forecast(db: str, destdir: str):
    db_con = duckdb.connect(db) #filepath to production duckdb database in duckdb_storage

    # query mart_combined__solar_capacity
    mn_consumers_forecast = db_con.execute(f'SELECT * FROM main_forecast.mart_mn_consumers__23').fetchdf()
    db_con.close()
    # Write dataframe to destdir
    mn_consumers_forecast.to_csv(destdir + "/mn_consumers__23.csv", index = False)