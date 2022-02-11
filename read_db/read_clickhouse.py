import pandahouse

connection = {
    'host': 'https://clickhouse.lab.karpov.courses',
    'password': 'password',
    'user': 'user',
    'database': 'simulator'
}

q = 'SELECT * FROM {db}.feed_actions where toDate(time) = today() limit 10'

df = pandahouse.read_clickhouse(q, connection=connection)

print(df.head())
