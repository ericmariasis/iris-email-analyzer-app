import textwrap
import nest_asyncio
from llama_index.embeddings.openai import OpenAIEmbedding
from openai import OpenAIError
from pydantic import ValidationError

nest_asyncio.apply()

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Settings, get_response_synthesizer
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.query_engine import SubQuestionQueryEngine, RetrieverQueryEngine
from llama_iris import IRISVectorStore
from dotenv import load_dotenv
from llama_index.core.retrievers import VectorIndexRetriever

import os
from .myconfig import *

load_dotenv()

os.environ["OPENAI_API_KEY"] = f'{OPENAI_API_KEY}'

username = f'{DB_USER}'
password = f'{DB_PASS}'
hostname = os.getenv('IRIS_HOSTNAME', f'{DB_URL}')
port = f'{DB_PORT}'
namespace = f'{DB_NAMESPACE}'

Settings.llm = OpenAI(temperature=0.2, model="gpt-3.5-turbo")

import ssl

certificateFile = "/usr/cert-demo/certificateSQLaaS.pem"

if os.path.exists(certificateFile):
    print("Located SSL certificate at '%s', initializing SSL configuration", certificateFile)
    sslcontext = ssl.create_default_context(cafile=certificateFile)
else:
    print("No certificate file found, continuing with insecure connection")
    sslcontext = None

from sqlalchemy import create_engine, text

url = f"iris://{username}:{password}@{hostname}:{port}/{namespace}"

vector_store = IRISVectorStore.from_params(
    connection_string=url,
    table_name="user",
    embed_dim=1536,  # openai embedding dimension
    # engine_args={"connect_args": {"sslcontext": sslcontext}}
)
storage_context = StorageContext.from_defaults(vector_store=vector_store)


def get_filename_before_dot(filename):
    name, extension = os.path.splitext(filename)
    return name


def get_clean_name(name):
    return name.replace(".", "_")


def run_query_on_files(files, query, top_k_similarity=3, similarity_threshold=0.5):
    # Check if the OpenAI API key is provided
    if not os.getenv("OPENAI_API_KEY"):
        return "Cannot run model. No API key provided."

    try:
        queryEngineTools = []
        for file in files:
            curDoc = SimpleDirectoryReader(input_files=[file]).load_data()

            # Get embed_dim and embed_type from document metadata (you may need to adapt this part based on your actual data)
            embed_dim = 1536
            embed_type = "openai"  # This should be fetched from the document metadata

            if embed_type == "openai":
                Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", embed_batch_size=100)

            index = VectorStoreIndex.from_documents(
                curDoc,
                storage_context=storage_context,
                show_progress=True,
            )
            vector_store = IRISVectorStore.from_params(
                connection_string=url,
                table_name=get_clean_name(get_filename_before_dot(file)),
                embed_dim=embed_dim,
            )

            try:
                index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
            except Exception as e:
                print(f"Failed to load index from storage: {e}")
                raise ValueError("Failed to load index from storage.") from e

            retriever = VectorIndexRetriever(
                index=index,
                similarity_top_k=top_k_similarity,
            )

            response_synthesizer = get_response_synthesizer()

            query_engine = RetrieverQueryEngine(
                retriever=retriever,
                response_synthesizer=response_synthesizer,
                node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=similarity_threshold)],
            )

            userResp = query_engine.query("Summarize this content.")
            print(textwrap.fill(str(userResp), 100))
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
