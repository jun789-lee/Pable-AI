# AI Diary App

Advanced AI-powered diary applications with both text and voice interfaces for daily reflection and automated diary generation.

## Applications

### 1. Text-Based AI Diary (`ai_diary.py`)
- Interactive text conversation with GPT-4o-mini
- Thoughtful questions to guide daily reflection
- First-person narrative diary generation
- Simple CLI interface

### 2. Voice AI Diary (`voice_diary_simple.py`) ⭐ **NEW**
- **Voice + Text input options**
- **Whisper STT** → **GPT-4o-mini** conversation
- Windows-compatible audio recording
- Built-in emotion analysis
- Budget controls and error handling

## Quick Start - Voice Diary

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run simple voice diary:**
   ```bash
   python voice_diary_simple.py
   ```

3. **Usage:**
   - Type **'v'** for voice input (ENTER to record/stop)
   - Type **'t'** for text input
   - Type **'quit'** to end and generate diary

See `VOICE_SETUP.md` for detailed setup instructions.

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up OpenAI API key:**
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key to `.env`:
     ```
     OPENAI_API_KEY=your_actual_api_key_here
     ```

## Features Comparison

| Feature | Text Diary | Voice Diary |
|---------|------------|-------------|
| Input Method | Text typing | Voice recording |
| AI Conversation | ✅ | ✅ |
| Emotion Analysis | Basic | Advanced |
| Audio Output | ❌ | ✅ TTS |
| Real-time | ❌ | ✅ |
| Budget Controls | ❌ | ✅ |
| Error Handling | Basic | Advanced |

## Files

- `ai_diary.py` - Text-based diary application
- `voice_diary_simple.py` - Simplified voice diary (Windows compatible)
- `voice_diary.py` - Advanced voice diary (experimental)
- `diary_entries.json` - Text diary entries
- `simple_voice_diary_YYYY-MM-DD.json` - Voice diary entries
- `HISTORY.md` - Development process documentation
- `CODING_TUTORIAL.md` - Step-by-step coding tutorial
- `VOICE_SETUP.md` - Voice diary setup guide

## Example Output

Both apps generate first-person diary entries like:
> "Today I felt a mix of accomplishment and tiredness. I completed that important project at work which gave me a real sense of satisfaction, but the long hours left me drained. I'm grateful for my supportive team and looking forward to a relaxing weekend..."