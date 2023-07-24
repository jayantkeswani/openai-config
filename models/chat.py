import json
import time
from multiprocessing import Pool
import requests
import httpx
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from prompts.default import get_vector_store_prompt_old, system_prompt
from custom_encodings.helper import count_tokens
from validation import process_html_with_selectors
from bs4 import BeautifulSoup
from itertools import permutations
MAX_RETRIES = 10

class ScrapperAI:
    def __init__(self, html_path) -> None:
        self.html_path = html_path
        self.raw_documents = TextLoader(self.html_path).load()
        self.text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=50, length_function=count_tokens)
        self.documents = self.text_splitter.split_documents(self.raw_documents)
        self.vector_store = Chroma.from_documents(self.documents, OpenAIEmbeddings())

    def get_response_from_vectorstore(self, question, k=5, max_length=None):
        if max_length:
            search_result = self.vector_store.similarity_search_with_score(question, k=k, max_length=max_length)
        else:
            search_result = self.vector_store.similarity_search_with_score(question, k=k)
        search_result_string = ""
        for result in search_result:
            search_result_string += result[0].page_content + " "
        return search_result_string

    async def chat_completion(self, prompt, model="gpt-4", max_response=1, temperature=0):
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
            "n": max_response,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=json.dumps(data))
            response_data = response.json()

        return response_data
    
    def validate(self, results):
        with open(self.html_path, 'r') as file:
            html_content = file.read()
        for result in results:
            response = self.get_values_from_html(html_content, result["cssSelectors"])
            result["possibleValues"] = response
        return results

    def get_values_from_html(self, html_content, css_selectors):
        soup = BeautifulSoup(html_content, 'html.parser')
        result = []
        indices = list(range(len(css_selectors)))
        index_permutations = []
        for r in range(1, len(indices) + 1):
            index_permutations.extend(permutations(indices, r))

        for permutation in index_permutations:
            selectors = [css_selectors[i] for i in permutation]
            selector = ' '.join(selectors)

            # Handle cleaning up selectors with "+"
            cleaned_selector = selector.replace(' + ', '+')

            # Handle empty spaces, quotes, and other characters at the beginning or end of selectors
            fixed_selectors = []
            for sel in cleaned_selector.split():
                if sel:
                    sel = sel.strip(' "\'<>')  # Strip out empty spaces, quotes, <, > at the beginning or end
                    if not sel.startswith(('.', '#')):
                        sel = '.' + sel  # Add dot (.) if missing
                    fixed_selectors.append(sel)

            fixed_selector = ' '.join(fixed_selectors)

            if fixed_selector:
                try:
                    elements = soup.select(fixed_selector)
                    for element in elements:
                        text = element.get_text(strip=True)
                        if text and text not in result:
                            result.append(text)
                except (ValueError, AttributeError, TypeError) as e:
                    print(f"Error occurred for selector '{fixed_selector}': {e}")
        return result


with open('prompts/prompts.json') as prompts:
    prompts = json.load(prompts)

with open('prompts/vectorstore_prompts.json') as vectorstore_prompts:
    vectorstore_prompts = json.load(vectorstore_prompts)

scrapper_ai = ScrapperAI("data/data.txt")
MAX_RETRIES = 10
results = []

for field in prompts:
    retries = 0
    while retries < MAX_RETRIES:
        try:
            vectorestore_result = scrapper_ai.get_response_from_vectorstore(vectorstore_prompts[field])
            prompt = f'<> {vectorestore_result} <> {get_vector_store_prompt_old(prompts[field])}'
            response = scrapper_ai.chat_completion(prompt, max_response=2)
            if not response.get("error"):
                print(f'{field}: {[choice["message"]["content"] for choice in response["choices"]]}')
                results.append({"field": field, "cssSelectors": [choice["message"]["content"] for choice in response["choices"]]})
                break
            else:
                if "Rate limit reached" in response["error"]["message"]:
                    retries += 1
                    time.sleep(1)
                elif "maximum context length" in response["error"]["message"]:
                    vectorestore_result = scrapper_ai.get_response_from_vectorstore(vectorstore_prompts[field], k=2, max_length=100)
                    prompt = f'<> {vectorestore_result} <> {get_vector_store_prompt_old(prompts[field])}'
                    response = scrapper_ai.chat_completion(prompt, max_response=2)
                    print(f'{field}: {[choice["message"]["content"] for choice in response["choices"]]}')
                    results.append({"field": field, "cssSelectors": [choice["message"]["content"] for choice in response["choices"]]})
                    break
                else:
                    print(f'{field}: {response["error"]["message"]}')
                    break
        except Exception as e:
            print(f'{field}: {e}')
            break

scrapper_ai.validate(results)
with open('prompts/results.json', 'w') as results_file:
    json.dump(results, results_file, indent=4)
