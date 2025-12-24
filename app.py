import streamlit as st        # Import the Streamlit library for building the web UI
import requests               # Import requests to make HTTP calls to the local Ollama server


# ---------- Page config (tab title, icon, layout) ----------
st.set_page_config(
    page_title="Free Meal Planner",  # Text shown in the browser tab title
    page_icon="🍳",                  # Small emoji/icon shown in the browser tab
    layout="centered",               # Center the main content on the page
)


# ---------- Main Title & Intro ----------
st.title("🍳 Free Meal Planner – 100% Local AI")  # Big bold title at the top of the page

# Short description explaining what the app does and why it's private/local
st.markdown(
    "Type the ingredients you have at home and let your **local AI chef** "
    "suggest a simple recipe. No accounts, no API keys, no data leaves your Mac."
)

# Horizontal line to separate intro from the rest of the page
st.markdown("---")


# ---------- Sidebar ----------
st.sidebar.header("About this app")  # Header text at the top of the sidebar

# Sidebar text explaining how the app works and which model it uses
st.sidebar.write(
    "- Runs on your local computer using **Ollama**.\n"
    "- AI model: `llama3.2:1b` (small, fast, free).\n"
    "- Great for quick meal ideas from leftover ingredients."
)

# Horizontal line inside the sidebar
st.sidebar.markdown("---")

# Small helper message in the sidebar about restarting Ollama if needed
st.sidebar.caption("Tip: Restart Ollama with `ollama serve` if recipes stop working.")


# ---------- Input Section ----------
st.subheader("1️⃣ Enter your fridge items")  # Subheading for the first step: entering ingredients

# Text input where the user types their ingredients as a single line of text
fridge_items = st.text_input(
    "What ingredients do you have?",                   # Label above the text box
    placeholder="e.g., eggs, spinach, cheese, bread",  # Example shown when the box is empty
)

# Small hint text under the input explaining how to format the ingredients
st.caption("Separate ingredients with commas. The AI will combine them into a single dish.")


# ---------- Helper: talk to Ollama ----------
def generate_recipe_local(ingredients: str) -> str:
    """
    Generate a structured recipe using the local Ollama model.

    Parameters
    ----------
    ingredients : str
        The raw string the user typed (e.g., 'eggs, spinach, cheese').

    Returns
    -------
    str
        Either a formatted recipe in markdown, or an error message starting with '❌'.
    """
    try:
        # Send a POST request to the local Ollama server running on your machine
        response = requests.post(
            "http://localhost:11434/api/generate",  # URL where Ollama listens for generate requests
            json={                                  # JSON body describing what we want the model to do
                "model": "llama3.2:1b",            # Name of the model to use (downloaded via `ollama pull`)
                "prompt": f"""You are a friendly home cook assistant.

The user has these ingredients: {ingredients}

Your task is to suggest ONE simple, tasty recipe they could make at home.

Important rules:
- You MUST use **every** listed ingredient in the recipe.
- You MUST mention **each ingredient by name** in the Ingredients section.
- You MAY also assume basic pantry items like oil, salt, pepper, and water.
- You MUST always answer with a recipe. Never say you can't fulfill the request.

Format your answer exactly like this:

# [Recipe Title]
**Prep Time:** X min | **Cook Time:** X min | **Serves:** X

## Ingredients
- ingredient 1
- ingredient 2

## Steps
1. First step
2. Second step
3. Third step""",      # Multi-line prompt telling the model its role, rules, and exact output format
                "stream": False,                    # Ask Ollama to return the full answer at once (not token-by-token)
                "options": {"temperature": 0.7,     # Model creativity: higher = more creative, lower = more deterministic
                            "num_predict": 400},    # Maximum number of tokens (roughly words/pieces) to generate
            },
            timeout=45,                             # Give the request up to 45 seconds before treating it as a timeout
        )

        # If Ollama did NOT return HTTP 200, something went wrong on the server side
        if response.status_code != 200:
            # Return an error message that starts with '❌', so the UI knows to show it as an error
            return f"❌ Ollama returned error {response.status_code}: {response.text}"

        # Convert the JSON response body into a Python dictionary
        data = response.json()

        # Get the 'response' field from the JSON, which contains the generated recipe text
        # If it doesn't exist, default to an empty string
        recipe_text = data.get("response", "").strip()

        # If the recipe text is empty, something went wrong with generation
        if not recipe_text:
            return "❌ I didn't receive any recipe text from the model. Please try again."

        # Normal case: return the recipe text to the caller
        return recipe_text

    # If the HTTP request fails because it can't reach the server (e.g., Ollama not running)
    except requests.exceptions.ConnectionError:
        return "❌ Could not connect to Ollama. Is `ollama serve` running in another terminal?"

    # If the request took longer than the timeout value (45 seconds)
    except requests.exceptions.Timeout:
        return "❌ The AI took too long to respond. Try again or use fewer ingredients."

    # Catch any other unexpected exception and show a generic error message
    except Exception as e:
        return f"❌ Unexpected error talking to the local AI: {str(e)}"



# ---------- Generate Button & Output ----------
st.markdown("---")                 # Horizontal line to separate input from the output section
st.subheader("2️⃣ Generate your recipe")  # Subheading for the second step: generating the recipe


# If the user has not typed any ingredients yet
if not fridge_items:
    # Show an info box prompting the user to enter ingredients first
    st.info("👆 Start by typing some ingredients above, then click the button.")
else:
    # Echo the ingredients back to the user for confirmation
    st.write(f"**Your ingredients:** {fridge_items}")

    # Create a button; when clicked, the code inside this block will run
    if st.button("🍲 Generate Recipe (Local AI)"):
        # Show a spinner while waiting for the AI response
        with st.spinner("Your local AI chef is cooking up ideas..."):
            # Call the helper function with the user’s ingredients
            recipe = generate_recipe_local(fridge_items)

        # Subheading for the output section
        st.subheader("📋 Your Generated Recipe")

        # If the returned text starts with our error prefix, show it in a red error box
        if recipe.startswith("❌"):
            st.error(recipe)
        else:
            # Otherwise, treat it as a successful recipe
            # Put the recipe inside an expander, expanded by default, to keep page tidy
            with st.expander("Click to view full recipe", expanded=True):
                # Render the recipe as markdown so headings, bold text, and lists look nice
                st.markdown(recipe)



# ---------- Footer ----------
st.markdown("---")  # Horizontal line before the footer

# Small footer text at the bottom of the page
st.caption(
    "Built with ❤️ using Streamlit and Ollama. "
    "All AI runs locally on your machine."
)
