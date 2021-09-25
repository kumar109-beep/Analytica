from pydrill.client import PyDrill
drill = PyDrill(host='localhost', port=8047)

# drill.profiles()

query = """select COUNT(*), district_name from table(dfs.parquet.`asha.parquet.gzip` (type => 'parquet', autoCorrectCorruptDates => false)) GROUP BY district_name"""


data = drill.query(query)


for xd in data:
    print(xd)
