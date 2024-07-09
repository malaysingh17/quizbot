from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST

def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)
        session["current_question_id"] = 0
        session["answers"] = {}
        session.save()
        return bot_responses

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses

def record_current_answer(answer, current_question_id, session):
    """
    Validates and stores the answer for the current question to Django session.
    """
    if current_question_id is None:
        return False, "No current question to record an answer for."

    answers = session.get("answers", {})
    question = PYTHON_QUESTION_LIST[current_question_id]

    if answer not in question["options"]:
        return False, f"Invalid answer. Please choose from {question['options']}."

    answers[current_question_id] = answer
    session["answers"] = answers

    return True, ""

def get_next_question(current_question_id):
    """
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    """
    if current_question_id is None or current_question_id + 1 >= len(PYTHON_QUESTION_LIST):
        return None, None

    next_question = PYTHON_QUESTION_LIST[current_question_id + 1]
    return next_question["question_text"], current_question_id + 1

def generate_final_response(session):
    """
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    """
    answers = session.get("answers", {})
    total_questions = len(PYTHON_QUESTION_LIST)
    correct_answers = 0

    for i, question in enumerate(PYTHON_QUESTION_LIST):
        correct_answer = question["answer"]
        user_answer = answers.get(i)

        if user_answer == correct_answer:
            correct_answers += 1

    return f"Quiz completed! Your score is {correct_answers} out of {total_questions}."
