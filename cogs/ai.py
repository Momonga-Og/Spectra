import discord
from discord.ext import commands
import requests
import json

# Replace with your actual Google Gemini API key
API_KEY = 'AIzaSyB8kx3kPnaCJQtcXnZa-QnPS0uNgYIFwoM'

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ai", description="Start a conversation with Spectra using AI.")
    async def ai(self, ctx: commands.Context, *, prompt: str):
        # Notify the user that the bot is processing the request
        await ctx.send("Thinking...")

        # Define the request payload for the AI API
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        # Set up headers and URL, then send the request to Google Gemini API
        headers = {
            'Content-Type': 'application/json'
        }
        
        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}'
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # Check if the response is successful
        if response.status_code == 200:
            result = response.json()
            # Print the raw JSON response for debugging
            print("API Response:", json.dumps(result, indent=2))

            # Try to find the AI response in the returned JSON
            ai_response = ""
            try:
                # Flexible extraction to handle potential variations in response structure
                if "contents" in result and result["contents"]:
                    first_content = result["contents"][0]
                    if "parts" in first_content and first_content["parts"]:
                        ai_response = first_content["parts"][0].get("text", "Response found but text is missing.")
                    else:
                        ai_response = "Response found but parts are missing."
                else:
                    ai_response = "Response found but contents are missing."

                await ctx.send(f"Spectra: {ai_response}")
            except Exception as e:
                # Catch any other parsing errors and provide feedback
                print(f"Error while parsing response: {e}")
                await ctx.send("Spectra: Unexpected response format received.")
        else:
            # Show the error message and status code for further investigation
            await ctx.send(f"Error: Unable to fetch a response from AI. Status code: {response.status_code}, Response: {response.text}")

async def setup(bot: commands.Bot):
    await bot.add_cog(AI(bot))
