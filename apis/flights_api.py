import requests

class AmadeusFlightProvider:
    AUTH_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
    LOCATIONS_URL = "https://test.api.amadeus.com/v1/reference-data/locations"
    FLIGHTS_URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = self._get_access_token()

    def _get_access_token(self):
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        response = requests.post(self.AUTH_URL, data=payload)
        response.raise_for_status()
        return response.json()['access_token']

    def _get_city_code(self, city_name: str) -> str:
        headers = {'Authorization': f'Bearer {self.token}'}
        params = {'keyword': city_name, 'subType': 'CITY'}

        response = requests.get(self.LOCATIONS_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get('data') and data['data'][0].get('iataCode'):
            return data['data'][0]['iataCode']
        else:
            raise ValueError(f"Could not find IATA code for city: {city_name}")

    def search_flights(self, origin: str, destination: str, departure_date: str, adults: int = 1, currency: str = "USD"):
        origin_code = origin if len(origin) == 3 else self._get_city_code(origin)
        destination_code = destination if len(destination) == 3 else self._get_city_code(destination)

        headers = {'Authorization': f'Bearer {self.token}'}
        params = {
            'originLocationCode': origin_code,
            'destinationLocationCode': destination_code,
            'departureDate': departure_date,
            'adults': adults,
            'currencyCode': currency,
            'max': 5
        }

        response = requests.get(self.FLIGHTS_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        flight_offers = []
        for offer in data.get('data', []):
            price = offer.get('price', {}).get('total')
            carrier = offer['validatingAirlineCodes'][0] if offer.get('validatingAirlineCodes') else "Unknown Airline"
            itinerary = offer.get('itineraries', [])[0]  # First leg
            segments = itinerary.get('segments', [])[0]  # First segment
            departure = segments.get('departure', {})
            arrival = segments.get('arrival', {})

            flight_offers.append({
                'carrier': carrier,
                'price': price,
                'currency': data.get('meta', {}).get('currency', currency),
                'departure_time': departure.get('at'),
                'departure_airport': departure.get('iataCode'),
                'arrival_time': arrival.get('at'),
                'arrival_airport': arrival.get('iataCode')
            })

        return flight_offers
