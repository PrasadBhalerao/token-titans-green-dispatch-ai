from __future__ import annotations

import json
from datetime import time
from typing import Any

import pandas as pd
import streamlit as st

from src.agents.orchestrator import apply_approval_decision, run_dispatch_workflow
from src.core.constraints import validate_routes
from src.core.data_loader import DispatchDataset
from src.core.metrics import compare_scenarios
from src.core.plan_store import save_run_artifact
from src.core.scenario_store import create_scenario_id, list_user_scenarios, load_user_scenario, save_user_scenario

try:
    import plotly.express as px
except ImportError:  # pragma: no cover - fallback only when optional UI dep is absent
    px = None


def render_dashboard(dataset: DispatchDataset) -> None:
    _inject_css()
    _ensure_editable_inputs(dataset)
    _ensure_workflow(dataset)

    st.title("GreenDispatch AI")
    st.caption("Agentic carbon-aware scheduling and dispatch optimizer")
    st.info(
        "Synthetic hackathon dataset only. No customer, confidential, personal, or client-branded data is used."
    )

    _render_sidebar(dataset)
    workflow = st.session_state["workflow"]
    active_scenario = st.session_state.get("active_scenario", _default_scenario_id(dataset))
    active_comparison = _comparison_for_active_scenario(workflow, active_scenario)
    optimization_scenario = _optimization_tab_scenario(active_scenario)
    optimization_comparison = _comparison_for_active_scenario(workflow, optimization_scenario)
    _render_headline_kpis(active_comparison, active_scenario)

    tabs = st.tabs(
        [
            "Baseline",
            "Optimized",
            "Agents",
            "Disruption",
            "Sustainability",
            "Summary",
            "Scenario Inputs",
        ]
    )
    with tabs[0]:
        _render_plan_tab(dataset, workflow, "baseline", "Manual Baseline Dispatch Plan")
    with tabs[1]:
        _render_optimized_tab(dataset, workflow, optimization_scenario, optimization_comparison)
    with tabs[2]:
        _render_agent_tab(workflow)
    with tabs[3]:
        _render_disruption_tab(dataset, workflow)
    with tabs[4]:
        _render_sustainability_tab(workflow)
    with tabs[5]:
        _render_summary_tab(workflow)
    with tabs[6]:
        _render_scenario_inputs(dataset)


def _ensure_workflow(dataset: DispatchDataset) -> None:
    if "selected_scenario" not in st.session_state:
        st.session_state["selected_scenario"] = _default_scenario_id(dataset)
    if "active_scenario" not in st.session_state:
        st.session_state["active_scenario"] = st.session_state["selected_scenario"]
    if "workflow" not in st.session_state:
        _refresh_workflow(dataset)
    if "show_disruption" not in st.session_state:
        st.session_state["show_disruption"] = False


def _ensure_editable_inputs(dataset: DispatchDataset) -> None:
    if "editable_jobs_df" not in st.session_state:
        st.session_state["editable_jobs_df"] = dataset.table("jobs")
    if "editable_vehicles_df" not in st.session_state:
        st.session_state["editable_vehicles_df"] = dataset.table("vehicles")
    if "editable_inputs_revision" not in st.session_state:
        st.session_state["editable_inputs_revision"] = 0


def _refresh_workflow(
    dataset: DispatchDataset,
    optimization_objective: str | None = None,
    use_live_llm: bool = False,
) -> None:
    objective = optimization_objective or st.session_state.get("selected_scenario", "optimized")
    st.session_state["workflow"] = run_dispatch_workflow(
        dataset,
        edited_jobs=st.session_state.get("editable_jobs_df", dataset.table("jobs")),
        edited_vehicles=st.session_state.get("editable_vehicles_df", dataset.table("vehicles")),
        persist=True,
        optimization_objective=objective,
        use_live_llm=use_live_llm,
    )


def _render_sidebar(dataset: DispatchDataset) -> None:
    with st.sidebar:
        st.header("Scenario")
        scenario_items = dataset.scenarios.get("scenarios", [])
        scenario_labels = {
            item["id"]: item["label"]
            for item in scenario_items
            if item["id"] != "reoptimized"
        }
        scenario_ids = list(scenario_labels)
        current_scenario = st.session_state.get("selected_scenario", _default_scenario_id(dataset))
        if current_scenario not in scenario_ids:
            current_scenario = _default_scenario_id(dataset)
        selected = st.selectbox(
            "Plan scenario",
            scenario_ids,
            index=scenario_ids.index(current_scenario),
            format_func=lambda value: scenario_labels[value],
        )
        st.session_state["selected_scenario"] = selected
        if st.button("Run optimization", use_container_width=True):
            _refresh_workflow(
                dataset,
                optimization_objective=selected,
                use_live_llm=selected != "baseline",
            )
            st.session_state["active_scenario"] = selected
            st.session_state["show_disruption"] = False
            st.success(_run_message(selected))

        st.divider()
        st.subheader("Loaded data")
        counts = dataset.row_counts()
        st.dataframe(
            pd.DataFrame(
                [{"table": table, "rows": rows} for table, rows in counts.items()]
            ),
            hide_index=True,
            use_container_width=True,
        )


def _render_headline_kpis(comparison: pd.DataFrame, active_scenario: str) -> None:
    st.caption(f"Active result: {_scenario_display_name(active_scenario)}")
    lookup = comparison.set_index("metric").to_dict(orient="index")
    cols = st.columns(5)
    values = [
        ("Trips consolidated", lookup["trips"], "count", "leaf"),
        ("Distance avoided", lookup["distance"], "km", "teal"),
        ("Fuel saved", lookup["fuel"], "L", "amber"),
        ("CO2e avoided", lookup["co2e"], "kg", "emerald"),
        ("Idle time reduced", lookup["idle_time"], "min", "sky"),
    ]
    for col, (label, metric, unit, tone) in zip(cols, values):
        with col:
            _metric_card(
                label,
                f"{metric['absolute_reduction']:.2f} {unit}",
                f"{metric['reduction_pct']:.1f}% reduction",
                tone,
            )


def _render_plan_tab(dataset: DispatchDataset, workflow: dict[str, Any], scenario: str, title: str) -> None:
    st.subheader(title)
    metrics = _workflow_scenario_metrics(workflow, scenario)
    cols = st.columns(4)
    with cols[0]:
        _metric_card("Trips", str(int(metrics["trips"])), "planned routes", "leaf")
    with cols[1]:
        _metric_card("Distance", f"{metrics['total_distance_km']:.2f} km", "total route distance", "teal")
    with cols[2]:
        _metric_card("Fuel", f"{metrics['total_fuel_liters']:.2f} L", "liquid fuel use", "amber")
    with cols[3]:
        _metric_card("CO2e", f"{metrics['total_co2e_kg']:.2f} kg", "estimated emissions", "emerald")
    cols = st.columns(4)
    with cols[0]:
        _metric_card("Idle time", f"{metrics['total_idle_minutes']:.0f} min", "vehicle waiting time", "sky")
    with cols[1]:
        _metric_card("SLA adherence", f"{metrics['sla_adherence_pct']:.1f}%", "jobs within window", "mint")
    with cols[2]:
        _metric_card("Avg utilization", f"{metrics['avg_capacity_utilization_pct']:.1f}%", "capacity used", "olive")
    with cols[3]:
        _metric_card("Cost index", f"{metrics['operating_cost_index']:.2f}", "operational proxy", "slate")

    st.markdown("#### Route plan")
    st.dataframe(_routes_for_display(dataset, scenario, workflow), hide_index=True, use_container_width=True)

    st.markdown("#### Job assignments")
    st.dataframe(_assignments_for_display(dataset, scenario, workflow), hide_index=True, use_container_width=True)

    st.markdown("#### Assumptions")
    _render_assumptions(workflow)


def _render_optimized_tab(
    dataset: DispatchDataset,
    workflow: dict[str, Any],
    scenario: str,
    comparison: pd.DataFrame,
) -> None:
    st.subheader(_scenario_display_name(scenario))
    _render_scenario_mode_note(scenario)
    _render_comparison_chart(comparison, _scenario_display_name(scenario))
    _render_plan_tab(dataset, workflow, scenario, "Route details")

    st.markdown("#### Constraint validation")
    st.dataframe(_constraints_for_scenario(workflow, scenario), hide_index=True, use_container_width=True)

    st.markdown("#### Human approval")
    st.caption("Agents recommend. Humans approve before the dispatch decision is finalized.")
    current_status = workflow["decision_summary"]["approval_status"]
    st.markdown(f"<span class='status-chip'>{current_status}</span>", unsafe_allow_html=True)
    note = st.text_input("Approval note", value="Reviewed during hackathon demo.")
    cols = st.columns(3)
    if cols[0].button("Approve", use_container_width=True):
        _apply_decision("approved", note)
    if cols[1].button("Reject", use_container_width=True):
        _apply_decision("rejected", note)
    if cols[2].button("Request revision", use_container_width=True):
        _apply_decision("revision_requested", note)


def _render_agent_tab(workflow: dict[str, Any]) -> None:
    st.subheader("Agent Workflow Trace")
    st.dataframe(pd.DataFrame(workflow["trace"]), hide_index=True, use_container_width=True)
    st.caption("Trace rows are structured JSON-serializable records saved with every run.")


def _render_disruption_tab(dataset: DispatchDataset, workflow: dict[str, Any]) -> None:
    st.subheader("Dynamic Disruption And Re-Optimization")
    event = workflow["disruption_event"]
    st.json(event)
    if st.button("Trigger disruption", use_container_width=True):
        st.session_state["show_disruption"] = True
    if st.session_state.get("show_disruption"):
        st.markdown("#### Reoptimized plan")
        st.dataframe(_routes_for_display(dataset, "reoptimized", workflow), hide_index=True, use_container_width=True)
        st.markdown("#### Reoptimized constraint validation")
        st.dataframe(workflow["reoptimized_constraints"], hide_index=True, use_container_width=True)
        optimized = _workflow_scenario_metrics(workflow, "optimized")
        reoptimized = _workflow_scenario_metrics(workflow, "reoptimized")
        delta = {
            "distance_delta_km": round(reoptimized["total_distance_km"] - optimized["total_distance_km"], 2),
            "fuel_delta_liters": round(reoptimized["total_fuel_liters"] - optimized["total_fuel_liters"], 2),
            "co2e_delta_kg": round(reoptimized["total_co2e_kg"] - optimized["total_co2e_kg"], 2),
        }
        st.markdown("#### Optimized vs reoptimized delta")
        st.json(delta)


def _render_sustainability_tab(workflow: dict[str, Any]) -> None:
    st.subheader("Agent Sustainability")
    metrics = workflow["agent_sustainability"]
    cols = st.columns(4)
    cols[0].metric("Execution mode", metrics["execution_mode"])
    cols[1].metric("LLM status", metrics["llm_status"])
    cols[2].metric("Model calls", metrics["model_calls"])
    cols[3].metric("Retries", metrics["retries"])
    cols = st.columns(4)
    cols[0].metric("Input tokens", metrics["input_tokens"])
    cols[1].metric("Output tokens", metrics["output_tokens"])
    cols[2].metric("Total tokens", metrics["total_tokens"])
    cols[3].metric("Model", metrics["model"])
    cols = st.columns(4)
    cols[0].metric("Tool calls", metrics["tool_calls"])
    cols[1].metric("Deterministic calculators", metrics["deterministic_calculators_used"])
    cols[2].metric("CO2e/model call", f"{metrics['co2e_avoided_per_model_call_kg']:.2f} kg")
    cols[3].metric("Distance/model call", f"{metrics['distance_avoided_per_model_call_km']:.2f} km")
    st.info(metrics["explanation"])
    if metrics.get("fallback_reason"):
        st.warning(metrics["fallback_reason"])
    if workflow.get("llm_optimizer_result", {}).get("risks_or_tradeoffs"):
        st.markdown("#### LLM identified tradeoffs")
        st.write(workflow["llm_optimizer_result"]["risks_or_tradeoffs"])


def _render_summary_tab(workflow: dict[str, Any]) -> None:
    st.subheader("Decision Summary")
    summary = workflow["decision_summary"]
    st.markdown(summary["recommendation"])
    st.json(summary["headline"])
    st.markdown("#### Approval audit")
    st.dataframe(pd.DataFrame(workflow["approval_audit"]), hide_index=True, use_container_width=True)
    st.download_button(
        "Download decision summary JSON",
        data=json.dumps(summary, indent=2),
        file_name="decision_summary.json",
        mime="application/json",
        use_container_width=True,
    )


def _render_scenario_inputs(dataset: DispatchDataset) -> None:
    st.subheader("Editable Scenario Inputs")
    st.caption("Use this to capture user-edited demo scenarios without overwriting source data.")
    st.info("The Add workload form refreshes optimization automatically. After editing table cells directly, click Run optimization in the sidebar.")
    if "scenario_input_message" in st.session_state:
        st.success(st.session_state.pop("scenario_input_message"))

    saved_scenarios = list_user_scenarios()
    if saved_scenarios:
        selected_scenario = st.selectbox("Load saved edited scenario", saved_scenarios)
        if st.button("Preview saved scenario JSON", use_container_width=True):
            st.json(load_user_scenario(selected_scenario))

    st.markdown("#### Editable jobs")
    jobs = st.data_editor(
        st.session_state["editable_jobs_df"],
        hide_index=True,
        use_container_width=True,
        num_rows="dynamic",
        key=f"edited_jobs_table_{st.session_state['editable_inputs_revision']}",
    )
    st.session_state["editable_jobs_df"] = jobs

    st.markdown("#### Editable vehicles")
    vehicles = st.data_editor(
        st.session_state["editable_vehicles_df"],
        hide_index=True,
        use_container_width=True,
        key=f"edited_vehicles_table_{st.session_state['editable_inputs_revision']}",
    )
    st.session_state["editable_vehicles_df"] = vehicles

    with st.form("add_job_form"):
        st.markdown("#### Add workload request")
        cols = st.columns(4)
        job_id = cols[0].text_input("Job ID", value="J_NEW")
        destination_options = dataset.table("locations")
        destination_options = destination_options[destination_options["location_type"] != "depot"]
        destination_id = cols[1].selectbox("Destination", destination_options["location_id"].tolist())
        demand_kg = cols[2].number_input("Demand kg", min_value=0, value=100)
        volume_m3 = cols[3].number_input("Volume m3", min_value=0.0, value=1.0)
        cols = st.columns(4)
        priority = cols[0].selectbox("Priority", ["normal", "high", "urgent"])
        ready_time = cols[1].time_input("Ready time", value=time(9, 0))
        due_time = cols[2].time_input("Due time", value=time(17, 0))
        service_minutes = cols[3].number_input("Service minutes", min_value=1, value=15)
        submitted = st.form_submit_button("Add job to edited scenario")
        if submitted:
            new_job = {
                "job_id": job_id,
                "destination_id": destination_id,
                "job_type": "delivery",
                "demand_kg": demand_kg,
                "volume_m3": volume_m3,
                "priority": priority,
                "ready_time": ready_time.strftime("%H:%M"),
                "due_time": due_time.strftime("%H:%M"),
                "service_minutes": service_minutes,
            }
            existing_ids = set(st.session_state["editable_jobs_df"]["job_id"].astype(str))
            if job_id in existing_ids:
                st.error(f"Job ID {job_id} already exists. Use a unique ID.")
            else:
                st.session_state["editable_jobs_df"] = pd.concat(
                    [st.session_state["editable_jobs_df"], pd.DataFrame([new_job])],
                    ignore_index=True,
                )
                st.session_state["editable_inputs_revision"] += 1
                _refresh_workflow(dataset)
                st.session_state["scenario_input_message"] = f"Added {job_id}. Optimized plan and metrics have been refreshed."
                _rerun()

    if st.button("Reset editable inputs", use_container_width=True):
        st.session_state["editable_jobs_df"] = dataset.table("jobs")
        st.session_state["editable_vehicles_df"] = dataset.table("vehicles")
        st.session_state["editable_inputs_revision"] += 1
        _refresh_workflow(dataset)
        st.session_state["scenario_input_message"] = "Editable inputs reset to source demo data."
        _rerun()

    if st.button("Save edited scenario JSON", use_container_width=True):
        scenario_id = create_scenario_id("user_edit")
        payload = {
            "scenario_id": scenario_id,
            "source": "Streamlit user edit",
            "jobs": st.session_state["editable_jobs_df"].to_dict(orient="records"),
            "vehicles": st.session_state["editable_vehicles_df"].to_dict(orient="records"),
        }
        path = save_user_scenario(scenario_id, payload)
        st.success(f"Saved {path.name}")


def _routes_for_display(dataset: DispatchDataset, scenario: str, workflow: dict[str, Any]) -> pd.DataFrame:
    routes = workflow["routes"]
    routes = routes[routes["scenario"] == scenario].copy()
    vehicles = workflow["vehicles"][["vehicle_id", "vehicle_name", "energy_type"]]
    return routes.merge(vehicles, on="vehicle_id", how="left")


def _assignments_for_display(dataset: DispatchDataset, scenario: str, workflow: dict[str, Any]) -> pd.DataFrame:
    assignments = workflow["assignments"]
    assignments = assignments[assignments["scenario"] == scenario].copy()
    jobs = workflow["jobs"]
    locations = dataset.table("locations")[["location_id", "name", "zone"]]
    return assignments.merge(jobs, on=["job_id", "destination_id"], how="left").merge(
        locations,
        left_on="destination_id",
        right_on="location_id",
        how="left",
    )


def _render_comparison_chart(comparison: pd.DataFrame, target_label: str) -> None:
    chart_data = comparison[comparison["metric"].isin(["distance", "fuel", "co2e", "idle_time", "planning_time"])].copy()
    if px is None:
        st.dataframe(chart_data, hide_index=True, use_container_width=True)
        return
    melted = chart_data.melt(
        id_vars=["metric", "unit"],
        value_vars=["baseline", "optimized"],
        var_name="plan",
        value_name="value",
    )
    melted["plan"] = melted["plan"].map(
        {
            "baseline": "Manual baseline",
            "optimized": target_label,
        }
    )
    fig = px.bar(melted, x="metric", y="value", color="plan", barmode="group", text_auto=".2f")
    fig.update_layout(height=360, margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig, use_container_width=True)


def _render_assumptions(workflow: dict[str, Any]) -> None:
    st.dataframe(
        workflow["vehicles"][
            [
                "vehicle_id",
                "energy_type",
                "fuel_rate_l_per_100km",
                "energy_rate_kwh_per_100km",
                "idle_fuel_l_per_hour",
                "idle_energy_kwh_per_hour",
                "co2e_factor",
                "co2e_factor_unit",
                "rate_basis",
            ]
        ],
        hide_index=True,
        use_container_width=True,
    )


def _workflow_scenario_metrics(workflow: dict[str, Any], scenario: str) -> dict[str, Any]:
    metrics = workflow["metrics"]
    row = metrics[metrics["scenario"] == scenario]
    if row.empty:
        raise ValueError(f"Metrics not found for scenario: {scenario}")
    return row.iloc[0].to_dict()


def _comparison_for_active_scenario(workflow: dict[str, Any], scenario: str) -> pd.DataFrame:
    if scenario == "baseline":
        return compare_scenarios(workflow["metrics"], "baseline", "baseline")
    return compare_scenarios(workflow["metrics"], "baseline", scenario)


def _optimization_tab_scenario(active_scenario: str) -> str:
    if active_scenario == "baseline":
        return "optimized"
    return active_scenario


def _constraints_for_scenario(workflow: dict[str, Any], scenario: str) -> pd.DataFrame:
    if scenario == "optimized":
        return workflow["optimized_constraints"]
    routes = workflow["routes"]
    routes = routes[routes["scenario"] == scenario].copy()
    return validate_routes(routes, workflow["vehicles"], workflow["jobs"])


def _default_scenario_id(dataset: DispatchDataset) -> str:
    scenario_ids = [
        item["id"]
        for item in dataset.scenarios.get("scenarios", [])
        if item["id"] != "reoptimized"
    ]
    if "optimized" in scenario_ids:
        return "optimized"
    return scenario_ids[0] if scenario_ids else "optimized"


def _scenario_display_name(scenario: str) -> str:
    labels = {
        "baseline": "Manual baseline dispatch plan",
        "optimized": "Agentic carbon-aware optimized plan",
        "fuel_optimized": "Fuel-optimized dispatch plan",
        "distance_optimized": "Distance-optimized dispatch plan",
        "reoptimized": "Vehicle unavailable disruption plan",
    }
    return labels.get(scenario, scenario)


def _render_scenario_mode_note(scenario: str) -> None:
    if scenario == "optimized":
        st.success("Agentic carbon-aware mode balances route consolidation, vehicle energy type, fuel, and CO2e.")
    elif scenario == "fuel_optimized":
        st.success("Fuel mode prioritizes lower liquid fuel use and may trade off CO2e or operational balance.")
    elif scenario == "distance_optimized":
        st.success("Distance mode prioritizes total kilometers and may trade off fuel or CO2e.")


def _run_message(scenario: str) -> str:
    messages = {
        "baseline": "Manual baseline selected and saved as the active reference plan.",
        "optimized": "Agentic carbon-aware optimization generated and saved.",
        "fuel_optimized": "Fuel-optimized scenario generated and saved.",
        "distance_optimized": "Distance-optimized scenario generated and saved.",
        "reoptimized": "Vehicle-unavailability disruption plan generated, saved, and displayed.",
    }
    return messages.get(scenario, "Optimization workflow generated and saved.")


def _rerun() -> None:
    if hasattr(st, "rerun"):
        st.rerun()
    else:  # pragma: no cover - compatibility for older Streamlit versions
        st.experimental_rerun()


def _apply_decision(decision: str, note: str) -> None:
    workflow = apply_approval_decision(st.session_state["workflow"], decision, note)
    st.session_state["workflow"] = workflow
    run_id = workflow["run_id"]
    save_run_artifact(run_id, "approval_audit", workflow["approval_audit"])
    save_run_artifact(run_id, "decision_summary", workflow["decision_summary"])
    st.success(f"Decision recorded: {decision}")


def _metric_card(label: str, value: str, caption: str, tone: str = "leaf") -> None:
    st.markdown(
        f"""
        <div class="kpi-card tone-{tone}">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{value}</div>
          <div class="kpi-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _inject_css() -> None:
    st.markdown(
        """
        <style>
        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"],
        #MainMenu,
        footer {
            display: none !important;
            height: 0 !important;
            visibility: hidden !important;
        }
        header[data-testid="stHeader"] {
            background: transparent !important;
            box-shadow: none !important;
            height: 2.75rem !important;
        }
        div[data-testid="collapsedControl"],
        div[data-testid="stSidebarCollapsedControl"],
        button[data-testid="baseButton-headerNoPadding"],
        section[data-testid="stSidebar"] button[kind="header"] {
            display: none !important;
            visibility: hidden !important;
            pointer-events: none !important;
        }
        section[data-testid="stSidebar"],
        section[data-testid="stSidebar"][aria-expanded="false"] {
            display: block !important;
            visibility: visible !important;
            transform: translateX(0) !important;
            min-width: 20rem !important;
            max-width: 20rem !important;
            width: 20rem !important;
        }
        section[data-testid="stSidebar"] > div:first-child {
            min-width: 20rem !important;
            max-width: 20rem !important;
            width: 20rem !important;
        }
        div[data-testid="stAppViewContainer"] {
            padding-top: 0 !important;
        }
        .stApp {
            background:
                linear-gradient(180deg, #f0fdf4 0%, #f8fafc 34%, #ffffff 100%);
            color: #0f172a;
        }
        .block-container {
            padding-top: 1rem;
        }
        h1, h2, h3 {
            color: #064e3b;
            letter-spacing: 0;
        }
        h1 {
            font-weight: 800;
        }
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #dcfce7 0%, #f0fdfa 46%, #f8fafc 100%);
            border-right: 1px solid #bbf7d0;
        }
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: #065f46;
        }
        div[data-testid="stAlert"] {
            border-radius: 8px;
            border-color: #a7f3d0;
        }
        .stButton > button {
            border-radius: 8px;
            border: 1px solid #059669;
            background: linear-gradient(135deg, #047857 0%, #16a34a 100%);
            color: #ffffff;
            font-weight: 700;
        }
        .stButton > button:hover {
            border-color: #065f46;
            background: linear-gradient(135deg, #065f46 0%, #15803d 100%);
            color: #ffffff;
        }
        .kpi-card {
            --card-border: #bbf7d0;
            --card-accent: #16a34a;
            --card-bg-start: #f0fdf4;
            --card-bg-end: #ffffff;
            border: 1px solid var(--card-border);
            border-left: 5px solid var(--card-accent);
            border-radius: 8px;
            padding: 14px 16px;
            background: linear-gradient(135deg, var(--card-bg-start) 0%, var(--card-bg-end) 100%);
            min-height: 112px;
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.07);
            margin-bottom: 0.75rem;
        }
        .tone-leaf {
            --card-border: #86efac;
            --card-accent: #16a34a;
            --card-bg-start: #dcfce7;
            --card-bg-end: #f7fee7;
        }
        .tone-teal {
            --card-border: #99f6e4;
            --card-accent: #0d9488;
            --card-bg-start: #ccfbf1;
            --card-bg-end: #f0fdfa;
        }
        .tone-amber {
            --card-border: #fde68a;
            --card-accent: #d97706;
            --card-bg-start: #fef3c7;
            --card-bg-end: #fffbeb;
        }
        .tone-emerald {
            --card-border: #6ee7b7;
            --card-accent: #059669;
            --card-bg-start: #d1fae5;
            --card-bg-end: #ecfdf5;
        }
        .tone-sky {
            --card-border: #bae6fd;
            --card-accent: #0284c7;
            --card-bg-start: #e0f2fe;
            --card-bg-end: #f0f9ff;
        }
        .tone-mint {
            --card-border: #a7f3d0;
            --card-accent: #10b981;
            --card-bg-start: #d1fae5;
            --card-bg-end: #f0fdf4;
        }
        .tone-olive {
            --card-border: #bef264;
            --card-accent: #65a30d;
            --card-bg-start: #ecfccb;
            --card-bg-end: #f7fee7;
        }
        .tone-slate {
            --card-border: #cbd5e1;
            --card-accent: #475569;
            --card-bg-start: #f1f5f9;
            --card-bg-end: #ffffff;
        }
        .kpi-label {
            color: #334155;
            font-size: 0.86rem;
            line-height: 1.2;
            font-weight: 700;
        }
        .kpi-value {
            color: #052e16;
            font-size: 1.55rem;
            font-weight: 700;
            margin-top: 8px;
        }
        .kpi-caption {
            color: #64748b;
            font-size: 0.82rem;
            margin-top: 8px;
        }
        .status-chip {
            display: inline-block;
            border: 1px solid #059669;
            border-radius: 999px;
            padding: 4px 10px;
            color: #047857;
            background: #d1fae5;
            font-weight: 600;
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid #d1fae5;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 8px 18px rgba(15, 23, 42, 0.04);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
