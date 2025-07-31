import os
import json
import datetime
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class AIDiary:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.data_file = 'diary_entries.json'
        self.conversation_history = []
        
        # Diary conversation questions
        self.questions = [
            "Hi! How are you feeling today?",
            "What was the most memorable moment of your day?",
            "Is there anything that made you particularly happy or sad today?",
            "What thoughts have been on your mind lately?",
            "How did you spend most of your time today?",
            "Was there anything challenging you faced today?",
            "What are you grateful for today?",
            "Is there anything you're looking forward to?",
            "How would you describe your energy level today?",
            "What would you like to remember about today?"
        ]
        
    def load_diary_data(self):
        if Path(self.data_file).exists():
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_diary_entry(self, entry):
        diary_data = self.load_diary_data()
        diary_data.append(entry)
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(diary_data, f, ensure_ascii=False, indent=2)
    
    def get_ai_response(self, user_input, question):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a compassionate diary companion. Ask thoughtful follow-up questions to help the user reflect on their day and express their feelings. Keep responses warm, supportive, and conversational. Ask only one follow-up question at a time."
                    },
                    {
                        "role": "assistant", 
                        "content": question
                    },
                    {
                        "role": "user", 
                        "content": user_input
                    }
                ],
                max_tokens=150,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Sorry, I'm having trouble connecting right now. Error: {str(e)}"
    
    def create_diary_summary(self, conversation_text):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """Create a personal diary entry summary in first-person narrative style. Include:
                        1. Emotional highlights (how I felt)
                        2. Key events (what happened)
                        3. Write as if the user is personally writing their diary entry
                        4. Keep it natural and reflective
                        5. Use 'I' statements throughout
                        
                        Format as a cohesive diary entry paragraph, not bullet points."""
                    },
                    {
                        "role": "user",
                        "content": f"Please summarize this conversation into a personal diary entry:\n\n{conversation_text}"
                    }
                ],
                max_tokens=300,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Could not create summary. Error: {str(e)}"
    
    def start_conversation(self):
        print("*** Welcome to your AI Diary! ***")
        print("I'm here to help you reflect on your day.")
        print("Type 'quit' anytime to finish and save your diary entry.\n")
        
        conversation_text = ""
        question_index = 0
        
        # Start with first question
        current_question = self.questions[question_index]
        print(f"AI: {current_question}")
        
        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'done']:
                break
            
            if not user_input:
                print("AI: I'm listening... please share your thoughts.")
                continue
            
            # Add to conversation history
            conversation_text += f"Q: {current_question}\nA: {user_input}\n\n"
            
            # Get AI response (follow-up or next question)
            if question_index < len(self.questions) - 1:
                # Sometimes ask follow-up, sometimes move to next question
                ai_response = self.get_ai_response(user_input, current_question)
                print(f"\nAI: {ai_response}")
                
                # Move to next question after follow-up
                question_index += 1
                if question_index < len(self.questions):
                    current_question = self.questions[question_index]
                    print(f"\nAI: {current_question}")
            else:
                # Final response
                ai_response = self.get_ai_response(user_input, current_question)
                print(f"\nAI: {ai_response}")
                print("\nAI: Thank you for sharing with me today. Let me create your diary entry...")
                break
        
        return conversation_text
    
    def run(self):
        conversation_text = self.start_conversation()
        
        if conversation_text:
            print("\n*** Creating your diary entry...")
            
            # Create summary
            diary_summary = self.create_diary_summary(conversation_text)
            
            # Create diary entry
            entry = {
                "date": datetime.datetime.now().isoformat(),
                "conversation": conversation_text,
                "diary_entry": diary_summary
            }
            
            # Save entry
            self.save_diary_entry(entry)
            
            print("\n" + "="*50)
            print("*** YOUR DIARY ENTRY ***")
            print("="*50)
            print(f"Date: {datetime.datetime.now().strftime('%B %d, %Y')}")
            print()
            print(diary_summary)
            print("="*50)
            print("*** Diary entry saved successfully! ***")
        else:
            print("No diary entry created. Come back anytime!")

if __name__ == "__main__":
    diary = AIDiary()
    diary.run()