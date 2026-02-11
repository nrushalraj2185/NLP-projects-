import requests
import os

BASE_URL = "http://localhost:8000"
RESUME_FILE = "Raju_Rastogi_Resume.docx"

def print_separator(title):
    print(f"\n{'='*20} {title} {'='*20}")

def test_general_advisor():
    print_separator("TEST 1: Career Advisor Mode (No Resume)")
    
    # 1. Start Session
    try:
        url = f"{BASE_URL}/chatbot/session/general"
        print(f"POST {url}")
        response = requests.post(url)
        
        if response.status_code != 200:
            print(f"❌ Failed to start session: {response.text}")
            return False
            
        data = response.json()
        session_id = data.get("session_id")
        welcome_msg = data.get("conversation_history")[0]["content"]
        suggestions = data.get("suggestions", [])
        
        print(f"✅ Session Started: {session_id}")
        print(f"👋 Welcome Message: {welcome_msg[:100]}...")
        print(f"💡 Suggestions: {suggestions}")
        
        if "Career Strategist" in welcome_msg or "ICA" in welcome_msg:
             print("✅ Persona Check: Valid (Career Strategist)")
        
        # 2. Send Message
        msg_payload = {
            "session_id": session_id,
            "message": "I love Python and building backend systems. What roles fit me?"
        }
        print(f"\n📤 Sending User Message: '{msg_payload['message']}'")
        chat_url = f"{BASE_URL}/chatbot/message"
        chat_response = requests.post(chat_url, json=msg_payload)
        
        if chat_response.status_code == 200:
            answer = chat_response.json().get("answer", "")
            print(f"🤖 Agent Response: {answer[:150]}...")
            if "Backend Developer" in answer or "Software Engineer" in answer or "Python" in answer:
                print("✅ Context Awareness: Success (Suggested relevant roles)")
            else:
                print("⚠️ Context Awareness: Response seemed generic, please check.")
        else:
            print(f"❌ Failed to chat: {chat_response.text}")

        return True
        
    except Exception as e:
        print(f"❌ Error in Test 1: {e}")
        return False

def test_resume_toolkit():
    print_separator("TEST 2: Resume Toolkit Mode (With Resume)")
    
    if not os.path.exists(RESUME_FILE):
        print(f"❌ Resume file {RESUME_FILE} not found. Skipping.")
        return False
        
    try:
        # 1. Start Session with Upload
        url = f"{BASE_URL}/chatbot/session"
        print(f"POST {url} with {RESUME_FILE}")
        
        with open(RESUME_FILE, "rb") as f:
            files = {"resume_file": f}
            response = requests.post(url, files=files)
            
        if response.status_code != 200:
            print(f"❌ Failed to upload resume: {response.text}")
            return False
            
        data = response.json()
        session_id = data.get("session_id")
        welcome_msg = data.get("conversation_history")[0]["content"]
        suggestions = data.get("suggestions", [])
        
        print(f"✅ Session Started: {session_id}")
        print(f"👋 Welcome Message: {welcome_msg[:100]}...")
        print(f"💡 Suggestions: {suggestions}")
        
        # Check specific Toolkit suggestions
        if "Perform Gap Analysis" in suggestions:
            print("✅ Suggestions Check: Contains Toolkit features")
            
        # 2. Send Message (Gap Analysis)
        msg_payload = {
            "session_id": session_id,
            "message": "Perform a gap analysis for a Senior Software Engineer role."
        }
        print(f"\n📤 Sending User Message: '{msg_payload['message']}'")
        chat_url = f"{BASE_URL}/chatbot/message"
        chat_response = requests.post(chat_url, json=msg_payload)
        
        if chat_response.status_code == 200:
            answer = chat_response.json().get("answer", "")
            print(f"🤖 Agent Response: {answer[:300]}...") # Print a bit more
            
            # Simple check for gap analysis keywords
            if "Gap" in answer or "Missing" in answer or "Improve" in answer:
                 print("✅ Toolkit Function: Gap Analysis executed")
            else:
                 print("⚠️ Toolkit Function: Response might not be gap analysis.")
        else:
             print(f"❌ Failed to chat: {chat_response.text}")
             
        return True

    except Exception as e:
        print(f"❌ Error in Test 2: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting ICA Agent verification...")
    if test_general_advisor():
        test_resume_toolkit()
    print("\n✅ Verification Complete.")
