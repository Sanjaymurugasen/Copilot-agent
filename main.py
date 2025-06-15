# from fastapi import FastAPI
# from pydantic import BaseModel

# app = FastAPI()

# # Activity level multipliers
# ACTIVITY_FACTORS = {
#     "Sedentary (little or no exercise)": 1.2,
#     "Lightly Active (light exercise 1-3 days/week)": 1.375,
#     "Moderately Active (moderate exercise 3-5 days/week)": 1.55,
#     "Very Active (hard exercise 6-7 days/week)": 1.725,
#     "Super Active (very hard exercise, physical job)": 1.9
# }

# # Gender options
# GENDER_OPTIONS = ["Male", "Female"]

# # Convert height in '5'9 format to inches
# def height_to_inches(height: str) -> int:
#     try:
#         ft, inch = map(int, height.split("'"))
#         return ft * 12 + inch
#     except ValueError:
#         raise ValueError("Invalid height format. Use format like '5'9")

# class UserData(BaseModel):
#     age: int
#     gender: str  # Should be "Male" or "Female"
#     weight_lbs: float
#     height_ft_in: str  # e.g., "5'9"
#     activity_level: str  # Should match one of ACTIVITY_FACTORS keys

# @app.post("/calculate")
# async def calculate_bmr_tdee(data: UserData):
#     # Validate gender
#     if data.gender not in GENDER_OPTIONS:
#         return {"error": f"Invalid gender: {data.gender}. Choose from {GENDER_OPTIONS}"}
    
#     # Validate activity level
#     if data.activity_level not in ACTIVITY_FACTORS:
#         return {"error": f"Invalid activity level: {data.activity_level}. Choose from {list(ACTIVITY_FACTORS.keys())}"}

#     # Convert height to inches
#     try:
#         height_inches = height_to_inches(data.height_ft_in)
#     except ValueError as ve:
#         return {"error": str(ve)}

#     # Convert height and weight to metric
#     height_cm = height_inches * 2.54
#     weight_kg = data.weight_lbs * 0.453592

#     # Calculate BMR using Mifflin-St Jeor
#     if data.gender == "Male":
#         bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * data.age) + 5
#     else:
#         bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * data.age) - 161

#     tdee = bmr * ACTIVITY_FACTORS[data.activity_level]

#     return {
#         "bmr": round(bmr),
#         "tdee": round(tdee),
#         "tips": {
#             "maintain": round(tdee),
#             "lose_weight": round(tdee - 500),
#             "gain_weight": round(tdee + 500)
#         }
#     }

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="BMR & TDEE Calculator", version="1.0.0")

# Activity level multipliers
ACTIVITY_FACTORS = {
    "Sedentary (little or no exercise)": 1.2,
    "Lightly Active (light exercise 1-3 days/week)": 1.375,
    "Moderately Active (moderate exercise 3-5 days/week)": 1.55,
    "Very Active (hard exercise 6-7 days/week)": 1.725,
    "Super Active (very hard exercise, physical job)": 1.9
}

# Gender options
GENDER_OPTIONS = ["Male", "Female"]

# Convert height in '5'9 format to inches
def height_to_inches(height: str) -> int:
    try:
        ft, inch = map(int, height.split("'"))
        return ft * 12 + inch
    except ValueError:
        raise ValueError("Invalid height format. Use format like '5'9")

class UserData(BaseModel):
    age: int
    gender: str  # Should be "Male" or "Female"
    weight_lbs: float
    height_ft_in: str  # e.g., "5'9"
    activity_level: str  # Should match one of ACTIVITY_FACTORS keys

@app.get("/")
async def root():
    return {"message": "BMR & TDEE Calculator API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "BMR TDEE Calculator"}

@app.get("/activity-levels")
async def get_activity_levels():
    return {"activity_levels": list(ACTIVITY_FACTORS.keys())}

@app.post("/calculate")
async def calculate_bmr_tdee(data: UserData):
    try:
        # Validate gender
        if data.gender not in GENDER_OPTIONS:
            raise HTTPException(status_code=400, detail=f"Invalid gender: {data.gender}. Choose from {GENDER_OPTIONS}")
        
        # Validate activity level
        if data.activity_level not in ACTIVITY_FACTORS:
            raise HTTPException(status_code=400, detail=f"Invalid activity level: {data.activity_level}. Choose from {list(ACTIVITY_FACTORS.keys())}")

        # Convert height to inches
        try:
            height_inches = height_to_inches(data.height_ft_in)
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))

        # Convert height and weight to metric
        height_cm = height_inches * 2.54
        weight_kg = data.weight_lbs * 0.453592

        # Calculate BMR using Mifflin-St Jeor
        if data.gender == "Male":
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * data.age) + 5
        else:
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * data.age) - 161

        tdee = bmr * ACTIVITY_FACTORS[data.activity_level]

        return {
            "success": True,
            "bmr": round(bmr),
            "tdee": round(tdee),
            "tips": {
                "maintain": round(tdee),
                "lose_weight": round(tdee - 500),
                "gain_weight": round(tdee + 500)
            },
            "user_info": {
                "age": data.age,
                "gender": data.gender,
                "activity_level": data.activity_level
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)