class ROICalculator:
    def __init__(self):
        # Custom plantation models
        self.models = {
            "sandalwood": {
                "years": 12,
                "cost_per_acre": 250000,
                "yield_value": 3200000,
            },
            "red_sanders": {
                "years": 15,
                "cost_per_acre": 180000,
                "yield_value": 5000000,
            },
            "fruit_mix": {
                "years": 8,
                "cost_per_acre": 150000,
                "yield_value": 900000,
            },
        }

    def calculate(self, model_name, acres):
        # Validate model_name
        if model_name not in self.models:
            raise ValueError(
                f"Invalid model '{model_name}'. Available models: {list(self.models.keys())}"
            )
        
        # Validate acres
        if acres <= 0:
            raise ValueError("Acres must be a positive number")
        
        model = self.models[model_name]

        total_cost = model["cost_per_acre"] * acres
        total_yield = model["yield_value"] * acres
        net_profit = total_yield - total_cost
        
        # Prevent division by zero (shouldn't happen with validation, but safety check)
        if total_cost == 0:
            raise ValueError("Total cost cannot be zero")
        
        roi_percent = (net_profit / total_cost) * 100

        return {
            "model": model_name,
            "acres": acres,
            "total_cost": total_cost,
            "total_yield": total_yield,
            "net_profit": net_profit,
            "roi_percent": round(roi_percent, 2),
            "duration_years": model["years"],
        }