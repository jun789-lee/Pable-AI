# AI Diary App

A simple CLI-based AI diary application that helps you reflect on your day through conversational questions and creates personalized diary entries.

## Features

- Interactive conversation with AI using GPT-4o-mini
- Thoughtful questions to guide daily reflection
- Automatic diary entry creation with emotional highlights and key events
- First-person narrative style summaries
- JSON storage for all diary entries

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

3. **Run the application:**
   ```bash
   python ai_diary.py
   ```

## How to Use

1. Run the script and start chatting with the AI
2. Answer the thoughtful questions about your day
3. Type 'quit' when you're done reflecting
4. Your diary entry will be automatically generated and saved

## Files

- `ai_diary.py` - Main application
- `diary_entries.json` - Your saved diary entries
- `requirements.txt` - Python dependencies
- `.env` - Your API key (create from .env.example)

## Example Output

The AI will create diary entries like:
> "Today I felt a mix of accomplishment and tiredness. I completed that important project at work which gave me a real sense of satisfaction, but the long hours left me drained. I'm grateful for my supportive team and looking forward to a relaxing weekend..."