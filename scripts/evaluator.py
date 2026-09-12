#!/usr/bin/env python3
"""
Election Analysis Scoring Engine - Knesset 2026
Implements the 6-criteria normalized weighting model, topic-weighted aggregation,
and integrates static party & candidate background data.
"""

import os
import json
from typing import Dict, Any, List, Optional

CRITERIA_WEIGHTS = {
    "c1_platform": 15.0,
    "c2_leader_statements": 15.0,
    "c3_leader_actions": 30.0,
    "c4_candidates_statements": 10.0,
    "c5_candidates_actions": 20.0,
    "c6_designated_executive": 20.0,
}

TOTAL_CRITERIA_WEIGHT = sum(CRITERIA_WEIGHTS.values())  # 110.0

def calculate_topic_score(criteria_scores: Dict[str, float]) -> float:
    """
    Calculate the normalized score for a single topic across the 6 criteria.
    Each criterion score must be between -100.0 and +100.0.
    """
    weighted_sum = 0.0
    for crit_key, raw_weight in CRITERIA_WEIGHTS.items():
        score = criteria_scores.get(crit_key, 0.0)
        score = max(-100.0, min(100.0, float(score)))
        weighted_sum += score * raw_weight
    
    return round(weighted_sum / TOTAL_CRITERIA_WEIGHT, 2)

def calculate_party_overall_score(
    party_topic_scores: Dict[str, float], 
    topic_weights: Dict[str, float]
) -> float:
    """
    Calculate the overall score for a party weighted across all topics.
    """
    total_topic_weight = 0.0
    weighted_sum = 0.0
    
    for topic_id, score in party_topic_scores.items():
        weight = topic_weights.get(topic_id, 1.0)
        weighted_sum += score * weight
        total_topic_weight += weight
        
    if total_topic_weight == 0.0:
        return 0.0
        
    return round(weighted_sum / total_topic_weight, 2)

def load_static_party_data(party_id: str, static_kb_dir: str) -> Dict[str, Any]:
    """
    Loads static data for a party: party.json, candidates.json, manifesto.md
    """
    p_dir = os.path.join(static_kb_dir, "parties", party_id)
    if not os.path.exists(p_dir):
        return {}

    data = {}
    party_file = os.path.join(p_dir, "party.json")
    if os.path.exists(party_file):
        try:
            with open(party_file, "r", encoding="utf-8") as f:
                data["party_info"] = json.load(f)
        except Exception:
            pass

    cand_file = os.path.join(p_dir, "candidates.json")
    if os.path.exists(cand_file):
        try:
            with open(cand_file, "r", encoding="utf-8") as f:
                cand_json = json.load(f)
                data["candidates"] = cand_json.get("candidates", [])
                data["total_candidates"] = cand_json.get("total_candidates_registered", len(data["candidates"]))
        except Exception:
            pass

    man_file = os.path.join(p_dir, "manifesto.md")
    if os.path.exists(man_file):
        try:
            with open(man_file, "r", encoding="utf-8") as f:
                data["manifesto_text"] = f.read()
        except Exception:
            pass

    return data

def evaluate_full_dataset(
    eval_data: Dict[str, Any], 
    profile_data: Dict[str, Any],
    static_kb_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Computes all topic scores, party overall scores, and ranks for the entire dataset
    against a given user profile. Enriches parties with static background data if available.
    """
    if static_kb_dir is None:
        default_static = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "static")
        if os.path.exists(default_static):
            static_kb_dir = default_static

    topics_list = profile_data.get("topics", [])
    topic_weights = {t["id"]: float(t.get("weight", 1.0)) for t in topics_list}
    
    evaluated_parties = {}
    
    for party_id, p_info in eval_data.get("parties", {}).items():
        topic_scores = {}
        evaluated_topics = {}
        
        for topic_id, t_eval in p_info.get("topics", {}).items():
            raw_scores = t_eval.get("scores", {})
            computed_score = calculate_topic_score(raw_scores)
            topic_scores[topic_id] = computed_score
            
            evaluated_topics[topic_id] = {
                "computed_score": computed_score,
                "scores": raw_scores,
                "notes": t_eval.get("notes", {}),
                "citations": t_eval.get("citations", [])
            }
            
        overall_score = calculate_party_overall_score(topic_scores, topic_weights)
        
        party_obj = {
            "name_he": p_info.get("name_he", party_id),
            "leader": p_info.get("leader", ""),
            "poll_mandates": p_info.get("poll_mandates", 0),
            "overall_score": overall_score,
            "topic_scores": topic_scores,
            "topics": evaluated_topics
        }

        # Enrich with static data if available
        if static_kb_dir:
            static_info = load_static_party_data(party_id, static_kb_dir)
            if static_info:
                party_obj["static_data"] = static_info

        evaluated_parties[party_id] = party_obj
        
    # Rank parties by overall score descending
    sorted_parties = sorted(
        evaluated_parties.items(), 
        key=lambda item: item[1]["overall_score"], 
        reverse=True
    )
    
    ranked_parties = {}
    for rank, (p_id, p_data) in enumerate(sorted_parties, start=1):
        p_data["rank"] = rank
        ranked_parties[p_id] = p_data
        
    return {
        "date": eval_data.get("date", ""),
        "profile_id": profile_data.get("profile_id", "default"),
        "profile_name": profile_data.get("profile_name", "Default Profile"),
        "profile_description": profile_data.get("description", ""),
        "topics": topics_list,
        "topic_weights": topic_weights,
        "parties": ranked_parties
    }
