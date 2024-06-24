import google.generativeai as genai

Model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest") #choose model 
prompt = Model.start_chat(history=[ 
#Insert Your Prompt Here, 
# Example Prompt:
 # {
 #  "role": "user",
 # "parts": ["Hello"]
 #},
 # {
 #  "role": "model",
 #  "parts": ["Hello! How can I help you?"]
 # },

])