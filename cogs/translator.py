# translator.py

import discord
from discord.ext import commands
from googletrans import Translator

class TranslatorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.translator = Translator()
        # Define flag emojis and their corresponding language codes
        self.LANGUAGE_MAP = {
            ":flag_us:": "en",  # English
            ":flag_fr:": "fr",  # French
            ":flag_es:": "es",  # Spanish
            ":flag_ar:": "ar",  # Arabic
            ":flag_de:": "de",  # German
            # Add more languages as needed
        }

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # Ignore bot reactions or reactions added by the message author
        if user.bot or reaction.message.author == user:
            return

        # Get the language code from the emoji
        language_code = self.LANGUAGE_MAP.get(str(reaction.emoji))
        if not language_code:
            return  # Exit if the emoji is not a supported flag

        # Get the original message content
        original_text = reaction.message.content

        # Translate the text
        try:
            translation = self.translator.translate(original_text, dest=language_code)
            translated_text = translation.text
            # Send the translation as a reply to the original message
            await reaction.message.reply(
                f"Translation ({language_code.upper()}): {translated_text}"
            )
        except Exception as e:
            print(f"Error: {e}")
            await reaction.message.channel.send("An error occurred while translating the message.")

async def setup(bot):
    await bot.add_cog(TranslatorCog(bot))
