# Cognition
Cognition is an advanced Retrieval-Augmented Generation (RAG) service. It is used with external data for specialized knowledge and will allow you to reference source information. In my case I use the service for offensive security related topics, however the data I use will not be provided in this project. This however will be a usable project for your own data to be leveraged.

# Project Info
This RAG service uses the following open source projects:
- https://github.com/anse-app/anse -> Web UI
- https://github.com/pixegami/langchain-rag-tutorial -> RAG functionality
- Custom python API to handle the interactions between each component.
- Usage is specific to OpenAI API.

# Setup
## OpenAI API Access
You will need an OpenAI API key, which will require an account setup with OpenAI.
- For testing purposes, you can set the API key and Project ID in a profile config, or store in environment variables.

```bash
~/Lab/Cognition$ cat ~/.bashrc | grep export | grep -E "(API|PROJECT)"
export OPENAI_API_KEY="sk-proj-yLzdiljr..."
export PROJECT_ID="proj_hLb6r..."
```
## Create Database
- Within the `RAG/Project` directory, create subdirectories `data/ingest`.
- Store the files you want processed in the ingest folder as markdown files, the naming convention does not matter.

```bash
~/Lab/Cognition/RAG/Project/data$ tree | head
.
└── ingest
    ├── 00 - AD High-Level Overview.md
    ├── 00 - ADCS.md
    ├── 00 - AWS Security Notes.md
    ├── 00 - AWS.md
    ├── 00 - Abusing Group Policy.md
    ├── 00 - Admin Shell.md
    ├── 00 - AppLocker.md
    ├── 00 - Auth Bypasses.md
```
- Once the files are added, run the `create_database.py` script to populate the database.
- I like to add a time check to see how long it takes.

```bash
time python3 create_database.py
```

## Querying the RAG Service
- After the database is complete, you can test the base functonality with `query_data.py`

```bash
python3 query_data.py "[Message(role='user', content='what is red teaming')]" 2>/dev/null
```

## Running the WebUI and Python API
Note for the python API, you will need to edit the `query_data.py` path.

```python
async def request_data_from_rag_database(msg):
    # RAG Addition
    rag_script = "/path/to/query_data.py"

    query_text = str(msg)
```

I typically run this in a tmux session for ease of use
```bash
tmux new -s RAG
```
Running the Web UI
```bash
cd ChatAPI/WebUI/anse
./run.sh
```
Running the python API
```bash
cd ChatAPI/Middleware
./run.sh
```

Once the services are running you can navigate to `http://localhost:3000` in a browser.

![Screenshot from 2024-11-27 11-44-45](https://github.com/user-attachments/assets/cf5826ad-f69e-4c66-b8d8-b5a681a79f5e)





