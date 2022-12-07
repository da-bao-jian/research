import json
from google.cloud import bigquery
from google.oauth2 import service_account

# Links:
# https://medium.com/google-cloud/full-relational-diagram-for-ethereum-public-data-on-google-bigquery-2825fdf0fb0b

# ----------------------------------------------------------------
# USER SETTINGS
# ----------------------------------------------------------------
pool_address = "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640"
key_path = "../molten-precinct-370900-13a790fde100.json" # TODO(developer): use the key to the service account

# ----------------------------------------------------------------
credentials = service_account.Credentials.from_service_account_file(
    key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# Get the Ethereum blockchain data
QUERY = (
"SELECT "
  "address,"
  "block_number,"
  "transaction_hash,"
  "block_timestamp,"
  "log_index,"
  "transaction_index,"
  "CONCAT('0x',(CAST(SUBSTRING(Data, 3, 64) as string))) as amount0,"
  "CONCAT('0x',(CAST(SUBSTRING(Data, 67, 64) as string))) as amount1,"
  "CONCAT('0x',(CAST(SUBSTRING(Data, 131, 64) as string))) as sqrtPrice,"
  "CONCAT('0x',(CAST(SUBSTRING(Data, 195, 64) as string))) as liquidity,"
"IF "
  "((CAST(CONCAT('0x',(CAST(SUBSTRING(DATA, 317, 16) AS string))) AS int)) > CAST('0xf00000' AS int), (CAST(CONCAT('0x',(CAST(SUBSTRING(DATA, 317, 16) AS string))) AS int))- CAST('0xffffff' AS int), CAST(CONCAT('0x',(CAST(SUBSTRING(DATA, 317, 16) AS string))) AS int)) AS tick "
"FROM "
  "`bigquery-public-data.crypto_ethereum.logs` "
"WHERE "
  "DATA != '' "
  "AND transaction_hash != '' "
  f"AND address = '{pool_address}' "
  "AND (CAST(SUBSTRING(DATA, 259, 64) AS string)) != '' "
"ORDER BY "
  "block_timestamp ASC, transaction_index "
)
query_job = client.query(QUERY)  # API request
rows = query_job.result()  # Waits for query to finish

# now let's store in the GC bucket

for row in rows:
    print(f"{row.address} - {row.block_number}")
