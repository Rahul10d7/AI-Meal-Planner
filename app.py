import streamlit as st
import requests
import json

st.title("🍳 Free Meal Planner - 100% Local AI")

st.subheader("Enter your fridge items")
fridge_items = st.text_input(
    "What ingredients do you have?",
    placeholder="e.g., eggs, spinach, cheese"
)

def generate_recipe_local(ingredients):
    """Generate beautifully structured recipe"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:1b",
                "prompt": f"""You are a friendly home cook assistant.

                    The user has these ingredients: {ingredients}

                    Your task is to suggest ONE simple, tasty recipe they could make at home.

                    Please ALWAYS answer with a recipe. If the ingredients are limited, just be creative and propose something basic.

                    Format your answer exactly like this:

                    # [Recipe Title]
                    **Prep Time:** X min | **Cook Time:** X min | **Serves:** X

                    ## Ingredients
                    - ingredient 1
                    - ingredient 2

                    ## Steps
                    1. First step
                    2. Second step
                    3. Third step""",

                "stream": False,
                "options": {"temperature": 0.7, "num_predict": 400},
            },
            timeout=45,
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "No 'response' field found.")
        else:
            return f"Ollama returned error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Ollama Error: {str(e)}"


if fridge_items:
    st.write(f"**Your ingredients:** {fridge_items}")
    
    if st.button("🍲 Generate Recipe (Local AI)"):
        with st.spinner("Your local AI is cooking..."):
            recipe = generate_recipe_local(fridge_items)

        st.subheader("📋 Your Generated Recipe")

        if recipe:
            with st.expander("Click to view full recipe", expanded=True):
                st.markdown(recipe)
        else:
            st.warning(
                "Hmm, no recipe text was returned. Try different ingredients or click the button again."
            )

else:
    st.info("👆 Enter ingredients! (Runs 100% free on your Mac)")
