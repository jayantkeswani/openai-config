import json
import tiktoken

def count_tokens(text: str) -> int:
    encoding = tiktoken.encoding_for_model("gpt-4")
    tokens = encoding.encode(text)
    return len(tokens)

def save_prompt(prompt, field):    
    with open('data/sent_prompts.json', 'r') as prompts_file:
        sent_prompts = json.load(prompts_file)
    sent_prompts[field] = prompt

    with open('data/sent_prompts.json', 'w') as prompts_file:
        json.dump(sent_prompts, prompts_file, indent=4)
