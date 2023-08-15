import requests
import os
import time
import json
from time import time
from datetime import datetime
from uuid import uuid4
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, Range, MatchValue
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import re
        
        
def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()
  
        
def timestamp_to_datetime(unix_time):
    datetime_obj = datetime.fromtimestamp(unix_time)
    datetime_str = datetime_obj.strftime("%A, %B %d, %Y at %I:%M%p %Z")
    return datetime_str


# Connect to Oobabooga Api
# For local streaming, the websockets are hosted without ssl - http://
HOST = 'localhost:5000'
URI = f'http://{HOST}/api/v1/chat'

# For reverse-proxied streaming, the remote will likely host with ssl - https://
# URI = 'https://your-uri-here.trycloudflare.com/api/v1/generate'

model = SentenceTransformer('all-mpnet-base-v2')


def check_local_server_running():
    try:
        response = requests.get("http://localhost:6333/dashboard/")
        return response.status_code == 200
    except requests.ConnectionError:
        return False


# Check if local server is running
if check_local_server_running():
    client = QdrantClient(url="http://localhost:6333")
    print("Connected to local Qdrant server.")
else:
    url = open_file('./qdrant_url.txt')
    api_key = open_file('./qdrant_api_key.txt')
    try:
        client = QdrantClient(url=url, api_key=api_key)
        print("Connected to cloud Qdrant server.")
    except Exception as e:
        print(f"Failed to Connect to Qdrant Server: {e}")
    


def oobabooga(instruction, prompt):
    history = {'internal': [], 'visible': []}
    request = {
        'user_input': prompt,
        'max_new_tokens': 800,
        'history': history,
        'mode': 'instruct',  # Valid options: 'chat', 'chat-instruct', 'instruct'
        'instruction_template': 'Llama-v2',  # Will get autodetected if unset
        'context_instruct': f"{instruction}",  # Optional
        'your_name': f'USER',
        'regenerate': False,
        '_continue': False,
        'stop_at_newline': False,
        'chat_generation_attempts': 1,
        # Generation params. If 'preset' is set to different than 'None', the values
        # in presets/preset-name.yaml are used instead of the individual numbers.
        'preset': 'None',  
        'do_sample': True,
        'temperature': 0.85,
        'top_p': 0.55,
        'typical_p': 1,
        'epsilon_cutoff': 0,  # In units of 1e-4
        'eta_cutoff': 0,  # In units of 1e-4
        'tfs': 1,
        'top_a': 0,
        'repetition_penalty': 1.18,
        'top_k': 35,
        'min_length': 100,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'mirostat_mode': 0,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,

        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 4096,
        'ban_eos_token': False,
        'skip_special_tokens': True,
        'stopping_strings': []
    }

    response = requests.post(URI, json=request)

    if response.status_code == 200:
        result = response.json()['results'][0]['history']
    #    print(json.dumps(result, indent=4))
        print()
    #    print(result['visible'][-1][1])
        return result['visible'][-1][1]
        
        
def Qdrant_Upload(bot_name, query):
    bot_name = 'ASSISTANT'
    while True:
        try:
            payload = list()       
            timestamp = time()
            timestring = timestamp_to_datetime(timestamp)
            # Define the collection name, make sure to change search query collection name too.
            collection_name = f"ENTER COLLECTION NAME HERE"
            try:
                collection_info = client.get_collection(collection_name=collection_name)
            except:
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE),
                )
            embedding = model.encode([query])[0].tolist()
            unique_id = str(uuid4())
            metadata = {
                'bot': bot_name,
                'time': timestamp,
                'message': query,
                'timestring': timestring,
                'uuid': unique_id,
                'memory_type': 'Long_Term_Memory'
            }
            client.upsert(collection_name=collection_name,
                                 points=[PointStruct(id=unique_id, payload=metadata, vector=embedding)])
            return
        except Exception as e:
            print(f"ERROR: {e}")
            return
            
            
def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()
        
    
# Custom Conversation History List, this was done so the api can be swapped without major code rewrites.
class MainConversation:
    def __init__(self, max_entries, main_prompt, greeting_prompt):
        try:
            # Set Maximum conversation Length
            self.max_entries = max_entries
            # Set path for Conversation History
            self.file_path = f'./main_conversation_history.json'
            # Set Main Conversatoin with Main and Greeting Prompt
            self.main_conversation = [main_prompt, greeting_prompt]
            # Load existing conversation from file or set to empty.
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.running_conversation = data.get('running_conversation', [])
            else:
                self.running_conversation = []
        except Exception as e:
            print(e)

    def append(self, usernameupper, user_input, botnameupper, output):
        # Append new entry to the running conversation
        entry = []
        entry.append(f"[INST] {usernameupper}: {user_input} [/INST]")
        entry.append(f"{botnameupper}: {output}")
        self.running_conversation.append("\n\n".join(entry))  # Join the entry with "\n\n"
        # Remove oldest entry if conversation length exceeds max entries
        while len(self.running_conversation) > self.max_entries:
            self.running_conversation.pop(0)
        self.save_to_file()

    def save_to_file(self):
        # Combine main conversation and formatted running conversation for saving to file
        data_to_save = {
            'main_conversation': self.main_conversation,
            'running_conversation': self.running_conversation
        }
        
        # Save the joined list to a json file
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=4)

    # Create function to call conversation history
    def get_conversation_history(self):
        if not os.path.exists(self.file_path):
            self.save_to_file()
        # Join Main Conversation and Running Conversation
        return self.main_conversation + ["\n\n".join(entry.split(" ")) for entry in self.running_conversation]
                  

if __name__ == '__main__':
    conversation = list()
    summary = list()
    bot_name = open_file('./Prompts/bot_name.txt')
    user_name = open_file('./Prompts/bot_name.txt')
    botnameupper = bot_name.upper()
    usernameupper = user_name.upper()
    main_prompt = open_file(f'./Prompts/prompt_main.txt').replace('<<NAME>>', bot_name)
    greeting_prompt = open_file(f'./Prompts/prompt_greeting.txt').replace('<<NAME>>', bot_name)
    collection_name = f"ENTER COLLECTION NAME HERE"
    # Define Maximum Conversation List
    max_entries = 7
    # Define the main conversation class and pass through the needed variables
    main_conversation = MainConversation(max_entries, main_prompt, greeting_prompt)
    while True:
        try:
            conversation_history = main_conversation.get_conversation_history()
            instruction = "[INST] <<SYS>>\nYou are in the middle of a conversation with a user, generate a natural sounding response to their message.\n<</SYS>>"
            user_input = input(f'\n\nUSER: ')
            db_result = None
            try:
                vector = model.encode([user_input])[0].tolist()
                hits = client.search(
                    collection_name=collection_name,
                    query_vector=vector, 
                    query_filter=Filter(
                        must=[
                            FieldCondition(
                                key="memory_type",
                                match=MatchValue(value="Long_Term_Memory")
                            )
                        ]
                    ),
                    limit=12
                )
                results = [hit.payload['message'] for hit in hits]
                # Sort results by most recent time    
                sorted_results = sorted(hits, key=lambda hit: hit.payload['time'], reverse=False)

                # Extract the 'message' field for the top 10 results
                db_result = [entry.payload['message'] for entry in sorted_results[:10]]
                print(f"{db_result}\n\n")
            except Exception as e:
                if "Not found: Collection" in str(e):
                    print("Collection has no memories.")
                else:
                    print(f"An unexpected error occurred: {str(e)}")
        #    print(db_result)
            conversation.append({'content': f"{botnameupper}'S LONG TERM MEMORY: {db_result}[/INST]"})
            conversation.append({'content': f"CURRENT CONVERSATION HISTORY: {main_conversation}"})
            conversation.append({'content': f"[INST] USER INPUT: {user_input} [/INST]"})    
            conversation.append({'content': f"{botnameupper}: "})    
            prompt = ''.join([message_dict['content'] for message_dict in conversation])
            output = oobabooga(instruction, prompt)
            print(f"{botnameupper}: {output}")
            main_conversation.append(usernameupper, user_input, botnameupper, output)
            instruction = f"[INST] <<SYS>>\nExtract short and concise memories based on {bot_name}'s final response for upload to a memory database.  These should be executive summaries and will serve as {bot_name}'s memories.  Use the bullet point format: •<Executive Summary>\n<</SYS>>"
            summary.append({'content': f"LOG: {output}[/INST][INST]SYSTEM: Use the log to extract the salient points about the user and {bot_name}'s conversation. These points should be used to create concise executive summaries in bullet point format to serve as {bot_name}'s memories. Each bullet point should be considered a separate memory and contain full context.  Use the bullet point format: •<Executive Summary>[/INST]{botnameupper}: Sure! Here are some memories based on {bot_name}'s response:"})
            prompt = ''.join([message_dict['content'] for message_dict in summary])
            output_sum = oobabooga(instruction, prompt)
            print(output_sum)
            mem_check = input(f'\n\nUpload Memories? Y or N?: ')
            if 'y' in mem_check.lower():
                # Split on bullet point or double linebreak.
                segments = re.split(r'•|\n\s*\n', output_sum)
                for segment in segments:
                    if segment.strip() == '':
                        continue
                    else:
                        Qdrant_Upload(bot_name, segment)
                print('\nUpload Successful')
            else:
                pass
            conversation.clear()
            summary.clear()
        except Exception as e:
            print(e)