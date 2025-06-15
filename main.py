from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
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

class UserData(BaseModel):
    age: int
    gender: str  # Should be "Male" or "Female"
    weight_lbs: float
    height_feet: int  # Feet as integer
    height_inches: int  # Inches as integer
    activity_level: str  # Should match one of ACTIVITY_FACTORS keys
    
    @validator('height_feet')
    def validate_feet(cls, v):
        if v < 0 or v > 8:  # Reasonable range for human height
            raise ValueError('Height in feet must be between 0 and 8')
        return v
    
    @validator('height_inches')
    def validate_inches(cls, v):
        if v < 0 or v >= 12:  # Inches should be 0-11
            raise ValueError('Height in inches must be between 0 and 11')
        return v
    
    @validator('age')
    def validate_age(cls, v):
        if v < 1 or v > 120:
            raise ValueError('Age must be between 1 and 120')
        return v
    
    @validator('weight_lbs')
    def validate_weight(cls, v):
        if v <= 0 or v > 1000:  # Reasonable weight range
            raise ValueError('Weight must be between 0 and 1000 lbs')
        return v

@app.get("/")
async def root():
    return {"message": "BMR & TDEE Calculator API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "BMR TDEE Calculator"}

@app.get("/activity-levels")
async def get_activity_levels():
    return {"activity_levels": list(ACTIVITY_FACTORS.keys())}

@app.get("/gender-options")
async def get_gender_options():
    return {"gender_options": GENDER_OPTIONS}

@app.post("/calculate")
async def calculate_bmr_tdee(data: UserData):
    try:
        # Validate gender
        if data.gender not in GENDER_OPTIONS:
            raise HTTPException(status_code=400, detail=f"Invalid gender: {data.gender}. Choose from {GENDER_OPTIONS}")
        
        # Validate activity level
        if data.activity_level not in ACTIVITY_FACTORS:
            raise HTTPException(status_code=400, detail=f"Invalid activity level: {data.activity_level}. Choose from {list(ACTIVITY_FACTORS.keys())}")

        # Convert height to total inches
        total_height_inches = (data.height_feet * 12) + data.height_inches

        # Convert height and weight to metric
        height_cm = total_height_inches * 2.54
        weight_kg = data.weight_lbs * 0.453592

        # Calculate BMR using Mifflin-St Jeor equation
        if data.gender == "Male":
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * data.age) + 5
        else:
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * data.age) - 161

        # Calculate TDEE
        tdee = bmr * ACTIVITY_FACTORS[data.activity_level]

        return {
            "success": True,
            "bmr": round(bmr),
            "tdee": round(tdee),
            "calorie_goals": {
                "maintain_weight": round(tdee),
                "lose_weight": round(tdee - 500),  # 500 calorie deficit for ~1 lb/week loss
                "gain_weight": round(tdee + 500)   # 500 calorie surplus for ~1 lb/week gain
            },
            "user_info": {
                "age": data.age,
                "gender": data.gender,
                "weight_lbs": data.weight_lbs,
                "height": f"{data.height_feet}'{data.height_inches}\"",
                "total_height_inches": total_height_inches,
                "activity_level": data.activity_level
            },
            "conversions": {
                "weight_kg": round(weight_kg, 1),
                "height_cm": round(height_cm, 1)
            }
        }
    
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

# Example endpoint to show expected request format
@app.get("/example-request")
async def get_example_request():
    return {
        "example_request": {
            "age": 30,
            "gender": "Male",
            "weight_lbs": 180.5,
            "height_feet": 5,
            "height_inches": 10,
            "activity_level": "Moderately Active (moderate exercise 3-5 days/week)"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
