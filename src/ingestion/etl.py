from clickhouse_driver import Client
import pandas as pd

# Connect to DB
client = Client('clickhouse', user='admin', password='admin123')

print("Generating dummy big data...")

# Create dummy data (Simulating 700M records on a small scale)
data = [
    {'name': 'John Doe', 'email': 'john@gmail.com', 'country': 'USA'},
    {'name': 'Jane Smith', 'email': 'jane@yahoo.com', 'country': 'USA'},
    {'name': 'Rahul Sharma', 'email': 'rahul@live.com', 'country': 'India'},
    {'name': 'Wei Zhang', 'email': 'wei@qq.com', 'country': 'China'}
]

# Insert into ClickHouse
print("Inserting data...")
client.execute('INSERT INTO records (name, email, country) VALUES', data)
print("Data Ingestion Complete!")