import json
from llm import query_llm
from config_reader import ConfigReader
from apis.weather_api import WeatherService
from apis.flights_api import AmadeusFlightProvider
from prompts import intent_and_entities_prompt, destination_prompt, packing_prompt_template, attractions_prompt_template, general_travel_prompt_template


class TravelAssistant:
    def __init__(self):
        self.history = []
        self._config = ConfigReader()
        self._flights_api = AmadeusFlightProvider(client_id=self._config.amadeus_cred['CLIENT_ID'],
                                                  client_secret=self._config.amadeus_cred['CLIENT_SECRET'])
        self._weather_api = WeatherService()

    def parse_intent_and_entities(self, user_input: str) -> dict:
        prompt = intent_and_entities_prompt.format(topics_list=self._config.prompt_classification,
                                                   user_input=user_input)
        response = query_llm(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"intent": "unknown", "destination": None, "duration": None, "origin": None, "date": None}

    def chat(self, user_input: str):
        parsed = self.parse_intent_and_entities(user_input)
        intent = parsed.get("intent", "unknown")
        destination = parsed.get("destination", None)
        duration = parsed.get("duration", None)
        origin = parsed.get("origin", None)
        date = parsed.get("date", None)

        if intent == "unknown":
            return "Sorry, I couldn't understand that. Can you rephrase?"

        if intent == 'flights':
            response = self._handle_flight_intent(destination=destination,origin=origin, date=date)

        if intent in ["packing", "attractions"] and not destination:
            destination = input("Which destination are you referring to? ").strip()
        if intent == "packing" and not duration:
            duration = input("For how many days? ").strip()

        if intent == "general travel":
            prompt = general_travel_prompt_template
            response = query_llm(prompt, self.history + [f"User: {user_input}"])
        elif intent == "destination":
            prompt = destination_prompt
            response = query_llm(prompt, self.history + [f"User: {user_input}"])
        elif intent == "packing":
            weather = self._handle_weather(destination=destination, date=date)
            prompt = packing_prompt_template.format(destination=destination, duration=duration, weather=weather)
            response = query_llm(prompt, self.history + [f"User: {user_input}"])
        elif intent == "attractions":
            prompt = attractions_prompt_template.format(destination=destination)
            response = query_llm(prompt, self.history + [f"User: {user_input}"])

        self.history.append(f"User: {user_input}")
        self.history.append(f"Assistant: {response}")
        return response

    def _handle_flight_intent(self, destination, origin, date):
        if not origin:
            origin = input("From which city are you flying? ").strip()
        if not destination:
            destination = input("To which city are you flying? ").strip()
        if not date:
            date = input("What is the departure date? (YYYY-MM-DD): ").strip()

        try:
            flights = self._flights_api.search_flights(origin=origin, destination=destination,
                                                          departure_date=date)
            if flights:
                response_lines = [f"Here are flights from {origin} to {destination} on {date}:"]
                for flight in flights:
                    response_lines.append(
                        f"- {flight['carrier']}: {flight['price']} {flight['currency']} | "
                        f"{flight['departure_airport']} → {flight['arrival_airport']} at {flight['departure_time']}")
                response = "\n".join(response_lines)
            else:
                response = f"Sorry, no flights found from {origin} to {destination} on {date}."
        except Exception as e:
            response = f"Error fetching flights: {e}"

        return response

    def _handle_weather(self,destination, date):
        weather_data = self._weather_api.get_weather(destination, date)

        if weather_data.get("temperature") is not None:
            weather_info = f"Current temperature {weather_data['temperature']}°C, {weather_data['description']}"
        elif weather_data.get("temperature_max") is not None:
            weather_info = f"Expected temperatures between {weather_data['temperature_min']}°C and {weather_data['temperature_max']}°C"
        else:
            weather_info = "Weather data unavailable"

        return weather_info
