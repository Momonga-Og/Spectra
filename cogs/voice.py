import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import logging
import random
from gtts import gTTS
from io import BytesIO
import speech_recognition as sr
import numpy as np
from pydub import AudioSegment
import wavelink

logging.basicConfig(level=logging.INFO)

class VoiceAI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}
        self.audio_effects = {
            "robot": self.apply_robot_effect,
            "echo": self.apply_echo_effect,
            "pitch_shift": self.apply_pitch_shift
        }

    def get_voice_state(self, guild_id):
        state = self.voice_states.get(guild_id)
        if not state:
            state = VoiceState(self.bot, self)
            self.voice_states[guild_id] = state
        return state

    async def cog_unload(self):
        for state in self.voice_states.values():
            await state.stop()

    def text_to_speech(self, text, effect=None):
        fp = BytesIO()
        tts = gTTS(text)
        tts.write_to_fp(fp)
        fp.seek(0)
        
        if effect and effect in self.audio_effects:
            return self.audio_effects[effect](fp)
        return fp

    def apply_robot_effect(self, audio_fp):
        audio = AudioSegment.from_file(audio_fp, format="mp3")
        robot_audio = audio.overlay(audio.invert_phase())
        output = BytesIO()
        robot_audio.export(output, format="mp3")
        output.seek(0)
        return output

    def apply_echo_effect(self, audio_fp):
        audio = AudioSegment.from_file(audio_fp, format="mp3")
        echo_audio = audio + audio.overlay(audio.fade_in(1000), position=100)
        output = BytesIO()
        echo_audio.export(output, format="mp3")
        output.seek(0)
        return output

    def apply_pitch_shift(self, audio_fp):
        audio = AudioSegment.from_file(audio_fp, format="mp3")
        shifted = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * 1.2)
        }).set_frame_rate(audio.frame_rate)
        output = BytesIO()
        shifted.export(output, format="mp3")
        output.seek(0)
        return output

    @app_commands.command(name='join', description='Join a voice channel')
    async def _join(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            return await interaction.response.send_message("You're not in a voice channel.")
        
        destination = interaction.user.voice.channel
        voice_state = self.get_voice_state(interaction.guild_id)

        if voice_state.voice:
            await voice_state.voice.move_to(destination)
        else:
            voice_state.voice = await destination.connect()

        await interaction.response.send_message(f"Joined {destination.name}")

    @app_commands.command(name='leave', description='Leave the voice channel')
    async def _leave(self, interaction: discord.Interaction):
        voice_state = self.get_voice_state(interaction.guild_id)
        if not voice_state.voice:
            return await interaction.response.send_message("Not connected to any voice channel.")
        
        await voice_state.stop()
        del self.voice_states[interaction.guild_id]
        await interaction.response.send_message("Left the voice channel.")

    @app_commands.command(name='speak', description='Make the bot speak a message')
    async def _speak(self, interaction: discord.Interaction, message: str):
        voice_state = self.get_voice_state(interaction.guild_id)
        if not voice_state.voice:
            return await interaction.response.send_message("I'm not in a voice channel. Use /join first.")
        
        await interaction.response.defer()
        audio_fp = self.text_to_speech(message, effect=random.choice(list(self.audio_effects.keys())))
        voice_state.voice.play(discord.FFmpegPCMAudio(audio_fp, pipe=True))
        await interaction.followup.send(f"Speaking: {message}")

    @app_commands.command(name='listen', description='Make the bot listen and transcribe speech')
    async def _listen(self, interaction: discord.Interaction):
        voice_state = self.get_voice_state(interaction.guild_id)
        if not voice_state.voice:
            return await interaction.response.send_message("I'm not in a voice channel. Use /join first.")
        
        await interaction.response.send_message("Listening... Speak now!")
        
        r = sr.Recognizer()
        with sr.Microphone() as source:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
        
        try:
            text = r.recognize_google(audio)
            await interaction.followup.send(f"I heard: {text}")
        except sr.UnknownValueError:
            await interaction.followup.send("Sorry, I couldn't understand that.")
        except sr.RequestError:
            await interaction.followup.send("Sorry, my speech recognition service is down.")

    @app_commands.command(name='play', description='Play a song from YouTube')
    async def _play_music(self, interaction: discord.Interaction, query: str):
        voice_state = self.get_voice_state(interaction.guild_id)
        if not voice_state.voice:
            return await interaction.response.send_message("I'm not in a voice channel. Use /join first.")
        
        await interaction.response.defer()
        
        try:
            track = await wavelink.YouTubeTrack.search(query, return_first=True)
        except Exception as e:
            return await interaction.followup.send(f"An error occurred while searching: {str(e)}")

        if not track:
            return await interaction.followup.send("No track found.")

        await voice_state.voice.play(track)
        await interaction.followup.send(f"Now playing: {track.title}")

class VoiceState:
    def __init__(self, bot, cog):
        self.bot = bot
        self.cog = cog
        self.voice = None
        self.current = None

    async def stop(self):
        if self.voice:
            await self.voice.disconnect()
            self.voice = None

async def setup(bot):
    await bot.add_cog(VoiceAI(bot))
