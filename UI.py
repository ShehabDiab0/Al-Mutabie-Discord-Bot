import discord
from discord.ext import commands
from discord import app_commands
import database
import dotenv # type: ignore
import os

class DeleteSelectMenu(discord.ui.View):
    def __init__(self,owner_id,guild_id):
        super().__init__()
        self.owner_id = owner_id
        self.guild_id = guild_id
        # self.tasks = database.get_tasks(self.owner_id,self.guild_id)
        

    @discord.ui.select( # the decorator that lets you specify the properties of the select menu
        placeholder = "Choose a Flavor!", # the placeholder text that will be displayed if nothing is selected
        min_values = 1, # the minimum number of values that must be selected by the users
        max_values = 1, # the maximum number of values that can be selected by the users
        options = [ # the list of options from which users can choose, a required field
            discord.SelectOption(
                label="Vanilla",
                description="Pick this if you like vanilla!"
            ),
            discord.SelectOption(
                label="Chocolate",
                description="Pick this if you like chocolate!"
            ),
            discord.SelectOption(
                label="Strawberry",
                description="Pick this if you like strawberry!"
            ),
            discord.SelectOption(
                label="Mint",
                description="Pick this if you like mint!"
            ),
            discord.SelectOption(
                label="Caramel",
                description="Pick this if you like caramel!"
            ),
            discord.SelectOption(
                label="Peanut Butter",
                description="Pick this if you like peanut butter!"
            ),
            discord.SelectOption(
                label="Cookies and Cream",
                description="Pick this if you like cookies and cream!"
            ),

        ]
    )
    async def select_callback(self, select, interaction): # the function called when the user is done selecting options
        await interaction.response.send_message(f"Awesome! I like {select.values[0]} too!")


