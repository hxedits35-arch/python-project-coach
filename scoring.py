def calculate_score(analysis_results: dict) -> tuple:
    """
    Calculates a code quality score from 0 to 100 and assigns a letter grade.
    Returns a tuple containing: (score, letter_grade, score_breakdown_dict)
    """
    # Start with a perfect score
    score = 100
    
    # Extract data from our analyzer results
    has_errors = len(analysis_results.get("errors", [])) > 0
    warnings = analysis_results.get("warnings", [])
    metrics = analysis_results.get("metrics", {})
    
    # 1. Critical Penalty: If the code has a syntax error, it won't run at all.
    if has_errors:
        return 0, "F", {"Readability": 0, "Style": 0, "Documentation": 0, "Maintainability": 0}
        
    # 2. Break down deductions across categories
    # Each warning costs a few points, capped to prevent negative scores
    total_warnings = len(warnings)
    warning_deduction = total_warnings * 5
    score -= warning_deduction
    
    # Specific targeted deductions based on metrics
    missing_docs = metrics.get("missing_docstrings", 0)
    poor_names = metrics.get("poor_variable_names", 0)
    deep_nesting = metrics.get("deep_nesting", 0)
    
    score -= (missing_docs * 8)   # Heavy penalty for no documentation
    score -= (poor_names * 4)     # Penalty for bad variable names
    score -= (deep_nesting * 6)   # Penalty for messy nested structures

    # Ensure score stays bounded between 0 and 100
    score = max(0, min(100, score))
    
    # 3. Determine the Letter Grade
    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    elif score >= 60:
        grade = "D"
    else:
        grade = "F"
        
    # 4. Generate a categorical breakdown for our UI charts later
    # This simulates a grading rubric for the hackathon bonus feature!
    breakdown = {
        "Documentation": max(0, 100 - (missing_docs * 30 + warning_deduction // 4)),
        "Readability": max(0, 100 - (poor_names * 20 + warning_deduction // 4)),
        "Maintainability": max(0, 100 - (deep_nesting * 25 + warning_deduction // 4)),
        "Overall Style": score
    }
    
    return score, grade, breakdown

# Simple local tester
if __name__ == "__main__":
    print("Testing scoring.py evaluation algorithm...")
    # Mocking a bad analysis result
    mock_results = {
        "errors": [],
        "warnings": ["Missing docstring", "Bad name"],
        "metrics": {
            "missing_docstrings": 1,
            "poor_variable_names": 2,
            "deep_nesting": 1,
            "total_functions": 1
        }
    }
    
    final_score, final_grade, visual_breakdown = calculate_score(mock_results)
    print(f"\nCalculated Score: {final_score}/100")
    print(f"Assigned Grade: {final_grade}")
    print(f"Chart Breakdown: {visual_breakdown}")