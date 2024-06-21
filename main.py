import os
import dotenv


def main():
    dotenv.load_dotenv()
    print(os.getenv("API_TOKEN"))

if __name__ == "__main__":
    main()