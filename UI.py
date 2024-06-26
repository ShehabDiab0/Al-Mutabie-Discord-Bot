import discord
from discord.ext import commands
from discord.ui import View, Modal , TextInput, Select, Button 
from discord.components import SelectOption
from discord import TextStyle
from discord import app_commands
import database
import dotenv # type: ignore
import os

class SingleTaskDropDown(Select):
    def __init__(self, tasks, modal) -> None:
        super().__init__(placeholder="Select Task",
                         options=[SelectOption(label=task.description, value=str(task.task_id)) for task in tasks],
                         min_values=1,
                         max_values=1)
        self.modal = modal

    async def callback(self, interaction: discord.Interaction):
        self.modal.selected_value = self.values[0]
        await interaction.response.send_modal(self.modal)
class MultiTaskDropDown(Select):
    def __init__(self, tasks, btn) -> None:
        super().__init__(placeholder="Select Task",
                         options=[SelectOption(label=task.description, value=str(task.task_id)) for task in tasks],
                         min_values=1,
                         max_values=len(tasks))
        self.btn = btn
        
    async def callback(self, interaction: discord.Interaction):
        self.btn.selected_values = self.values
        await interaction.response.defer()

class DeleteButton(Button):
    def __init__(self) -> None:
        super().__init__(label="Delete", style=discord.ButtonStyle.danger)
        self.selected_values = []
        
    async def callback(self, interaction: discord.Interaction):
        print("=Selected Values", self.selected_values)
        for task in self.selected_values:
            print("Task", task)
            database.delete_task(task)
        await interaction.response.send_message("Tasks Deleted", ephemeral=True)
class DeleteTaskView(View):
    def __init__(self, tasks) -> None:
        super().__init__()
        self.tasks = tasks
        self.delete_button = DeleteButton()
        self.select = MultiTaskDropDown(tasks, self.delete_button)

        self.add_item(self.select)
        self.add_item(self.delete_button)


# class UpdateButton(Button):
#     def __init__(self) -> None:
#         super().__init__(label="Update", style=discord.ButtonStyle.primary)
#         self.selected_value = []
#         self.new_value = ""
        
#     async def callback(self, interaction: discord.Interaction):
#         database.update_subscriber_task(self.selected_value[0], self.new_value)
#         await interaction.response.send_message("Task Updated", ephemeral=True)
class UpdateTextInput(TextInput):
    def __init__(self,new_placeholder,new_label) -> None:
        super().__init__(placeholder=new_placeholder,label=new_label)
        self.required = False
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

class UpdateTaskModal(Modal):
    def __init__(self, tasks) -> None:
        super().__init__(title="Update Task")
        self.tasks = tasks
        self.selected_value = None
        self.task_desc_input = UpdateTextInput(new_placeholder="Write New Description", new_label="Task Description")
        self.task_completion_inptut = UpdateTextInput(new_placeholder="Write New Completion Percentage", new_label="Task Completion")
        self.add_item(self.task_desc_input)
        self.add_item(self.task_completion_inptut)

    async def on_submit(self, interaction: discord.Interaction):
        self.new_desc = self.task_desc_input.value
        self.new_completion = self.task_completion_inptut.value
        
        if(self.new_desc != "" and self.new_completion != ""): 
            database.update_task_desc(self.selected_value, self.new_desc)
            database.update_task_completion_percentage(self.selected_value, self.new_completion)
            await interaction.response.send_message("Task Description and Completion Updated", ephemeral=True)
        elif(self.new_completion == "" and self.new_desc != ""):
            database.update_task_desc(self.selected_value, self.new_desc)
            await interaction.response.send_message("Task Description Updated", ephemeral=True)
        elif(self.new_desc == "" and self.new_completion != ""):
            database.update_task_completion_percentage(self.selected_value, self.new_completion)
            await interaction.response.send_message("Task Completion Updated", ephemeral=True)
        else:
            await interaction.response.send_message("No Changes Made", ephemeral=True)
        
# Bonjour
class UpdateTaskView(View):
    def __init__(self, tasks) -> None:
        super().__init__()
        self.tasks = tasks
        self.modal = UpdateTaskModal(tasks)
        self.select = SingleTaskDropDown(self.tasks,self.modal)
        self.add_item(self.select)
        

    






