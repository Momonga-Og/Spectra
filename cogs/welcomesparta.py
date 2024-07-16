import discord
from discord.ext import commands
from discord import app_commands

class WelcomeSparta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Check if the member joined the specific server
        if member.guild.id == 1214430768143671377:  # Sparta server ID
            # Send public welcome message
            public_channel = member.guild.get_channel(1214456735356420096)  # Public channel ID
            welcome_message = (
                f"🎉 Welcome {member.mention} to Sparta! 🎉\n"
                "We're thrilled to have you here! Make sure to check out our channels and enjoy your stay. 🎊"
            )
            image_url = "https://github.com/Momonga-Og/Spectra/blob/db4e92dd8deaba15608bd0856f265f742097fc72/th.jpeg"  # Update this with your image URL
            embed = discord.Embed(description=welcome_message, color=discord.Color.blue())
            embed.set_image(url=image_url)
            await public_channel.send(embed=embed)

            # Send private welcome message with buttons
            dm_message = (
                "Hello, I'm Spectra, the self-automated bot created for the Sparta guild on Dofus Touch. "
                "First, I want to welcome you to our guild, and we are happy that our family has a new member. "
                "Check out our channels and my functions and commands. I do a lot of things. "
                "I hope you have a wonderful experience in our Discord server."
            )

            view = WelcomeView(member.guild.roles)
            await member.send(dm_message, view=view)

class WelcomeView(discord.ui.View):
    def __init__(self, roles):
        super().__init__()
        self.roles = roles

    @discord.ui.button(label="Change your Discord server name", style=discord.ButtonStyle.primary)
    async def change_name_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Please enter your new server name:", ephemeral=True)

        def check(m):
            return m.author == interaction.user and isinstance(m.channel, discord.DMChannel)

        try:
            message = await self.bot.wait_for('message', check=check, timeout=60)
            await interaction.user.edit(nick=message.content)
            await interaction.followup.send(f"Your server name has been changed to {message.content}", ephemeral=True)
        except asyncio.TimeoutError:
            await interaction.followup.send("You took too long to respond. Please try again.", ephemeral=True)

    @discord.ui.button(label="Choose Member or Guest", style=discord.ButtonStyle.secondary)
    async def choose_role_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        options = [
            discord.SelectOption(label="Member", description="Join as a Member"),
            discord.SelectOption(label="Guest", description="Join as a Guest"),
        ]
        select = discord.ui.Select(placeholder="Choose your role", options=options)
        select.callback = self.select_callback
        self.add_item(select)
        await interaction.response.send_message("Please choose your role:", view=self, ephemeral=True)

    async def select_callback(self, interaction: discord.Interaction):
        role_name = interaction.data['values'][0]
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if role:
            await interaction.user.add_roles(role)
            await interaction.followup.send(f"You have been assigned the {role_name} role.", ephemeral=True)
        else:
            await interaction.followup.send(f"Role '{role_name}' not found. Please contact an admin.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(WelcomeSparta(bot))
