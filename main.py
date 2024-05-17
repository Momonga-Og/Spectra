import discord
from discord.ext import commands
from discord import app_commands
from gtts import gTTS
import os
import asyncio
import random

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.message_content = True

# Initialize bot with commands.Bot
bot = commands.Bot(command_prefix="!", intents=intents)
blocked_users = []

def text_to_speech(text, filename):
    tts = gTTS(text)
    tts.save(filename)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        try:
            if not member.bot:  # Ensure the bot doesn't greet itself
                if not bot.voice_clients:
                    vc = await after.channel.connect()
                else:
                    vc = bot.voice_clients[0]

                audio_file = f'{member.name}_welcome.mp3'
                welcome_text = f'Welcome to the voice channel, {member.name}!'
                text_to_speech(welcome_text, audio_file)

                vc.play(discord.FFmpegPCMAudio(audio_file))

                while vc.is_playing():
                    await asyncio.sleep(1)

                if vc.is_connected():
                    await vc.disconnect()

                # Clean up the audio file after use
                os.remove(audio_file)
        except Exception as e:
            print(f"Error in on_voice_state_update: {e}")
@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        try:
            if not member.bot and member.id not in blocked_users:
                if not bot.voice_clients:
                    vc = await after.channel.connect()
                else:
                    vc = bot.voice_clients[0]

                audio_file = f'{member.name}_welcome.mp3'
                welcome_text = f'Welcome to the voice channel, {member.name}!'
                text_to_speech(welcome_text, audio_file)

                vc.play(discord.FFmpegPCMAudio(audio_file))

                while vc.is_playing():
                    await asyncio.sleep(1)

                if vc.is_connected():
                    await vc.disconnect()

                # Clean up the audio file after use
                os.remove(audio_file)
        except Exception as e:
            print(f"Error in on_voice_state_update: {e}")
# /block command
@bot.tree.command(name="block", description="Block the bot from greeting you")
async def block(interaction: discord.Interaction, user: discord.Member):
    # You may want to add some permission checks here to restrict who can use this command
    # For example, only allow administrators to block users
    
    # Add the user to the blocked list
    # You need to have a mechanism to store blocked users, such as a database or file
    # For simplicity, I'll assume you have a list called 'blocked_users'
    blocked_users.append(user.id)
    await interaction.response.send_message(f"The bot will no longer greet {user.name}", ephemeral=True)


# /pm command
@bot.tree.command(name="pm", description="Send a message to a specific user (Admin only)")
@app_commands.checks.has_permissions(administrator=True)
async def pm(interaction: discord.Interaction, user: discord.Member, *, message: str):
    author = interaction.user.name
    await user.send(f"Message from {author}: {message}")
    await interaction.response.send_message(f"Message sent to {user.name}", ephemeral=True)

# /pm-role command
@bot.tree.command(name="pm-role", description="Send a message to all users in a specific role (Admin only)")
@app_commands.checks.has_permissions(administrator=True)
async def pm_role(interaction: discord.Interaction, role: discord.Role, *, message: str):
    author = interaction.user.name
    for member in role.members:
        try:
            await member.send(f"Message from {author}: {message}")
        except discord.Forbidden:
            pass  # Skip users who have DMs disabled
    await interaction.response.send_message(f"Message sent to all members with the role {role.name}", ephemeral=True)

# /pm-all command
@bot.tree.command(name="pm-all", description="Send a message to all users in the server (Admin only)")
@app_commands.checks.has_permissions(administrator=True)
async def pm_all(interaction: discord.Interaction, *, message: str):
    guild = interaction.guild
    for member in guild.members:
        if not member.bot:  # Skip bots
            try:
                await member.send(message)
            except discord.Forbidden:
                pass  # Skip users who have DMs disabled
    await interaction.response.send_message("Message sent to all users in the server", ephemeral=True)

# Error handler for /pm-all
@pm_all.error
async def pm_all_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

# Remaining commands and error handlers remain the same as before...


# /kick command
@bot.tree.command(name="kick", description="Kick a specific user from the server")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, user: discord.Member, *, reason: str = "No reason provided"):
    await user.kick(reason=reason)
    await interaction.response.send_message(f"{user.name} has been kicked. Reason: {reason}", ephemeral=True)

@kick.error
async def kick_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

# /ban command
@bot.tree.command(name="ban", description="Ban a specific user from the server")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, user: discord.Member, *, reason: str = "No reason provided"):
    await user.ban(reason=reason)
    await interaction.response.send_message(f"{user.name} has been banned. Reason: {reason}", ephemeral=True)

@ban.error
async def ban_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

# /mute command
@bot.tree.command(name="mute", description="Mute a specific user in the server")
@app_commands.checks.has_permissions(mute_members=True)
async def mute(interaction: discord.Interaction, user: discord.Member):
    await user.edit(mute=True)
    await interaction.response.send_message(f"{user.name} has been muted", ephemeral=True)

@mute.error
async def mute_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

# /deafen command
@bot.tree.command(name="deafen", description="Deafen a specific user in the server")
@app_commands.checks.has_permissions(deafen_members=True)
async def deafen(interaction: discord.Interaction, user: discord.Member):
    await user.edit(deafen=True)
    await interaction.response.send_message(f"{user.name} has been deafened", ephemeral=True)

@deafen.error
async def deafen_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

# /poll command
@bot.tree.command(name="poll", description="Create a poll in the server")
async def poll(interaction: discord.Interaction, question: str, option1: str, option2: str):
    embed = discord.Embed(title="Poll", description=question, color=discord.Color.blue())
    embed.add_field(name="Option 1", value=option1, inline=False)
    embed.add_field(name="Option 2", value=option2, inline=False)
    message = await interaction.channel.send(embed=embed)
    await message.add_reaction('1️⃣')
    await message.add_reaction('2️⃣')
    await interaction.response.send_message("Poll created!", ephemeral=True)

# /pick command
@bot.tree.command(name="pick", description="Pick a random user from the server")
async def pick(interaction: discord.Interaction):
    guild = interaction.guild
    members = [member for member in guild.members if not member.bot]
    selected_member = random.choice(members)
    await interaction.response.send_message(f"Picked user: {selected_member.name}", ephemeral=True)

# /pick-s command
@bot.tree.command(name="pick-s", description="Pick a random user from a specific role")
async def pick_s(interaction: discord.Interaction, role: discord.Role):
    members = [member for member in role.members if not member.bot]
    if not members:
        await interaction.response.send_message(f"No members found in the role {role.name}", ephemeral=True)
        return
    selected_member = random.choice(members)
    await interaction.response.send_message(f"Picked user: {selected_member.name} from role {role.name}", ephemeral=True)

# /cname command
@bot.tree.command(name="cname", description="Change a user's nickname")
@app_commands.checks.has_permissions(manage_nicknames=True)
async def c_name(interaction: discord.Interaction, user: discord.Member, *, new_nickname: str):
    await user.edit(nick=new_nickname)
    await interaction.response.send_message(f"{user.name}'s nickname has been changed to {new_nickname}", ephemeral=True)

@c_name.error
async def c_name_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

# /mhelp command
@bot.tree.command(name="mhelp", description="Show the bot's commands and their descriptions")
async def m_help(interaction: discord.Interaction):
    embed = discord.Embed(title="Bot Commands", color=discord.Color.green())
    commands_list = [
        ("/pm [user] [message]", "Send a message to a specific user"),
        ("/pm-role [role] [message]", "Send a message to all users in a specific role"),
        ("/pm-all [message]", "Send a message to all users in the server (Admin only)"),
        ("/kick [user] [reason]", "Kick a specific user from the server (Admin/Mod only)"),
        ("/ban [user] [reason]", "Ban a specific user from the server (Admin/Mod only)"),
        ("/mute [user]", "Mute a specific user in the server (Admin/Mod only)"),
        ("/deafen [user]", "Deafen a specific user in the server (Admin/Mod only)"),
        ("/poll [question] [option1] [option2]", "Create a poll in the server"),
        ("/pick", "Pick a random user from the server"),
        ("/pick-s [role]", "Pick a random user from a specific role"),
        ("/cname [user] [new_nickname]", "Change a user's nickname (Admin/Mod only)"),
        ("/mhelp", "Show this help message")
    ]
    
    for name, desc in commands_list:
        embed.add_field(name=name, value=desc, inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

bot.run(DISCORD_BOT_TOKEN)
