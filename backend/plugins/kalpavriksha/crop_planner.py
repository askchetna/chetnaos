# kalpavriksha/crop_planner.py
# Simple heuristic Crop Planner for quick demo / integration

class CropPlanner:
    def __init__(self):
        # basic crop profiles (heuristic)
        # Each profile: preferred pH range, temp range (C), water depth preference (ft), soil types, base yield per acre (tons), price/kg approx (INR)
        self.profiles = {
            "Sandalwood": {"ph": (6.0,7.5), "temp": (20,35), "water_depth": (5,50), "soils":["loamy","sandy"], "yield": 0.02, "price": 300000}, # long-cycle asset, price shown as tree value
            "Mango": {"ph": (5.5,7.5), "temp": (20,35), "water_depth": (3,20), "soils":["loamy","clay"], "yield": 8, "price": 400}, # tons/acre, price/kg ~400
            "Banana": {"ph": (5.5,7.0), "temp": (22,35), "water_depth": (1,10), "soils":["loamy"], "yield": 30, "price": 20},
            "Teak": {"ph": (5.5,7.5), "temp": (20,34), "water_depth": (3,30), "soils":["sandy","loamy"], "yield": 0.1, "price": 50000},
            "RedSanders": {"ph": (6.0,7.5), "temp": (22,34), "water_depth": (4,20), "soils":["sandy","loamy"], "yield": 0.02, "price": 350000},
            "Agarwood": {"ph": (5.5,7.0), "temp": (25,35), "water_depth": (3,15), "soils":["loamy"], "yield": 0.01, "price": 800000}
        }

    def score_crop(self, crop_name, ph, temp, water_depth, soil_type, road_access):
        p = self.profiles[crop_name]
        score = 0

        # pH score
        ph_min, ph_max = p["ph"]
        if ph_min <= ph <= ph_max:
            score += 30
        else:
            # partial match
            diff = min(abs(ph - ph_min), abs(ph - ph_max))
            score += max(0, 30 - diff*5)

        # temperature
        tmin, tmax = p["temp"]
        if tmin <= temp <= tmax:
            score += 25
        else:
            diff = min(abs(temp - tmin), abs(temp - tmax))
            score += max(0, 25 - diff*2)

        # water depth
        wmin, wmax = p["water_depth"]
        if wmin <= water_depth <= wmax:
            score += 20
        else:
            diff = min(abs(water_depth - wmin), abs(water_depth - wmax))
            score += max(0, 20 - diff*2)

        # soil type
        if soil_type.lower() in p["soils"]:
            score += 15
        else:
            score += 5

        # road access preference (closer/highway gives premium to short-term crops)
        if road_access and road_access.lower() in ("highway","good","paved"):
            score += 10
        else:
            score += 5

        return round(score, 1)

    def estimate_economics(self, crop_name, acres):
        p = self.profiles[crop_name]
        # naive yearly revenue estimate: yield * price * acres
        # note: for trees we put tree-value; for short-term crops use yield & price
        if crop_name in ("Sandalwood","RedSanders","Teak","Agarwood"):
            # tree crops long term: show per-acres asset value range (demo)
            value = p["price"] * acres  # simplistic (price per mature acre equivalent)
            return {"yearly_revenue_estimate": None, "asset_value_estimate": value}
        else:
            # annual crop
            yearly_revenue = p["yield"] * p["price"] * acres
            # estimate cost as % of revenue
            yearly_cost = yearly_revenue * 0.35
            yearly_profit = yearly_revenue - yearly_cost
            return {"yearly_revenue_estimate": round(yearly_revenue,2), "yearly_cost_estimate": round(yearly_cost,2), "yearly_profit_estimate": round(yearly_profit,2)}

    def calculate(self, data):
        """
        data: {
          "soil_ph": float,
          "temp": float,
          "water_depth": float,
          "soil_type": "loamy",
          "road_access": "highway" or "katcha",
          "acres": float (optional)
        }
        """
        ph = float(data.get("soil_ph", 7.0))
        temp = float(data.get("temp", 28.0))
        water_depth = float(data.get("water_depth", 10.0))
        soil_type = data.get("soil_type", "loamy")
        road_access = data.get("road_access", "katcha")
        acres = float(data.get("acres", 1.0))

        scores = {}
        for crop in self.profiles:
            scores[crop] = self.score_crop(crop, ph, temp, water_depth, soil_type, road_access)

        # sort by score
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # build recommendations with economics
        recommendations = []
        for crop, sc in ranked:
            econ = self.estimate_economics(crop, acres)
            recommendations.append({
                "crop": crop,
                "score": sc,
                "economics": econ,
                "note": "Long-cycle asset" if crop in ("Sandalwood","RedSanders","Teak","Agarwood") else "Annual/Short-term crop"
            })

        return {
            "input": {"soil_ph": ph, "temp": temp, "water_depth": water_depth, "soil_type": soil_type, "road_access": road_access, "acres": acres},
            "ranked_recommendations": recommendations
        }