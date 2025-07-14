def judge_true_or_false_from_string(input_string):
    if "true" in input_string or "True" in input_string:
        return True
    elif "false" in input_string or "False" in input_string:
        return False
    else:
        raise(Exception, "No Target Error in judge_true_or_false_from_string.")
    
def extract_feedback_for_general_purpose(input_string):
    if "true" in input_string or "True" in input_string:
        return True
    else:
        return input_string