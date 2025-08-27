import requests

class HyundaiOffersAgent:
    URL = "https://www.hyundaiusa.com/var/hyundai/services/incentiveAws.featuredOfferByZip.service"

    def __init__(self, zip_code: str):
        self.zip_code = zip_code

    def fetch_raw_data(self) -> dict:
        params = {"brand": "hyundai", "zip": self.zip_code}
        headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
        resp = requests.get(self.URL, params=params, headers=headers)
        resp.raise_for_status()
        return resp.json()

    def extract_offers(self) -> list[dict]:
        offers = []
        raw = self.fetch_raw_data()

        for entry in raw.get("data", []):
            for year in entry.get("years", []):
                model_year = year.get("modelYear")
                for vehicle in year.get("vehicles", []):
                    model_name = vehicle.get("modelName")
                    fuel = vehicle.get("vehicleFuelType")
                    group = vehicle.get("modelGroupCode")
                    card_order = vehicle.get("cardOrder", {})

                    for key in ["lease1", "lease2", "lowApr", "savings"]:
                        offer = card_order.get(key)
                        if offer:
                            offers.append({
                                "model": model_name,
                                "modelYear": offer.get("modelYear", model_year),
                                "trim": offer.get("trimName"),
                                "type": key,
                                "monthlyPayment": float(offer["offerMonthlyPayment"]) if "offerMonthlyPayment" in offer else None,
                                "term": offer.get("term"),
                                "apr": offer.get("apr"),
                                "price": offer.get("price"),
                                "description": offer.get("shortDescription"),
                                "disclaimer": offer.get("disclaimer"),
                                "fuel": fuel,
                                "groupCode": group,
                            })
        return offers

    def get_offers_by_type(self, offer_type: str) -> list[dict]:
        return [o for o in self.extract_offers() if o["type"] in offer_type.lower()]

    def get_all_model_names(self) -> list[str]:
        offers = self.extract_offers()
        return sorted(set(o["model"] for o in offers if o.get("model")))

    def get_available_payment_offers(
        self,
        model: str | None = None,
        max_price: float | None = None
    ) -> list[dict]:
        filtered = []
        for offer in self.extract_offers():
            mp = offer.get("monthlyPayment")
            if not isinstance(mp, (int, float)):
                continue

            if model and offer.get("model", "").lower() != model.lower():
                continue

            if max_price is not None and mp > max_price:
                continue

            filtered.append(offer)
        return filtered
