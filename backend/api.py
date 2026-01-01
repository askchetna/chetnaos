"""
Kalpavriksha API Routes - FastAPI endpoints
These routes are integrated into the main FastAPI app
"""
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional

from kalpavriksha.evaluator import LandEvaluator
from kalpavriksha.roi import ROICalculator
from kalpavriksha.crop_planner import CropPlanner

# Initialize evaluators
evaluator = LandEvaluator()
roi_calculator = ROICalculator()
crop_planner = CropPlanner()

# Request Models
class EvaluateRequest(BaseModel):
    ph: float
    water_depth: float
    soil: str
    temp: float
    road: str

class ROIRequest(BaseModel):
    acres: float
    model: str

class CropRequest(BaseModel):
    soil_ph: float
    temp: float
    water_depth: float
    soil_type: str
    road_access: str
    acres: Optional[float] = 1.0

def setup_kalpavriksha_routes(app):
    """Setup Kalpavriksha routes on the FastAPI app"""
    
    @app.post("/evaluate")
    async def evaluate_land(payload: EvaluateRequest):
        """Land evaluation endpoint"""
        try:
            result = evaluator.evaluate(
                ph=payload.ph,
                water_depth=payload.water_depth,
                soil=payload.soil,
                temp=payload.temp,
                road=payload.road,
            )
            return result
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

    @app.post("/roi")
    async def calc_roi(payload: ROIRequest):
        """ROI calculation endpoint"""
        try:
            if payload.acres <= 0:
                raise HTTPException(status_code=400, detail="Acres must be a positive number")
            
            if payload.model not in roi_calculator.models:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid model. Available models: {list(roi_calculator.models.keys())}"
                )
            
            result = roi_calculator.calculate(payload.model, payload.acres)
            return result
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

    @app.post("/crop")
    async def api_crop(payload: CropRequest):
        """Crop planning endpoint"""
        try:
            data = {
                "soil_ph": payload.soil_ph,
                "temp": payload.temp,
                "water_depth": payload.water_depth,
                "soil_type": payload.soil_type,
                "road_access": payload.road_access,
                "acres": payload.acres
            }
            result = crop_planner.calculate(data)
            return result
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
