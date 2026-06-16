# Kalpavriksha Land Evaluator v1
# Author: Mangla Prasad Pandey
# Plugin for ChetnaOS

class LandEvaluator:
    def __init__(self):
        # Weightage score system
        self.weights = {
            "soil_ph": 0.25,
            "water_table": 0.20,
            "soil_type": 0.20,
            "climate": 0.20,
            "accessibility": 0.15
        }

    def score_ph(self, ph):
        if 6.5 <= ph <= 7.5:
            return 100
        elif 6.0 <= ph <= 8.0:
            return 70
        else:
            return 30

    def score_water(self, depth):
        if depth <= 80:
            return 100
        elif depth <= 150:
            return 70
        else:
            return 40

    def score_soil(self, soil):
        good_soils = ["loamy", "red", "sandy-loam"]
        if soil in good_soils:
            return 100
        elif soil == "black":
            return 70
        else:
            return 40

    def score_climate(self, temp):
        if 20 <= temp <= 35:
            return 100
        elif 15 <= temp <= 40:
            return 70
        else:
            return 40

    def score_access(self, road):
        if road == "highway":
            return 100
        elif road == "village":
            return 70
        else:
            return 40

    def evaluate(self, ph, water_depth, soil, temp, road):
        scores = {
            "pH Score": self.score_ph(ph),
            "Water Table Score": self.score_water(water_depth),
            "Soil Score": self.score_soil(soil),
            "Climate Score": self.score_climate(temp),
            "Accessibility Score": self.score_access(road),
        }

        final_score = (
            scores["pH Score"] * self.weights["soil_ph"]
            + scores["Water Table Score"] * self.weights["water_table"]
            + scores["Soil Score"] * self.weights["soil_type"]
            + scores["Climate Score"] * self.weights["climate"]
            + scores["Accessibility Score"] * self.weights["accessibility"]
        )

        return {
            "individual_scores": scores,
            "final_land_score": round(final_score, 2),
            "recommendation": self.get_recommendation(final_score)
        }

    def get_recommendation(self, score):
        if score >= 85:
            return "Perfect for Sandalwood Plantation"
        elif score >= 70:
            return "Good for Fruit Trees + Sandalwood Mix"
        else:
            return "Not Ideal — Needs Soil/Water Correction"


if __name__ == "__main__":
    ev = LandEvaluator()
    result = ev.evaluate(
        ph=7.0,
        water_depth=80,
        soil="loamy",
        temp=28,
        road="highway",
    )
    print(result)