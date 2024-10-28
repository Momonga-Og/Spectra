import discord
from discord.ext import commands
import requests
import json

API_KEY = 'AIzaSyB8kx3kPnaCJQtcXnZa-QnPS0uNgYIFwoM'

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ai", description="Start a conversation with Spectra using AI.")
    async def ai(self, ctx: commands.Context, *, prompt: str):
        await ctx.send("Thinking...")

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

        headers = {
            'Content-Type': 'application/json'
        }
        
        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}'
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            result = response.json()
            
            # Debug line to print the full JSON response to see its structure
            await ctx.send(f"Debugging Response JSON: ```{json.dumps(result, indent=2)}```")

            # Attempt to extract AI response
            if "contents" in result and result["contents"]:
                first_content = result["contents"][0]
                if "parts" in first_content and first_content["parts"]:
                    ai_response = first_content["parts"][0].get("text", "Response text is missing.")
                else:
                    ai_response = "Spectra: Response found but parts are missing."
            elif "error" in result:
                error_message = result["error"].get("message", "Unknown error")
                ai_response = f"Spectra: API error - {error_message}"
            else:
                ai_response = "Spectra: Unexpected response structure."

            await ctx.send(ai_response)
        else:
            await ctx.send(f"Error: Unable to fetch a response from AI. Status code: {response.status_code}, Response: {response.text}")

async def setup(bot: commands.Bot):
    await bot.add_cog(AI(bot))
