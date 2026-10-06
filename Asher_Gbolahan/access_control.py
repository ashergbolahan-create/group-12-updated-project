"""Local-only use by default; verified, allowlisted OIDC users for sharing."""
import os
import streamlit as st


def require_access() -> None:
    required = os.getenv("AUTH_REQUIRED", "false").strip().lower() == "true"
    address = st.get_option("server.address")
    if not required:
        if address not in {"127.0.0.1", "localhost", "::1"}:
            st.error("Shared access requires sign-in. Configure authentication and set AUTH_REQUIRED=true, or run on localhost.")
            st.stop()
        return
    allowed = {email.strip().lower() for email in os.getenv("ALLOWED_EMAILS", "").split(",") if email.strip()}
    if not allowed:
        st.error("Set ALLOWED_EMAILS before enabling shared access.")
        st.stop()
    try:
        auth = st.secrets["auth"]
        if not all(auth.get(key) for key in ("redirect_uri", "cookie_secret", "client_id", "client_secret", "server_metadata_url")):
            raise ValueError("Incomplete authentication configuration")
    except (FileNotFoundError, KeyError, ValueError):
        st.error("Complete .streamlit/secrets.toml using secrets.toml.example to enable Google sign-in.")
        st.stop()
    if not st.user.is_logged_in:
        st.title("Sign in to the student register")
        if st.button("Sign in with Google"):
            st.login()
        st.stop()
    email = str(st.user.get("email", "")).lower()
    if st.user.get("email_verified") is not True or email not in allowed:
        st.error("This account does not have access to the student register.")
        if st.button("Sign out"):
            st.logout()
        st.stop()
    with st.sidebar:
        st.caption(f"Signed in as {email}")
        if st.button("Sign out"):
            st.logout()
