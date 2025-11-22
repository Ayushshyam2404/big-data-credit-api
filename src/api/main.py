from fastapi import FastAPI, Header, HTTPException
import redis
import uuid
import time
from clickhouse_driver import Client
from clickhouse_driver.errors import NetworkError

app = FastAPI()

# Connect to Redis (Credit System)
# We use a simple retry for Redis too
r = redis.Redis(host='redis', port=6379, decode_responses=True)

# Connect to ClickHouse (Database)
# RETRY LOGIC: Try to connect 10 times, waiting 2 seconds each time
client = None
for i in range(10):
    try:
        # Connect as the new ADMIN user
        client = Client('clickhouse', user='admin', password='admin123')
        client.execute("SELECT 1")
        print("Connected to ClickHouse!")
        break
    except Exception as e:
        print(f"⏳ Database not ready yet, waiting... ({e})")
        time.sleep(2)

if client is None:
    print("Could not connect to Database after retries.")

# 1. Setup Database (Run once automatically)
@app.on_event("startup")
def startup():
    if client:
        client.execute("CREATE TABLE IF NOT EXISTS records (name String, email String, country String) ENGINE = MergeTree() ORDER BY country")

# 2. Admin: Create a User and give Credits
@app.post("/create_user")
def create_user(username: str, credits: int):
    api_key = str(uuid.uuid4())
    r.set(f"user:{api_key}", credits)
    return {"username": username, "api_key": api_key, "credits": credits}

# 3. The Data Endpoint (Costs 1 Credit)
@app.get("/get_data")
def get_data(country: str, api_key: str = Header(None)):
    # A. Check if API Key exists
    current_credits = r.get(f"user:{api_key}")
    
    if current_credits is None:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
    # B. Check if they have enough credits
    if int(current_credits) < 1:
        raise HTTPException(status_code=402, detail="Insufficient Credits")
    
    # C. Deduct 1 Credit
    r.decr(f"user:{api_key}", 1)
    
    # D. Get Data from DB
    if client:
        data = client.execute(f"SELECT * FROM records WHERE country = '{country}'")
        return {
            "data": data,
            "remaining_credits": int(current_credits) - 1
        }
    return {"error": "Database connection failed"}