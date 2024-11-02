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
        print("Reaction detected!")  # Debug: Check if a reaction was detected
        
        if user.bot or reaction.message.author == user:
            print("Ignored reaction by bot or author.")  # Debug
            return

        # Check if the emoji is recognized in LANGUAGE_MAP
        language_code = self.LANGUAGE_MAP.get(str(reaction.emoji))
        print(f"Emoji: {reaction.emoji}, Language Code: {language_code}")  # Debug
        
        if not language_code:
            print("Emoji not supported.")  # Debug
            return  # Exit if the emoji is not a supported flag

        original_text = reaction.message.content
        print(f"Original text: {original_text}")  # Debug

        try:
            # Translate the text
            translation = self.translator.translate(original_text, dest=language_code)
            translated_text = translation.text
            await reaction.message.reply(f"Translation ({language_code.upper()}): {translated_text}")
            print("Translation sent!")  # Debug
        except Exception as e:
            print(f"Error: {e}")
            await reaction.message.channel.send("An error occurred while translating the message.")

async def setup(bot):
    await bot.add_cog(TranslatorCog(bot))
