import textwrap

import nest_asyncio
from openai import OpenAIError
from pydantic import ValidationError

nest_asyncio.apply()

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.llms.openai import OpenAI

from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_iris import IRISVectorStore

import os
from .myconfig import *

os.environ["OPENAI_API_KEY"] = f'{OPENAI_API_KEY}'

username = f'{DB_USER}'
password = f'{DB_PASS}'
hostname = os.getenv('IRIS_HOSTNAME', f'{DB_URL}')
port = f'{DB_PORT}'
namespace = f'{DB_NAMESPACE}'

from llama_index.core import Settings

Settings.llm = OpenAI(temperature=0.2, model="gpt-3.5-turbo")

import ssl

certificateFile = "/usr/cert-demo/certificateSQLaaS.pem"

if (os.path.exists(certificateFile)):
    print("Located SSL certficate at '%s', initializing SSL configuration", certificateFile)
    sslcontext = ssl.create_default_context(cafile=certificateFile)
else:
    print("No certificate file found, continuing with insecure connection")
    sslcontext = None

from sqlalchemy import create_engine, text

url = f"iris://{username}:{password}@{hostname}:{port}/{namespace}"

engine = create_engine(url, connect_args={"sslcontext": sslcontext})
with engine.connect() as conn:
    print(conn.execute(text("SELECT 'hello world!'")).first()[0])

# StorageContext captures how vectors will be stored
vector_store = IRISVectorStore.from_params(
    connection_string = url,
    table_name = "user",
    embed_dim = 1536,  # openai embedding dimension
    engine_args = { "connect_args": {"sslcontext": sslcontext} }
)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
def get_filename_before_dot(filename):
    name, extension = os.path.splitext(filename)
    return name


def run_query_on_files(files, query):
    # Check if the OpenAI API key is provided
    if not os.getenv("OPENAI_API_KEY"):
        return "Cannot run model. No API key provided."

    try:
        queryEngineTools = []
        for file in files:
            curDoc = SimpleDirectoryReader(input_files=[file]).load_data()
            # index = VectorStoreIndex.from_documents(
            #     curDoc,
            #     storage_context=storage_context,
            #     show_progress=True,
            # )
            # query_engine = index.as_query_engine()
            # userResp = query_engine.query("Summarize this content.")
            # print(textwrap.fill(str(userResp), 100))
            curVectorStore = VectorStoreIndex.from_documents(curDoc)
            curEngine = curVectorStore.as_query_engine(similarity_top_k=3)
            curTool = QueryEngineTool(query_engine=curEngine, metadata=ToolMetadata(
                name=get_filename_before_dot(file),
                description=get_filename_before_dot(file)
            ))
            queryEngineTools.append(curTool)

        if len(files) > 0:
            s_engine = SubQuestionQueryEngine.from_defaults(query_engine_tools=queryEngineTools)
            response = s_engine.query(query)
            return response
        return ''
    except OpenAIError as e:
        return "Cannot run model. Invalid API key or other OpenAI error."
    except ValidationError as e:
        print(f"Validation error: {str(e)}")
        return "Validation error occurred."
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return "An unexpected error occurred."
