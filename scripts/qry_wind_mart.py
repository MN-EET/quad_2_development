import duckdb
import pandas

def fetch_wind_capacity(db: str, destdir: str):
    db_con = duckdb.connect(db) #filepath to production duckdb database in duckdb_storage

    # query mart_total__wind_capacity
    wind_capacity = db_con.execute(f'SELECT * FROM main_generators.mart_total__wind_capacity').fetchdf()
    db_con.close()
    # Write dataframe to destdir
    wind_capacity.to_csv(destdir + "/wind_capacity.csv", index = False)