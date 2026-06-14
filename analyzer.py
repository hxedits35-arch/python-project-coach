# Import our custom modules that we built earlier
import quality_checker
import scoring
import ai_review  # This stays the same
import resources

def run_full_code_analysis(code_content: str) -> dict:
    """
    Coordinates the entire analysis pipeline:
    1. Static parsing with AST
    2. Score generation
    3. Educational link mapping
    4. Cloud Llama 3 critique via Groq Cloud
    
    Returns a unified dictionary containing all results.
    """
    # Step 1: Run the AST structure scan
    structural_analysis = quality_checker.analyze_code_structure(code_content)
    
    # Step 2: Calculate the score, grade, and chart visual breakdown
    score, grade, breakdown = scoring.calculate_score(structural_analysis)
    
    # Step 3: Gather free web links tailored to their exact errors
    learning_links = resources.get_learning_resources(
        structural_analysis["warnings"], 
        structural_analysis["metrics"]
    )
    
    # Step 4: Call Groq Cloud Llama 3 for the empathetic, student-friendly review
    # We combine errors and warnings into one simple list for the AI prompt
    all_issues = structural_analysis["errors"] + structural_analysis["warnings"]
    
    # 🛠️ UPDATED LINE: Calling our new cloud function instead of the local one
    ai_feedback = ai_review.get_cloud_ai_review(code_content, all_issues)
    
    # Package everything up beautifully for our Streamlit UI to consume
    full_report = {
        "score": score,
        "grade": grade,
        "breakdown": breakdown,
        "errors": structural_analysis["errors"],
        "warnings": structural_analysis["warnings"],
        "resources": learning_links,
        "ai_critique": ai_feedback,
        "original_code": code_content # Storing this so our chat follow-up can use it later
    }
    
    return full_report


def ask_follow_up(user_message: str, current_report: dict) -> str:
    """
    Handles conversational follow-up questions from the Streamlit chat box.
    Leverages your existing ai_review module to chat contextually with Llama 3.
    """
    # Check if your ai_review module already has a chat handler, 
    # otherwise we dynamically structure a prompt using your existing cloud configuration
    if hasattr(ai_review, "get_chat_response"):
        return ai_review.get_chat_response(user_message, current_report)
    
    # If ai_review doesn't have a chat function yet, we can pass a context-rich prompt
    # directly to your existing get_cloud_ai_review or structured chat pipeline:
    contextual_prompt = (
        f"You are the Python Project Coach. The user is asking a follow-up question regarding their code.\n\n"
        f"--- ORIGINAL CODE SUBMITTED ---\n{current_report.get('original_code', 'No code provided.')}\n\n"
        f"--- YOUR INITIAL CRITIQUE ---\n{current_report['ai_critique']}\n\n"
        f"--- USER'S FOLLOW-UP QUESTION ---\n{user_message}\n\n"
        f"Provide an empathetic, encouraging, and highly educational response directly answering their question."
    )
    
    try:
        # Re-using your cloud connection setup to answer the specific chat bubble
        # Passing an empty list for issues since the context is built directly into the prompt string above
        chat_reply = ai_review.get_cloud_ai_review(contextual_prompt, [])
        return chat_reply
    except Exception as e:
        return f"Hey! I ran into a small connectivity hiccup replying to that: {str(e)}. Try asking me again!"


# Simple local tester
if __name__ == "__main__":
    print("Testing backend integration pipeline in analyzer.py...")
    sample_student_code = "def check(val):\n    if val == True:\n        print('Yes')\n    return val"
    
    # Running the full pipeline
    report = run_full_code_analysis(sample_student_code)
    
    print("\n--- Pipeline Execution Summary ---")
    print(f"Final Grade assigned: {report['grade']} ({report['score']}/100)")
    print(f"Number of warnings caught: {len(report['warnings'])}")
    print(f"Number of resources recommended: {len(report['resources'])}")
    
    # Testing the new chat follow-up logic locally
    print("\nTesting conversational follow-up...")
    test_reply = ask_follow_up("How can I fix the 'val == True' warning?", report)
    print(f"Coach Reply: {test_reply[:120]}...")
    
    print("\nAI Coach has processed code successfully!")