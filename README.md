# Travel Assistant

## Features
- Extracts info from natural language (intent, destination, duration, etc).
- Understands user queries, and can handle:
  - Destination recommendation
  - Flight search by dates - **using AMADEUS api**
  - Packing recommendation by weather - **using OPEN-MATEO api**
  - Attractions recommendation by users preferences
  - General queries for fluent conversation
- Uses real-time weather data.
- Uses real-time filghts data
- Conversation history maintained.

## How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Ensure Ollama is running locally:
   ```bash
   ollama run llama3.2
   ```
3. Run the assistant:
   ```bash
   python main.py
   ```

## Prompt Engineering Notes
- One-shot JSON extraction for intent + entities.
- Chain-of-thought for destination reasoning.
- External API data blended contextually.

## Future Improvements:
- Conversation to be able to handle multiple intents, how will be done?
  1. Change intent prompt to return list of intents and required metadata
  2. In conversation handler - handle the list on intents and create a centric promprt from the list
- integrate better the apis to be able to handle more cases

## Example Conversation
See `transcripts/sample_convo.txt`