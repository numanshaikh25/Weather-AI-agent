import httpx


def get_weather(city: str) -> str:
    """Fetch current weather for a city using wttr.in API.

    Args:
        city: Name of the city to get weather for

    Returns:
        Weather condition and temperature as a string
    """
    url = f"https://wttr.in/{city.lower()}.?format=%C+%t"

    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        return response.text.strip()
    except httpx.HTTPError as e:
        return f"Error fetching weather: {e}"
