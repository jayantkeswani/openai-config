import os
import sys
import json
from langchain.chains import ConversationalRetrievalChain, RetrievalQAWithSourcesChain, RetrievalQA
from langchain.text_splitter import CharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.memory import ConversationBufferMemory
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma
from langchain.schema import SystemMessage, HumanMessage
from langchain.vectorstores import FAISS
import logging
from prompts.default import vector_store_prompt
from time import sleep

logging.getLogger("openai").setLevel(logging.DEBUG)
os.environ['OPENAI_API_KEY'] = "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"

if len(sys.argv) > 1:
  query = sys.argv[1]

messages = []
with open('prompts/prompts.json') as prompts:
    prompts = json.load(prompts)

raw_documents = TextLoader('data/data.txt').load()
text_splitter = CharacterTextSplitter(chunk_size=400, chunk_overlap=0)
documents = text_splitter.split_documents(raw_documents)

embeddings = OpenAIEmbeddings()
vector_store = FAISS.from_documents(documents, embeddings)

# for field in prompts:
#   search_result = vector_store.similarity_search_with_score("What is the CSS selector for the ingredients in the HTML?", k=3)
#   print(search_result)

# system_template={"role": "assistant", "content": "You are an assistant that has all the knowledge about CSS selectors and web scraping."}
# messages.append(system_template)

# system_template={"role": "assistant", "content": "You are an assistant that has all the knowledge about CSS selectors and web scraping."}
# messages.append(system_template)

# chain = ConversationalRetrievalChain.from_llm(
#             llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo"), 
#             retriever=vector_store.as_retriever(),
#             )

# chain = ConversationalRetrievalChain.from_llm(
#             llm=OpenAI(temperature=0, model="gpt-4"), 
#             chain_type="stuff",
#             retriever=vector_store.as_retriever(),
#             model_kwargs={"memory":ConversationBufferMemory()}
#             )

for field in prompts:
  retriever = vector_store.as_retriever(search_kwargs={"k": 4}, search_type='mmr')
  chain = RetrievalQA.from_chain_type(llm=ChatOpenAI(temperature=0, model="gpt-4"),
                                    chain_type="map_reduce",
                                    retriever=retriever,
                                    return_source_documents=True,
                                    verbose=False)
  # prompt = f'<>{vector_store.similarity_search(prompts[field], k=2)}<> {get_vector_store_prompt(prompts[field])}'
  prompt = prompts[field] + vector_store_prompt
  # result = chain({"question": prompt, "chat_history": messages})
  result = chain({"query": prompt})
  error_list = ["does not contain any information", "not explicitly provided in the given context.", "not"]
  for error in error_list:
     if error in result['result']:
      print("recheking")
      retriever = vector_store.as_retriever(search_kwargs={"k": 5}, search_type='similarity')
      chain = RetrievalQA.from_chain_type(llm=ChatOpenAI(temperature=0, model="gpt-4"),
                                    chain_type="stuff",
                                    retriever=retriever,
                                    return_source_documents=True,
                                    verbose=False)
      # prompt = f'<>{vector_store.similarity_search(prompts[field], k=2)}<> {get_vector_store_prompt(prompts[field])}'
      prompt = prompts[field] + vector_store_prompt
      # result = chain({"question": prompt, "chat_history": messages})
      result = chain({"query": prompt})

  messages.append((prompt, result['result']))
  print(result['result'])

while True:
  query = None
  if not query:
    query = input("Prompt: ")
  if prompt in ['quit', 'q', 'exit']:
    sys.exit()

  prompt = HumanMessage(f' {vector_store.similarity_search(query)} {vector_store_prompt(query)}')
  # result = chain({"question": prompt, "chat_history": messages})
  messages.append((prompt, result['result']))
  retriever = vector_store.as_retriever(search_kwargs={"k": 5})
  chain = RetrievalQA.from_chain_type(llm=ChatOpenAI(temperature=0, model="gpt-4"),
                                    chain_type="stuff",
                                    retriever=retriever,
                                    return_source_documents=True,
                                    verbose=False)
  result = chain(prompt)
  print(result['result'])
  query = None