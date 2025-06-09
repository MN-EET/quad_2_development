import duckdb
import pandas

def fetch_solar_capacity(db: str, destdir: str):
    db_con = duckdb.connect(db) #filepath to production duckdb database in duckdb_storage

    # query mart_combined__solar_capacity
    solar_capacity = db_con.execute(f'SELECT * FROM main.mart_combined__solar_capacity').fetchdf()
    db_con.close()
    # Write dataframe to destdir
    solar_capacity.to_csv(destdir + "/solar_capacity.csv", index = False)