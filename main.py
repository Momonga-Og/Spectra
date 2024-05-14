import discord
from gtts import gTTS
import os
import asyncio  
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.members = True  
intents.voice_states = True  

client = discord.Client(intents=intents)

def text_to_speech(text, filename):
    tts = gTTS(text)
    tts.save(filename)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        try:
            if not client.voice_clients:
                vc = await after.channel.connect()
            else:
                vc = client.voice_clients[0]
            
            audio_file = f'{member.name}_welcome.mp3'
            welcome_text = f'Welcome to the voice channel, {member.name}!'
            text_to_speech(welcome_text, audio_file)
            
            vc.play(discord.FFmpegPCMAudio(audio_file))

            while vc.is_playing():
                await asyncio.sleep(1)

            if vc.is_connected():
                await vc.disconnect()

            # Clean up the audio file after use
            # os.remove(audio_file)
        except Exception as e:
            logging.error(f"Error in on_voice_state_update: {e}")

client.run(DISCORD_BOT_TOKEN)
