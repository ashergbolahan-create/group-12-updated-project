"""Gemini assistant and email grade reports.

Owned by: Grace Ukpai Akpu  |  Branch: feature/ai-email-integration
"""

from .email_service import render_email_report, send_grade_report
from .gemini_assistant import ask_gemini, render_ai_assistant, summarize_student

__all__ = [
    "ask_gemini",
    "summarize_student",
    "render_ai_assistant",
    "send_grade_report",
    "render_email_report",
]
