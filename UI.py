import discord
from discord.ext import commands
from discord.ui import View, Modal , TextInput, Select, Button 
from discord.components import SelectOption
from discord import TextStyle
from discord import app_commands
import database
import dotenv # type: ignore
import os



class TaskView(View):
    def __init__(self, tasks) -> None:
        super().__init__()
        self.tasks = tasks
        self.options = [SelectOption(label=task.description, value=str(task.task_id)) for task in tasks]
        print("Options")
        print(self.options)

        self.select = Select(placeholder="Select Task",
                             options=self.options,
                             min_values=1,
                             max_values=len(self.tasks))
         
        self.select.call_back = self.select_callback
        self.add_item(self.select)

        self.delete = Button(label="Delete", style=discord.ButtonStyle.danger)
        # self.delete.call_back = self.delete_callback
        self.add_item(self.delete)
        
    async def select_callback(self, interaction: discord.Interaction, select: Select):
        selected_tasks = [task for task in self.tasks if task.task_id in select.values]
        print("Trying to Delete")
        for task in selected_tasks:
            database.delete_task(task)
        await interaction.response.send_message("Tasks Deleted", ephemeral=True)

    






