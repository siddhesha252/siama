"""
project_history.py  —  Project History & Data Loader for SIAMA
Drop this file next to siama_app.py and database.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import database as db


# ─────────────────────────────────────────────────────
# SECTION DEFINITIONS (keep in sync with siama_app.py)
# ─────────────────────────────────────────────────────
STEPS = {
    "SIT": ["Predefined Roles & Questionnaires", "Role × Actor Database",
            "Role Card", "Role Map"],
    "SAT": ["Relationship Matrix", "Management Tool", "Conflict Resolution",
            "Knowledge & Responsibility", "Value Exchange Map"],
    "MAT": ["PESTEL", "Gap Analysis", "Behavioral Segmentation", "User Persona",
            "Customer Journey", "Mystery Shopping", "Complaint Analysis", "Brand Audit"],
    "CRAFT": ["Nature of Craft — Current", "Nature of Craft — Desired"],
}


# ─────────────────────────────────────────────────────
# Helper: build a snapshot dict for one project
# ─────────────────────────────────────────────────────
def get_project_snapshot(project_id: int) -> dict:
    """
    Returns counts and completion info for a project.
    Runs multiple small DB queries — cache aggressively in caller.
    """
    actors        = db.get_sit_actors(project_id)
    stakeholders  = db.get_sit_stakeholders(project_id)
    ratings       = db.get_sat_ratings(project_id)
    conflicts     = db.get_sat_conflicts(project_id)
    value_maps    = db.get_sat_value_maps(project_id)
    knowledge     = db.get_sat_knowledge(project_id)
    subgroups     = db.get_sat_subgroups(project_id)
    segments      = db.get_mat_segments(project_id)
    personas      = db.get_mat_personas(project_id)
    complaints    = db.get_mat_complaints(project_id)
    mystery       = db.get_mat_mystery_shopping(project_id)
    pestel        = db.get_mat_pestel(project_id)
    gap           = db.get_mat_gap(project_id)
    journey       = db.get_mat_journey(project_id)
    brand_audit   = db.get_mat_brand_audit(project_id)
    progress      = db.get_step_progress(project_id)

    sit_done = sum(1 for i in range(1, 5) if progress.get(f"SIT_{i}"))
    sat_done = sum(1 for i in range(1, 6) if progress.get(f"SAT_{i}"))
    mat_done = sum(1 for i in range(1, 9) if progress.get(f"MAT_{i}"))
    craft_done = sum(1 for i in range(1, 3) if progress.get(f"CRAFT_{i}"))

    total_steps = 4 + 5 + 8 + 2
    total_done  = sit_done + sat_done + mat_done + craft_done
    overall_pct = int(total_done / total_steps * 100)

    return {
        "progress":     progress,
        "overall_pct":  overall_pct,
        "total_done":   total_done,
        "total_steps":  total_steps,
        "sit_done":     sit_done,
        "sat_done":     sat_done,
        "mat_done":     mat_done,
        "craft_done":   craft_done,
        "counts": {
            "Actors":              len(actors),
            "Stakeholder Interviews": len(stakeholders),
            "SAT Ratings":         len(ratings),
            "Subgroups":           len(subgroups),
            "Conflicts Logged":    len(conflicts),
            "Value Maps":          len(value_maps),
            "Knowledge Groups":    len(knowledge),
            "Behavioral Segments": len(segments),
            "Personas":            len(personas),
            "Complaints":          len(complaints),
            "Mystery Shopping":    len(mystery),
            "Customer Journey Stages": len(journey),
            "PESTEL filled":       1 if pestel else 0,
            "Gap Analysis filled": 1 if gap else 0,
            "Brand Audit filled":  1 if brand_audit else 0,
        },
        "raw": {
            "actors":       actors,
            "stakeholders": stakeholders,
            "ratings":      ratings,
            "conflicts":    conflicts,
            "value_maps":   value_maps,
            "knowledge":    knowledge,
            "subgroups":    subgroups,
            "segments":     segments,
            "personas":     personas,
            "complaints":   complaints,
            "mystery":      mystery,
            "pestel":       pestel,
            "gap":          gap,
            "journey":      journey,
            "brand_audit":  brand_audit,
        }
    }


# ─────────────────────────────────────────────────────
# Main render function — call this in the menu block
# ─────────────────────────────────────────────────────
def render_project_history():
    st.markdown('<div class="main-header">📁 Project History</div>',
                unsafe_allow_html=True)

    all_projects = db.get_all_projects()

    if not all_projects:
        st.info("No projects saved yet. Create your first project in the sidebar.")
        return

    # ── TOP SUMMARY TABLE ─────────────────────────────
    st.subheader(f"All Projects ({len(all_projects)})")

    summary_rows = []
    for p in all_projects:
        snap = get_project_snapshot(p["id"])
        summary_rows.append({
            "Project":      p["name"],
            "Created":      p["created_at"][:10],
            "Overall %":    snap["overall_pct"],
            "SIT":          f"{snap['sit_done']}/4",
            "SAT":          f"{snap['sat_done']}/5",
            "MAT":          f"{snap['mat_done']}/8",
            "Craft":        f"{snap['craft_done']}/2",
            "Actors":       snap["counts"]["Actors"],
            "Ratings":      snap["counts"]["SAT Ratings"],
            "id":           p["id"],
        })

    df_summary = pd.DataFrame(summary_rows)

    # Color-code the completion bar
    st.dataframe(
        df_summary.drop(columns=["id"]).style.bar(
            subset=["Overall %"], color="#1f77b4", vmin=0, vmax=100
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")

    # ── PROJECT DETAIL VIEWER ─────────────────────────
    st.subheader("🔍 View / Load a Project")

    project_options = {f"{p['name']}  (created {p['created_at'][:10]})": p
                       for p in all_projects}
    chosen_label = st.selectbox("Select a project to inspect", list(project_options.keys()))
    chosen = project_options[chosen_label]
    pid    = chosen["id"]

    # Button to make this the active project
    col_load, col_delete = st.columns([3, 1])
    with col_load:
        if st.button(f"✅ Set '{chosen['name']}' as active project", type="primary",
                     use_container_width=True):
            st.session_state["project_id"] = pid
            # Clear in-memory nature_of_craft so it reloads from DB
            if "nature_of_craft" in st.session_state:
                del st.session_state["nature_of_craft"]
            st.success(f"Active project switched to **{chosen['name']}**. "
                       "All toolkit pages will now show this project's data.")
            st.rerun()

    with col_delete:
        if st.button("🗑️ Delete project", type="secondary", use_container_width=True):
            st.session_state[f"confirm_delete_{pid}"] = True

    if st.session_state.get(f"confirm_delete_{pid}"):
        st.warning(f"⚠️  This will permanently delete **{chosen['name']}** and ALL its data.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Yes, delete permanently", type="primary"):
                db.delete_project(pid)
                del st.session_state[f"confirm_delete_{pid}"]
                if st.session_state.get("project_id") == pid:
                    st.session_state["project_id"] = None
                st.success("Project deleted.")
                st.rerun()
        with c2:
            if st.button("Cancel"):
                del st.session_state[f"confirm_delete_{pid}"]
                st.rerun()

    st.markdown("---")

    # ── SNAPSHOT ─────────────────────────────────────
    snap = get_project_snapshot(pid)

    # Progress gauges
    st.subheader(f"📊 Progress — {chosen['name']}")

    gauge_cols = st.columns(5)
    sections_info = [
        ("Overall",  snap["overall_pct"],    snap["total_steps"]),
        ("SIT",      snap["sit_done"] * 25,  4),
        ("SAT",      snap["sat_done"] * 20,  5),
        ("MAT",      snap["mat_done"] * 12,  8),    # 12.5 per step ≈ int
        ("Craft",    snap["craft_done"] * 50, 2),
    ]
    for col, (label, pct, total) in zip(gauge_cols, sections_info):
        # clamp to 100
        pct = min(pct, 100)
        col.metric(label, f"{pct}%")
        col.progress(pct / 100)

    # Step checklist
    with st.expander("📋 Step-by-step checklist"):
        progress = snap["progress"]
        for section, steps in STEPS.items():
            st.markdown(f"**{section}**")
            for i, step_name in enumerate(steps, 1):
                done = progress.get(f"{section}_{i}", False)
                icon = "✅" if done else "⬜"
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{icon} Step {i}: {step_name}")

    st.markdown("---")

    # ── DATA TABS ─────────────────────────────────────
    st.subheader("📂 Saved Data")
    raw = snap["raw"]

    data_tabs = st.tabs(["SIT", "SAT", "MAT — Tools", "Nature of Craft"])

    # ── SIT tab ───────────────────────────────────────
    with data_tabs[0]:
        st.markdown("#### Actors in Value Chain")
        if raw["actors"]:
            df_actors = pd.DataFrame(raw["actors"])[
                ["role", "name", "location", "contact", "details"]
            ]
            st.dataframe(df_actors, use_container_width=True, hide_index=True)

            # Role distribution chart
            role_counts = df_actors["role"].value_counts().reset_index()
            role_counts.columns = ["Role", "Count"]
            fig = px.bar(role_counts, x="Role", y="Count",
                         title="Actors by Role", color="Role",
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No actors saved yet for this project.")

        st.markdown("#### Stakeholder Questionnaire Responses")
        if raw["stakeholders"]:
            for s in raw["stakeholders"]:
                with st.expander(f"Role: {s['role']}  —  saved {s.get('created_at','')[:10]}"):
                    if isinstance(s.get("responses"), dict):
                        for q, a in s["responses"].items():
                            st.markdown(f"**Q:** {q}")
                            st.write(a or "_No response_")
                    else:
                        st.write(s.get("responses"))
        else:
            st.info("No questionnaire responses saved yet.")

    # ── SAT tab ───────────────────────────────────────
    with data_tabs[1]:
        if raw["ratings"]:
            st.markdown("#### Stakeholder Ratings")
            df_r = pd.DataFrame(raw["ratings"])[
                ["stakeholder", "power", "interest", "legitimacy", "urgency"]
            ]
            st.dataframe(df_r, use_container_width=True, hide_index=True)

            # Radar chart of averages
            avg = df_r[["power","interest","legitimacy","urgency"]].mean()
            fig_radar = go.Figure(go.Scatterpolar(
                r=avg.values.tolist() + [avg.values[0]],
                theta=["Power","Interest","Legitimacy","Urgency","Power"],
                fill="toself", name="Avg rating"
            ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                title="Average Stakeholder Profile"
            )
            st.plotly_chart(fig_radar, use_container_width=True)

            # Power-Interest scatter
            fig_pi = px.scatter(df_r, x="power", y="interest",
                                text="stakeholder", title="Power vs Interest")
            fig_pi.update_traces(textposition="top center")
            fig_pi.add_hline(y=5, line_dash="dash", line_color="gray")
            fig_pi.add_vline(x=5, line_dash="dash", line_color="gray")
            st.plotly_chart(fig_pi, use_container_width=True)
        else:
            st.info("No SAT ratings saved yet.")

        if raw["conflicts"]:
            st.markdown("#### Conflict Data")
            st.dataframe(pd.DataFrame(raw["conflicts"])[
                ["stakeholder", "cooperativeness", "competitiveness", "description"]
            ], use_container_width=True, hide_index=True)

        if raw["value_maps"]:
            st.markdown("#### Value Exchange Maps")
            for vm in raw["value_maps"]:
                with st.expander(f"📊 {vm['stakeholder']}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"**Pains:** {vm['pains']}")
                        st.write(f"**Gains:** {vm['gains']}")
                        st.write(f"**Jobs:** {vm['jobs']}")
                    with c2:
                        st.write(f"**Pain Relievers:** {vm['pain_relievers']}")
                        st.write(f"**Gain Creators:** {vm['gain_creators']}")
                        st.write(f"**Products/Services:** {vm['products_services']}")

        if raw["knowledge"]:
            st.markdown("#### Knowledge & Responsibility")
            st.dataframe(pd.DataFrame(raw["knowledge"])[
                ["group_name","knowledge","responsibilities","skills"]
            ], use_container_width=True, hide_index=True)

    # ── MAT tab ───────────────────────────────────────
    with data_tabs[2]:
        mat_view = st.selectbox("View MAT tool", [
            "PESTEL", "Gap Analysis", "Behavioral Segments",
            "Personas", "Customer Journey", "Mystery Shopping",
            "Complaints", "Brand Audit"
        ])

        if mat_view == "PESTEL" and raw["pestel"]:
            p = raw["pestel"]
            cols = st.columns(2)
            fields = ["political","economic","social","technological","environmental","legal"]
            for i, f in enumerate(fields):
                cols[i % 2].markdown(f"**{f.title()}**")
                cols[i % 2].write(p.get(f) or "_Not filled_")

        elif mat_view == "Gap Analysis" and raw["gap"]:
            g = raw["gap"]
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Current State**"); st.write(g.get("current_state",""))
                st.markdown("**Strengths**");     st.write(g.get("current_strengths",""))
                st.markdown("**Weaknesses**");    st.write(g.get("current_weaknesses",""))
            with c2:
                st.markdown("**Desired State**"); st.write(g.get("desired_state",""))
                st.markdown("**Opportunities**"); st.write(g.get("opportunities",""))
                st.markdown("**Threats**");       st.write(g.get("threats",""))
            st.markdown("**Action Plan**"); st.write(g.get("action_plan",""))

        elif mat_view == "Behavioral Segments" and raw["segments"]:
            for seg in raw["segments"]:
                with st.expander(f"👥 {seg['name']}"):
                    st.write(f"Purchase Behavior: {seg['purchase_behavior']}")
                    st.write(f"Usage Rate: {seg['usage_rate']}")
                    st.write(f"Benefits Sought: {seg['benefits_sought']}")

        elif mat_view == "Personas" and raw["personas"]:
            for p in raw["personas"]:
                with st.expander(f"👤 {p['name']}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"Age: {p['age_range']} | Occupation: {p['occupation']}")
                        st.write(f"Location: {p['location']} | Income: {p['income_level']}")
                    with c2:
                        st.write(f"Education: {p['education']} | Family: {p['family_status']}")
                    st.write(f"Goals: {p['goals']}")
                    st.write(f"Pain Points: {p['pain_points']}")

        elif mat_view == "Customer Journey" and raw["journey"]:
            stage_data = {r["stage"]: r for r in raw["journey"]}
            for stage in ["Awareness","Consideration","Purchase","Usage","Loyalty"]:
                r = stage_data.get(stage, {})
                with st.expander(f"📍 {stage}"):
                    st.write(f"Touchpoints: {r.get('touchpoints','')}")
                    st.write(f"Actions: {r.get('actions','')}")
                    st.write(f"Emotions: {r.get('emotions','')}")
                    st.write(f"Pain Points: {r.get('pain_points','')}")
                    st.write(f"Opportunities: {r.get('opportunities','')}")

        elif mat_view == "Mystery Shopping" and raw["mystery"]:
            for ms in raw["mystery"]:
                with st.expander(f"🛍️ {ms['location']} — {ms.get('visit_date','')}"):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Ambiance",        ms.get("ambiance","-"))
                    c2.metric("Staff Behavior",  ms.get("staff_behavior","-"))
                    c3.metric("Product Knowledge",ms.get("product_knowledge","-"))
                    st.write(f"Observations: {ms.get('observations','')}")
                    st.write(f"Recommendations: {ms.get('recommendations','')}")

        elif mat_view == "Complaints" and raw["complaints"]:
            df_c = pd.DataFrame(raw["complaints"])
            st.dataframe(df_c[["category","severity","status","description"]],
                         use_container_width=True, hide_index=True)
            col1, col2 = st.columns(2)
            with col1:
                fig = px.pie(df_c, names="category", title="By Category")
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig2 = px.bar(df_c["severity"].value_counts().reset_index(),
                              x="severity", y="count", title="By Severity")
                st.plotly_chart(fig2, use_container_width=True)

        elif mat_view == "Brand Audit" and raw["brand_audit"]:
            ba = raw["brand_audit"]
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Mission:**");  st.write(ba.get("brand_mission",""))
                st.markdown("**Vision:**");   st.write(ba.get("brand_vision",""))
                st.markdown("**Values:**");   st.write(ba.get("brand_values",""))
            with c2:
                st.markdown("**USP:**");      st.write(ba.get("usp",""))
                st.markdown("**Personality:**"); st.write(ba.get("personality",""))

            metrics = ["awareness","recognition","loyalty","satisfaction","position","consistency"]
            vals    = [ba.get(m, 5) for m in metrics]
            fig_r = go.Figure(go.Scatterpolar(
                r=vals + [vals[0]],
                theta=[m.title() for m in metrics] + [metrics[0].title()],
                fill="toself"
            ))
            fig_r.update_layout(polar=dict(radialaxis=dict(range=[0,10])),
                                title="Brand Performance Radar")
            st.plotly_chart(fig_r, use_container_width=True)
        else:
            st.info(f"No data saved for {mat_view} in this project yet.")

    # ── Nature of Craft tab ───────────────────────────
    with data_tabs[3]:
        current_sel = db.get_nature_of_craft(pid, "current")
        desired_sel = db.get_nature_of_craft(pid, "desired")

        if not current_sel and not desired_sel:
            st.info("No Nature of Craft data saved yet.")
        else:
            curr_count = sum(1 for v in current_sel.values() if v)
            des_count  = sum(1 for v in desired_sel.values() if v)
            c1, c2 = st.columns(2)
            c1.metric("Current characteristics selected", curr_count)
            c2.metric("Desired characteristics selected", des_count)

            # Build comparison table
            rows = []
            all_keys = set(current_sel) | {k.replace("current_","desired_") for k in current_sel}
            for ck in current_sel:
                dk = ck.replace("current_","desired_")
                cv = current_sel.get(ck, False)
                dv = desired_sel.get(dk, False)
                if cv or dv:
                    parts = ck.split("_", 2)
                    rows.append({
                        "Dimension":      parts[1].split("(")[0].strip() if len(parts) > 1 else "",
                        "Characteristic": parts[2] if len(parts) > 2 else "",
                        "Current":        "✓" if cv else "✗",
                        "Desired":        "✓" if dv else "✗",
                        "Action":         ("✅ Maintain" if cv and dv else
                                           "⬆️ Develop"  if not cv and dv else
                                           "⬇️ Reduce"   if cv and not dv else ""),
                    })
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
