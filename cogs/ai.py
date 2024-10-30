import discord
from discord.ext import commands
import requests
import json
import os

API_KEY = 'AIzaSyB8kx3kPnaCJQtcXnZa-QnPS0uNgYIFwoM'
ADMIN_USER_ID = 486652069831376943  # Only Abdellatif can use administrative commands

class SpectraAI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conversation_file = 'conversation_history.json'
        self.conversation_data = self.load_conversation_data()

    def load_conversation_data(self):
        if os.path.exists(self.conversation_file):
            with open(self.conversation_file, 'r') as file:
                return json.load(file)
        return {}

    def save_conversation_data(self):
        with open(self.conversation_file, 'w') as file:
            json.dump(self.conversation_data, file, indent=4)

    def store_conversation(self, user_id, prompt, response):
        if str(user_id) not in self.conversation_data:
            self.conversation_data[str(user_id)] = []
        self.conversation_data[str(user_id)].append({
            'prompt': prompt,
            'response': response
        })
        self.save_conversation_data()

    def get_conversation_history(self, user_id):
        if str(user_id) in self.conversation_data:
            conversations = self.conversation_data[str(user_id)][-5:]
            return "\n".join([f"User: {entry['prompt']}\nAI: {entry['response']}" for entry in conversations])
        return "No conversation history available."

    async def process_ai_instruction(self, ctx, ai_response):
        if ctx.author.id == ADMIN_USER_ID:
            if "ban" in ai_response or "role" in ai_response or "mute" in ai_response:
                return f"Executing admin command: {ai_response}"
        return None

    @commands.hybrid_command(name="ai", description="Ask Spectra AI for assistance.")
    async def ai(self, ctx: commands.Context, *, prompt: str):
        user_id = ctx.author.id
        conversation_history = self.get_conversation_history(user_id)
        conversation_history += f"\nUser: {prompt}"

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
            if "candidates" in result and result["candidates"]:
                ai_response = result["candidates"][0].get("content", {}).get("parts", [{}])[0].get("text", "Response text is missing.")
            else:
                ai_response = "Spectra: Unexpected response structure."

            ai_response = ai_response[:1900]
            self.store_conversation(user_id, prompt, ai_response)

            admin_response = await self.process_ai_instruction(ctx, ai_response)
            if admin_response:
                await ctx.send(admin_response)
            else:
                await ctx.send(ai_response)
        else:
            await ctx.send(f"Error: Unable to fetch a response from AI. Status code: {response.status_code}, Response: {response.text}")

async def setup(bot: commands.Bot):
    await bot.add_cog(SpectraAI(bot))
