from openai import OpenAI

def main():
    # Initialize OpenAI client
    client = OpenAI()
    
    conversation_history = []

    while True:
        # Prompt user for input
        user_input = input("\nEnter text (or 'exit' to quit): ")
        
        if user_input.lower() == 'exit':
            break
        
        # Add user message to conversation history
        conversation_history.append({"role": "user", "content": user_input})
        
        # Create chat completion stream with the conversation history
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation_history,
            stream=True,
        )

        response_content = ""
        
        # Print the streamed response
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")
                response_content += chunk.choices[0].delta.content
        
        # Add assistant message to conversation history
        conversation_history.append({"role": "assistant", "content": response_content})
        
        print()  # Print a newline for better readability between responses

if __name__ == "__main__":
    main()
