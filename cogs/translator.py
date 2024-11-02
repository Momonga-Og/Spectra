# translator.py
import discord
from googletrans import Translator

translator = Translator()

# Define flag emojis and their corresponding language codes
LANGUAGE_MAP = {
    "🇺🇸": "en",  # English
    "🇫🇷": "fr",  # French
    "🇪🇸": "es",  # Spanish
    "🇦🇪": "ar",  # Arabic
    "🇩🇪": "de",  # German
    # Add more languages as needed
}

async def handle_reaction(reaction, user):
    # Ignore bot reactions or reactions added by the message author
    if user.bot or reaction.message.author == user:
        return

    # Get the language code from the emoji
    language_code = LANGUAGE_MAP.get(str(reaction.emoji))
    if not language_code:
        return  # Exit if the emoji is not a supported flag

    # Get the original message content
    original_text = reaction.message.content

    # Translate the text
    try:
        translation = translator.translate(original_text, dest=language_code)
        translated_text = translation.text
        # Send the translation as a reply or DM
        await reaction.message.reply(
            f"Translation ({language_code.upper()}): {translated_text}"
        )
    except Exception as e:
        print(f"Error: {e}")
