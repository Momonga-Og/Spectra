import discord
from discord.ext import commands
from discord import app_commands
import logging

class Relocate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="relocate", description="Relocate a message to a different channel")
    async def relocate(self, interaction: discord.Interaction, message_id: str, target_channel: discord.TextChannel):
        await interaction.response.defer(ephemeral=True)  # Defer the response to give time for processing

        logging.info(f"Relocate command invoked by {interaction.user} for message {message_id} to {target_channel}")

        try:
            # Fetch the message by ID
            channel = interaction.channel
            message = await channel.fetch_message(message_id)
            
            logging.info(f"Fetched message: {message.content}")

            # Send the message content to the target channel
            await target_channel.send(f"**Message from {message.author.name} in {channel.mention}:**\n{message.content}")

            # Delete the original message
            try:
                await message.delete()
                logging.info("Original message deleted")
                await interaction.followup.send("Message relocated successfully.")
            except discord.errors.NotFound:
                logging.warning("Message was not found or already deleted")
                await interaction.followup.send("Message was not found or already deleted.")
        except discord.errors.NotFound:
            logging.error("The message ID provided does not exist")
            await interaction.followup.send("The message ID provided does not exist.")
        except Exception as e:
            logging.exception(f"Error in relocate command: {e}")
            await interaction.followup.send(f"An error occurred while processing your request: {e}")

async def setup(bot):
    cog = Relocate(bot)
    await bot.add_cog(cog)
    if not bot.tree.get_command('relocate'):
        bot.tree.add_command(cog.relocate)
