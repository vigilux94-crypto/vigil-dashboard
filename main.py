from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from datetime import datetime
import uvicorn
import json
import os
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "vigil_history.json"

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({"alerts": [], "billing": []}, f)

def save_to_db(category, entry):
    with open(DB_FILE, "r") as f:
        data = json.load(f)
    data[category].insert(0, entry)
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

@app.get("/api/status/")
def check_status(brpm: int, stress: int, lat: float = 0.0):
    res = {"color": "GREEN", "alert": "VORTEX STABLE"}
    if brpm < 8:
        res = {"color": "RED", "alert": "CRITICAL: RESPIRATORY DROP"}
        save_to_db("alerts", {"type": "RED", "val": f"{brpm} BRPM", "time": str(datetime.now())})
    return res

@app.get("/api/history/")
def get_history():
    with open(DB_FILE, "r") as f:
        return json.load(f)

@app.post("/api/billing/")
def log_billing(client_name: str, miles: float):
    entry = {
        "client": client_name,
        "receipt": f"B-LOG-{datetime.now().strftime('%M%S')}", 
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
        "miles": miles
    }
    save_to_db("billing", entry)
    return entry

@app.get("/api/export-csv/")
def export_csv():
    with open(DB_FILE, "r") as f:
        data = json.load(f)
    
    output = io.StringIO()
    output.write("ClientName,ReceiptID,Timestamp,Miles\n")
    for b in data['billing']:
        output.write(f"{b['client']},{b['receipt']},{b['timestamp']},{b['miles']}\n")
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=vigil_medicaid_report.csv"}
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
