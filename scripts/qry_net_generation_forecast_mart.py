import duckdb
import pandas

def fetch_net_generation_forecast(db: str, destdir: str):
    db_con = duckdb.connect(db) #filepath to production duckdb database in duckdb_storage

    # query mart_combined__solar_capacity
    net_generation_forecast = db_con.execute(f'SELECT * FROM main_forecast.mart_mn_net_generation_forecast__23').fetchdf()
    db_con.close()
    # Write dataframe to destdir
    net_generation_forecast.to_csv(destdir + "/mn_net_generation_forecast__23.csv", index = False)