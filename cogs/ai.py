import discord
from discord.ext import commands
import requests
import json
import sqlite3

API_KEY = 'AIzaSyB8kx3kPnaCJQtcXnZa-QnPS0uNgYIFwoM'
ADMIN_USER_ID = 486652069831376943  # Only Abdellatif can use administrative commands

class SpectraAI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('conversation_history.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation (
                user_id INTEGER,
                prompt TEXT,
                response TEXT
            )
        ''')
        self.conn.commit()

    def store_conversation(self, user_id, prompt, response):
        self.cursor.execute('INSERT INTO conversation (user_id, prompt, response) VALUES (?, ?, ?)',
                            (user_id, prompt, response))
        self.conn.commit()

    def get_conversation_history(self, user_id):
        self.cursor.execute('SELECT prompt, response FROM conversation WHERE user_id = ? ORDER BY rowid DESC LIMIT 5', (user_id,))
        rows = self.cursor.fetchall()
        return "\n".join([f"User: {row[0]}\nAI: {row[1]}" for row in rows])

    async def process_ai_instruction(self, ctx, ai_response):
        # Process AI instructions only if it's an administrative action and from the admin user
        if ctx.author.id == ADMIN_USER_ID:
            if "ban" in ai_response or "role" in ai_response or "mute" in ai_response:
                # Parse and execute the admin command as necessary
                # Example:
                return f"Executing admin command: {ai_response}"
        return None  # If not an admin command or if user is not admin

    async def execute_spectra_command(self, ctx, command_name, *args):
        # Execute Spectra commands as per AI response or user request
        ...

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
                first_candidate = result["candidates"][0]
                content = first_candidate.get("content", {})
                if "parts" in content and content["parts"]:
                    ai_response = content["parts"][0].get("text", "Response text is missing.")
                else:
                    ai_response = "Spectra: Response found but parts are missing."
            else:
                ai_response = "Spectra: Unexpected response structure."

            ai_response = ai_response[:1900]

            self.store_conversation(user_id, prompt, ai_response)

            # Check for administrative instruction
            admin_response = await self.process_ai_instruction(ctx, ai_response)
            if admin_response:
                await ctx.send(admin_response)
            else:
                # Handle non-administrative response for everyone
                await ctx.send(ai_response)
        else:
            await ctx.send(f"Error: Unable to fetch a response from AI. Status code: {response.status_code}, Response: {response.text}")

async def setup(bot: commands.Bot):
    await bot.add_cog(SpectraAI(bot))
