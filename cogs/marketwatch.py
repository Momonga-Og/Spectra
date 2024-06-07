import discord
from discord.ext import commands
from discord import app_commands
import requests
from bs4 import BeautifulSoup
import logging

class MarketWatch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="marketwatch", description="Check the market prices for an item")
    async def marketwatch(self, interaction: discord.Interaction, item: str):
        await interaction.response.defer()  # Defer the response to give time for scraping

        try:
            # URL for the base market page
            url = "https://www.vulbis.com/?Touch&server=Dodge&gids=&percent=0&craftableonly=false&select-type=1&sellchoice=false&buyqty=1&sellqty=1&percentsell=0"
            response = requests.get(url)
            if response.status_code != 200:
                await interaction.followup.send("Failed to retrieve data from the website.")
                return

            # Log the raw HTML content for debugging purposes
            raw_html = response.content.decode('utf-8')
            logging.info(raw_html)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table', {'id': 'myTable'})  # Update with the correct table id or class

            if not table:
                await interaction.followup.send("Could not find the market data table.")
                return

            rows = table.find_all('tr')
            item_data = []
            for row in rows:
                columns = row.find_all('td')
                if columns and item.lower() in columns[0].text.lower():
                    item_name = columns[0].text.strip()
                    price_in_market = columns[3].text.strip()  # Adjust index based on the actual column
                    craft_price = columns[6].text.strip()  # Adjust index based on the actual column
                    item_data.append({
                        'name': item_name,
                        'price_in_market': price_in_market,
                        'craft_price': craft_price
                    })

            if not item_data:
                await interaction.followup.send(f"No data found for item: {item}")
                return

            # Format the data for Discord message
            embed = discord.Embed(title=f"Market Watch for {item}", color=discord.Color.blue())
            for data in item_data:
                embed.add_field(
                    name=data['name'], 
                    value=f"Price in Market: {data['price_in_market']} Kamas\nCraft Price: {data['craft_price']} Kamas", 
                    inline=False
                )
            await interaction.followup.send(embed=embed)

        except Exception as e:
            logging.exception(f"Error in marketwatch command: {e}")
            await interaction.followup.send(f"An error occurred while processing your request: {e}")

async def setup(bot):
    cog = MarketWatch(bot)
    await bot.add_cog(cog)
    if not bot.tree.get_command('marketwatch'):
        bot.tree.add_command(cog.marketwatch)
