from agent.agent import LaptopAgent

from dotenv import load_dotenv

load_dotenv()


def main():

    agent = LaptopAgent()

    print("\nLaptop Agent v0.1")
    print("Type 'exit' to quit.\n")

    while True:

        user_input = input("You > ")

        if user_input.lower() == "exit":
            print("Goodbye.")
            break

        try:
            response = agent.respond(user_input)

            print(f"\nAgent > {response}\n")

        except Exception as error:
            print(f"\nError: {error}\n")

if __name__ == "__main__":
    main()
