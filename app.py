from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from src.agents.learning import LearningAgent
from src.runner import run_all_agents, simulate_learning_feedback
from src.world import CloudWorld

st.set_page_config(page_title="Cloud Resource Advisor", layout="wide")
st.title("Cloud Resource and Cost Optimization Advisor")
st.caption(
    "BITS PGAIML · PCAM ZG519 Agentic AI · Assignment-1 · Group 11 — "
    "compare five classical agents and one local Ollama LLM agent on shared scenarios."
)

world = CloudWorld()
scenarios = world.list_scenarios()
labels = {f"{s['id']}: {s['name']} ({s['kind']})": s["id"] for s in scenarios}

selected_label = st.selectbox("Scenario", list(labels))
scenario_id = labels[selected_label]
scenario = world.get_scenario(scenario_id)

col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("Scenario")
    st.write(scenario["description"])
    st.json(scenario["metrics"])
with col2:
    st.subheader("SLA targets")
    st.json(world.perceive(scenario_id)["sla"])

include_llm = st.checkbox("Include LLM agent (Ollama)", value=True)
run_clicked = st.button("Run all agents", type="primary")

if "learning_agent" not in st.session_state:
    st.session_state.learning_agent = LearningAgent()

if run_clicked:
    with st.spinner("Running agents..."):
        payload = run_all_agents(
            scenario_id,
            include_llm=include_llm,
            learning_agent=st.session_state.learning_agent,
        )
    st.session_state.last_run = payload

if "last_run" in st.session_state:
    payload = st.session_state.last_run
    st.subheader("Comparison")
    df = pd.DataFrame(payload["comparison"])
    st.dataframe(df, use_container_width=True)

    for result in payload["results"]:
        with st.expander(f"{result['agent']} → {result['recommendation']}", expanded=False):
            st.markdown(f"**Reasoning:** {result.get('reasoning', '')}")
            st.markdown(f"**Current state:** {result.get('current_state_summary', '')}")
            st.markdown(f"**Trade-offs:** {result.get('trade_offs', '')}")
            st.markdown(f"**Monitoring plan:** {result.get('monitoring_plan', '')}")
            if result.get("tool_trace"):
                st.markdown("**Tool evidence**")
                st.json(result["tool_trace"])
            if result.get("learning_stats"):
                st.markdown("**Learning stats**")
                st.json(result["learning_stats"])
            if result.get("limitations"):
                st.info(result["limitations"])

    st.subheader("Update Learning Agent experience")
    action = st.selectbox(
        "Action outcome to record",
        [
            "keep_current",
            "scale_up",
            "scale_down",
            "enable_autoscaling",
            "rightsize_compute",
        ],
    )
    success = st.checkbox("Mark as success", value=True)
    notes = st.text_input("Notes", value=f"Feedback for scenario {scenario_id}")
    if st.button("Record learning outcome"):
        update = simulate_learning_feedback(
            st.session_state.learning_agent,
            scenario_id,
            action,
            success,
            notes,
        )
        st.success(f"Updated {update}")

    st.download_button(
        "Download run JSON",
        data=json.dumps(payload, indent=2),
        file_name=f"scenario_{scenario_id}_results.json",
        mime="application/json",
    )
