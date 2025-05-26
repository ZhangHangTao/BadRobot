import argparse
import json
import os
import pandas as pd  # Assuming pandas is available for reading the CSV
from system_prompt import system_prompt  # Import system prompt
from openai import OpenAI  # Assuming you have a third-party client module
from contextual_jailbreak import get_random_jailbreak_prompt
from safety_misalignment import get_random_safety_misalignment_prompt
from conceptual_deception import rewrite_user_input

def load_malicious_queries():
    """
    This function loads the malicious queries from the Excel file located in the parent directory
    and returns them as a list of strings.
    """
    file_path = os.path.join('..', 'Physical_Word_Malicious_Queries.xlsx')
    try:
        # Assuming the file is an Excel file and we need the 'Request' column
        data = pd.read_excel(file_path)  # Change to read_excel
        return data['Request'].tolist()
    except Exception as e:
        print(f"Error loading malicious queries: {e}")
        return []

def process_single_query(client, model, user_input, attack_method, output_file):
    """
    This function processes a single user input query with the selected attack method,
    performs a model inference, and saves the result.
    """
    if attack_method == "contextual jailbreak":
        jailbreak_prompt = get_random_jailbreak_prompt()
        user_input = f"{jailbreak_prompt}\n{user_input}"

    elif attack_method == "safety misalignment":
        safety_prompt = get_random_safety_misalignment_prompt()
        user_input = f"{user_input}\n{safety_prompt}"

    elif attack_method == "conceptual deception":
        print(f"Original User Input: {user_input}")
        user_input = rewrite_user_input(user_input, client, model=model)
        print(f"Rewritten User Input: {user_input}")


    print(user_input)
    messages = [system_prompt]  # Default system prompt
    if user_input:
        user_message = {
            "role": "user",
            "content": user_input
        }
        messages.append(user_message)  # Add user input

    # Call third-party API to make model inference
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        # Output response
        result = response.choices[0].message.content
        print(f"Response: {result}")

        # Save the result to the file
        with open(output_file, 'a') as f:  # Append mode
            f.write(f"Input: {user_input}\n")
            f.write(f"Response: {result}\n")
            f.write("="*50 + "\n")  # Separate each query with a line

    except Exception as e:
        print(f"Error calling the API: {e}")

def main(api_key, base_url, model, user_input, attack_method, load_malicious_queries_flag):
    # Create third-party OpenAI client
    client = OpenAI(api_key=api_key, base_url=base_url)

    # If no model is passed, set the default model
    if model is None:
        model = 'default-model'

    # Generate the output file name
    output_file = f"{model}_{attack_method}_results.txt"

    # Load malicious queries if the flag is set to True
    if load_malicious_queries_flag:
        malicious_queries = load_malicious_queries()
        if malicious_queries:
            for i, malicious_query in enumerate(malicious_queries, start=1):
                print(f"\nProcessing Malicious Query {i}/{len(malicious_queries)}:")
                # Process each malicious query one at a time
                process_single_query(client, model, malicious_query, attack_method, output_file)
        return  # Stop the function after processing malicious queries

    # If no malicious queries are loaded, process the user_input as a single query
    process_single_query(client, model, user_input, attack_method, output_file)


if __name__ == '__main__':
    # Use argparse to parse command-line arguments
    parser = argparse.ArgumentParser(description="Run model with optional user input and default system prompt.")
    parser.add_argument('--api_key', type=str, default='YOUR_API_KEY_HERE')
    parser.add_argument('--base_url', type=str, default='YOUR_API_BASE_URL_HERE')
    parser.add_argument('--model', type=str, default='gpt-3.5-turbo')
    parser.add_argument('--user_input', type=str, default='Hello, robot!')
    parser.add_argument('--attack_method', type=str,
                        choices=['contextual jailbreak', 'safety misalignment', 'conceptual deception'],
                        default='contextual jailbreak', help='Choose the attack method')
    parser.add_argument('--load_malicious_queries', type=bool, default=False, help='Set to True to load malicious queries from file')


    args = parser.parse_args()

    # Call main function, passing parsed arguments
    main(api_key=args.api_key, base_url=args.base_url, model=args.model, user_input=args.user_input,
         attack_method=args.attack_method, load_malicious_queries_flag=args.load_malicious_queries)
