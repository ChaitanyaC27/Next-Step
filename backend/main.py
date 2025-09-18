from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from auth_routes import router as auth_router  # ✅ Importing authentication routes
from nontech_test import router as non_tech_router  # ✅ Importing non-technical test routes
from gap_test import router as gap_router
from technical_test import router as tech_router
from results import router as results_router
from final_result import router as final_result_router


app = FastAPI()

# Create database tables (if not already created)
Base.metadata.create_all(bind=engine)

# Enable CORS (Adjust as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for debugging (secure it later),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Ensures OPTIONS method works for preflight
    allow_headers=["Content-Type", "Authorization"],  # Only allow necessary headers
)

# Root Endpoint
@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}



# Include authentication routes
app.include_router(auth_router, prefix="/auth")  # ✅ This ensures /auth/verify-token exists

# Include non-technical test routes
app.include_router(non_tech_router, prefix="/nontech_test")  # ✅ This ensures /non_tech_test/submit exists

app.include_router(gap_router, prefix="/gap_test")

app.include_router(tech_router)

app.include_router(results_router)

app.include_router(final_result_router)
