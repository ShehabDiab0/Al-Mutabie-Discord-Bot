import discord
from discord.ext import commands
from discord.ui import View, Modal , TextInput, Select, Button 
from discord.components import SelectOption
from discord import TextStyle
from discord import app_commands
import helpers
from data_access import tasks_access
from data_access import subscribers_access
from models.subscriber import Subscriber

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
            tasks_access.delete_task(task)
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
    def __init__(self, new_placeholder, new_label) -> None:
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
            tasks_access.update_task_desc(self.selected_value, self.new_desc)
            tasks_access.update_task_completion_percentage(self.selected_value, self.new_completion)
            await interaction.response.send_message("Task Description and Completion Updated", ephemeral=True)
        elif(self.new_completion == "" and self.new_desc != ""):
            tasks_access.update_task_desc(self.selected_value, self.new_desc)
            await interaction.response.send_message("Task Description Updated", ephemeral=True)
        elif(self.new_desc == "" and self.new_completion != ""):
            tasks_access.update_task_completion_percentage(self.selected_value, self.new_completion)
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


class SelfReportInput(TextInput):
    def __init__(self, tasks) -> None:
        super().__init__(label="Enter Task Completion Percentages (Co)", 
                         placeholder="1- Read a 20 pages - [0.6]\n(Copy the Output of show_tasks command and paste here)",
                         style=discord.TextStyle.long)
        self.tasks = tasks

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()


class SelfReportModal(Modal):
    def __init__(self, tasks) -> None:
        super().__init__(title="Self Report")
        self.tasks = tasks
        self.formatted_text = helpers.convert_tasks_to_self_report(tasks)
        self.input = SelfReportInput(self.tasks)
        self.add_item(self.input)
         

    async def on_submit(self, interaction: discord.Interaction):
        completion_percentages = helpers.convert_formatted_tasks_to_percentages(self.input.value)
        for i, task in enumerate(self.tasks):
            tasks_access.update_task_completion_percentage(task.task_id, completion_percentages[i])
        await interaction.response.send_message("Self Report Completed", ephemeral=True)
        


class RegisterationInput(TextInput):
    def __init__(self, placeholder, label, required=False) -> None:
        super().__init__(label=label, 
                         placeholder=placeholder,
                         style=discord.TextStyle.long)
        self.required = required

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()



class RegisterationModal(Modal):
    def __init__(self) -> None:
        super().__init__(title="Registeration")
        self.default_yellow_card_input = RegisterationInput(placeholder="Write your default Yellow card description.", label="Default Yellow Card Description", required=True)
        self.default_red_card_input = RegisterationInput(placeholder="Write your default Red card description.", label="Default Red Card Description", required=True)
        self.threshold = RegisterationInput(placeholder="Write Your threshold percentage you want >= 0.5 and <= 1 (Default is 0.6)", label="Threshold Percentage", required=False)
        self.add_item(self.default_yellow_card_input)
        self.add_item(self.default_red_card_input)
        self.add_item(self.threshold)

    async def on_submit(self, interaction: discord.Interaction):
        yellow_card_description = self.default_yellow_card_input.value
        red_card_description = self.default_red_card_input.value
        threshold = self.threshold.value

        if threshold == "":
            threshold = 0.6

        if not helpers.is_float(threshold):
            await interaction.response.send_message("Please Enter a number >= 0.5 and <= 1 or leave it empty, (Default is 0.6)", ephemeral=True)
            return

        threshold = float(threshold)
        if threshold > 1 or threshold < 0.5:
            await interaction.response.send_message('يا متخازل ------ Completion Threshold has to be >= 0.5 and <= 1')
            return

        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild.id)
        new_subscriber = Subscriber(user_id, guild_id, yellow_card_description, red_card_description, threshold)

        subscribers_access.subscribe_user(new_subscriber)
        await interaction.response.send_message(
            f"Be Proud, you are a hard worker, you subscribed to the program successfully {interaction.user.mention}",
            ephemeral=True
        )
        
        
