from build_generator_file import build_generator_table

build_generator_table("https://mn.gov/puc/assets/PUBLIC%20MN%20Utility%20Report%20through%2012-31-2023%20%28released%209-10-2024%29%20%281%29_tcm14-643879.xlsx",
                      "https://www.eia.gov/electricity/data/eia860/xls/eia8602023.zip",
                      "puc_der_2023",
                      "eia_860_generators_2023")