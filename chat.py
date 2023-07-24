import json
import asyncio
import requests
from common import save_prompt
from vector_store import ScrapperVS
from prompts.default import system_prompt

MAX_RETRIES = 5

def chat_completion(prompt, model="gpt-4", temperature=0):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer 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"
    }
    messages = []
    messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "n": 1,
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    response_data = response.json()

    return response_data

async def process_field_async(field, prompts, vectorstore_prompts, vector_store):
    retries = 0
    while retries < MAX_RETRIES:
        try:
            vectorestore_result = vector_store.get_response_from_vectorstore(vectorstore_prompts[field], k=8)
            prompt = f'{vectorestore_result} {prompts[field]}'
            save_prompt(prompt, field)
            response = chat_completion(prompt)
            if not response.get("error"):
                content = json.loads(response["choices"][0]["message"]["content"])
                print(content)
                return content
            else:
                if "Rate limit reached" in response["error"]["message"]:
                    retries += 1
                    await asyncio.sleep(1)
                elif "maximum context length" in response["error"]["message"]:
                    vectorestore_result = vector_store.get_response_from_vectorstore(vectorstore_prompts[field], k=2, max_length=100)
                    prompt = f'{vectorestore_result} {prompts[field]}'
                    response = chat_completion(prompt)
                    content = json.loads(response["choices"][0]["message"]["content"])
                    print(content)
                    return content
                else:
                    print(f'{field}: {response["error"]["message"]}')
                    break
        except Exception as e:
            print(f'{field}: {e}')
            break


async def main():
    with open('prompts/prompts.json') as prompts_file:
        prompts = json.load(prompts_file)

    with open('prompts/vectorstore_prompts.json') as vectorstore_prompts_file:
        vectorstore_prompts = json.load(vectorstore_prompts_file)

    vector_store = ScrapperVS("data/data.txt")
    results = []
    tasks = [process_field_async(field, prompts, vectorstore_prompts, vector_store) for field in prompts]

    # Run the tasks concurrently
    results = await asyncio.gather(*tasks)

    with open('data/results.json', 'w') as results_file:
        json.dump(results, results_file, indent=4)

if __name__ == "__main__":
    asyncio.run(main())
