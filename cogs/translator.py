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
        print("Reaction detected.")

        # Ignore bot reactions
        if user.bot:
            print("Ignoring reaction from a bot.")
            return

        channel = reaction.message.channel
        bot_permissions = channel.permissions_for(channel.guild.me)
        if not bot_permissions.read_message_history:
            print("Bot lacks 'read_message_history' permission.")
            return
        if not bot_permissions.send_messages:
            print("Bot lacks 'send_messages' permission.")
            return

        emoji_used = str(reaction.emoji)
        language_code = self.LANGUAGE_MAP.get(emoji_used)
        if not language_code:
            print(f"Unsupported emoji detected: {emoji_used}")
            return

        original_text = reaction.message.content.strip()
        if not original_text:
            print("Message content is empty or non-text. Skipping.")
            return

        print(f"Translating message: '{original_text}' to {LANGUAGES.get(language_code, 'unknown language')}.")

        try:
            translation = self.translator.translate(original_text, dest=language_code)
            translated_text = translation.text
            source_lang = LANGUAGES.get(translation.src, translation.src).capitalize()
            target_lang = LANGUAGES.get(language_code, language_code).capitalize()
            print(f"Translation successful: '{original_text}' from {source_lang} to {target_lang} -> '{translated_text}'")

            embed = discord.Embed(
                title="Translation Result",
                description=f"{user.mention} requested a translation:",
                color=discord.Color.blue()
            )
            embed.add_field(name="Original Text", value=f"`{original_text}`", inline=False)
            embed.add_field(name="Translated Text", value=f"`{translated_text}`", inline=False)
            embed.add_field(name="Languages", value=f"**From:** {source_lang}\n**To:** {target_lang}", inline=False)
            embed.set_footer(text="Powered by Google Translate")
            
            await channel.send(embed=embed)

        except Exception as e:
            print(f"Translation failed: {e}")
            await channel.send("An error occurred while translating the message. Please try again later.")

    @commands.command()
    async def translate_message(self, ctx, message_id: int, lang: str):
        """Translate an older message given its ID and target language."""
        try:
            message = await ctx.channel.fetch_message(message_id)
            original_text = message.content.strip()

            if not original_text:
                await ctx.send("The specified message is empty or non-text.")
                return

            translation = self.translator.translate(original_text, dest=lang)
            translated_text = translation.text
            source_lang = LANGUAGES.get(translation.src, translation.src).capitalize()
            target_lang = LANGUAGES.get(lang, lang).capitalize()
            print(f"Translation successful: '{original_text}' from {source_lang} to {target_lang} -> '{translated_text}'")

            embed = discord.Embed(
                title="Translation Result",
                description=f"Translation of message ID {message_id}:",
                color=discord.Color.green()
            )
            embed.add_field(name="Original Text", value=f"`{original_text}`", inline=False)
            embed.add_field(name="Translated Text", value=f"`{translated_text}`", inline=False)
            embed.add_field(name="Languages", value=f"**From:** {source_lang}\n**To:** {target_lang}", inline=False)
            embed.set_footer(text="Powered by Google Translate")

            await ctx.send(embed=embed)

        except Exception as e:
            print(f"Translation failed: {e}")
            await ctx.send("An error occurred while translating the message. Please try again later.")

async def setup(bot):
    await bot.add_cog(TranslatorCog(bot))
