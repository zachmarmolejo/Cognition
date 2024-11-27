from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
from openai import OpenAI
import logging
import subprocess
import os


app = FastAPI()


client = OpenAI()

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setting origins to run against local endpoint
origins = ["*"] # bad practice but it works

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str = Field(..., description="Role of the message sender, e.g., 'user'")
    content: str = Field(..., description="Content of the message")

class RequestModel(BaseModel):
    messages: List[Message] = Field(..., description="List of messages")
    max_tokens: int = Field(..., description="Maximum number of tokens")
    model: str = Field(..., description="Model to be used, e.g., 'gpt-4'")
    temperature: float = Field(..., description="Sampling temperature")
    stream: bool = Field(..., description="Whether to stream the response")


# Send data to OpenAI API
async def forward_request_to_openai(data: RequestModel):
    
    try:
        response_content = ""
        stream = client.chat.completions.create(
            model=data.model,
            messages=[message.model_dump() for message in data.messages],
            max_tokens=data.max_tokens,
            temperature=data.temperature,
            stream=data.stream
        )

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                #print(chunk.choices[0].delta.content, end="")
                response_content += chunk.choices[0].delta.content

        logger.info(f"OpenAI API request successful: {response_content}")
        return {"choices": [{"message": {"role": "user", "content": response_content}}]}
    except KeyError as e:
        logger.error(f"OpenAI API request failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OpenAI API request failed: {str(e)}")

async def request_data_from_rag_database(msg):
    # RAG Addition
    rag_script = "/home/parallels/Lab/Cognition/RAG/Project/query_data.py"

    query_text = str(msg)

    #pattern = r"content='([^']*)'\)"
    #match = re.findall(pattern, input_string)

    # pull the last instance of content each time to query against
    #query_text = match[-1]

    # Uncomment for debugging
    print("Data LOG to RAG: " + query_text)

    try:
        result = subprocess.run(
            ["python3", rag_script, query_text],
            capture_output=True,
            text=True,
            check=True,
            env=os.environ.copy(),
            cwd=os.path.dirname(rag_script)
        )

        #print("Output:\n", result.stdout)
        return {"choices": [{"message": {"role": "user", "content": result.stdout}}]}
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")

@app.post("/v1/chat/completions")
async def process_request(request: RequestModel):

    response = await request_data_from_rag_database(request.messages)
    response_string = str(response)

    print("RAG Info: " + response_string)

    if "Unable to find matching results." not in response_string:
        return response
    else:
        #print ("Direct Request: " + str(request))
        response = await forward_request_to_openai(request)
        # Uncomment for debugging
        # print("API Response: " + str(response))
        return response
