from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from geopy.distance import geodesic

app = FastAPI()

# District data
districts = {
    "WK": {"name": "Wakiso", "latitude": 0.395800, "longitude": 32.479160},
    "TR": {"name": "Tororo", "latitude": 0.694330, "longitude": 34.179499},
    "SRT": {"name": "Soroti", "latitude": 1.714500, "longitude": 33.619461},
    "MK": {"name": "Mukono", "latitude": 0.356610, "longitude": 32.752300},
    "MPG": {"name": "Mpigi", "latitude": 0.231213, "longitude": 32.318724},
    "MBR": {"name": "Mbarara", "latitude": -0.605675, "longitude": 30.648550},
    "MBL": {"name": "Mbale", "latitude": 1.070940, "longitude": 34.179008},
    "MSK": {"name": "Masaka", "latitude": -0.346950, "longitude": 31.739270},
    "LRA": {"name": "Lira", "latitude": 2.235000, "longitude": 32.909722},
    "KSE": {"name": "Kasese", "latitude": 0.169800, "longitude": 30.070000},
    "KLA": {"name": "Kampala", "latitude": 0.322805, "longitude": 32.574841},
    "KBL": {"name": "Kabale", "latitude": -1.241956, "longitude": 29.985616},
    "JJA": {"name": "Jinja", "latitude": 0.424444, "longitude": 33.204167},
    "HMA": {"name": "Hoima", "latitude": 1.430547, "longitude": 31.352270},
    "FRTP": {"name": "Fort Portal", "latitude": 0.654626, "longitude": 30.280117},
    "BSA": {"name": "Busia", "latitude": 0.467000, "longitude": 34.090000},
    "BSH": {"name": "Bushenyi", "latitude": -0.542377, "longitude": 30.196452},
    "BGY": {"name": "Bundibugyo", "latitude": 0.707531, "longitude": 30.063635},
    "AR": {"name": "Arua", "latitude": 3.173538, "longitude": 31.309866},
    "NTG": {"name": "Ntungamo", "latitude": -0.875076, "longitude": 30.265696},
}

# Risk factors
risk_factors = {
    "GRC": 1.08,
    "BNP": 1.15,
    "CMP": 1.12,
    "FPW": 1.15,
    "FPV": 1.24,
    "HVC": 1.25,
    "STP": 1.13,
    "LCT": 1.12,
    "EGT": 1.35,
    "BPF": 1.26
}

# Delivery time risk factors
time_risk_factors = {
    "48 HOUR": 0.7,
    "5 days": 0.65,
    "7 days": 0.55,
}

# Pydantic model for the request body
class DeliveryCostRequest(BaseModel):
    pickup_code: str
    delivery_code: str
    item_category: str
    weight: float
    delivery_time: str

# Cost calculation function
def calculate_cost(weight, distance, risk_factor, time_risk_factor):
    unit_cost_per_kg_per_km = 40  # This can change based on the weight of the user.
    weight_impact_cost = weight * distance * unit_cost_per_kg_per_km
    total_cost = weight_impact_cost * risk_factor * time_risk_factor
    return total_cost

# Distance calculation function
def calculate_distance(pickup_code, delivery_code):
    pickup_coords = (districts[pickup_code]['latitude'], districts[pickup_code]['longitude'])
    delivery_coords = (districts[delivery_code]['latitude'], districts[delivery_code]['longitude'])
    return geodesic(pickup_coords, delivery_coords).km

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/calculate_delivery_cost")
def calculate_delivery_cost(request: DeliveryCostRequest):
    # Get risk factors
    risk_factor = risk_factors.get(request.item_category)
    time_risk_factor = time_risk_factors.get(request.delivery_time)

    # Validate inputs
    if not risk_factor:
        return {"error": "Invalid item category"}
    if not time_risk_factor:
        return {"error": "Invalid delivery time"}

    # Calculate distance
    distance = calculate_distance(request.pickup_code, request.delivery_code)

    # Calculate total cost
    total_cost = calculate_cost(request.weight, distance, risk_factor, time_risk_factor)

    return {
        "pickup": districts[request.pickup_code]['name'],
        "delivery": districts[request.delivery_code]['name'],
        "distance_km": distance,
        "total_cost": total_cost
    }
