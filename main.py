import os
import sys
import logging
from groq import Groq
from colorama import init, Fore, Style

# Set up logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Check for input prompt and role preset
if len(sys.argv) < 1:
    logger.error("Input prompt and role preset must be provided.")
    sys.exit(1)
input_prompt = sys.argv[1]

# Set environment variable for the Groq API key
os.environ['GROQ_API_KEY'] = '<KEY>'
# Initialize the Groq client with the API key
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Define the universal context
universal_context = """
Expectations:
1. Keep responses concise and clear.
2. Refrain from long responses, keep it around or less than 450 characters.
3. Maintain a professional opinion and adhere to best practices.
4. Act as if you are collaborating in a corporate environment.
5. Focus on the specific role's responsibilities and expertise.
6. Always stick to the language constraint.
7. Keep a consistent workflow between members.
8. Performance is always key.
9. Refrain from giving ratings.
Standards:
1. Use the K.I.S.S. rule (Keep It Simple, Stupid).
2. Use the Rule of Three rule (duplication).
3. Use the Ninety-Ninety rule (failure to anticipate the hard parts).
4. Use the Efficiency versus code clarity rule (chasing false efficiency).
5. Use the Naming of things rule (subprograms and variables).
"""

# Define role presets
role_presets = {
    "programmer": {
        "Analyst": "Analyze the requirements and constraints then create an initial draft.",
        "Reviewer": "Review the code and brief analysis, readability, and quality control.",
        "Developer": "Revise the draft to now complete a well-structured and refactored solution.",
        "Manager": "Briefly summarize and explain the usage of this solution."
    },
    "writer": {
        "Analyst": "Analyze the topic and outline the main points for this writing task concisely and generate a first draft.",
        "Reviewer": "Review the draft and add comments on the structure, coherence, and quality control.",
        "Developer": "Create a well-structured and refined final draft based on the outline.",
        "Manager": "Briefly summarize and explain the main points and purpose of the final draft."
    },
    "analyst": {
        "Analyst": "Analyze the data requirements and constraints for this analysis task concisely and generate a first draft.",
        "Reviewer": "Review the analysis and add comment notes on the methodology, readability, and quality control.",
        "Developer": "Create a well-structured and detailed final analysis based on the draft.",
        "Manager": "Briefly summarize and explain the findings and implications of the analysis."
    }
}

# Assign what role the AI should take on
# options: programmer, writer and analyst
config_role = role_presets['programmer']

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def call_groq_api(role, additional_context, prompt, model="llama3-8b-8192"):
    logger.info(f'[{role}.{model}] fetching...')
    full_prompt = f"{universal_context}\n\nRole: {role}\n{additional_context}\n{prompt}"
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": full_prompt}],
            model=model,
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error: {e}")
        return "Exception caught, abort all tasks."

def strip_data(output):
    output = output.strip().replace('. ', '.\n')
    return output

def get_response(role, additional_context, prompt):
    return call_groq_api(role, additional_context, prompt)

def chain_agents(initial_prompt, preset):
    # Analyst phase
    print_separator(f"{Fore.CYAN}Analyst Draft")
    response1 = strip_data(get_response("Analyst", preset["Analyst"], initial_prompt))
    draft_catch = f"DRAFT:\n```{response1}```"
    print(f"{Fore.RESET}{response1}")

    # Peer Reviewer phase
    print_separator(f"{Fore.YELLOW}Peer Review")
    response2 = strip_data(get_response("Reviewer", preset["Reviewer"], response1))
    feedback_catch = f"REVIEW:\n```{response2}```"
    print(f"{Fore.RESET}{response2}")

    # Developer phase
    print_separator(f"{Fore.GREEN}Developer")
    response3 = strip_data(get_response("Developer", preset["Developer"], f"{response2}\n{draft_catch}"))
    print(f"{Fore.RESET}{response3}")

    # Finalizer phase
    print_separator(f"{Fore.MAGENTA}Manager")
    final_output = strip_data(get_response("Manager", preset["Manager"], f"{response3}\n{feedback_catch}"))
    print(f"{Fore.RESET}{final_output}")

    return final_output

def print_separator(label=None):
    if label is not None:
        print(f"{Fore.BLUE}╞[{label}{Fore.RESET}{Fore.BLUE}]{'═' * 100}╕{Fore.RESET}")
        return
    print(f"{Fore.BLUE}╞{'═' * 150}╕{Fore.RESET}")

if __name__ == "__main__":
    clear_screen()
    final_output = chain_agents(input_prompt, config_role)
    logger.info("Finished task")
    