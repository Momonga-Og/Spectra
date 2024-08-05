import discord
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

    async def cog_before_invoke(self, ctx):
        ctx.voice_state = self.get_voice_state(ctx.guild.id)

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
        # Implement robot voice effect
        audio = AudioSegment.from_file(audio_fp, format="mp3")
        robot_audio = audio.overlay(audio.invert_phase())
        output = BytesIO()
        robot_audio.export(output, format="mp3")
        output.seek(0)
        return output

    def apply_echo_effect(self, audio_fp):
        # Implement echo effect
        audio = AudioSegment.from_file(audio_fp, format="mp3")
        echo_audio = audio + audio.overlay(audio.fade_in(1000), position=100)
        output = BytesIO()
        echo_audio.export(output, format="mp3")
        output.seek(0)
        return output

    def apply_pitch_shift(self, audio_fp):
        # Implement pitch shift effect
        audio = AudioSegment.from_file(audio_fp, format="mp3")
        shifted = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * 1.2)
        }).set_frame_rate(audio.frame_rate)
        output = BytesIO()
        shifted.export(output, format="mp3")
        output.seek(0)
        return output

    @commands.command(name='join', invoke_without_subcommand=True)
    async def _join(self, ctx):
        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return
        ctx.voice_state.voice = await destination.connect()

    @commands.command(name='speak')
    async def _speak(self, ctx, *, message):
        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)
        audio_fp = self.text_to_speech(message, effect=random.choice(list(self.audio_effects.keys())))
        ctx.voice_state.voice.play(discord.FFmpegPCMAudio(audio_fp, pipe=True))

    @commands.command(name='listen')
    async def _listen(self, ctx):
        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)
        
        r = sr.Recognizer()
        with sr.Microphone() as source:
            audio = r.listen(source)
        
        try:
            text = r.recognize_google(audio)
            await ctx.send(f"I heard: {text}")
        except sr.UnknownValueError:
            await ctx.send("Sorry, I couldn't understand that.")
        except sr.RequestError:
            await ctx.send("Sorry, my speech recognition service is down.")

    @commands.command(name='music')
    async def _play_music(self, ctx, *, query: str):
        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)
        
        player = await wavelink.NodePool.get_node().get_player(ctx.guild)
        tracks = await wavelink.YouTubeTrack.search(query)
        if not tracks:
            await ctx.send("No tracks found.")
            return
        await player.play(tracks[0])
        await ctx.send(f"Now playing: {tracks[0].title}")

class VoiceState:
    def __init__(self, bot, cog):
        self.bot = bot
        self.cog = cog
        self.voice = None
        self.audio_player = None

    async def stop(self):
        if self.voice:
            await self.voice.disconnect()
            self.voice = None

async def setup(bot):
    await bot.add_cog(VoiceAI(bot))

async def main():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='!', intents=intents)

    async def start_nodes():
        node = await wavelink.NodePool.create_node(
            bot=bot,
            host='localhost',
            port=2333,
            password='youshallnotpass'
        )

    bot.loop.create_task(start_nodes())
    await bot.add_cog(VoiceAI(bot))
    await bot.start('your_token_here')

if __name__ == "__main__":
    asyncio.run(main())
