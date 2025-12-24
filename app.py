import streamlit as st

st.title("🥘 Free Meal Planner")
st.write("Hello World! Your AI meal planner is ready to build")

st.subheader("Step 1: Enter your fridge items")

fridge_items = st.text_area(
    "What ingredients do you have in your fridge?",
    placeholder="e.g., eggs, spinach, chicken, tomatoes, cheese",
)

if fridge_items: 
    st.write("You entered these **fridge items**:")
    st.write(fridge_items)
else:
    st.write("👆 Start by typing the ingredients you have at home.")

