import os
import sys

import openai
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader, TextLoader, UnstructuredHTMLLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma

import constants

os.environ["OPENAI_API_KEY"] = constants.APIKEY

# Enable to save to disk & reuse the model (for repeated queries on the same data)
PERSIST = False

# query = "I have provided you with a lot of information about my code. Tell me what you think about it."
# query = "Give me some details about the code I have provided"
query = '''
I need details about the css class from the text I have provided. Here is the json config for the css class
<>
{
  "type": "detail",
  "extract": {
    "name": [
      {
        "select": {
          "query": ".fed-pdp-product-details-title h1",
          "mode": "FIRST"
        },
        "method": {
          "text": {}
        }
      }
    ],
    "price": [
      {
        "select": {
          "query": ".normalPrice",
          "mode": "FIRST"
        },
        "method": {
          "text": {}
        },
        "parsers": [
          {
            "spel": {
              "expr": "#root.replace(',' , '')"
            }
          }
        ]
      }
    ],
    "netQuantity": [
      {
        "select": {
          "query": ".fed-pdp-product-details-title h1",
          "mode": "FIRST"
        },
        "method": {
          "text": {}
        },
        "parsers": [
          {
            "patternSpel": {
              "regex": "(?i)((?<net>\\d+([,.]\\d+)?) ?(?<unit>(kg|gm|g|cl|ml|ltr|litre|L|l|uds|Pack|pcs|Pieces|oz|Sachets|s|Capsules|ea)) ?x? ?(?<quantity>\\d*) ?(\\+ (?<free>\\d+) Free)?|((?<quantity1>\\d*) ?x ?(?<net1>\\d+([,.]\\d+)?) ?(?<unit1>(kg|gm|g|cl|ml|ltr|litre|L|l|uds|Pack|pcs|Pieces|oz|Sachets|s|Capsules|ea))))",
              "expr": "(#net1 != null && #net1 != '') ? #net1+ #unit1+ ' x ' + #quantity1 : (#quantity != null && #quantity !='') ? ((#free != null && #free != '') ? #net+ #unit+ ' x ' + (T(java.lang.Integer).parseInt(#quantity) + T(java.lang.Integer).parseInt(#free)) : #net+ #unit+ ' x ' + #quantity) : (#net != null && #net != '' && #unit!= null && #unit!='') ? #net + ' ' + #unit: ''"
            }
          }
        ]
      }
    ],
    "productNo": [
      {
        "select": {
          "query": "div[data-productid]",
          "mode": "FIRST"
        },
        "method": {
          "attr": {
            "key": "data-productid"
          }
        }
      }
    ],
    "gtin": [
      {
        "select": {
          "query": ".product-classifications .row:has(div:containsOwn(Barcode))",
          "mode": "FIRST"
        },
        "method": {
          "text": {
            "own": true
          }
        },
        "parsers": [
          {
            "pattern": {
              "regex": "\\d{13}"
            }
          }
        ]
      }
    ],
    "promotionText": [
      {
        "select": {
          "query": ".fed-pdp-product-details-price-promo .promotion",
          "mode": "SPLIT"
        },
        "method": {
          "text": {}
        }
      },
      {
        "select": {
          "query": ".oldPrice",
          "mode": "SPLIT"
        },
        "method": {
          "text": {}
        },
        "parsers": [
          {
            "spel": {
              "expr": "'Was ' + #root.replace(',', '')"
            }
          }
        ]
      }
    ],
    "description": [
      {
        "select": {
          "query": ".product-classifications .row:has(div:containsOwn(Description))",
          "mode": "FIRST"
        },
        "method": {
          "text": {
            "own": true
          }
        }
      }
    ],
    "ingredients": [
      {
        "select": {
          "query": ".product-classifications .row:has(div:containsOwn(Ingredients))",
          "mode": "FIRST"
        },
        "method": {
          "text": {
            "own": true
          }
        }
      }
    ],
    "ingredientsHtml": [
      {
        "select": {
          "query": ".product-classifications .row:has(div:containsOwn(Ingredients))",
          "mode": "FIRST"
        },
        "method": {
          "html": {}
        }
      }
    ],
    "nutrition": [
      {
        "select": {
          "query": ".nutritional-info",
          "mode": "FIRST"
        },
        "method": {
          "text": {}
        }
      }
    ],
    "allergens": [
      {
        "select": {
          "query": ".product-classifications .row:has(div:containsOwn(Allergen Warnings))",
          "mode": "FIRST"
        },
        "method": {
          "text": {
            "own": true
          }
        }
      }
    ],
    "storage": [
      {
        "select": {
          "query": ".product-classifications .row:has(div:containsOwn(Storage))",
          "mode": "FIRST"
        },
        "method": {
          "text": {
            "own": true
          }
        }
      }
    ],
    "features": [
      {
        "select": {
          "query": "div.product-classifications div.row:contains(Features) li",
          "mode": "SPLIT"
        },
        "method": {
          "text": {}
        }
      }
    ],
    "imageURL": [
      {
        "select": {
          "query": ".gallery-image img",
          "mode": "SPLIT"
        },
        "method": {
          "attr": {
            "key": "abs:data-src"
          }
        }
      }
    ],
    "instructions": [
      {
        "select": {
          "query": ".product-classifications .row:has(div:containsOwn(Usage)), .product-classifications .row:has(div:containsOwn(Serving Suggestions))",
          "mode": "SPLIT"
        },
        "method": {
          "text": {
            "own": true
          }
        },
        "join": {
          "separator": " "
        }
      }
    ],
    "outOfStock": [
      {
        "select": {
          "query": ".upfrontOutOfStockMsg",
          "mode": "FIRST"
        },
        "method": {
          "text": {}
        }
      }
    ],
    "badge": [
      {
        "select": {
          "query": ".maximumQtyDisplayMsgContainer b",
          "mode": "FIRST"
        },
        "method": {
          "text": {
            "own": true
          }
        }
      }
    ],
    "brand": [
      {
        "select": {
          "query": ".ef-custom-brand",
          "mode": "FIRST"
        },
        "method": {
          "text": {}
        }
      }
    ],
    "bulletPoints": [
      {
        "select": {
          "query": "div.product-classifications div.row:contains(Features) li, div.product-classifications div.row:contains(Lifestyle) li",
          "mode": "SPLIT"
        },
        "method": {
          "text": {}
        }
      }
    ]
  },
  "feedback": {
    "avgRating": [
      {
        "select": {
          "query": ".fed-pdp-product-details .rating[data-rating]",
          "mode": "FIRST"
        },
        "method": {
          "attr": {
            "key": "data-rating"
          }
        },
        "parsers": [
          {
            "pattern": {
              "regex": "\"rating\":\"(?<rating>(\\d+[.]\\d{1,2})|())",
              "group": "rating"
            }
          }
        ]
      }
    ],
    "commentCount": [
      {
        "select": {
          "query": "div.rating .js-openTab",
          "mode": "FIRST"
        },
        "method": {
          "text": {}
        },
        "parsers": [
          {
            "pattern": {
              "regex": "\\d+"
            }
          }
        ]
      }
    ],
    "comments": {
      "split": ".review-list .review-entry",
      "dateLabel": [
        {
          "select": {
            "query": ".autor .date",
            "mode": "FIRST"
          },
          "method": {
            "text": {
              "own": true
            }
          },
          "parsers": [
            {
              "pattern": {
                "regex": "\\((?<dateLabel>\\d{1,2}\/\\d{1,2}\/\\d{4})\\)",
                "group": "dateLabel"
              }
            }
          ]
        }
      ],
      "dateParser": {
        "formatted": {
          "format": "dd/MM/yyyy"
        }
      },
      "rating": [
        {
          "select": {
            "query": ".rating-stars .glyphicon-star",
            "mode": "SPLIT"
          },
          "method": {
            "attr": {
              "key": "class"
            }
          },
          "join": {
            "separator": " "
          },
          "parsers": [
            {
              "spel": {
                "expr": "T(org.apache.commons.lang3.StringUtils).countMatches(#root, 'active')"
              }
            }
          ]
        }
      ],
      "username": [
        {
          "select": {
            "query": ".autor",
            "mode": "FIRST"
          },
          "method": {
            "text": {
              "own": true
            }
          }
        }
      ],
      "content": [
        {
          "select": {
            "query": "div.content",
            "mode": "SPLIT"
          },
          "method": {
            "text": {}
          }
        }
      ],
      "subject":[
        {
          "select": {
            "query": "div.title",
            "mode": "FIRST"
          },
          "method": {
            "text": {}
          }
        }
      ]
    }
  },
  "extractor": {
    "direct": {}
  }
}
<>
Between <><> is the json config for the html code I have provided. I need the text from the html code. The css class "fed-pdp-product-details-title" 
is used to select the title of the product in the HTML code. What is the title of the product?
'''
# find the fed-pdp-product-details-title from the text not the json config.
if len(sys.argv) > 1:
  query = sys.argv[1]

if PERSIST and os.path.exists("persist"):
  print("Reusing index...\n")
  vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
  index = VectorStoreIndexWrapper(vectorstore=vectorstore)
else:
  # loader = TextLoader("data/data.txt") # Use this line if you only need data.txt
  # loader = DirectoryLoader("PNP-ZA/")
  # loader = UnstructuredHTMLLoader("data/website.html")
  loader = TextLoader("data/website2.txt")
  if PERSIST:
    # index = VectorstoreIndexCreator().from_documents([loader])
    index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory":"persist"}).from_loaders([loader])
  else:
    index = VectorstoreIndexCreator().from_loaders([loader])

chain = ConversationalRetrievalChain.from_llm(
  llm=ChatOpenAI(model="gpt-3.5-turbo"),
  retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
)

chat_history = []
while True:
  if not query:
    query = input("Prompt: ")
  if query in ['quit', 'q', 'exit']:
    sys.exit()
  result = chain({"question": query, "chat_history": chat_history})
  print(result['answer'])

  chat_history.append((query, result['answer']))
  query = None
