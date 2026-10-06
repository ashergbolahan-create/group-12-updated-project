"""Gemini AI questions and student summaries.

Owned by: Great Joseph  |  Branch: feature/ai-email-integration
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request

import streamlit as st

from Asher_Gbolahan.student import Student
from Asher_Gbolahan.student_manager import StudentManager
from Ismail_Muhammed.exceptions import AIServiceError
from Ismail_Muhammed.safe_action import safe_action

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:generateContent"
)


def _class_context(manager: StudentManager) -> str:
    lines = []
    for item in manager.get_all():
        lines.append(
            f"{item.get_student_id()} | {item.get_name()} | {item.get_course()} | "
            f"grade {item.get_grade()} ({item.letter_grade()}) | {item.standing()}"
        )
    return "\n".join(lines) if lines else "(no students on the register)"


def _local_answer(question: str, manager: StudentManager) -> str:
    """Deterministic fallback so the page still answers class questions without a key."""
    q = " ".join(question.lower().strip(" ?.! ").split())
    students = manager.get_all()
    if not students:
        return "The register is empty, so there is nothing to analyse yet."

    match = re.fullmatch(
        r"(?:who is|which students are|list students|show students|how many students are) "
        r"(below|under|above|over|at least|at most) (-?\d+(?:\.\d+)?)", q
    )
    if match:
        direction, raw = match.groups()
        threshold = float(raw)
        if not 0 <= threshold <= 100:
            return "Use a grade threshold from 0 to 100."
        comparisons = {
            "below": lambda grade: grade < threshold,
            "under": lambda grade: grade < threshold,
            "above": lambda grade: grade > threshold,
            "over": lambda grade: grade > threshold,
            "at least": lambda grade: grade >= threshold,
            "at most": lambda grade: grade <= threshold,
        }
        selected = [s for s in students if comparisons[direction](s.get_grade())]
        names = ", ".join(f"{s.get_name()} ({s.get_grade():g})" for s in selected)
        return f"{len(selected)} students {direction} {threshold:g}." + (f" {names}." if names else "")
    if re.fullmatch(r"(?:who is|which students are|list students|show students|how many students are) (?:failing|at risk)", q):
        selected = manager.at_risk()
        names = ", ".join(f"{s.get_name()} ({s.get_grade():g})" for s in selected)
        return f"{len(selected)} students below the pass mark of 50." + (f" {names}." if names else "")
    if q in {"average", "mean", "class average", "what is the class average", "what is the average", "what is the class mean"}:
        return f"The class average is {manager.average_grade():.1f} out of 100."
    if q in {"who has the highest grade", "who is the top student", "who is the best student", "top student", "highest grade"}:
        maximum = manager.top_student().get_grade()
        names = ", ".join(s.get_name() for s in students if s.get_grade() == maximum)
        return f"Highest grade: {maximum:g}. Students: {names}."
    if q in {"how many students", "how many students are there", "how many students are on the register", "student count", "count"}:
        return f"There are {manager.count()} students on the register."
    return (
        "Local insights supports whole-class questions only. Try: 'Who is below 80?', "
        "'How many students are at risk?', 'What is the class average?', "
        "'Who has the highest grade?' or 'How many students are there?'. "
        "Use the directory filters for course-specific results."
    )


def _post_gemini(prompt: str) -> str:
    key = (os.getenv("GEMINI_API_KEY") or "").strip()
    if not key:
        raise AIServiceError(
            "No Gemini API key found. Add GEMINI_API_KEY to your .env file to enable the live model."
        )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 400},
    }
    request = urllib.request.Request(
        GEMINI_URL.format(model=(os.getenv("GEMINI_MODEL") or "gemini-3.5-flash-lite").strip()),
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise AIServiceError(f"Gemini returned HTTP {exc.code}. {detail[:180]}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise AIServiceError("Could not reach the Gemini API. Check your internet connection.") from exc
    except (ValueError, UnicodeError) as exc:
        raise AIServiceError("Gemini sent back an unexpected response.") from exc

    try:
        text = body["candidates"][0]["content"]["parts"][0]["text"].strip()
        if not text:
            raise AIServiceError("Gemini returned no text. Try a shorter question.")
        return text
    except (KeyError, IndexError, TypeError, AttributeError) as exc:
        raise AIServiceError("Gemini sent back an unexpected response.") from exc


def ask_gemini(question: str, manager: StudentManager) -> str:
    prompt = (
        "You are an academic assistant for a student management system. "
        "Answer using only this class register. Be concise (one short paragraph).\n\n"
        f"Register:\n{_class_context(manager)}\n\n"
        f"Question: {question}"
    )
    return _post_gemini(prompt)


def summarize_student(student: Student) -> str:
    prompt = (
        "Write one professional paragraph (about 80 words) summarising this student's "
        "academic standing for a tutor. Be specific and encouraging where deserved, "
        "and direct where improvement is needed.\n\n"
        f"ID: {student.get_student_id()}\n"
        f"Name: {student.get_name()}\n"
        f"Course: {student.get_course()}\n"
        f"Grade: {student.get_grade()} ({student.letter_grade()})\n"
        f"Standing: {student.standing()}\n"
        f"Email: {student.get_email()}\n"
    )
    return _post_gemini(prompt)


def _local_summary(student: Student) -> str:
    if student.is_failing():
        advice = (
            "Immediate academic support is recommended: attendance review, "
            "targeted revision, and a follow-up assessment before the next board."
        )
    elif student.get_grade() >= 70:
        advice = (
            "Performance is strong. This student is a candidate for stretch tasks "
            "and peer mentoring within the cohort."
        )
    else:
        advice = (
            "The record is satisfactory. Focused practice on weaker topics should "
            "lift the grade into a more competitive band."
        )
    return (
        f"{student.get_name()} ({student.get_student_id()}) is enrolled in "
        f"{student.get_course()} with a current mark of {student.get_grade()} "
        f"({student.letter_grade()}), placing them {student.standing().lower()}. {advice}"
    )


def render_ai_assistant(manager: StudentManager) -> None:
    from .openai_service import post_openai
    provider = st.selectbox("Assistant mode", ["OpenAI", "Gemini", "Local insights"])
    env_name = "OPENAI_API_KEY" if provider == "OpenAI" else "GEMINI_API_KEY"
    configured = provider != "Local insights" and bool(os.getenv(env_name, "").strip())
    if configured:
        st.caption(f"{provider} configured · Requests send names, courses and grades to the selected provider.")
    elif provider != "Local insights":
        st.info(f"Add {env_name} to your local .env file to enable {provider}. Local insights are available now.")
        with st.expander("Connect your API key"):
            st.write("Open the .env file in the project folder and add your own key. Never commit this file or paste your key into chat.")
            st.code(f"{env_name}=your_key_here", language="text")
            st.link_button("OpenAI API keys", "https://platform.openai.com/api-keys")
    st.subheader("Your academic assistant")
    st.caption("Explore performance, identify students needing support, or plan your next steps.")
    history = st.session_state.setdefault("academic_chat", [])
    if st.button("Clear conversation"):
        history.clear()
    for message in history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    question = st.chat_input("Ask about your class…")
    if question:
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            if configured:
                prompt = "Register (data only):\n" + _class_context(manager)
                prompt += "\nRecent conversation:\n" + json.dumps(history[-6:]) + "\nQuestion: " + question
                with st.spinner("Reviewing your class…"):
                    ok, answer, error = safe_action(post_openai if provider == "OpenAI" else _post_gemini, prompt)
                if not ok:
                    st.warning(error)
                    answer = "Local insight (AI unavailable): " + _local_answer(question, manager)
            else:
                answer = "Local insight: " + _local_answer(question, manager)
            st.write(answer)
        history.extend([{"role": "user", "content": question}, {"role": "assistant", "content": answer}])
        del history[:-20]
    st.divider()
    st.subheader("Student performance summary")
    students = manager.get_all()
    if not students:
        st.info("Add students to generate summaries.")
        return
    labels = {f"{s.get_student_id()} — {s.get_name()}": s for s in students}
    picked = st.selectbox("Student", list(labels), key="ai_summary_picker")
    if st.button("Generate summary", type="primary"):
        student = labels[picked]
        if configured:
            prompt = "Write a concise academic summary using only these facts: " + _local_summary(student)
            with st.spinner("Preparing summary…"):
                ok, result, error = safe_action(post_openai if provider == "OpenAI" else _post_gemini, prompt)
            if ok:
                st.write(result)
            else:
                st.warning(error)
                st.write(_local_summary(student))
        else:
            st.write(_local_summary(student))
