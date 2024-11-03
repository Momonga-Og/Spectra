# translator.py

import discord
from discord.ext import commands
from googletrans import Translator, LANGUAGES

class TranslatorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            # Initialize the Translator and test it with a basic translation
            self.translator = Translator()
            test_translation = self.translator.translate("Hello", dest="es")
            print(f"Translator initialized successfully. Test translation: 'Hello' to Spanish -> '{test_translation.text}'")
        except Exception as e:
            print(f"Error initializing Translator: {e}")

        # Language map for reactions
        self.LANGUAGE_MAP = {
            "🇺🇸": "en",  # English
            "🇫🇷": "fr",  # French
            "🇪🇸": "es",  # Spanish
            ":flag_es:": "es",  # Spanish (emoji code version)
            "🇦🇪": "ar",  # Arabic
            "🇩🇪": "de",  # German
            # Add other languages if necessary
        }

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        print("Reaction detected.")  # Confirm reaction is detected

        # Check permissions explicitly
        channel = reaction.message.channel
        bot_member = channel.guild.me
        if not channel.permissions_for(bot_member).read_message_history:
            print("Bot lacks 'read_message_history' permission.")
            return
        if not channel.permissions_for(bot_member).send_messages:
            print("Bot lacks 'send_messages' permission.")
            return

        # Ignore if reaction is from a bot or from the message author
        if user.bot or reaction.message.author == user:
            print("Ignoring reaction from bot or message author.")
            return

        # Check if emoji corresponds to a supported language
        emoji_used = str(reaction.emoji)
        language_code = self.LANGUAGE_MAP.get(emoji_used)
        if not language_code:
            print(f"Unsupported emoji detected: {emoji_used}")
            return

        # Log the message content and target language
        original_text = reaction.message.content
        print(f"Attempting to translate message: '{original_text}' to {LANGUAGES.get(language_code, 'unknown language')}.")

        # Attempt translation
        try:
            translation = self.translator.translate(original_text, dest=language_code)
            translated_text = translation.text
            source_lang = translation.src.upper()
            print(f"Translation successful: '{original_text}' from {source_lang} to {language_code.upper()} -> '{translated_text}'")

            # Send the translated message in the same channel, tagging the user
            await channel.send(
                f"{user.mention} requested a translation:\n"
                f"**From {source_lang} To {language_code.upper()}**:\n{translated_text}"
            )

        except Exception as e:
            error_message = f"Translation failed: {e}"
            print(error_message)

            # Send error message in the same channel for immediate feedback
            await channel.send(
                "An error occurred while translating the message. Please try again or contact support."
            )

            # Optionally, send error details to an admin channel for tracking
            # error_channel_id = 123456789012345678  # Replace with your actual channel ID
            # error_channel = bot.get_channel(error_channel_id)
            # if error_channel:
            #     await error_channel.send(f"Translation error in {channel.name} by {user.name}: {error_message}")

async def setup(bot):
    await bot.add_cog(TranslatorCog(bot))
