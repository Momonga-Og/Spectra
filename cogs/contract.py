import discord
from discord.ext import commands
from discord import app_commands

class Contract(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.contracts = {}

    @app_commands.command(name="contract", description="Initiate a contract between two users")
    @app_commands.describe(input_user="The user to contract with")
    async def contract(self, interaction: discord.Interaction, input_user: discord.User):
        who_invoked = interaction.user
        input_user = input_user

        contract_text = f"""
Sparta Contract 

Ice Dofus Contract Between {who_invoked.mention} and {input_user.mention}

This Contract is Guaranteed By The guild Sparta from Dodge Server Dofus Touch

This contract Is For Gaming Purposes Not related To the real life 

{input_user.mention} needs to provide the following things: 
1. Provide an Account ranged From LvL 195 to 200
2. Provide a set ranged from 180 to 200
3. Provide Kamas for {who_invoked.mention} to pay for resources to craft Keys And Quest Objects 
4. All the Resources Dropped By the Account of {input_user.mention} are belongs To {who_invoked.mention}. We are talking about legendary Weapons and rare Resources and Quest resources. {input_user.mention} has no right to claim those Resources after they got Dropped 
5. The methods of payment between and the amount of this service should stay confidential between {input_user.mention} and {who_invoked.mention}. Whether the payment is real money or game money (Kamas) the amount will not be mentioned in this Contract 
6. In case of dispute there is no refund no matter what  

{who_invoked.mention} needs to provide the following things: 
1. Provide an Ice Dofus for {input_user.mention} 
2. The delay of providing Dofus touch is between 5 days to 15 days 

Disclaimer: If any of the parties didn't follow the rules, they will be kicked and banned from the game guild and the Discord server and will be canceled by our community and will be propagated as a scammer. Also, this contract will be signed digitally by each party's Discord identity. The second you click on the “yes” button, the contract is signed and will be validated and there's no way for faking it or editing it or deleting it. This contract is saved in a JSON file stored in the bot data and the only person who can access it is the bot itself and the creator. The contract will always be available.
"""

        self.contracts[who_invoked.id] = {
            "input_user": input_user.id,
            "contract_text": contract_text,
            "signed": [],
            "channel_id": interaction.channel_id,
            "guild_id": interaction.guild_id  # Store guild ID
        }

        view = ContractView(self.bot, who_invoked.id, input_user.id, self.contracts)
        await who_invoked.send(f"Please review and sign the contract:\n\n{contract_text}", view=view)
        await input_user.send(f"Please review and sign the contract:\n\n{contract_text}", view=view)

class ContractView(discord.ui.View):
    def __init__(self, bot, who_invoked_id, input_user_id, contracts):
        super().__init__()
        self.bot = bot
        self.who_invoked_id = who_invoked_id
        self.input_user_id = input_user_id
        self.contracts = contracts

    @discord.ui.button(label="Sign Contract", style=discord.ButtonStyle.primary)
    async def sign_contract(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        contract = self.contracts[self.who_invoked_id]

        if user_id not in contract["signed"]:
            contract["signed"].append(user_id)

        if len(contract["signed"]) == 2:
            guild = self.bot.get_guild(contract["guild_id"])
            channel = guild.get_channel(contract["channel_id"])
            final_contract = f"{contract['contract_text']}\n\nSigned by:\n{guild.get_member(self.who_invoked_id).mention}\n{guild.get_member(self.input_user_id).mention}"
            await channel.send(f"Contract signed between {guild.get_member(self.who_invoked_id).mention} and {guild.get_member(self.input_user_id).mention}:\n{final_contract}")
            await interaction.response.send_message("Contract signed successfully!", ephemeral=True)
        else:
            await interaction.response.send_message("You have signed the contract. Waiting for the other party to sign.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Contract(bot))
