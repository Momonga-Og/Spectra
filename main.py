import discord
from discord.ext import commands
from discord import app_commands
from gtts import gTTS
import os
import asyncio

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.message_content = True

# Initialize bot with commands.Bot
bot = commands.Bot(command_prefix="!", intents=intents)

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

# /pm command
@bot.tree.command(name="pm", description="Send a message to a specific user")
async def pm(interaction: discord.Interaction, user: discord.Member, *, message: str):
    await user.send(message)
    await interaction.response.send_message(f"Message sent to {user.name}", ephemeral=True)

# /pm-role command
@bot.tree.command(name="pm-role", description="Send a message to all users in a specific role")
async def pm_role(interaction: discord.Interaction, role: discord.Role, *, message: str):
    for member in role.members:
        try:
            await member.send(message)
        except discord.Forbidden:
            pass  # Skip users who have DMs disabled
    await interaction.response.send_message(f"Message sent to all members with the role {role.name}", ephemeral=True)

# /pm-all command
@bot.tree.command(name="pm-all", description="Send a message to all users in the server")
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

bot.run(DISCORD_BOT_TOKEN)
