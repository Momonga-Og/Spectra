# translator.py

import discord
from discord.ext import commands
from googletrans import Translator

class TranslatorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.translator = Translator()
        # Define Unicode flag emojis and corresponding language codes
        self.LANGUAGE_MAP = {
            "🇺🇸": "en",  # English (US)
            "🇫🇷": "fr",  # French
            "🇪🇸": "es",  # Spanish
            "🇦🇪": "ar",  # Arabic
            "🇩🇪": "de",  # German
            # Add more languages as needed
        }

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # Ignore reactions added by bots or the message author
        if user.bot or reaction.message.author == user:
            return

        # Check if the emoji corresponds to a supported language
        language_code = self.LANGUAGE_MAP.get(str(reaction.emoji))
        if not language_code:
            return  # Exit if the emoji is not a supported flag

        # Get the original message content
        original_text = reaction.message.content

        try:
            # Translate the text
            translation = self.translator.translate(original_text, dest=language_code)
            translated_text = translation.text
            source_lang = translation.src.upper()  # Get the source language code in uppercase

            # Send a reply with the translation, formatted as in the example
            await reaction.message.reply(
                f"**From {source_lang} To {language_code.upper()}**:\n{translated_text}\n\n"
                f"Translation requested by {user.mention} from Flag-Reaction Feature."
            )

        except Exception as e:
            print(f"Error: {e}")
            await reaction.message.channel.send("An error occurred while translating the message.")

async def setup(bot):
    await bot.add_cog(TranslatorCog(bot))
