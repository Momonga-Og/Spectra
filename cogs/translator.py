# translator.py

import discord
from discord.ext import commands
from googletrans import Translator, LANGUAGES

class TranslatorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Initialize the translator and confirm it's functional
        self.translator = Translator()
        try:
            test_translation = self.translator.translate("Hello", dest="es")
            print(f"Translator initialized successfully. Test translation: 'Hello' -> '{test_translation.text}'")
        except Exception as e:
            print(f"Error initializing Translator: {e}")

        # Language map for reactions
        self.LANGUAGE_MAP = {
            "🇺🇸": "en",  # English
            "🇫🇷": "fr",  # French
            "🇪🇸": "es",  # Spanish
            "🇦🇪": "ar",  # Arabic
            "🇩🇪": "de",  # German
            # Add more languages as needed
        }

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # Confirm reaction detection
        print("Reaction detected.")

        # Check the bot's permissions for reading message history and sending messages
        channel = reaction.message.channel
        bot_permissions = channel.permissions_for(channel.guild.me)
        if not bot_permissions.read_message_history:
            print("Bot lacks 'read_message_history' permission.")
            return
        if not bot_permissions.send_messages:
            print("Bot lacks 'send_messages' permission.")
            return

        # Ignore reactions from bots or the author of the message
        if user.bot or reaction.message.author == user:
            print("Ignoring reaction from a bot or the message author.")
            return

        # Check if the emoji used corresponds to a supported language
        emoji_used = str(reaction.emoji)
        language_code = self.LANGUAGE_MAP.get(emoji_used)
        if not language_code:
            print(f"Unsupported emoji detected: {emoji_used}")
            return

        # Log the translation attempt
        original_text = reaction.message.content
        print(f"Translating message: '{original_text}' to {LANGUAGES.get(language_code, 'unknown language')}.")

        # Translate the text
        try:
            translation = self.translator.translate(original_text, dest=language_code)
            translated_text = translation.text
            source_lang = LANGUAGES.get(translation.src, translation.src).capitalize()
            target_lang = LANGUAGES.get(language_code, language_code).capitalize()
            print(f"Translation successful: '{original_text}' from {source_lang} to {target_lang} -> '{translated_text}'")

            # Send the translation in the same channel
            await channel.send(
                f"{user.mention} requested a translation:\n"
                f"**From {source_lang} to {target_lang}**:\n{translated_text}"
            )

        except Exception as e:
            print(f"Translation failed: {e}")
            await channel.send("An error occurred while translating the message. Please try again later.")

async def setup(bot):
    await bot.add_cog(TranslatorCog(bot))
