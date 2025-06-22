import streamlit as st

def render_sources(sources):
    if not sources:
        return
    st.markdown("**Sources used:**")
    for src in sources:
        highlight = src.get("highlight", False)
        name = src.get("metadata", {}).get("source", "[chunk]")
        sim = src.get("similarity", 0.0)
        if highlight:
            st.markdown(f"- 🟢 **{name}** (sim: {sim:.2f})")
        else:
            st.markdown(f"- {name} (sim: {sim:.2f})")

def render_grounding_score(score):
    st.markdown(f"**Grounding Score:** ")
    st.progress(score if score <= 1 else 1)
    if score >= 0.75:
        st.success(f"{score:.2f} (Well grounded)")
    elif score >= 0.5:
        st.warning(f"{score:.2f} (Somewhat grounded)")
    else:
        st.error(f"{score:.2f} (Low grounding)")

def render_latency(latency):
    st.caption(f"⏱️ Latency: {latency}") 