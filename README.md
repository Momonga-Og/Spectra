# Imcoming
Discord Bot 
Name: Imcoming Bot
Purpose
The Imcoming Bot is designed to enhance the experience of Discord users by providing text-to-speech functionality and voice channel automation. It can greet users who join voice channels, convert text to audio, and engage in other voice-related interactions.

Core Features
Voice Channel Greetings: The bot automatically greets users who join a voice channel. It uses Google Text-to-Speech (gTTS) to create a custom greeting message, which is then played in the voice channel.
Text-to-Speech: The bot can convert text into audio files, allowing for a wide range of voice-based interactions.
Automated Audio Playback: The bot plays audio messages when users join specific voice channels. It disconnects after playing the audio to avoid redundancy or unnecessary connections.
Discord Intents: Supports a variety of intents, including member events and voice state events, allowing it to monitor voice channel activity and respond accordingly.
Technical Implementation
Discord Library: Built using discord.py, a popular Python library for creating Discord bots.
Google Text-to-Speech (gTTS): Converts text into speech, used for creating audio files for voice channel greetings.
FFmpeg Integration: Utilizes FFmpeg for audio processing, required for playing audio in Discord voice channels.
Asynchronous Handling: Uses asyncio for efficient, non-blocking operations.
