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
            # URL construction based on the given item
            base_url = "https://www.vulbis.com/?Touch&server=Dodge&gids=&percent=0&craftableonly=false&select-type=1&sellchoice=false&buyqty=1&sellqty=1&percentsell=0"
            response = requests.get(base_url)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Locate the table or data on the page (adjust this based on the actual structure)
            table = soup.find('table', {'class': 'item-list'})  # Replace with actual class or id
            rows = table.find_all('tr')

            item_data = None
            for row in rows:
                columns = row.find_all('td')
                item_name = columns[0].text.strip()
                if item.lower() in item_name.lower():
                    item_data = {
                        'name': item_name,
                        'price': columns[1].text.strip(),  # Adjust index based on actual column
                        'quantity': columns[2].text.strip()  # Adjust index based on actual column
                    }
                    break

            if item_data:
                embed = discord.Embed(title="Market Watch", color=discord.Color.blue())
                embed.add_field(name="Item", value=item_data['name'], inline=False)
                embed.add_field(name="Price", value=item_data['price'], inline=False)
                embed.add_field(name="Quantity", value=item_data['quantity'], inline=False)
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"No data found for item: {item}")

        except Exception as e:
            logging.exception(f"Error in marketwatch command: {e}")
            await interaction.followup.send("An error occurred while processing your request.")

async def setup(bot):
    cog = MarketWatch(bot)
    await bot.add_cog(cog)
    if not bot.tree.get_command('marketwatch'):
        bot.tree.add_command(cog.marketwatch)
