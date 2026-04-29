"""
database.py  —  SIAMA Supabase integration layer
Place this file in the same folder as siama_app_merged.py
"""

import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import json


# ─────────────────────────────────────────────
# 1.  CONNECTION  (reads from Streamlit secrets)
# ─────────────────────────────────────────────
@st.cache_resource
def get_supabase_client() -> Client:
    url  = st.secrets["SUPABASE_URL"]
    key  = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


# ─────────────────────────────────────────────
# 2.  PROJECT  helpers
# ─────────────────────────────────────────────
def get_all_projects():
    sb = get_supabase_client()
    res = sb.table("projects").select("*").order("created_at", desc=True).execute()
    return res.data or []


def create_project(name: str, description: str = "") -> dict:
    sb = get_supabase_client()
    res = sb.table("projects").insert({
        "name": name,
        "description": description,
    }).execute()
    return res.data[0] if res.data else {}


def delete_project(project_id: int):
    sb = get_supabase_client()
    sb.table("projects").delete().eq("id", project_id).execute()


# ─────────────────────────────────────────────
# 3.  SIT  helpers
# ─────────────────────────────────────────────
def save_sit_stakeholder(project_id: int, role: str, responses: dict):
    sb = get_supabase_client()
    sb.table("sit_stakeholders").insert({
        "project_id": project_id,
        "role": role,
        "responses": json.dumps(responses),
    }).execute()


def get_sit_stakeholders(project_id: int):
    sb = get_supabase_client()
    res = sb.table("sit_stakeholders").select("*").eq("project_id", project_id).execute()
    rows = res.data or []
    for r in rows:
        if isinstance(r.get("responses"), str):
            r["responses"] = json.loads(r["responses"])
    return rows


def save_sit_actor(project_id: int, role: str, name: str, location: str,
                   contact: str, details: str):
    sb = get_supabase_client()
    sb.table("sit_actors").insert({
        "project_id": project_id,
        "role": role,
        "name": name,
        "location": location,
        "contact": contact,
        "details": details,
    }).execute()


def get_sit_actors(project_id: int):
    sb = get_supabase_client()
    res = sb.table("sit_actors").select("*").eq("project_id", project_id).execute()
    return res.data or []


def delete_sit_actor(actor_id: int):
    sb = get_supabase_client()
    sb.table("sit_actors").delete().eq("id", actor_id).execute()


# ─────────────────────────────────────────────
# 4.  SAT  helpers
# ─────────────────────────────────────────────
def save_sat_rating(project_id: int, stakeholder: str, power: int, interest: int,
                    legitimacy: int, urgency: int, interactions: str,
                    tasks: str, knowledge: str):
    sb = get_supabase_client()
    sb.table("sat_relationship_data").upsert({
        "project_id": project_id,
        "stakeholder": stakeholder,
        "power": power,
        "interest": interest,
        "legitimacy": legitimacy,
        "urgency": urgency,
        "interactions": interactions,
        "tasks": tasks,
        "knowledge": knowledge,
    }, on_conflict="project_id,stakeholder").execute()


def get_sat_ratings(project_id: int):
    sb = get_supabase_client()
    res = sb.table("sat_relationship_data").select("*").eq("project_id", project_id).execute()
    return res.data or []


def save_sat_subgroup(project_id: int, name: str, description: str):
    sb = get_supabase_client()
    sb.table("sat_subgroups").upsert({
        "project_id": project_id,
        "name": name,
        "description": description,
    }, on_conflict="project_id,name").execute()


def get_sat_subgroups(project_id: int):
    sb = get_supabase_client()
    res = (sb.table("sat_subgroups")
             .select("*, sat_subgroup_members(stakeholder)")
             .eq("project_id", project_id)
             .execute())
    return res.data or []


def assign_to_subgroup(project_id: int, subgroup_name: str, stakeholder: str):
    sb = get_supabase_client()
    sg = (sb.table("sat_subgroups")
            .select("id")
            .eq("project_id", project_id)
            .eq("name", subgroup_name)
            .single()
            .execute())
    if sg.data:
        sb.table("sat_subgroup_members").upsert({
            "subgroup_id": sg.data["id"],
            "stakeholder": stakeholder,
        }, on_conflict="subgroup_id,stakeholder").execute()


def remove_from_subgroup(subgroup_id: int, stakeholder: str):
    sb = get_supabase_client()
    sb.table("sat_subgroup_members").delete().eq("subgroup_id", subgroup_id).eq("stakeholder", stakeholder).execute()


def save_sat_conflict(project_id: int, stakeholder: str, cooperativeness: int,
                      competitiveness: int, description: str):
    sb = get_supabase_client()
    sb.table("sat_conflict_data").insert({
        "project_id": project_id,
        "stakeholder": stakeholder,
        "cooperativeness": cooperativeness,
        "competitiveness": competitiveness,
        "description": description,
    }).execute()


def get_sat_conflicts(project_id: int):
    sb = get_supabase_client()
    res = sb.table("sat_conflict_data").select("*").eq("project_id", project_id).execute()
    return res.data or []


def save_sat_knowledge(project_id: int, group_name: str, knowledge: str,
                       responsibilities: str, skills: str):
    sb = get_supabase_client()
    sb.table("sat_knowledge_data").upsert({
        "project_id": project_id,
        "group_name": group_name,
        "knowledge": knowledge,
        "responsibilities": responsibilities,
        "skills": skills,
    }, on_conflict="project_id,group_name").execute()


def get_sat_knowledge(project_id: int):
    sb = get_supabase_client()
    res = sb.table("sat_knowledge_data").select("*").eq("project_id", project_id).execute()
    return res.data or []


def save_sat_value_map(project_id: int, stakeholder: str, pains: str, gains: str,
                       jobs: str, pain_relievers: str, gain_creators: str,
                       products_services: str):
    sb = get_supabase_client()
    sb.table("sat_value_map").insert({
        "project_id": project_id,
        "stakeholder": stakeholder,
        "pains": pains,
        "gains": gains,
        "jobs": jobs,
        "pain_relievers": pain_relievers,
        "gain_creators": gain_creators,
        "products_services": products_services,
    }).execute()


def get_sat_value_maps(project_id: int):
    sb = get_supabase_client()
    res = sb.table("sat_value_map").select("*").eq("project_id", project_id).execute()
    return res.data or []


# ─────────────────────────────────────────────
# 5.  MAT  helpers
# ─────────────────────────────────────────────
def save_mat_pestel(project_id: int, data: dict):
    sb = get_supabase_client()
    sb.table("mat_pestel").upsert({"project_id": project_id, **data},
                                  on_conflict="project_id").execute()


def get_mat_pestel(project_id: int):
    sb = get_supabase_client()
    res = sb.table("mat_pestel").select("*").eq("project_id", project_id).maybe_single().execute()
    return res.data if res else {}


def save_mat_gap(project_id: int, data: dict):
    sb = get_supabase_client()
    sb.table("mat_gap").upsert({"project_id": project_id, **data},
                               on_conflict="project_id").execute()


def get_mat_gap(project_id: int):
    sb = get_supabase_client()
    res = sb.table("mat_gap").select("*").eq("project_id", project_id).maybe_single().execute()
    return res.data if res else {}


def save_mat_segment(project_id: int, data: dict):
    sb = get_supabase_client()
    sb.table("mat_behavioral_segments").insert({"project_id": project_id, **data}).execute()


def get_mat_segments(project_id: int):
    sb = get_supabase_client()
    res = sb.table("mat_behavioral_segments").select("*").eq("project_id", project_id).execute()
    return res.data or []


def save_mat_persona(project_id: int, data: dict):
    sb = get_supabase_client()
    sb.table("mat_personas").insert({"project_id": project_id, **data}).execute()


def get_mat_personas(project_id: int):
    sb = get_supabase_client()
    res = sb.table("mat_personas").select("*").eq("project_id", project_id).execute()
    return res.data or []


def save_mat_journey(project_id: int, journey_data: dict):
    sb = get_supabase_client()
    for stage, content in journey_data.items():
        sb.table("mat_customer_journey").upsert({
            "project_id": project_id,
            "stage": stage,
            **content,
        }, on_conflict="project_id,stage").execute()


def get_mat_journey(project_id: int):
    sb = get_supabase_client()
    res = sb.table("mat_customer_journey").select("*").eq("project_id", project_id).execute()
    return res.data or []


def save_mat_mystery_shopping(project_id: int, data: dict):
    sb = get_supabase_client()
    sb.table("mat_mystery_shopping").insert({"project_id": project_id, **data}).execute()


def get_mat_mystery_shopping(project_id: int):
    sb = get_supabase_client()
    res = sb.table("mat_mystery_shopping").select("*").eq("project_id", project_id).execute()
    return res.data or []


def save_mat_complaint(project_id: int, data: dict):
    sb = get_supabase_client()
    sb.table("mat_complaints").insert({"project_id": project_id, **data}).execute()


def get_mat_complaints(project_id: int):
    sb = get_supabase_client()
    res = sb.table("mat_complaints").select("*").eq("project_id", project_id).execute()
    return res.data or []


def save_mat_brand_audit(project_id: int, data: dict):
    sb = get_supabase_client()
    sb.table("mat_brand_audit").upsert({"project_id": project_id, **data},
                                       on_conflict="project_id").execute()


def get_mat_brand_audit(project_id: int):
    sb = get_supabase_client()
    res = sb.table("mat_brand_audit").select("*").eq("project_id", project_id).maybe_single().execute()
    return res.data if res else {}


# ─────────────────────────────────────────────
# 6.  NATURE OF CRAFT  helpers
# ─────────────────────────────────────────────
def save_nature_of_craft(project_id: int, status_type: str, selections: dict):
    sb = get_supabase_client()
    rows = []
    for key, selected in selections.items():
        parts = key.split("_", 2)
        if len(parts) == 3:
            rows.append({
                "project_id": project_id,
                "status_type": status_type,
                "primary_dimension": parts[1],
                "item": parts[2],
                "selected": selected,
            })
    if rows:
        sb.table("nature_of_craft").upsert(
            rows,
            on_conflict="project_id,status_type,primary_dimension,item"
        ).execute()


def get_nature_of_craft(project_id: int, status_type: str):
    sb = get_supabase_client()
    res = (sb.table("nature_of_craft")
             .select("*")
             .eq("project_id", project_id)
             .eq("status_type", status_type)
             .execute())
    result = {}
    for row in (res.data or []):
        key = f"{status_type}_{row['primary_dimension']}_{row['item']}"
        result[key] = row["selected"]
    return result


# ─────────────────────────────────────────────
# 7.  PROGRESS TRACKING  helpers
# ─────────────────────────────────────────────
def update_step_progress(project_id: int, section: str, step: int, completed: bool):
    sb = get_supabase_client()
    sb.table("step_progress").upsert({
        "project_id": project_id,
        "section": section,
        "step": step,
        "completed": completed,
    }, on_conflict="project_id,section,step").execute()


def get_step_progress(project_id: int):
    sb = get_supabase_client()
    res = sb.table("step_progress").select("*").eq("project_id", project_id).execute()
    progress = {}
    for row in (res.data or []):
        key = f"{row['section']}_{row['step']}"
        progress[key] = row["completed"]
    return progress
