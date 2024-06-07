import discord
from discord.ext import commands
from discord import app_commands
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging

class MarketWatch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="marketwatch", description="Check the market prices for an item")
    async def marketwatch(self, interaction: discord.Interaction, item: str):
        await interaction.response.defer()  # Defer the response to give time for scraping

        try:
            # Setup Chrome options
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--headless")  # Ensure GUI is off
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            # Set path to chromedriver as per your configuration
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

            # Open the website
            url = "https://www.vulbis.com/?Touch&server=Dodge&gids=&percent=0&craftableonly=false&select-type=1&sellchoice=false&buyqty=1&sellqty=1&percentsell=0"
            driver.get(url)

            # Wait for the table to be present
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.item-list')))

            # Find the table
            table = driver.find_element(By.CSS_SELECTOR, 'table.item-list')  # Update with the correct selector
            rows = table.find_elements(By.TAG_NAME, 'tr')

            item_data = []
            for row in rows:
                columns = row.find_elements(By.TAG_NAME, 'td')
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
        finally:
            driver.quit()  # Ensure the browser is closed

async def setup(bot):
    cog = MarketWatch(bot)
    await bot.add_cog(cog)
    if not bot.tree.get_command('marketwatch'):
        bot.tree.add_command(cog.marketwatch)
