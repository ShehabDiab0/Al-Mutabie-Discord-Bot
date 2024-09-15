import discord
from discord.ext import commands
from discord.ui import View, Modal , TextInput, Select, Button 
from discord.components import SelectOption
from discord import TextStyle
from discord import app_commands
import helpers
from data_access import tasks_access
from data_access import subscribers_access
from data_access import weeks_access
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
        
class UpdateTaskView(View):
    def __init__(self, tasks) -> None:
        super().__init__()
        self.tasks = tasks
        self.modal = UpdateTaskModal(tasks)
        self.select = SingleTaskDropDown(self.tasks, self.modal)
        self.add_item(self.select)


# Template if we would like to implement other self report for previous weeks
# class WeekChoiceModal(Modal):
#     def __init__(self, tasks, curr_idx):
#         super().__init__(title="Self Report Week Choice")
#         self.add_item(TextInput(label=f"Week Number to Self Report",
#                                 placeholder=f"Write any Week number From 1 to {weeks_access.get_current_week()}",
#                                 style=discord.TextStyle.short,
#                                 required=True))

#     async def on_submit(self, interaction: discord.Interaction):
#         week_num = self.children[0]
#         view = View()
#         yes_button = button("Yes!") # TO BE CREATED IF NEEDED
#         no_button = button("No!") # TO BE CREATED IF NEEDED
#         await interaction.response.send_message(f"Are you sure you want to Report tasks of Week {week_num}", view=view, ephemeral=True)

class WeeksDropDown(Select):
    def __init__(self, weeks: list[int]) -> None:
        super().__init__(placeholder="Select Week",
                         options=[SelectOption(label=f'Week {week}', value=week) for week in weeks],
                         min_values=1,
                         max_values=1)
        self.options[0].label += ' (Current Week)'
        self.options[1].label += ' (Last Week)'
        # self.options.append(SelectOption(label='Other', value=0))

    async def callback(self, interaction: discord.Interaction):
        week_num = int(self.values[0])
        # if week_num == 0:
        # choose a week
        #     await interaction.response.send_modal()
        #     return
        
        user_id = interaction.user.id
        guild_id = interaction.guild.id
        subscriber = Subscriber(user_id, guild_id)
        tasks = tasks_access.get_subscriber_tasks(subscriber, week_num)
        
        if not tasks:
            await interaction.response.send_message(f"You have no tasks to report", ephemeral=True)
            return
        
        await interaction.response.send_modal(SelfReportModal(tasks=tasks, curr_idx=0))


class SelfReportButton(Button):
    def __init__(self, label, tasks, curr_idx) -> None:
        super().__init__(label=label, style=discord.ButtonStyle.primary)
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
            label_task = f'{task.description if len(task.description) < 26 else (task.description[:26] + "..")} {round(task.completion_percentage, 2)}'
            # self.add_item(TextInput(label=f"Task {curr_idx+idx+1}, Write a float number between 1-100", placeholder=f"{task.description}", custom_id=str(curr_idx+idx), style=discord.TextStyle.short))
            self.add_item(TextInput(label=f"Task {curr_idx+idx+1}: {label_task}",
                                    placeholder=f"Write a float number between 1-100",
                                    custom_id=str(curr_idx+idx),
                                    style=discord.TextStyle.short,
                                    required=False))

    async def on_submit(self, interaction: discord.Interaction):
        failed_to_update = []
        for i, child in enumerate(self.children):
            if child.value == "":
                continue
            completion_percentage = child.value
            if not helpers.is_valid_number(str(completion_percentage)) or float(completion_percentage) < 0 or float(completion_percentage) > 100:
                failed_to_update.append(i + 1)
                continue

            tasks_access.update_task_completion_percentage(self.tasks[self.curr_idx + i].task_id, float(completion_percentage))
            self.tasks[self.curr_idx + i].completion_percentage = float(completion_percentage)
        
        # means it's the last modal
        if self.end_idx >= len(self.tasks):
            if len(failed_to_update) == 0:
                await interaction.response.send_message(f"Self Report Completed", ephemeral=True)
                return
            
            await interaction.response.send_message(f"You Reached the last page, but Failed to Update these tasks: {failed_to_update}, if there are anyother tasks then they are updated", ephemeral=True)

        # modals only allow 5 text fields, so we need to ask if the used wants to continue or not
        view = View()
        next_button = SelfReportButton("Next ➡️", self.tasks, self.end_idx)
        previous_button = SelfReportButton("⬅️ Prev", self.tasks, self.curr_idx)
        view.add_item(previous_button)
        view.add_item(next_button)

        question_message = f"Do you want to enter the next page to edit tasks from {self.curr_idx+6} to {min(self.end_idx+5, len(self.tasks))}"
        if len(self.tasks) - self.end_idx == 1:
            question_message = f"Do you want to edit the last task {self.end_idx + 1}"

        if len(failed_to_update) > 0:
            question_message += f"\nAlso Failed to update Tasks: {failed_to_update}"
        await interaction.response.send_message(question_message, view=view, ephemeral=True)


class SelfReportView(View):
    def __init__(self, weeks: list[int]) -> None:
        super().__init__()
        self.select = WeeksDropDown(weeks)
        self.add_item(self.select)


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
        self.default_yellow_card_input = RegisterationInput(placeholder="What's your penalty if you got a Yellow Card?", label="Default Yellow Card Description", required=True)
        self.default_red_card_input = RegisterationInput(placeholder="What's your penalty if you got a Red Card?", label="Default Red Card Description", required=True)
        self.threshold = RegisterationInput(placeholder="Write Your threshold percentage you want >= 50.0 and <= 100.0 (Default is 60.0)", label="Threshold Percentage", required=False)
        self.strict_mode = RegisterationInput(
            placeholder="Write \"Go Easy On Me\" If you want to disable it (it's on by default).",
            label="Strict Mode", required=False)
        self.add_item(self.default_yellow_card_input)
        self.add_item(self.default_red_card_input)
        self.add_item(self.threshold)
        self.add_item(self.strict_mode)

    async def on_submit(self, interaction: discord.Interaction):
        yellow_card_description = self.default_yellow_card_input.value
        red_card_description = self.default_red_card_input.value
        threshold = self.threshold.value
        strict_mode = self.strict_mode.value

        if threshold == "":
            threshold = 60.0

        if strict_mode == "Go Easy On Me":
            strict_mode = False
        else:
            strict_mode = True

        if not helpers.is_float(threshold):
            await interaction.response.send_message("Please Enter a number >= 50.0 and <= 100.0 or leave it empty, (Default is 60.0)", ephemeral=True)
            return

        threshold = float(threshold)
        if threshold > 100.0 or threshold < 50.0:
            await interaction.response.send_message('يا متخازل ------ Completion Threshold has to be >= 50.0 and <= 100.0')
            return

        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild.id)
        new_subscriber = Subscriber(user_id, guild_id, yellow_card_description, red_card_description, strict_mode=strict_mode, threshold_percentage=threshold)

        subscribers_access.subscribe_user(new_subscriber)
        await interaction.response.send_message(
            f"Be Proud, you are a hard worker, you subscribed to the program successfully {interaction.user.mention}",
            ephemeral=True
        )

class ColorModeDropDown(Select):
    def __init__(self) -> None:
        super().__init__(placeholder="Select Color Mode",
                         options=[SelectOption(label=f'Default Mode', value="dfm"),
                                  SelectOption(label=f'Highlight Mode', value=f'hlm'),
                                  SelectOption(label=f'Font Color Mode', value=f'fcm'),
                                  SelectOption(label=f'Strike Mode', value=f'skm'),
                                  SelectOption(label=f'Shifted Strike Mode', value=f'ssm'),
                                  ],
                         min_values=1,
                         max_values=1)

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        guild_id = interaction.guild.id
        new_color_mode = self.values[0]
        subscribers_access.update_color_mode(user_id, guild_id, new_color_mode)

        await interaction.response.send_message(f"Color Mode Updated :^)", ephemeral=True)

class ColorModeView(View):
    def __init__(self) -> None:
        super().__init__()
        self.add_item(ColorModeDropDown())

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
