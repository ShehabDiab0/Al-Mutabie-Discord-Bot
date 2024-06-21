import os
import dotenv
import discord

def main():
    client = discord.Client(intents=discord.Intents.all())

    @client.event
    async def on_message(message):
        if message.author != client.user:
            await message.channel.send("HEY!")

    dotenv.load_dotenv()
    client.run(os.getenv("API_TOKEN"))

if __name__ == "__main__":
    main()