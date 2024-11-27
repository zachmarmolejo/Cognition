import argparse
import re
# from dataclasses import dataclass
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """

You are part of an ongoing conversation, this is the previous conversation history. Note there will be no history if it is the initial request:

{conversation_history}

Answer the following question while considering the previous conversation context to ensure coherence and relevance. Use the provided context and integrate it with the ongoing discussion:

{context}

---

Note if the context does not align with the conversation history (unless there is no coversation history yet), return "Unable to find matching results." 

If the question asks for a command-line example, ensure that the command is provided within a code block with syntax highlighting.

Question: {question}
"""


def main():
    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text

    # DEBUG
    # print(f"\n[!] LOG - Query Text: {query_text}\n")


    # regex pull last instance of content to query rag db
    pattern_1 = r"Message\(role='user', content='([^']*)'\)"
    match_1 = re.findall(pattern_1, query_text)

    #print(f"LOG - Initial Match: {match_1[1]}\n")

    # regex pull for assistant reponses
    pattern_2 = r'Message\(role=\'assistant\', content="([^"]*)"\)'
    match_2 = re.findall(pattern_2, query_text)

    #print(f"LOG - Initial Match: {match_2[1]}\n")

    history = ""
    # for question, answer in zip(match_1, match_2):
    #     history += f"\nQuestion: {question}\n\nAnswer: {answer}" + "\n"

    for i in range(min(len(match_1), len(match_2))):
        question = match_1[i]
        answer = match_2[i]
        history += f"\nQuestion: {question}\n\nAnswer: {answer}\n"

    # Handle the case where there are unmatched questions
    if len(match_1) > len(match_2):
        for i in range(len(match_2), len(match_1)):
            question = match_1[i]
            history += f"\nQuestion: {question}\n\nAnswer: [No answer provided]\n"
    

    # pull the last instance of content each time to query against
    content = match_1[-1]
    
    # DEBUG
    # print(f"[!] LOG - REGEX String: {content}\n")

    # Prepare the DB.
    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_relevance_scores(content, k=5)
    if len(results) == 0 or results[0][1] < 0.7:
        # If no relevant data only this will return and the query will then go directly to OpenAI
        print(f"Unable to find matching results.")  
        return

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(conversation_history=history, context=context_text, question=content)
    
    # Uncomment to get all the prompt data for context
    #print(prompt)

    model = ChatOpenAI()

    response_text = model.predict(prompt)

    sources = [doc.metadata.get("source", None) for doc, _score in results]

    # Data to send back to Web UI
    formatted_response = f"{response_text}\\\nSources: {sources}"
    print(formatted_response)

if __name__ == "__main__":
    main()