import duckdb
import pandas

def fetch_storage_capacity(db: str, destdir: str):
    db_con = duckdb.connect(db) #filepath to production duckdb database in duckdb_storage

    # query mart_combined__storage_capacity
    storage_capacity = db_con.execute(f'SELECT * FROM main.mart_combined__storage_capacity').fetchdf()
    db_con.close()
    # Write dataframe to destdir
    storage_capacity.to_csv(destdir + "/storage_capacity.csv", index = False)