import discord
from discord.ext import commands, tasks
import os
from utils.scheduler import schedule_reboot

# Load environment variables
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.message_content = True

# Initialize bot with commands.Bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Load cogs
bot.load_extension('cogs.general')
bot.load_extension('cogs.voice')
bot.load_extension('cogs.admin')

# Schedule the reboot task
schedule_reboot(bot)

bot.run(DISCORD_BOT_TOKEN)
