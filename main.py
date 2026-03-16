from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
from datetime import datetime

# --- THE BRAIN ---
class RelapsePredictor(nn.Module):
    def __init__(self, input_size=8):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_size, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )
    def forward(self, x):
        return self.fc(x)

model = RelapsePredictor(input_size=8)
optimizer = optim.Adam(model.parameters(), lr=0.01)
criterion = nn.BCELoss()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Global variable to store the "Current" vector for training
last_vector = None

@app.get("/api/vitals/")
def get_vitals():
    global last_vector
    # Generate fresh data
    df = pd.DataFrame({
        "HR": [np.random.normal(70, 5)], "HRV": [np.random.normal(50, 10)],
        "Stress": [np.clip(np.random.normal(30, 15), 0, 100)], "Sleep": [np.random.randint(50, 100)],
        "Activity": [np.random.randint(0, 100)], "Craving": [np.random.randint(0, 100)],
        "Mood": [np.random.randint(1, 10)], "HighRiskLocation": [np.random.choice([0,1], p=[0.9,0.1])]
    })
    last_vector = torch.tensor(df.values, dtype=torch.float32)
    
    with torch.no_grad():
        prediction = model(last_vector).item()
    
    return {
        "integrity": round((1 - prediction) * 100, 1),
        "risk_prob": round(prediction, 4),
        "time": datetime.now().strftime("%H:%M:%S")
    }

@app.post("/api/train/")
async def train_model(request: Request):
    global last_vector
    data = await request.json()
    label = torch.tensor([[float(data['actual_outcome'])]], dtype=torch.float32)
    
    # Training Step
    model.train()
    optimizer.zero_grad()
    output = model(last_vector)
    loss = criterion(output, label)
    loss.backward()
    optimizer.step()
    model.eval()
    
    print(f"[AI TRAINING] Outcome recorded: {data['actual_outcome']} | Loss: {loss.item():.4f}")
    return {"status": "Model Updated", "loss": loss.item()}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
