import discord
from discord.ext import commands
import os
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.blocked_users = {}

    def text_to_speech(self, text, filename):
        tts = gTTS(text)
        tts.save(filename)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None and after.channel is not None:
            guild_id = member.guild.id
            if guild_id not in self.blocked_users:
                self.blocked_users[guild_id] = set()
            
            if not member.bot and member.id not in self.blocked_users[guild_id]:
                try:
                    vc = None
                    if not self.bot.voice_clients:
                        vc = await after.channel.connect(timeout=60)
                    else:
                        vc = self.bot.voice_clients[0]
                        if vc.channel != after.channel:
                            await vc.move_to(after.channel)

                    if vc and vc.is_connected():
                        audio_file = f'{member.name}_welcome.mp3'
                        welcome_text = f'Welcome to the voice channel, {member.name}!'
                        self.text_to_speech(welcome_text, audio_file)

                        vc.play(discord.FFmpegPCMAudio(audio_file))

                        while vc.is_playing():
                            await asyncio.sleep(1)

                        if vc.is_connected():
                            await vc.disconnect()

                        os.remove(audio_file)
                    else:
                        logging.error("Failed to connect or play audio")
                except Exception as e:
                    logging.exception("Error in voice state update: %s", e)

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
bot.add_cog(Voice(bot))

async def close_sessions():
    await bot.session.close()

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user}')
    if not hasattr(bot, 'synced'):
        try:
            synced = await bot.tree.sync()
            logging.info(f"Synced {len(synced)} commands")
            bot.synced = True
        except Exception as e:
            logging.exception("Failed to sync commands")

@bot.event
async def on_disconnect():
    logging.info("Bot disconnected")

@bot.event
async def on_close():
    logging.info("Bot is closing")
    await close_sessions()

async def reboot_bot():
    logging.info("Rebooting bot")
    await bot.close()
    os.execl(sys.executable, sys.executable, *sys.argv)

def schedule_reboot(bot):
    async def reboot_task():
        while True:
            await asyncio.sleep(18000)  # 5 hours
            await reboot_bot()

    bot.loop.create_task(reboot_task())

async def load_extensions():
    try:
        await bot.load_extension('cogs.general')
        await bot.load_extension('cogs.moderation')
        await bot.load_extension('cogs.poll')
        await bot.load_extension('cogs.admin')
        await bot.load_extension('cogs.voice')
        await bot.load_extension('cogs.relocate')
        await bot.load_extension('cogs.watermark')
        await bot.load_extension('cogs.serverstats')
        await bot.load_extension('cogs.talk')
    except Exception as e:
        logging.exception("Failed to load extensions")

async def main():
    async with bot:
        await load_extensions()
        schedule_reboot(bot)
        token = os.getenv('DISCORD_BOT_TOKEN')
        if not token:
            logging.error("Bot token not found. Please set the DISCORD_BOT_TOKEN environment variable.")
            return
        await bot.start(token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.exception("Bot encountered an error and stopped")
