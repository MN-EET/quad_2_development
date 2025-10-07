import duckdb
import pandas

def fetch_storage_capacity(db: str, destdir: str):
    db_con = duckdb.connect(db) #filepath to production duckdb database in duckdb_storage

    # query mart_combined__storage_capacity
    storage_capacity = db_con.execute(f'SELECT * FROM main_generators.mart_combined__storage_capacity WHERE year_interconnected <= 2024').fetchdf()
    db_con.close()

    max_year = storage_capacity['year_interconnected'].max()
    total_capacity = round(storage_capacity['nameplate_mw'].sum(), 2)

    storage_capacity['capacity_label'] = storage_capacity.apply(
        lambda x: total_capacity if x['year_interconnected'] == max_year else None,
        axis=1
    )

    # Write dataframe to destdir
    storage_capacity.to_csv(destdir + "/storage_capacity.csv", index = False)