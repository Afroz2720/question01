"""
Streamlit app - PDF question generator.
Uses OpenRouter with free models.
"""

import streamlit as st

from config import DEFAULT_MODEL, OPENROUTER_API_KEY
from pdf_export import generate_answers_pdf, generate_question_paper_pdf
from pdf_utils import extract_text_from_pdf
from question_generator import (
    QUESTION_TYPES,
    generate_questions,
)

# OpenRouter models: Claude, OpenAI, Llama, Gemini (and free options)
MODELS = [
    # Free (reliable)
    "meta-llama/llama-3.2-3b-instruct:free",
    "google/gemini-2.0-flash-exp:free",
    "openrouter/free",
    # Claude (Anthropic) - requires credits
    "anthropic/claude-sonnet-4",
    "anthropic/claude-3.5-sonnet",
    "anthropic/claude-3-haiku",
    "anthropic/claude-opus-4.6",
    # OpenAI
    "openai/gpt-4o",
    "openai/gpt-4o-mini",
    "openai/gpt-4-turbo",
    "openai/gpt-3.5-turbo",
    # Llama (Meta)
    "meta-llama/llama-3.3-70b-instruct",
    "meta-llama/llama-3.2-1b-instruct:free",
    "meta-llama/llama-3.1-8b-instruct",
    # Gemini (Google)
    "google/gemini-flash-1.5",
    "google/gemini-pro",
    "google/gemma-2-9b-it:free",
]


def render_mcq(question: dict, idx: int) -> None:
    """Render an MCQ question."""
    st.markdown(f"**{idx}. {question.get('question', '')}**")
    for opt in question.get("options", []):
        st.markdown(f"- {opt}")
    correct = question.get("correct", "")
    if correct:
        st.caption(f"Correct answer: {correct}")


def render_fill_blank(question: dict, idx: int) -> None:
    """Render a fill-in-the-blank question."""
    sentence = question.get("sentence", "")
    answer = question.get("answer", "")
    st.markdown(f"**{idx}. {sentence}**")
    if answer:
        with st.expander("View answer"):
            st.write(answer)


def render_short_answer(question: dict, idx: int) -> None:
    """Render a short answer question."""
    st.markdown(f"**{idx}. {question.get('question', '')}**")
    expected = question.get("expected_answer", "")
    if expected:
        with st.expander("Expected answer"):
            st.write(expected)


RENDERERS = {
    "mcq": render_mcq,
    "fill_blank": render_fill_blank,
    "short_answer": render_short_answer,
}


def main() -> None:
    st.set_page_config(
        page_title="Test Item Generator",
        page_icon="📝",
        layout="wide",
    )

    st.title("📝 Test Item Generator")
    st.markdown(
        "Upload a PDF, choose the question type, "
        "and generate MCQs, fill in the blanks, or short answers via OpenRouter."
    )

    # Sidebar - Configuration (API key, model, type)
    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input(
            "OpenRouter API Key",
            type="password",
            placeholder="sk-or-v1-...",
            help="Get a key at https://openrouter.ai/keys",
        )
        default_idx = next(
            (i for i, m in enumerate(MODELS) if m == DEFAULT_MODEL), 0
        )
        model = st.selectbox(
            "Model",
            options=MODELS,
            index=default_idx,
            help="Claude, OpenAI, Llama, Gemini models via OpenRouter",
        )
        question_type = st.selectbox(
            "Question type",
            options=list(QUESTION_TYPES.keys()),
            format_func=lambda k: QUESTION_TYPES[k],
        )

    # Upload PDF
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload a PDF to extract text and generate questions.",
    )

    if uploaded_file is None:
        st.info("👆 Upload a PDF to get started.")
        return

    pdf_content = uploaded_file.read()
    pdf_text = extract_text_from_pdf(pdf_content)

    if not pdf_text or len(pdf_text.strip()) < 50:
        st.warning(
            "Could not extract enough text from the PDF. "
            "Check that the file is not scanned (image) or empty."
        )
        return

    st.success(f"✅ Text extracted: {len(pdf_text)} characters")

    with st.expander("Preview extracted text"):
        st.text(pdf_text[:2000] + ("..." if len(pdf_text) > 2000 else ""))

    # Generate button
    effective_api_key = (api_key or "").strip() or OPENROUTER_API_KEY
    if st.button("🚀 Generate questions", type="primary"):
        if not effective_api_key:
            st.error("Enter your OpenRouter API key in the sidebar or in .env")
        else:
            with st.spinner("Generating..."):
                questions, error = generate_questions(
                    pdf_text=pdf_text,
                    question_type=question_type,
                    model=model,
                    api_key=effective_api_key,
                )

            if error:
                st.error(error)
            elif not questions:
                st.error("No questions generated. Try a different model or PDF.")
            else:
                st.session_state["questions"] = questions
                st.session_state["question_type"] = question_type
                st.rerun()

    # Affichage des questions avec expander (open/close) et téléchargement
    questions = st.session_state.get("questions", [])
    q_type = st.session_state.get("question_type", question_type)

    if questions:
        st.subheader(f"Generated questions ({len(questions)})")

        # Download buttons (PDF)
        col1, col2 = st.columns(2)
        with col1:
            qp_pdf = generate_question_paper_pdf(questions, q_type)
            st.download_button(
                "📄 Download question paper (PDF)",
                data=qp_pdf,
                file_name="question_paper.pdf",
                mime="application/pdf",
            )
        with col2:
            ans_pdf = generate_answers_pdf(questions, q_type)
            st.download_button(
                "📋 Download answers (PDF)",
                data=ans_pdf,
                file_name="answers.pdf",
                mime="application/pdf",
            )

        # Questions section - expandable (open/close)
        with st.expander("📝 View questions (expand / collapse)", expanded=True):
            renderer = RENDERERS.get(q_type, render_mcq)
            for i, q in enumerate(questions, 1):
                with st.container():
                    renderer(q, i)
                    st.divider()


if __name__ == "__main__":
    main()
