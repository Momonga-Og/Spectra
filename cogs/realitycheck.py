import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio

class RealityCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.questions = [
            {"question": "Do you sometimes feel like you're being watched?", "answer": "yes"},
            {"question": "Have you ever felt like your reflection in the mirror is not really you?", "answer": "yes"},
            {"question": "Do you ever hear whispers when you're alone?", "answer": "yes"},
            {"question": "Do you remember what you were doing before starting this test?", "answer": "yes"},
            {"question": "Are you sure you're alone right now?", "answer": "yes"},
            {"question": "Do you trust your own memories?", "answer": "yes"},
            {"question": "Do you feel a presence in the room with you?", "answer": "yes"},
            {"question": "Can you be certain that your surroundings are real?", "answer": "yes"},
            {"question": "Do you ever feel like you're living in a dream?", "answer": "yes"},
            {"question": "Are you who you think you are?", "answer": "yes"}
        ]
        self.scenarios = [
            "You hear a faint whisper calling your name. What do you do?",
            "You see a shadow moving in the corner of your eye. How do you react?",
            "You feel a cold breeze, but all the windows are closed. What's your first thought?",
            "Your reflection in the mirror seems to lag behind your movements. What do you think?",
            "You receive a message from an unknown number saying, 'I know what you did.' How do you respond?"
        ]

    @app_commands.command(name="starttest", description="Start the horror-themed reality check test.")
    async def start_test(self, interaction: discord.Interaction):
        await interaction.response.send_message("Welcome to the Reality Check Test... Are you ready to face your fears?")
        score = 0

        for i in range(3):  # Asking 3 random questions
            question = random.choice(self.questions)
            await interaction.followup.send(question["question"])

            def check(m):
                return m.author == interaction.user and m.channel == interaction.channel

            try:
                msg = await self.bot.wait_for('message', timeout=30.0, check=check)
                if msg.content.lower() == question["answer"]:
                    score += 1
                    await interaction.followup.send("Interesting... Let's continue.")
                else:
                    await interaction.followup.send("That's not the answer I was expecting...")
            except asyncio.TimeoutError:
                await interaction.followup.send("You took too long to respond... Are you scared?")

        for i in range(2):  # Presenting 2 random scenarios
            scenario = random.choice(self.scenarios)
            await interaction.followup.send(scenario)

            def check(m):
                return m.author == interaction.user and m.channel == interaction.channel

            try:
                msg = await self.bot.wait_for('message', timeout=30.0, check=check)
                await interaction.followup.send(f"Interesting response: {msg.content}")
            except asyncio.TimeoutError:
                await interaction.followup.send("Too scared to respond?")

        await interaction.followup.send(f"Test completed! Your score is {score}/3. Did you uncover anything unsettling?")

async def setup(bot):
    await bot.add_cog(realityCheck(bot))
