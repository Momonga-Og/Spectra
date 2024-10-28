import discord
from discord.ext import commands
import requests
import json

API_KEY = 'AIzaSyB8kx3kPnaCJQtcXnZa-QnPS0uNgYIFwoM'

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Dictionary to store conversation history per user
        self.user_memory = {}

    @commands.hybrid_command(name="ai", description="Start a conversation with Spectra using AI.")
    async def ai(self, ctx: commands.Context, *, prompt: str):
        user_id = ctx.author.id

        # Initialize memory for the user if it doesn't exist
        if user_id not in self.user_memory:
            self.user_memory[user_id] = []

        # Add the new prompt to the user's memory
        self.user_memory[user_id].append(f"User: {prompt}")

        # Construct the conversation history as input
        conversation_history = "\n".join(self.user_memory[user_id])

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": conversation_history
                        }
                    ]
                }
            ]
        }

        headers = {
            'Content-Type': 'application/json'
        }

        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}'
        response = requests.post(url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            result = response.json()
            
            # Extract AI response
            if "candidates" in result and result["candidates"]:
                first_candidate = result["candidates"][0]
                content = first_candidate.get("content", {})
                if "parts" in content and content["parts"]:
                    ai_response = content["parts"][0].get("text", "Response text is missing.")
                else:
                    ai_response = "Spectra: Response found but parts are missing."
            elif "error" in result:
                error_message = result["error"].get("message", "Unknown error")
                ai_response = f"Spectra: API error - {error_message}"
            else:
                ai_response = "Spectra: Unexpected response structure."

            # Add AI response to user's memory
            self.user_memory[user_id].append(f"Spectra: {ai_response}")

            # Split response into chunks of up to 1900 characters
            max_length = 1900
            chunks = [ai_response[i:i + max_length] for i in range(0, len(ai_response), max_length)]
            
            for chunk in chunks:
                await ctx.send(chunk)
        else:
            await ctx.send(f"Error: Unable to fetch a response from AI. Status code: {response.status_code}, Response: {response.text}")

async def setup(bot: commands.Bot):
    await bot.add_cog(AI(bot))
