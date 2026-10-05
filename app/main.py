from fastapi import FastAPI

from app.api.routes.tour_packages import router as tour_packages_router

app = FastAPI(
    title="Tour Package Management API"
)

app.include_router(tour_packages_router)


@app.get("/health")
def health():
    return {"status": "ok"}
