from fastapi import FastAPI, Query, Path
from hyundai_agent import HyundaiOffersAgent
from fastapi.openapi.utils import get_openapi

app = FastAPI(root_path="/hyundai")

@app.get("/offers")
def get_all_offers(zip: str = Query(...)):
    agent = HyundaiOffersAgent(zip)
    return agent.extract_offers()


@app.get("/offers/with-payment")
def get_offers_with_payment(
    zip: str = Query(...),
    model: str | None = Query(None),
    maxPrice: float | None = Query(None)
):
    agent = HyundaiOffersAgent(zip)
    return agent.get_available_payment_offers(model=model, max_price=maxPrice)

@app.get("/offers/{offer_type}")
def get_filtered(
    offer_type: str = Path(..., description="Offer type: lease, finance, rebate"),
    zip: str = Query(...)
):
    agent = HyundaiOffersAgent(zip)
    return agent.get_offers_by_type(offer_type)

@app.get("/models")
def list_models(zip: str = Query(...)):
    agent = HyundaiOffersAgent(zip)
    return agent.get_all_model_names()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Hyundai Offer API",
        version="1.0.0",
        description="API to get Hyundai lease/finance/cash offers by ZIP",
        routes=app.routes,
    )

    # Add servers for GPT to understand
    openapi_schema["servers"] = [
        {"url": "https://hyundai-api-agent.onrender.com"}
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi