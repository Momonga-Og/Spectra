import discord
from discord.ext import commands
import logging

logging.basicConfig(level=logging.INFO)

hidden_words = ["word1", "word2", "word3", "word4", "word5"]
prize_message = "Congratulations! You've found a hidden word and won 5 MK!"

class WordCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        for word in hidden_words:
            if word in message.content.lower():
                # Announce in the channel
                embed = discord.Embed(
                    title="🎉 We Have a Winner! 🎉",
                    description=f"{message.author.mention} has found a hidden word and won a prize!\n\n{prize_message}",
                    color=discord.Color.gold()
                )
                embed.add_field(name="Hidden Word Found", value=word, inline=False)
                embed.add_field(name="Prize", value="5 MK", inline=False)
                embed.set_footer(text="Congratulations to the winner!")
                
                await message.channel.send(embed=embed)
                await message.channel.send("@everyone")

                # DM the winner
                try:
                    await message.author.send(f"🎉 Congratulations! You've found the hidden word '{word}' and won 5 MK! 🎉")
                except discord.Forbidden:
                    logging.info(f"Couldn't send DM to {message.author.name}")

                break

def setup(bot):
    bot.add_cog(WordCog(bot))
