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
        self.task_completion_inptut = UpdateTextInput(new_placeholder="Write New Completion Percentage (0-100)", new_label="Task Completion")
        self.add_item(self.task_desc_input)
        self.add_item(self.task_completion_inptut)

    async def on_submit(self, interaction: discord.Interaction):
        self.new_desc = self.task_desc_input.value
        self.new_completion = self.task_completion_inptut.value
        
        if(self.new_desc != "" and self.new_completion != ""): 
            tasks_access.update_task_desc(self.selected_value, self.new_desc)
            if not helpers.is_valid_number(self.new_completion) or float(self.new_completion) < 0 or float(self.new_completion) > 100:
                await interaction.response.send_message("Updated Task Description, but Completion Percentage should be between 0 and 100", ephemeral=True)
                return
            tasks_access.update_task_completion_percentage(self.selected_value, self.new_completion)
            await interaction.response.send_message("Task Description and Completion Updated", ephemeral=True)
        elif(self.new_completion == "" and self.new_desc != ""):
            tasks_access.update_task_desc(self.selected_value, self.new_desc)
            await interaction.response.send_message("Task Description Updated", ephemeral=True)
        elif(self.new_desc == "" and self.new_completion != ""):
            if not helpers.is_valid_number(self.new_completion) or float(self.new_completion) < 0 or float(self.new_completion) > 100:
                await interaction.response.send_message("Completion Percentage should be between 0 and 100", ephemeral=True)
                return
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

class SelfReportButton(Button):
    def __init__(self, tasks, curr_idx) -> None:
        super().__init__(label="Next", style=discord.ButtonStyle.primary)
        self.tasks = tasks
        self.curr_idx = curr_idx
        self.end_idx = min(curr_idx + 5, len(self.tasks))
        
    async def callback(self, interaction: discord.Interaction):
        modal = SelfReportModal(self.tasks, self.curr_idx)
        await interaction.response.send_modal(modal)

class SelfReportModal(Modal):
    def __init__(self, tasks, curr_idx):
        super().__init__(title="Report Task Completion")
        self.tasks = tasks
        self.curr_idx = curr_idx
        self.end_idx = min(curr_idx + 5, len(tasks))
        self.formatted_text = helpers.convert_tasks_to_self_report(tasks)

        for idx, task in enumerate(tasks[curr_idx:self.end_idx]):
            self.add_item(TextInput(label=f"Task {curr_idx+idx+1}", placeholder=f"{task.description}", custom_id=str(curr_idx+idx), style=discord.TextStyle.short))

    async def on_submit(self, interaction: discord.Interaction):
        print(self.curr_idx)
        failed_to_update = []
        for i, child in enumerate(self.children):
            completion_percentage = child.value
            if not helpers.is_valid_number(str(completion_percentage)) or float(completion_percentage) < 0 or float(completion_percentage) > 100:
                failed_to_update.append(i + 1)
                continue

            tasks_access.update_task_completion_percentage(self.tasks[self.curr_idx + i].task_id, float(completion_percentage))
            print('done')
        
        if self.end_idx < len(self.tasks):
            view = View()
            next_button = SelfReportButton(self.tasks, self.end_idx)
            view.add_item(next_button)
            question_message = f"Do you want to view the next page to edit tasks from {self.curr_idx+5} to {min(self.end_idx+5, len(self.tasks))}"
            await interaction.response.send_message(question_message, view=view, ephemeral=True)
            return

        if len(failed_to_update) == 0:
            await interaction.response.send_message(f"Self Report Completed", ephemeral=True)
            return
        
        await interaction.response.send_message(f"Failed to Updated these tasks: {failed_to_update}, if there are anyother tasks then they are updated", ephemeral=True)


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
        self.threshold = RegisterationInput(placeholder="Write Your threshold percentage you want >= 50.0 and <= 100.0 (Default is 60.0)", label="Threshold Percentage", required=False)
        self.add_item(self.default_yellow_card_input)
        self.add_item(self.default_red_card_input)
        self.add_item(self.threshold)

    async def on_submit(self, interaction: discord.Interaction):
        yellow_card_description = self.default_yellow_card_input.value
        red_card_description = self.default_red_card_input.value
        threshold = self.threshold.value

        if threshold == "":
            threshold = 60.0

        if not helpers.is_float(threshold):
            await interaction.response.send_message("Please Enter a number >= 50.0 and <= 100.0 or leave it empty, (Default is 60.0)", ephemeral=True)
            return

        threshold = float(threshold)
        if threshold > 100.0 or threshold < 50.0:
            await interaction.response.send_message('يا متخازل ------ Completion Threshold has to be >= 50.0 and <= 100.0')
            return

        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild.id)
        new_subscriber = Subscriber(user_id, guild_id, yellow_card_description, red_card_description, threshold)

        subscribers_access.subscribe_user(new_subscriber)
        await interaction.response.send_message(
            f"Be Proud, you are a hard worker, you subscribed to the program successfully {interaction.user.mention}",
            ephemeral=True
        )


class EditProfileModal(Modal):
    def __init__(self) -> None:
        super().__init__(title="Registeration")
        self.default_yellow_card_input = RegisterationInput(placeholder="Write your new default Yellow card description.", label="Default Yellow Card Description", required=False)
        self.default_red_card_input = RegisterationInput(placeholder="Write your new default Red card description.", label="Default Red Card Description", required=False)
        self.threshold = RegisterationInput(placeholder="Write Your new threshold percentage you want >= 50.0 and <= 100.0", label="Threshold Percentage", required=False)
        self.add_item(self.default_yellow_card_input)
        self.add_item(self.default_red_card_input)
        self.add_item(self.threshold)

    async def on_submit(self, interaction: discord.Interaction):
        yellow_card_description = self.default_yellow_card_input.value
        red_card_description = self.default_red_card_input.value
        threshold = self.threshold.value

        if threshold == "":
            threshold = 60.0

        if not helpers.is_float(threshold):
            await interaction.response.send_message("Please Enter a number >= 50.0 and <= 100.0 or leave it empty, (Default is 60.0)", ephemeral=True)
            return

        threshold = float(threshold)
        if threshold > 100.0 or threshold < 50.0:
            await interaction.response.send_message('يا متخازل ------ Completion Threshold has to be >= 50.0 and <= 100.0')
            return

        is_updated: bool = False
        threshold_status: str = ""
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild.id)
        
        if yellow_card_description != "":
            subscribers_access.update_subscriber_yellow_card(user_id, guild_id, yellow_card_description)
            is_updated = True
        if red_card_description != "":
            subscribers_access.update_subscriber_red_card(user_id, guild_id, red_card_description)
            is_updated = True
        
        if threshold != "":
            if helpers.is_float(threshold) and float(threshold) <= 100.0 and float(threshold) >= 50.0:
                subscribers_access.update_subscriber_threshold(user_id, guild_id, float(threshold))
                is_updated = True 
            else:
                threshold_status = " And Couldn't update Threshold يا متحايل"
        



        if is_updated:
            await interaction.response.send_message(
                f"Profile Updated Successfully {interaction.user.mention}" + threshold_status,
                ephemeral=True
            )
            return
        
        await interaction.response.send_message(
            f"No Changes Made :^)",
            ephemeral=True
        )
        return
