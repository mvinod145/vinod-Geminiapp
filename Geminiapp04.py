import streamlit as st
import google.generativeai as genai 
import sqlite3

# Database setup
conn = sqlite3.connect('chat_history.db')  
c = conn.cursor()

c.execute('''
          CREATE TABLE IF NOT EXISTS history  
          (role TEXT, message TEXT)  
          ''')
          
# Generative AI setup          
api_key = 'AIzaSyAeOEwAmWNZJ4ndYK02KSU-ooDP1KHuv-8'
genai.configure(api_key=api_key)  

generation_config = {
  "temperature": 0.3,
  "max_output_tokens": 500  
}

safety_settings = []

model = genai.GenerativeModel(
  model_name="gemini-pro",
  generation_config=generation_config,
  safety_settings=safety_settings
)

# Streamlit UI
st.title("Chatbot")   

chat_history = st.session_state.get("chat_history", [])

if len(chat_history) % 2 == 0:
  role = "user"
else:  
  role = "model"
  
for message in chat_history:
  r, t = message["role"], message["parts"][0]["text"]  
  st.markdown(f"**{r.title()}:** {t}")
  
user_input = st.text_input("")  

if user_input: 
  chat_history.append({"role": role, "parts": [{"text": user_input}]})
  
  if role == "user":
    response = model.generate_content(chat_history)  
    response_text = response.text
    chat_history.append({"role": "model", "parts": [{"text": response_text}]}) 
    
  st.session_state["chat_history"] = chat_history

  for message in chat_history:
    r, t = message["role"], message["parts"][0]["text"]
    st.markdown(f"**{r.title()}:** {t}")

if st.button("Display History"):
    c.execute("SELECT * FROM history")
    rows = c.fetchall()

    for row in rows:
        st.markdown(f"**{row[0].title()}:** {row[1]}")
        
# Save chat history to database
for message in chat_history:
    c.execute("INSERT INTO history VALUES (?, ?)", 
            (message["role"], message["parts"][0]["text"])) 
    conn.commit() 

conn.close()