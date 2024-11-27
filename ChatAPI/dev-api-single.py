from openai import OpenAI
import argparse
import os

def main(): 

    # Setup argparse
    parser = argparse.ArgumentParser(description='Interact with OpenAI API.')
    parser.add_argument('-d', '--data', type=str, required=True, help='Text input for the OpenAI API')
    args = parser.parse_args()

    data = args.data

    client = OpenAI(
    organization='org-MBHC0y3264pOCnAzYj0YsRM6',
    project=os.environ['PROJECT_ID'],
    )

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": data}],
        stream=True,
    )

    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")
    print("\n")

if __name__ == "__main__":
    main()