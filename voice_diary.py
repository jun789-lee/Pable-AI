import os
import json
import datetime
import time
import io
import tempfile
from pathlib import Path
import pyaudio
import keyboard
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class VoiceDiary:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.conversation_data = []
        self.api_usage_count = 0
        self.max_api_calls = 100  # Budget control
        
        # Audio settings
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.SILENCE_THRESHOLD = 500
        self.SILENCE_DURATION = 2.0
        
        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()
        
        print("*** Voice AI Diary Initialized ***")
        print("Controls:")
        print("- Hold SPACEBAR to record voice")
        print("- Release SPACEBAR to stop recording")
        print("- Press 'q' to end conversation and generate diary")
        print("- Press 'Ctrl+C' to exit without saving")
    
    def check_api_limit(self):
        """Check if API usage is within budget"""
        if self.api_usage_count >= self.max_api_calls:
            print(f"\\n*** API BUDGET LIMIT REACHED ({self.max_api_calls} calls) ***")
            print("Shutting down to prevent excessive costs.")
            return False
        return True
    
    def record_audio(self):
        """Record audio while spacebar is held"""
        print("\\n*** Hold SPACEBAR and speak...")
        
        frames = []
        stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        # Wait for spacebar press
        while not keyboard.is_pressed('space'):
            time.sleep(0.01)
        
        print("*** Recording... (release SPACEBAR to stop)")
        
        # Record while spacebar is held
        while keyboard.is_pressed('space'):
            data = stream.read(self.CHUNK)
            frames.append(data)
        
        print("*** Recording stopped")
        
        stream.stop_stream()
        stream.close()
        
        if not frames:
            return None
        
        # Convert to audio file
        audio_data = b''.join(frames)
        return audio_data
    
    def transcribe_audio(self, audio_data, retry_count=0):
        """Convert audio to text using Whisper"""
        if not self.check_api_limit():
            return None
            
        try:
            # Create unique temp file name to avoid conflicts
            import uuid
            temp_filename = f"voice_diary_{uuid.uuid4().hex}.wav"
            temp_path = os.path.join(tempfile.gettempdir(), temp_filename)
            
            # Convert raw audio to WAV format
            import wave
            wav_file = wave.open(temp_path, 'wb')
            wav_file.setnchannels(self.CHANNELS)
            wav_file.setsampwidth(self.audio.get_sample_size(self.FORMAT))
            wav_file.setframerate(self.RATE)
            wav_file.writeframes(audio_data)
            wav_file.close()
            
            # Small delay to ensure file is fully written
            time.sleep(0.1)
            
            # Transcribe using Whisper
            with open(temp_path, 'rb') as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="en"
                )
                
            self.api_usage_count += 1
            
            # Clean up temp file with retry
            try:
                os.unlink(temp_path)
            except:
                time.sleep(0.5)
                try:
                    os.unlink(temp_path)
                except:
                    pass  # File cleanup failed, but transcription succeeded
            
            return response.text.strip()
                
        except Exception as e:
            print(f"STT Error: {str(e)}")
            
            if retry_count < 1:
                print("Retrying transcription...")
                time.sleep(1)  # Wait before retry
                return self.transcribe_audio(audio_data, retry_count + 1)
            else:
                print("STT failed twice. Falling back to text input.")
                return input("Type your message: ").strip()
    
    def get_ai_response(self, user_message, conversation_history):
        """Get AI response using GPT-4o-mini"""
        if not self.check_api_limit():
            return None, None
            
        try:
            # Build conversation context
            messages = [
                {
                    "role": "system",
                    "content": """You are a supportive friend helping someone reflect on their day through a voice diary. 
                    
                    Guidelines:
                    - Be warm, empathetic, and encouraging
                    - Ask thoughtful follow-up questions to help them express emotions
                    - Guide conversation naturally without being pushy
                    - Help them explore their feelings and daily experiences
                    - Keep responses conversational and under 50 words
                    - At the end, also provide a brief emotion analysis in this format: EMOTION_ANALYSIS: [dominant_emotion] [intensity_0_to_1]
                    
                    Example: "That sounds really challenging. How did that make you feel in the moment? EMOTION_ANALYSIS: frustrated 0.7" """
                }
            ]
            
            # Add conversation history
            for item in conversation_history[-6:]:  # Last 6 messages for context
                messages.append({
                    "role": "user" if item["speaker"] == "user" else "assistant",
                    "content": item["message"]
                })
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=100,
                temperature=0.7
            )
            
            self.api_usage_count += 1
            ai_response = response.choices[0].message.content.strip()
            
            # Extract emotion analysis
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
            print(f"AI Response Error: {str(e)}")
            return "I'm having trouble responding right now. Could you try again?", None
    
    def speak_text(self, text):
        """Convert text to speech using OpenAI TTS"""
        if not self.check_api_limit():
            return
            
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="nova",
                input=text,
                speed=1.0
            )
            
            self.api_usage_count += 1
            
            # Create unique temp file for audio
            import uuid
            temp_filename = f"voice_diary_tts_{uuid.uuid4().hex}.mp3"
            temp_path = os.path.join(tempfile.gettempdir(), temp_filename)
            
            try:
                # Save TTS audio to file
                response.stream_to_file(temp_path)
                time.sleep(0.2)  # Ensure file is fully written
                
                # Play using system command (cross-platform)
                import subprocess
                import platform
                
                if platform.system() == "Windows":
                    # Simple approach - just print text for Windows compatibility
                    print(f"AI: {text}")
                    print("(Audio playback disabled on Windows due to file access issues)")
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["afplay", temp_path], timeout=10)
                else:  # Linux
                    subprocess.run(["mpg123", temp_path], timeout=10)
                
            except Exception as audio_error:
                print(f"TTS Error: {audio_error}")
                print(f"AI: {text}")  # Fallback to text display
            
            finally:
                # Clean up temp file with retry
                try:
                    time.sleep(0.5)
                    os.unlink(temp_path)
                except:
                    try:
                        time.sleep(1)
                        os.unlink(temp_path)
                    except:
                        pass  # File cleanup failed, but audio succeeded
                
        except Exception as e:
            print(f"TTS Error: {str(e)}")
            print(f"AI: {text}")  # Fallback to text display
    
    def generate_diary_entry(self):
        """Generate first-person diary entry from conversation"""
        if not self.conversation_data:
            return "No conversation to summarize today."
            
        if not self.check_api_limit():
            return "Cannot generate diary due to API limit."
        
        try:
            # Prepare conversation text
            conversation_text = ""
            for item in self.conversation_data:
                speaker = "I said" if item["speaker"] == "user" else "The AI asked"
                conversation_text += f"{speaker}: {item['message']}\\n"
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """Create a personal diary entry in first-person narrative style from this conversation. 
                        
                        Requirements:
                        - Write as if the user is personally writing their diary
                        - Include emotional highlights and key events
                        - Use 'I' statements throughout
                        - Keep it natural and reflective
                        - Write as one cohesive paragraph
                        - Capture the essence of their day and feelings"""
                    },
                    {
                        "role": "user",
                        "content": f"Create a diary entry from this conversation:\\n\\n{conversation_text}"
                    }
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            self.api_usage_count += 1
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Diary Generation Error: {str(e)}")
            return "Could not generate diary entry due to an error."
    
    def save_conversation(self, diary_entry):
        """Save conversation and diary to JSON file"""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = f"voice_diary_{today}.json"
        
        # Calculate overall emotion analysis
        emotions = [item.get("emotion") for item in self.conversation_data if item.get("emotion")]
        dominant_emotion = "neutral"
        avg_intensity = 0.5
        
        if emotions:
            emotion_counts = {}
            total_intensity = 0
            for emotion in emotions:
                if emotion:
                    emotion_counts[emotion["dominant"]] = emotion_counts.get(emotion["dominant"], 0) + 1
                    total_intensity += emotion["intensity"]
            
            if emotion_counts:
                dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]
                avg_intensity = total_intensity / len(emotions)
        
        data = {
            "date": today,
            "conversation": self.conversation_data,
            "summary": diary_entry,
            "emotion_analysis": {
                "dominant": dominant_emotion,
                "intensity": round(avg_intensity, 2)
            },
            "api_usage": self.api_usage_count
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\\n*** Conversation saved to {filename} ***")
    
    def start_conversation(self):
        """Main conversation loop"""
        print("\\n*** Starting Voice Diary Session ***")
        self.speak_text("Hi! I'm here to help you reflect on your day. How are you feeling right now?")
        
        while True:
            try:
                # Check for quit command
                if keyboard.is_pressed('q'):
                    print("\\n*** Ending conversation... ***")
                    break
                
                # Record user input
                audio_data = self.record_audio()
                if not audio_data:
                    continue
                
                # Transcribe audio
                user_text = self.transcribe_audio(audio_data)
                if not user_text:
                    continue
                
                print(f"You: {user_text}")
                
                # Get AI response
                ai_response, emotion = self.get_ai_response(user_text, self.conversation_data)
                if not ai_response:
                    break
                
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
                
                print(f"AI: {ai_response}")
                
                # Speak AI response
                self.speak_text(ai_response)
                
                time.sleep(0.1)  # Brief pause
                
            except KeyboardInterrupt:
                print("\\n*** Session interrupted ***")
                return None
        
        return True
    
    def run(self):
        """Main application loop"""
        try:
            conversation_completed = self.start_conversation()
            
            if conversation_completed and self.conversation_data:
                print("\\n*** Generating your diary entry... ***")
                diary_entry = self.generate_diary_entry()
                
                print("\\n" + "="*50)
                print("*** YOUR VOICE DIARY ENTRY ***")
                print("="*50)
                print(f"Date: {datetime.datetime.now().strftime('%B %d, %Y')}")
                print()
                print(diary_entry)
                print("="*50)
                
                self.save_conversation(diary_entry)
                print(f"*** API Usage: {self.api_usage_count} calls ***")
                
            else:
                print("No diary entry created.")
                
        except Exception as e:
            print(f"Application Error: {str(e)}")
        
        finally:
            self.audio.terminate()

if __name__ == "__main__":
    try:
        diary = VoiceDiary()
        diary.run()
    except KeyboardInterrupt:
        print("\\n*** Voice Diary App Closed ***")