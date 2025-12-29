import json
import os
from pathlib import Path

import requests
from celery import shared_task


RESULTS_DIR = Path(os.getenv("API_RESULTS_DIR", "api_results"))


def _save_response(data, filename):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    filepath = RESULTS_DIR / filename
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
    return filepath


@shared_task(bind=True)
def fetch_holidays(self, api_params):
    api_key = os.getenv("HOLIDAYS_API_KEY")
    if not api_key:
        raise ValueError("HOLIDAYS_API_KEY is not set")

    response = requests.get(
        url="https://holidays.abstractapi.com/v1/",
        params={
            "api_key": api_key,
            "country": api_params.get("country", "US"),
            "year": api_params.get("year", 2025),
            "month": api_params.get("month", 12),
            "day": api_params.get("day", 25),
        },
        timeout=15,
    )
    response.raise_for_status()

    filename = (
        "holidays_"
        f'{api_params.get("country", "US")}_'
        f'{api_params.get("year", 2025)}_'
        f'{api_params.get("month", 12)}_'
        f'{api_params.get("day", 25)}.json'
    )
    filepath = _save_response(response.json(), filename)
    return {"file": str(filepath)}


@shared_task(bind=True)
def fetch_weather(self, api_params):
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        raise ValueError("WEATHER_API_KEY is not set")

    response = requests.get(
        url="http://api.weatherstack.com/current",
        params={
            "access_key": api_key,
            "query": api_params.get("query", "New York"),
        },
        timeout=15,
    )
    response.raise_for_status()

    query = api_params.get("query", "New York").replace(" ", "_")
    filename = f"weather_{query}.json"
    filepath = _save_response(response.json(), filename)
    return {"file": str(filepath)}
