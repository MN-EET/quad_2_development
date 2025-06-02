import duckdb

con = duckdb.connect("generator_database.duckdb")

con.execute("""
    CREATE TABLE solar_archive AS
    SELECT * FROM read_csv_auto('C:/Users/dduffy/OneDrive - State of Minnesota - MN365/EIA Data/solar_generators_source.csv')
""")