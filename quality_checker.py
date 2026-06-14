import ast

def analyze_code_structure(code_content: str) -> dict:
    """
    Uses Python's built-in AST module to analyze code layout,
    detect common beginner errors, and collect structural metrics.
    """
    results = {
        "errors": [],
        "warnings": [],
        "metrics": {
            "missing_docstrings": 0,
            "poor_variable_names": 0,
            "deep_nesting": 0,
            "total_functions": 0
        }
    }
    
    # 1. Attempt to parse the code. If it has syntax errors, catch them instantly.
    try:
        root = ast.parse(code_content)
    except SyntaxError as se:
        results["errors"].append(f"Syntax Error on line {se.lineno}: {se.msg} (Check your indentation or missing colons!)")
        return results

    # 2. Walk through the code structure to analyze functions, variables, and loops
    for node in ast.walk(root):
        
        # Check Functions
        if isinstance(node, ast.FunctionDef):
            results["metrics"]["total_functions"] += 1
            
            # Check for missing docstrings
            if ast.get_docstring(node) is None:
                results["metrics"]["missing_docstrings"] += 1
                results["warnings"].append(f"Function '{node.name}' is missing a docstring explanation.")
            
            # Check for long functions (Rule of thumb for beginners: keep it under 25 lines)
            func_lines = node.end_lineno - node.lineno
            if func_lines > 25:
                results["warnings"].append(f"Function '{node.name}' is a bit long ({func_lines} lines). Try breaking it down!")

        # Check Variable/Argument Names (Look for single letter names like x, y, z that aren't loop counters)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if len(node.id) == 1 and node.id not in ['i', 'j', 'k', '_']:
                results["metrics"]["poor_variable_names"] += 1
                results["warnings"].append(f"Line {node.lineno}: Single-letter variable name '{node.id}' can be confusing. Use descriptive names like 'user_age' instead.")

        # Check for deep nesting (e.g., an 'if' inside an 'if' inside a 'for' loop)
        if isinstance(node, (ast.If, ast.For, ast.While)):
            # Track how deep this node goes
            for child in ast.iter_child_nodes(node):
                for sub_child in ast.iter_child_nodes(child):
                    if isinstance(sub_child, (ast.If, ast.For, ast.While)):
                        results["metrics"]["deep_nesting"] += 1
                        results["warnings"].append(f"Line {sub_child.lineno}: Deeply nested loop or conditional found. Consider simplifying.")

    return results

# Simple local tester
if __name__ == "__main__":
    test_bad_code = """
def calc(x):
    if x > 10:
        if x < 100:
            for i in range(x):
                print(i)
    return x * 2
"""
    print("Testing quality_checker.py against messy code sample...")
    analysis = analyze_code_structure(test_bad_code)
    print("\n--- Warnings Found ---")
    for warning in analysis["warnings"]:
        print(f"⚠️ {warning}")