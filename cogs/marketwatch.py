import discord
from discord.ext import commands
from bs4 import BeautifulSoup
import requests

class MarketWatch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def marketwatch(self, ctx, *, item_name: str):
        try:
            url = f"https://www.vulbis.com/?Touch&server=Dodge&gids=&percent=0&craftableonly=false&select-type=1&sellchoice=false&buyqty=1&sellqty=1&percentsell=0"
            response = requests.get(url)
            if response.status_code != 200:
                await ctx.send("Failed to retrieve data from the website.")
                return

            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table', {'id': 'myTable'})  # Update with the correct table id or class

            if not table:
                await ctx.send("Could not find the market data table.")
                return

            rows = table.find_all('tr')
            item_data = []
            for row in rows:
                columns = row.find_all('td')
                if columns and item_name.lower() in columns[0].text.lower():
                    item_data.append([col.text.strip() for col in columns])

            if not item_data:
                await ctx.send(f"No data found for item: {item_name}")
                return

            # Format the data for Discord message
            embed = discord.Embed(title=f"Market Watch for {item_name}", color=discord.Color.blue())
            for item in item_data:
                embed.add_field(name=item[0], value=f"Price: {item[1]}, Quantity: {item[2]}", inline=False)
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"An error occurred while processing the command: {e}")

async def setup(bot):
    await bot.add_cog(MarketWatch(bot))
