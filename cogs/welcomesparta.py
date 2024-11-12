import discord
from discord.ext import commands
from discord import app_commands
import asyncio

# Define intents with MEMBERS intent enabled
intents = discord.Intents.default()
intents.members = True  # Enable members intent for on_member_join event


class WelcomeSparta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Check if the member joined the specific server
        if member.guild.id == 1214430768143671377:  # Sparta server ID
            try:
                # Send public welcome message
                public_channel = member.guild.get_channel(1214456735356420096)  # Public channel ID
                if public_channel:
                    welcome_message = (
                        f"🎉 Welcome {member.mention} to Sparta! 🎉\n"
                        "We're thrilled to have you here! Make sure to check out our channels and enjoy your stay. 🎊"
                    )
                    image_url = "https://github.com/Momonga-Og/Spectra/blob/db4e92dd8deaba15608bd0856f265f742097fc72/th.jpeg?raw=true"  
                    embed = discord.Embed(description=welcome_message, color=discord.Color.blue())
                    embed.set_image(url=image_url)
                    await public_channel.send(embed=embed)
                    print("Public welcome message sent successfully.")
                else:
                    print("Public channel not found or inaccessible.")

                # Send private welcome message with buttons
                dm_message = (
                    "Hello, I'm Spectra, the self-automated bot created for the Sparta guild on Dofus Touch. "
                    "Welcome to our guild! Check out our channels and my functions and commands. "
                    "I hope you have a wonderful experience in our Discord server."
                )
                
                view = WelcomeView(self.bot, member.guild.roles, member.guild)
                await member.send(dm_message, view=view)
                print("DM sent with WelcomeView successfully.")
            except Exception as e:
                print(f"Error in on_member_join: {e}")

class WelcomeView(discord.ui.View):
    def __init__(self, bot, roles, guild):
        super().__init__()
        self.bot = bot
        self.roles = roles
        self.guild = guild

    @discord.ui.button(label="Change your Discord server name", style=discord.ButtonStyle.primary)
    async def change_name_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Please enter your new server name:", ephemeral=True)
        print("Prompted user to enter a new server name.")
        
        def check(m):
            return m.author == interaction.user and isinstance(m.channel, discord.DMChannel)

        try:
            message = await self.bot.wait_for('message', check=check, timeout=60)
            member = self.guild.get_member(interaction.user.id)
            if member:
                await member.edit(nick=message.content)
                await interaction.followup.send(f"Your server name has been changed to {message.content}", ephemeral=True)
                print(f"Nickname changed to {message.content} for {interaction.user}.")
            else:
                await interaction.followup.send("Failed to find your member data. Please contact an admin.", ephemeral=True)
                print("Member data not found in guild.")
        except asyncio.TimeoutError:
            await interaction.followup.send("You took too long to respond. Please try again.", ephemeral=True)
            print("User timed out while entering new server name.")
        except Exception as e:
            print(f"Error in change_name_button: {e}")

    @discord.ui.button(label="Choose Member or Guest", style=discord.ButtonStyle.secondary)
    async def choose_role_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        options = [
            discord.SelectOption(label="🌀-𝕸𝖊𝖒𝖇𝖊𝖗-🌀", description="Join as a Member"),
            discord.SelectOption(label="Guest", description="Join as a Guest"),
        ]
        select = discord.ui.Select(placeholder="Choose your role", options=options)
        select.callback = self.select_callback
        self.add_item(select)
        await interaction.response.send_message("Please choose your role:", view=self, ephemeral=True)
        print("Prompted user to choose a role.")

    async def select_callback(self, interaction: discord.Interaction):
        role_name = interaction.data['values'][0]
        role = discord.utils.get(self.roles, name=role_name)
        member = self.guild.get_member(interaction.user.id)
        if role and member:
            try:
                await member.add_roles(role)
                await interaction.followup.send(f"You have been assigned the {role_name} role.", ephemeral=True)
                print(f"Role '{role_name}' assigned to {interaction.user}.")
            except Exception as e:
                await interaction.followup.send(f"Failed to assign the role {role_name}. Please contact an admin.", ephemeral=True)
                print(f"Error assigning role '{role_name}': {e}")
        else:
            await interaction.followup.send(f"Role '{role_name}' not found or failed to find your member data. Please contact an admin.", ephemeral=True)
            print("Role or member data not found.")

async def setup(bot):
    await bot.add_cog(welcomesparta(bot))
    print("WelcomeSparta cog loaded successfully.")
