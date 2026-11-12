from __future__ import annotations

import json
import os

import pandas as pd
import streamlit as st

from src.agents.learning import LearningAgent
from src.runner import run_all_agents, simulate_learning_feedback
from src.world import CloudWorld

st.set_page_config(
    page_title="Cloud Resource and Cost Optimization Advisor",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Cloud Resource and Cost Optimization Advisor")
st.caption(
    "Six agents, one scenario, side-by-side. All data is simulated. "
    "Agents only recommend; nothing changes any cloud resource."
)

world = CloudWorld()
scenarios = world.list_scenarios()
labels = {
    f"{s['id']}: {s['description'][:48]}{'...' if len(s['description']) > 48 else ''}": s["id"]
    for s in scenarios
}

with st.sidebar:
    st.header("Controls")
    selected_label = st.selectbox("Select scenario", list(labels))
    scenario_id = labels[selected_label]

    st.subheader("Utility agent weights")
    cost_w = st.slider("Cost", 0.0, 1.0, 0.40, 0.05)
    perf_w = st.slider("Performance", 0.0, 1.0, 0.40, 0.05)
    avail_w = st.slider("Availability", 0.0, 1.0, 0.20, 0.05)

    st.subheader("LLM agent (Ollama)")
    llm_model = st.text_input("Model", value=os.getenv("OLLAMA_MODEL", "qwen3:latest"))
    llm_host = st.text_input("Host", value=os.getenv("OLLAMA_HOST", "http://localhost:11434"))
    include_llm = st.checkbox("Include LLM agent", value=True)
    run_clicked = st.button("Run all agents", type="primary", use_container_width=True)

scenario = world.get_scenario(scenario_id)
percept = world.perceive(scenario_id)
kpis = percept["kpis"]
series = percept["timeseries"]

st.markdown(f"### Scenario {scenario_id}: {scenario['description']}")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Instance", kpis["instance"])
m2.metric("Monthly cost", f"${kpis['monthly_cost_usd']:.0f}")
m3.metric(
    "CPU now",
    f"{kpis['cpu_now_pct']:.1f}%",
    help=f"avg {kpis['cpu_avg_6h_pct']}% | limit {kpis['cpu_limit_pct']}%",
)
m4.metric(
    "Response now",
    f"{kpis['response_now_ms']:.0f} ms",
    help=f"p95 {kpis['p95_response_ms']} | target {kpis['response_target_ms']}",
)
m5.metric(
    "Availability",
    f"{kpis['availability_pct']:.2f}%",
    help=f"target {kpis['availability_target_pct']}%",
)
st.caption(
    f"CPU avg {kpis['cpu_avg_6h_pct']}% over last 6h · limit {kpis['cpu_limit_pct']}% · "
    f"p95 {kpis['p95_response_ms']} ms · target {kpis['response_target_ms']} ms · "
    f"availability target {kpis['availability_target_pct']}%"
)

c1, c2 = st.columns(2)
with c1:
    st.markdown("**CPU % over 24 hours**")
    cpu_df = pd.DataFrame({"hour": series["hour"], "CPU %": series["cpu_pct"]}).set_index("hour")
    st.line_chart(cpu_df, height=260)
with c2:
    st.markdown(f"**Response time (ms) over 24 hours (target {kpis['response_target_ms']} ms)**")
    rt_df = pd.DataFrame(
        {
            "hour": series["hour"],
            "Response ms": series["response_ms"],
            "Target": [kpis["response_target_ms"]] * len(series["hour"]),
        }
    ).set_index("hour")
    st.line_chart(rt_df, height=260)

if "learning_agent" not in st.session_state:
    st.session_state.learning_agent = LearningAgent()

weights = {"cost": cost_w, "performance": perf_w, "availability": avail_w}

if run_clicked:
    st.session_state.learning_agent = LearningAgent(
        cost_weight=cost_w,
        performance_weight=perf_w,
        availability_weight=avail_w,
    )
    with st.spinner("Running six agents on the same scenario percept..."):
        payload = run_all_agents(
            scenario_id,
            include_llm=include_llm,
            learning_agent=st.session_state.learning_agent,
            utility_weights=weights,
            llm_model=llm_model,
            llm_host=llm_host,
        )
    st.session_state.last_run = payload

if "last_run" in st.session_state:
    payload = st.session_state.last_run
    st.divider()
    st.subheader("Agent decisions")
    st.dataframe(
        pd.DataFrame(payload["comparison"])[["agent", "display", "recommendation"]],
        use_container_width=True,
        hide_index=True,
    )
    st.info(payload["why_decisions_differ"])

    for result in payload["results"]:
        title = result.get("display_recommendation") or result.get("recommendation")
        with st.expander(f"{result['agent']}: {title}", expanded=True):
            st.markdown(f"**Current state:** {result.get('current_state_summary', '')}")
            st.markdown(f"**Reasoning:** {result.get('reasoning', '')}")
            st.markdown(f"**Trade-offs:** {result.get('trade_offs', '')}")
            st.markdown(f"**Monitoring plan:** {result.get('monitoring_plan', '')}")
            if result.get("utility_ranking"):
                st.markdown("**Utility ranking**")
                st.dataframe(
                    pd.DataFrame(
                        result["utility_ranking"], columns=["action", "utility"]
                    ),
                    hide_index=True,
                    use_container_width=True,
                )
            if result.get("learning_stats"):
                st.markdown("**Learning stats**")
                st.dataframe(pd.DataFrame(result["learning_stats"]).T, use_container_width=True)
            if result.get("tool_trace"):
                st.markdown("**Tool evidence**")
                st.json(result["tool_trace"])
            if result.get("limitations"):
                st.warning(result["limitations"])

    st.divider()
    st.subheader("Update Learning Agent experience")
    lc1, lc2, lc3 = st.columns([2, 1, 2])
    with lc1:
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
    with lc2:
        success = st.checkbox("Mark as success", value=True)
    with lc3:
        notes = st.text_input("Notes", value=f"Feedback for scenario {scenario_id}")
    if st.button("Record learning outcome"):
        update = simulate_learning_feedback(
            st.session_state.learning_agent,
            scenario_id,
            action,
            success,
            notes,
        )
        st.success(update)

    st.download_button(
        "Download run JSON",
        data=json.dumps(payload, indent=2),
        file_name=f"scenario_{scenario_id}_results.json",
        mime="application/json",
    )
else:
    st.info("Set sidebar options, then click **Run all agents** to compare decisions.")
