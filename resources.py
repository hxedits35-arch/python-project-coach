def get_learning_resources(warnings: list, metrics: dict) -> list:
    """
    Scans detected warnings and metrics to return targeted, 
    100% free educational links for the user to read and learn from.
    """
    # A local catalog linking programming mistakes to free educational resources
    RESOURCE_CATALOG = {
        "docstring": {
            "title": "🐍 Python Docstrings Tutorial",
            "description": "Learn how to document your functions using docstrings so your code is professional and easy to read.",
            "url": "https://realpython.com/documenting-python-code/"
        },
        "variable_names": {
            "title": "💡 Python Variable Naming Rules & Best Practices",
            "description": "An easy-to-follow guide on how to choose meaningful names for your variables and constants.",
            "url": "https://www.w3schools.com/python/python_variables_names.asp"
        },
        "nesting": {
            "title": "🚀 Flattening Your Code: Avoid Deep Nesting",
            "description": "See why nesting too many 'if' statements or loops makes code confusing, and learn how to fix it.",
            "url": "https://realpython.com/python-conditional-statements/"
        },
        "functions": {
            "title": "📦 How to Write Clean Functions in Python",
            "description": "Master breaking down huge, complicated chunks of code into small, reusable functions.",
            "url": "https://www.w3schools.com/python/python_functions.asp"
        },
        "general": {
            "title": "📚 Official Python Beginner's Guide",
            "description": "The perfect starting place to bookmark and search for any Python syntax or built-in tool.",
            "url": "https://docs.python.org/3/tutorial/index.html"
        }
    }

    recommended_resources = []
    triggered_keys = set()

    # 1. Check metrics to find structural problems
    if metrics.get("missing_docstrings", 0) > 0:
        triggered_keys.add("docstring")
        
    if metrics.get("poor_variable_names", 0) > 0:
        triggered_keys.add("variable_names")
        
    if metrics.get("deep_nesting", 0) > 0:
        triggered_keys.add("nesting")

    # 2. Scan text warnings for general function issues
    for warning in warnings:
        if "Function" in warning and "long" in warning:
            triggered_keys.add("functions")

    # 3. Pull matching resource blocks from our catalog
    for key in triggered_keys:
        recommended_resources.append(RESOURCE_CATALOG[key])

    # 4. Always provide a fallback general resource so the user never sees an empty list
    if not recommended_resources:
        recommended_resources.append(RESOURCE_CATALOG["general"])

    return recommended_resources

# Simple local tester
if __name__ == "__main__":
    print("Testing resources.py recommendation mapper...")
    mock_warnings = ["Function 'calculate' is a bit long (42 lines)."]
    mock_metrics = {"missing_docstrings": 1, "poor_variable_names": 0, "deep_nesting": 0}
    
    links = get_learning_resources(mock_warnings, mock_metrics)
    print("\n--- Recommended Resources for Student ---")
    for link in links:
        print(f"\n* {link['title']}")
        print(f"  {link['description']}")
        print(f"  URL: {link['url']}")