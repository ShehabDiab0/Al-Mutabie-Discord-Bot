import os
import dotenv # type: ignore THIS IS TO FIX PYLANCE ON MY MACHINE
import bot


if __name__ == "__main__":
    dotenv.load_dotenv()
    bot.run(os.getenv("API_TOKEN"))