import os

def load_prompt(prompt_name: str) -> str:
    """
    Loads a prompt from a .txt file in the src/prompts directory.
    """
    # Assuming this is run from the root or src, we try to find the prompts dir
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prompt_path = os.path.join(base_dir, "prompts", f"{prompt_name}.txt")
    
    if not os.path.exists(prompt_path):
        # Fallback if called differently
        prompt_path = os.path.join("src", "prompts", f"{prompt_name}.txt")

    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"Prompt file not found: {prompt_name}.txt at {prompt_path}")

    with open(prompt_path, "r") as f:
        return f.read().strip()
