import os
import json
import datetime
import time
import io
import tempfile
import uuid
from pathlib import Path
import pyaudio
import wave
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class SimpleVoiceDiary:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.conversation_data = []
        self.api_usage_count = 0
        self.max_api_calls = 50  # Reduced for testing
        
        # Audio settings
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000  # Reduced for better compatibility
        
        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()
        
        print("*** Simple Voice AI Diary ***")
        print("Commands:")
        print("1. Press ENTER to start recording")
        print("2. Press ENTER again to stop recording")
        print("3. Type 'quit' to end conversation")
    
    def check_api_limit(self):
        if self.api_usage_count >= self.max_api_calls:
            print(f"\\n*** API BUDGET LIMIT REACHED ({self.max_api_calls} calls) ***")
            return False
        return True
    
    def record_audio_simple(self):
        """Simple audio recording with ENTER key"""
        input("\\nPress ENTER to start recording...")
        
        print("*** RECORDING... Press ENTER to stop ***")
        
        frames = []
        stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        # Start recording
        import threading
        recording = True
        
        def stop_recording():
            nonlocal recording
            input()  # Wait for ENTER
            recording = False
        
        # Start the stop thread
        stop_thread = threading.Thread(target=stop_recording)
        stop_thread.daemon = True
        stop_thread.start()
        
        # Record until stopped
        while recording:
            try:
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                frames.append(data)
            except:
                break
        
        print("*** Recording stopped ***")
        
        stream.stop_stream()
        stream.close()
        
        if not frames:
            return None
        
        return b''.join(frames)
    
    def transcribe_audio(self, audio_data):
        """Convert audio to text using Whisper"""
        if not self.check_api_limit():
            return None
            
        try:
            # Create unique temp file
            temp_filename = f"voice_diary_{uuid.uuid4().hex}.wav"
            temp_path = os.path.join(tempfile.gettempdir(), temp_filename)
            
            # Save as WAV
            with wave.open(temp_path, 'wb') as wav_file:
                wav_file.setnchannels(self.CHANNELS)
                wav_file.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                wav_file.setframerate(self.RATE)
                wav_file.writeframes(audio_data)
            
            # Transcribe
            with open(temp_path, 'rb') as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="en"
                )
            
            self.api_usage_count += 1
            
            # Cleanup
            try:
                os.unlink(temp_path)
            except:
                pass
            
            return response.text.strip()
                
        except Exception as e:
            print(f"STT Error: {str(e)}")
            return input("STT failed. Please type your message: ").strip()
    
    def get_ai_response(self, user_message):
        """Get AI response using GPT-4o-mini"""
        if not self.check_api_limit():
            return None, None
            
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a supportive friend helping someone with their voice diary. Be warm, empathetic, and ask thoughtful follow-up questions. Keep responses under 50 words. At the end, include emotion analysis: EMOTION_ANALYSIS: [emotion] [0.0-1.0]"""
                    },
                    {"role": "user", "content": user_message}
                ],
                max_tokens=100,
                temperature=0.7
            )
            
            self.api_usage_count += 1
            ai_response = response.choices[0].message.content.strip()
            
            # Extract emotion
            emotion_analysis = None
            if "EMOTION_ANALYSIS:" in ai_response:
                parts = ai_response.split("EMOTION_ANALYSIS:")
                ai_response = parts[0].strip()
                emotion_part = parts[1].strip().split()
                if len(emotion_part) >= 2:
                    emotion_analysis = {
                        "dominant": emotion_part[0],
                        "intensity": float(emotion_part[1])
                    }
            
            return ai_response, emotion_analysis
            
        except Exception as e:
            print(f"AI Error: {str(e)}")
            return "I'm having trouble responding. Could you try again?", None
    
    def generate_diary_entry(self):
        """Generate diary entry from conversation"""
        if not self.conversation_data:
            return "No conversation to summarize."
            
        try:
            conversation_text = ""
            for item in self.conversation_data:
                speaker = "I said" if item["speaker"] == "user" else "AI asked"
                conversation_text += f"{speaker}: {item['message']}\\n"
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Create a first-person diary entry from this conversation. Write as if the user is personally writing their diary. Include emotions and key events. Use 'I' statements throughout."
                    },
                    {
                        "role": "user",
                        "content": f"Create a diary entry:\\n\\n{conversation_text}"
                    }
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            self.api_usage_count += 1
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Could not generate diary entry: {str(e)}"
    
    def save_conversation(self, diary_entry):
        """Save to JSON file"""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = f"simple_voice_diary_{today}.json"
        
        data = {
            "date": today,
            "conversation": self.conversation_data,
            "diary_entry": diary_entry,
            "api_usage": self.api_usage_count
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\\n*** Saved to {filename} ***")
    
    def run(self):
        """Main conversation loop"""
        print("\\n*** Starting Simple Voice Diary ***")
        print("AI: Hi! I'm here to help you reflect on your day. How are you feeling?")
        
        while True:
            try:
                choice = input("\\nEnter 'v' for voice, 't' for text, or 'quit' to end: ").lower()
                
                if choice == 'quit':
                    break
                elif choice == 'v':
                    # Voice input
                    audio_data = self.record_audio_simple()
                    if audio_data:
                        user_text = self.transcribe_audio(audio_data)
                        if not user_text:
                            continue
                    else:
                        continue
                elif choice == 't':
                    # Text input
                    user_text = input("You: ").strip()
                    if not user_text:
                        continue
                else:
                    print("Please enter 'v', 't', or 'quit'")
                    continue
                
                print(f"You: {user_text}")
                
                # Get AI response
                ai_response, emotion = self.get_ai_response(user_text)
                if not ai_response:
                    break
                
                print(f"AI: {ai_response}")
                
                # Store conversation
                self.conversation_data.append({
                    "speaker": "user",
                    "message": user_text,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "emotion": emotion
                })
                
                self.conversation_data.append({
                    "speaker": "ai",
                    "message": ai_response,
                    "timestamp": datetime.datetime.now().isoformat()
                })
                
            except KeyboardInterrupt:
                print("\\n*** Interrupted ***")
                break
        
        # Generate diary
        if self.conversation_data:
            print("\\n*** Generating diary entry... ***")
            diary_entry = self.generate_diary_entry()
            
            print("\\n" + "="*50)
            print("*** YOUR DIARY ENTRY ***")
            print("="*50)
            print(diary_entry)
            print("="*50)
            
            self.save_conversation(diary_entry)
            print(f"API calls used: {self.api_usage_count}")
        
        self.audio.terminate()
        print("\\n*** Voice Diary Complete ***")

if __name__ == "__main__":
    try:
        diary = SimpleVoiceDiary()
        diary.run()
    except Exception as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\\n*** Goodbye! ***")