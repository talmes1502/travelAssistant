from cli import get_input, print_output
from conversation import TravelAssistant

def main():
    print("Welcome to your Travel Assistant!\nI'm here to help you plan you next amazing trip\nI'm an expert in:")
    print('1. Filght Search and prices\n2. Destination Recommendations\n3. Packing\n4. Attractions\n')
    assistant = TravelAssistant()

    while True:
        user_input = get_input("Ask me anything (or type 'exit' to quit): \n")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        response = assistant.chat(user_input)
        print_output(response)

if __name__ == "__main__":
    main()