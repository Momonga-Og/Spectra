import discord
from discord.ext import commands, tasks
from collections import defaultdict
import datetime
import asyncio

class WarningSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.action_counts = defaultdict(lambda: defaultdict(list))
        self.warned_users = set()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        actions = []
        if before.self_mute != after.self_mute:
            actions.append("mute/unmute")
        if before.self_deaf != after.self_deaf:
            actions.append("deafen/undeafen")
        if before.channel != after.channel:
            if before.channel is None:
                actions.append("join")
            elif after.channel is None:
                actions.append("leave")
            else:
                actions.append("move")

        now = datetime.datetime.utcnow()

        for action in actions:
            self.action_counts[member.id][action].append(now)
            total_actions = sum(len(times) for times in self.action_counts[member.id].values())

            if total_actions > 2 and member.id not in self.warned_users:
                self.warned_users.add(member.id)
                if after.channel:
                    await self.warn_user_in_voice(member, after.channel)
                else:
                    await self.warn_user_in_text(member)

    async def warn_user_in_voice(self, member, channel):
        voice_channel = discord.utils.get(member.guild.voice_channels, id=channel.id)
        if voice_channel:
            vc = await voice_channel.connect()
            await self.send_warning(member, vc)
            await vc.disconnect()

    async def warn_user_in_text(self, member):
        channel = discord.utils.get(member.guild.text_channels)
        if channel:
            await channel.send(
                f"Please {member.mention}, the functions you are using are not for amusement. They are for practical work, and you are disturbing your fellow users. This is my last warning, or you will be kicked from the server."
            )

    async def send_warning(self, member, vc):
        if vc.is_connected():
            vc.play(discord.FFmpegPCMAudio("warning_message.mp3"))
            while vc.is_playing():
                await asyncio.sleep(1)
        await member.send(
            f"Please {member.display_name}, the functions you are using are not for amusement. They are for practical work, and you are disturbing your fellow users. This is my last warning, or you will be kicked from the server."
        )

    @tasks.loop(minutes=1)
    async def reset_counts(self):
        now = datetime.datetime.utcnow()
        for user_id, actions in list(self.action_counts.items()):
            for action, timestamps in list(actions.items()):
                self.action_counts[user_id][action] = [ts for ts in timestamps if (now - ts).total_seconds() <= 3600]
            if not self.action_counts[user_id]:
                del self.action_counts[user_id]

    @commands.Cog.listener()
    async def on_ready(self):
        self.reset_counts.start()

async def setup(bot):
    await bot.add_cog(WarningSystem(bot))
