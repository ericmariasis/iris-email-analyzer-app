import nest_asyncio
from openai import OpenAIError

nest_asyncio.apply()

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.llms.openai import OpenAI

from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import SubQuestionQueryEngine

import os
from .myconfig import *

os.environ["OPENAI_API_KEY"] = f'{OPENAI_API_KEY}'

from llama_index.core import Settings

Settings.llm = OpenAI(temperature=0.2, model="gpt-3.5-turbo")


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
