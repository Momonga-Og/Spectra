# translator.py

import discord
from discord.ext import commands
from googletrans import Translator, LANGUAGES

class TranslatorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            self.translator = Translator()
            print("Translator initialized successfully.")
        except Exception as e:
            print(f"Error initializing Translator: {e}")

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
        # Check if the bot has permissions to read message history and send messages
        if not reaction.message.channel.permissions_for(reaction.message.guild.me).read_message_history:
            print("Bot lacks permission to read message history.")
            return
        
        if not reaction.message.channel.permissions_for(reaction.message.guild.me).send_messages:
            print("Bot lacks permission to send messages.")
            return

        # Ignore reactions added by bots or the message author
        if user.bot or reaction.message.author == user:
            print("Ignoring bot reaction or message author reaction.")
            return

        # Check if the emoji corresponds to a supported language
        language_code = self.LANGUAGE_MAP.get(str(reaction.emoji))
        if not language_code:
            print(f"Unsupported emoji: {reaction.emoji}")
            return  # Exit if the emoji is not a supported flag

        # Get the original message content
        original_text = reaction.message.content
        print(f"Translating message: {original_text} to {LANGUAGES.get(language_code, 'unknown language')}.")

        try:
            # Translate the text
            translation = self.translator.translate(original_text, dest=language_code)
            translated_text = translation.text
            source_lang = translation.src.upper()  # Get the source language code in uppercase
            print(f"Translated from {source_lang} to {language_code.upper()} successfully.")

            # Send a reply with the translation, formatted as in the example
            await reaction.message.reply(
                f"**From {source_lang} To {language_code.upper()}**:\n{translated_text}\n\n"
                f"Translation requested by {user.mention} from Flag-Reaction Feature."
            )

        except Exception as e:
            error_msg = f"Error during translation: {e}"
            print(error_msg)
            await reaction.message.channel.send("An error occurred while translating the message.")

async def setup(bot):
    await bot.add_cog(TranslatorCog(bot))
