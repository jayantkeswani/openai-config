import json
import time
import requests
from langchain.document_loaders import TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from prompts.default import system_prompt
from langchain.text_splitter import (RecursiveCharacterTextSplitter, Language)
from common import save_prompt

MAX_RETRIES = 10

class ScrapperAI:
    def __init__(self, html_path) -> None:
        self.html_path = html_path
        self.raw_documents = TextLoader(self.html_path).load()
        self.html_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.HTML, chunk_size=500, chunk_overlap=0
        )
        self.html_docs = self.html_splitter.create_documents([self.raw_documents[0].page_content])
        for document in self.html_docs:
            if len(document.metadata) < 1:
                document.metadata["source"] = "data/data.html"
        self.vector_store = Chroma.from_documents(self.html_docs, OpenAIEmbeddings())

    def get_response_from_vectorstore(self, question, k=5, max_length=None):
        if max_length:
            search_result = self.vector_store._similarity_search_with_relevance_scores(question, k=k, max_length=max_length)
        else:
            search_result = self.vector_store._similarity_search_with_relevance_scores(question, k=k)
        search_result_string = ""
        for result in search_result:
            search_result_string += result[0].page_content + " "
        return search_result_string

    def chat_completion(self, prompt, model="gpt-4", temperature=0):
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

def process_field(field, prompts, vectorstore_prompts, scrapper_ai):
    retries = 0
    while retries < MAX_RETRIES:
        try:
            vectorestore_result = scrapper_ai.get_response_from_vectorstore(vectorstore_prompts[field], k=8)
            prompt = f'{vectorestore_result} {prompts[field]}'
            save_prompt(prompt, field)
            response = scrapper_ai.chat_completion(prompt, max_response=1)
            if not response.get("error"):
                content = json.loads(response["choices"][0]["message"]["content"])
                print(content)
                return content
            else:
                if "Rate limit reached" in response["error"]["message"]:
                    retries += 1
                    time.sleep(1)
                elif "maximum context length" in response["error"]["message"]:
                    vectorestore_result = scrapper_ai.get_response_from_vectorstore(vectorstore_prompts[field], k=2, max_length=100)
                    prompt = f'{vectorestore_result} {prompts[field]}'
                    response = scrapper_ai.chat_completion(prompt, max_response=1)
                    content = json.loads(response["choices"][0]["message"]["content"])
                    print(content)
                    return content
                else:
                    print(f'{field}: {response["error"]["message"]}')
                    break
        except Exception as e:
            print(f'{field}: {e}')
            break


if __name__ == "__main__":
    url = "https://www.pnp.co.za/pnpstorefront/pnp/en/All-Products/Beverages/Water/Flavoured-Water/Bonaqua-Pump-Still-Lemon-Flavoured-Drink-750ml-x-6/p/000000000000783004_CK"
    html_content = requests.get(url).text

    with open('data/data_URL.txt', 'w') as file:
        file.write(html_content)

    with open('prompts/prompts.json') as prompts_file:
        prompts = json.load(prompts_file)

    with open('prompts/vectorstore_prompts.json') as vectorstore_prompts_file:
        vectorstore_prompts = json.load(vectorstore_prompts_file)

    scrapper_ai = ScrapperAI("data/data_URL.txt")
    results = []
    tasks = []
    for field in prompts:
        task = process_field(field, prompts, vectorstore_prompts, scrapper_ai)
        results.append(task)

    with open('data/results.json', 'w') as results_file:
        json.dump(results, results_file, indent=4)
