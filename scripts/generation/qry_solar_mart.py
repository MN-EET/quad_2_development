import duckdb
import pandas

def fetch_solar_capacity(db: str, destdir: str):
    db_con = duckdb.connect(db) #filepath to production duckdb database in duckdb_storage

    # query mart_combined__solar_capacity
    solar_capacity = db_con.execute(f'SELECT * FROM main_generators.mart_combined__solar_capacity').fetchdf()
    db_con.close()

    #create label
    max_year = solar_capacity['year_interconnected'].max()
    total_capacity = round(solar_capacity['nameplate_mw'].sum(), 2)

    solar_capacity['capacity_label'] = solar_capacity.apply(
        lambda x: total_capacity if x['year_interconnected'] == max_year else None,
        axis=1
    )

    # Write dataframe to destdir
    solar_capacity.to_csv(destdir + "/solar_capacity.csv", index = False)