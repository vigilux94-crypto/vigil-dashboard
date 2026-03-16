from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

app = FastAPI(title="Vigil Backend API")

# Security Bridge: Allows the HTML file to talk to the Python file
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VigilEngine:
    def __init__(self):
        self.is_locked = False # Unlocked for testing UI

    def get_traffic_light(self, brpm: int, stress_level: int):
        if brpm < 8:
            return {"color": "RED", "alert": "RED STATUS: Critical Vitals (Overdose Risk). Alerting EMS."}
        elif stress_level > 80:
            return {"color": "YELLOW", "alert": "YELLOW STATUS: High Stress/Craving. Triggering Peer Support."}
        return {"color": "GREEN", "alert": "GREEN STATUS: Vitals Stable. Client Compliant."}

engine = VigilEngine()

@app.get("/api/status/")
def check_vitals(brpm: int, stress: int):
    return engine.get_traffic_light(brpm, stress)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
