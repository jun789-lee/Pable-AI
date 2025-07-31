# Voice AI Diary Setup Guide

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install system audio dependencies:**
   
   **Windows:**
   - PyAudio should install automatically
   - If issues, install: `pip install pipwin && pipwin install pyaudio`
   
   **macOS:**
   ```bash
   brew install portaudio
   pip install pyaudio
   ```
   
   **Linux:**
   ```bash
   sudo apt-get install portaudio19-dev python3-pyaudio
   pip install pyaudio
   ```

3. **Run voice diary:**
   ```bash
   python voice_diary.py
   ```

## Voice Controls

- **Hold SPACEBAR** - Record your voice
- **Release SPACEBAR** - Stop recording
- **Press 'q'** - End conversation and generate diary
- **Ctrl+C** - Exit without saving

## Features

✅ **Push-to-talk voice recording**
✅ **Whisper STT transcription**
✅ **GPT-4o-mini conversation**
✅ **OpenAI TTS with Nova voice**
✅ **Built-in emotion analysis**
✅ **First-person diary generation**
✅ **JSON conversation storage**
✅ **API budget controls (100 calls limit)**
✅ **Error handling with fallback to text**

## File Output

Creates `voice_diary_YYYY-MM-DD.json` with:
- Complete conversation history
- Emotion analysis for each message
- Generated diary summary
- API usage tracking

## Troubleshooting

**Audio Issues:**
- Ensure microphone permissions are granted
- Check default audio devices in system settings
- Try running as administrator on Windows

**API Errors:**
- Verify OpenAI API key in .env file
- Check API quota and billing
- Monitor budget limit (adjustable in code)

**Import Errors:**
- Install missing packages individually
- Use virtual environment for clean setup