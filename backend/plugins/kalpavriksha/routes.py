"""
Kalpavriksha domain plugin — land evaluation, ROI, crop planning.
Canonical location: backend.plugins.kalpavriksha
"""
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional

from .evaluator import LandEvaluator
from .roi import ROICalculator
from .crop_planner import CropPlanner

evaluator = LandEvaluator()
roi_calculator = ROICalculator()
crop_planner = CropPlanner()


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
    @app.post("/evaluate")
    async def evaluate_land(payload: EvaluateRequest):
        try:
            return evaluator.evaluate(
                ph=payload.ph,
                water_depth=payload.water_depth,
                soil=payload.soil,
                temp=payload.temp,
                road=payload.road,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

    @app.post("/roi")
    async def calc_roi(payload: ROIRequest):
        try:
            if payload.acres <= 0:
                raise HTTPException(status_code=400, detail="Acres must be a positive number")
            if payload.model not in roi_calculator.models:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid model. Available models: {list(roi_calculator.models.keys())}",
                )
            return roi_calculator.calculate(payload.model, payload.acres)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

    @app.post("/crop")
    async def api_crop(payload: CropRequest):
        try:
            data = {
                "soil_ph": payload.soil_ph,
                "temp": payload.temp,
                "water_depth": payload.water_depth,
                "soil_type": payload.soil_type,
                "road_access": payload.road_access,
                "acres": payload.acres,
            }
            return crop_planner.calculate(data)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
