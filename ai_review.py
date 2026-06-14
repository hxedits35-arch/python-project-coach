import streamlit as st
from groq import Groq
import os

def get_cloud_ai_review(user_code: str, detected_issues: list) -> str:
    """
    Sends the user's code and detected issues to a live Llama model hosted on Groq Cloud.
    Returns a beginner-friendly educational critique.
    """
    
    # 1. Format the detected issues into a readable string for the AI prompt
    issues_str = "\n".join([f"- {issue}" for issue in detected_issues]) if detected_issues else "No major syntax or structural issues detected."

    # 2. Craft a strict system prompt to keep the AI encouraging, educational, and focused
    system_prompt = (
        "You are 'Python Project Coach', an encouraging, empathetic, and expert programming teacher. "
        "Your goal is to help beginner programmers improve their code. "
        "Never be overly critical or insulting. Explain WHY changes matter, not just WHAT to change. "
        "Format your response beautifully using Markdown with clear headings, bullet points, and code blocks."
    )

    # 3. Construct the user prompt with the code and the context
    user_prompt = f"""
    Please review the following Python code written by a beginner student.
    
    [Detected Issues from Static Analysis]:
    {issues_str}
    
    [User's Code]:
    ```python
    {user_code}
    ```
    
    Provide your review in the following structured format:
    1. 🎉 **Encouraging Summary**: A quick, positive note on what they did right.
    2. 💡 **Concept Breakdown**: Explain the biggest issues found in beginner-friendly terms. 
    3. 🚀 **Before & After Example**: Show a small snippet of their original code alongside a better, refactored version, explaining the core benefit of the fix.
    """

    try:
        # 4. Pull the API key securely from Streamlit secrets (with local environment fallback for testing)
        if "GROQ_API_KEY" in st.secrets:
            api_key = st.secrets["GROQ_API_KEY"]
        else:
            api_key = os.environ.get("GROQ_API_KEY")
            
        if not api_key:
            raise ValueError("Groq API Key not found in Streamlit Secrets or Environment Variables.")

        client = Groq(api_key=api_key)

        # 5. Request a response from the updated, live Llama 3.1 model
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",  
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3, # Low temperature makes the AI's response more structured and reliable
        )
        return completion.choices[0].message.content

    except Exception as e:
        # Graceful fallback error message if cloud connection fails
        return (
            "⚠️ **Could not connect to Cloud AI Coach.**\n\n"
            "Please check your internet connection or verify that your Groq API Key "
            f"is set up correctly in your secrets configuration.\n\n*Error details: {e}*"
        )

# Simple test block to make sure it works independently
if __name__ == "__main__":
    print("Testing connection to Groq Cloud AI...")
    sample_code = "def calc(x):\n    y = x * 2\n    return y"
    sample_issues = ["Poor variable names ('x', 'y')", "Missing function docstring"]
    
    # This will now successfully use your local machine's environment key if testing standalone
    try:
        feedback = get_cloud_ai_review(sample_code, sample_issues)
        print("\n--- AI Coach Response ---")
        print(feedback)  
    except Exception as e:
        print(f"\nTo test this file directly, run your main dashboard app via: streamlit run app.py")