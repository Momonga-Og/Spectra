# warning.py
import discord
from discord.ext import commands

class Warning(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_warnings = {}

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author == self.bot.user:
            channel = message.channel
            await channel.send(f"{message.author.mention}, next time if you delete any of my messages, you will be kicked from the server. Please be respectful.")
            self.user_warnings[message.author.id] = self.user_warnings.get(message.author.id, 0) + 1
            if self.user_warnings[message.author.id] >= 1:  # Adjust the threshold if needed
                await message.author.kick(reason="Deleted bot messages")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel != after.channel or before.mute != after.mute or before.deaf != after.deaf:
            if member.id not in self.user_warnings:
                self.user_warnings[member.id] = 0

            self.user_warnings[member.id] += 1
            if self.user_warnings[member.id] >= 3:  # Adjust the threshold if needed
                await member.send("You have been warned for repeatedly disconnecting or muting/unmuting users in voice chat. Continued abuse will result in a kick.")
                if self.user_warnings[member.id] >= 5:  # Adjust the threshold if needed
                    await member.kick(reason="Abused voice chat functionalities")

async def setup(bot):
    await bot.add_cog(Warning(bot))
