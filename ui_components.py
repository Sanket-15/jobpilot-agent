"""Small Streamlit UI helpers for JobPilot Agent."""

from __future__ import annotations

from html import escape
from typing import Iterable

import streamlit as st


def inject_global_styles() -> None:
    """Inject a contained modern Streamlit dashboard style."""

    st.markdown(
        """
        <style>
        :root {
            --jp-bg: #f5f7fb;
            --jp-card: #ffffff;
            --jp-border: #dbe4f0;
            --jp-text: #172033;
            --jp-muted: #64748b;
            --jp-primary: #1d4ed8;
            --jp-primary-soft: #dbeafe;
            --jp-accent: #0f766e;
            --jp-accent-soft: #ccfbf1;
            --jp-violet: #6d28d9;
            --jp-violet-soft: #ede9fe;
            --jp-warning: #b45309;
            --jp-warning-soft: #fef3c7;
            --jp-danger: #b91c1c;
            --jp-danger-soft: #fee2e2;
            --jp-success: #047857;
            --jp-success-soft: #d1fae5;
            --jp-shadow: 0 16px 42px rgba(15, 23, 42, 0.08);
        }

        .stApp {
            background:
                radial-gradient(circle at 12% 8%, rgba(29, 78, 216, 0.11), transparent 30%),
                radial-gradient(circle at 88% 4%, rgba(13, 148, 136, 0.11), transparent 34%),
                linear-gradient(180deg, #f8fbff 0%, var(--jp-bg) 48%, #eef4fb 100%);
            color: var(--jp-text);
            font-family: Inter, "Segoe UI", Roboto, Arial, sans-serif;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 4rem;
            max-width: 1420px;
        }

        h1, h2, h3 {
            color: var(--jp-text);
            letter-spacing: 0;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            border: 1px solid rgba(148, 163, 184, 0.36);
            border-radius: 18px;
            box-shadow: 0 12px 32px rgba(15, 23, 42, 0.06);
            background: rgba(255, 255, 255, 0.78);
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.45rem;
            background: rgba(255, 255, 255, 0.68);
            border: 1px solid rgba(148, 163, 184, 0.32);
            border-radius: 18px;
            padding: 0.45rem;
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 14px;
            padding: 0.6rem 0.95rem;
            font-weight: 650;
            color: #334155;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, var(--jp-primary), var(--jp-violet));
            color: #ffffff;
        }

        .stButton > button,
        .stDownloadButton > button {
            border-radius: 12px;
            border: 1px solid rgba(29, 78, 216, 0.2);
            font-weight: 700;
            box-shadow: 0 8px 20px rgba(29, 78, 216, 0.08);
        }

        .stTextArea textarea,
        .stTextInput input,
        .stSelectbox div[data-baseweb="select"] > div {
            border-radius: 12px;
        }

        [data-testid="stMetric"] {
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(248, 250, 252, 0.92));
            border: 1px solid rgba(148, 163, 184, 0.28);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
        }

        .jp-hero {
            padding: 2rem;
            border-radius: 28px;
            border: 1px solid rgba(148, 163, 184, 0.28);
            background:
                linear-gradient(135deg, rgba(29, 78, 216, 0.94), rgba(79, 70, 229, 0.88) 48%, rgba(15, 118, 110, 0.92)),
                radial-gradient(circle at 80% 0%, rgba(255, 255, 255, 0.28), transparent 28%);
            box-shadow: var(--jp-shadow);
            color: #ffffff;
            margin-bottom: 1.15rem;
        }

        .jp-hero h1 {
            color: #ffffff;
            margin: 0 0 0.35rem 0;
            font-size: 2.45rem;
            line-height: 1.1;
        }

        .jp-hero p {
            color: rgba(255, 255, 255, 0.88);
            font-size: 1.06rem;
            margin: 0.2rem 0 1rem 0;
        }

        .jp-badge-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.8rem;
        }

        .jp-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.28rem 0.62rem;
            border-radius: 999px;
            border: 1px solid rgba(148, 163, 184, 0.28);
            background: #f8fafc;
            color: #334155;
            font-weight: 700;
            font-size: 0.82rem;
            margin: 0.12rem 0.2rem 0.12rem 0;
        }

        .jp-badge-info { background: var(--jp-primary-soft); color: #1e40af; }
        .jp-badge-success { background: var(--jp-success-soft); color: var(--jp-success); }
        .jp-badge-warning { background: var(--jp-warning-soft); color: var(--jp-warning); }
        .jp-badge-danger { background: var(--jp-danger-soft); color: var(--jp-danger); }
        .jp-badge-violet { background: var(--jp-violet-soft); color: var(--jp-violet); }

        .jp-card,
        .jp-callout {
            border-radius: 20px;
            border: 1px solid rgba(148, 163, 184, 0.28);
            background: rgba(255, 255, 255, 0.84);
            box-shadow: 0 12px 32px rgba(15, 23, 42, 0.06);
            padding: 1.05rem 1.15rem;
            margin: 0.85rem 0;
        }

        .jp-card h3,
        .jp-callout h3 {
            margin: 0 0 0.35rem 0;
            font-size: 1.05rem;
        }

        .jp-muted {
            color: var(--jp-muted);
            font-size: 0.94rem;
        }

        .jp-section {
            margin: 1.2rem 0 0.65rem 0;
        }

        .jp-section h2 {
            font-size: 1.35rem;
            margin-bottom: 0.15rem;
        }

        .jp-step {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 2rem;
            height: 2rem;
            border-radius: 999px;
            background: linear-gradient(135deg, var(--jp-primary), var(--jp-violet));
            color: #ffffff;
            font-weight: 800;
            margin-right: 0.55rem;
        }

        .jp-callout-info { background: linear-gradient(135deg, #eff6ff, #ecfeff); border-color: #bfdbfe; }
        .jp-callout-warning { background: linear-gradient(135deg, #fffbeb, #fff7ed); border-color: #fde68a; }
        .jp-callout-success { background: linear-gradient(135deg, #ecfdf5, #f0fdfa); border-color: #a7f3d0; }
        .jp-callout-danger { background: linear-gradient(135deg, #fef2f2, #fff1f2); border-color: #fecaca; }

        .jp-divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(148, 163, 184, 0.55), transparent);
            margin: 1.25rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero_header() -> None:
    """Render the polished top-level app hero."""

    st.markdown(
        """
        <div class="jp-hero">
            <h1>JobPilot Agent</h1>
            <p>AI-assisted job search workflow from profile to application log.</p>
            <div class="jp-badge-row">
                <span class="jp-badge">Bilingual</span>
                <span class="jp-badge">Local-first</span>
                <span class="jp-badge">Human-reviewed</span>
                <span class="jp-badge">No auto-apply</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_safety_banner() -> None:
    """Render the core safety banner."""

    render_warning_box(
        "JobPilot prepares application materials. You review and submit manually. "
        "Do not use generated claims unless they reflect real experience."
    )


def render_feature_badges(items: Iterable[str], variant: str = "info") -> None:
    """Render a row of small badges."""

    badges = "".join(render_status_badge(item, variant=variant, return_html=True) for item in items)
    st.markdown(f"<div class=\"jp-badge-row\">{badges}</div>", unsafe_allow_html=True)


def render_section_header(title: str, subtitle: str | None = None, icon: str | None = None) -> None:
    """Render a modern section header."""

    icon_html = f"{escape(icon)} " if icon else ""
    subtitle_html = f"<div class=\"jp-muted\">{escape(subtitle)}</div>" if subtitle else ""
    st.markdown(
        f"""
        <div class="jp-section">
            <h2>{icon_html}{escape(title)}</h2>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_title(title: str, caption: str = "") -> None:
    """Backward-compatible section title helper."""

    render_section_header(title, caption or None)


def render_card(title: str, body: str | None = None, icon: str | None = None) -> None:
    """Render a simple informational card."""

    icon_html = f"{escape(icon)} " if icon else ""
    body_html = f"<p class=\"jp-muted\">{escape(body)}</p>" if body else ""
    st.markdown(
        f"""
        <div class="jp-card">
            <h3>{icon_html}{escape(title)}</h3>
            {body_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: int | str | None, helper: str | None = None) -> None:
    """Render a polished metric using Streamlit's native metric plus helper text."""

    display_value = "Not scored" if value in (None, "") else str(value)
    if isinstance(value, int):
        display_value = f"{value}/100"
    st.metric(label, display_value)
    if helper:
        st.caption(helper)


def render_score_metric(label: str, value: int | str | None, confidence: str | None = None) -> None:
    """Render a score metric with optional confidence text."""

    render_metric_card(label, value, f"Confidence: {confidence}" if confidence else None)


def render_status_badge(label: str, variant: str = "neutral", return_html: bool = False) -> str | None:
    """Render a status badge or return its HTML."""

    class_map = {
        "success": "jp-badge-success",
        "warning": "jp-badge-warning",
        "danger": "jp-badge-danger",
        "info": "jp-badge-info",
        "violet": "jp-badge-violet",
        "neutral": "",
    }
    html = f"<span class=\"jp-badge {class_map.get(variant, '')}\">{escape(str(label))}</span>"
    if return_html:
        return html
    st.markdown(html, unsafe_allow_html=True)
    return None


def render_score_badge(score: int | None, confidence: str | None = None) -> None:
    """Render a score as a colored badge."""

    if score is None:
        render_status_badge("Not scored", "neutral")
        return
    if score >= 75:
        variant = "success"
    elif score >= 50:
        variant = "warning"
    else:
        variant = "danger"
    label = f"{score}/100" + (f" · {confidence}" if confidence else "")
    render_status_badge(label, variant)


def render_warning_box(message: str) -> None:
    """Render a polished warning callout."""

    _render_callout(message, "warning")


def render_info_box(message: str) -> None:
    """Render a polished info callout."""

    _render_callout(message, "info")


def render_success_box(message: str) -> None:
    """Render a polished success callout."""

    _render_callout(message, "success")


def render_list_card(title: str, items: list[str], empty_text: str = "No items provided.") -> None:
    """Render a list inside a card-like expander-friendly block."""

    body = items or [empty_text]
    rendered_items = "".join(f"<li>{escape(str(item))}</li>" for item in body)
    st.markdown(
        f"""
        <div class="jp-card">
            <h3>{escape(title)}</h3>
            <ul>{rendered_items}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_text_panel(title: str, text: str) -> None:
    """Render a readable title before copy-friendly text."""

    render_card(title)
    render_copy_friendly_text(title, text)


def render_copy_friendly_text(label: str, text: str, height: int = 260) -> None:
    """Render copy-friendly long text in a text area."""

    st.text_area(
        label=label,
        value=text or "Not provided.",
        height=height,
    )


def render_step_header(step_number: int, title: str, caption: str | None = None) -> None:
    """Render a numbered step header."""

    caption_html = f"<div class=\"jp-muted\">{escape(caption)}</div>" if caption else ""
    st.markdown(
        f"""
        <div class="jp-section">
            <h2><span class="jp-step">{step_number}</span>{escape(title)}</h2>
            {caption_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_callout(message: str, variant: str) -> None:
    """Render a callout with a variant class."""

    st.markdown(
        f"""
        <div class="jp-callout jp-callout-{variant}">
            {escape(message)}
        </div>
        """,
        unsafe_allow_html=True,
    )
