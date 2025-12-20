from typing import Dict, Any, List

def extract_player_stats(member: Dict[str, Any], is_me: bool, team: str) -> Dict[str, Any]:
    """
    Extract specific stats for a single player.
    """
    weapon = member.get("weapon", {})
    return {
        "weapon_key": weapon.get("key"),
        "weapon_name": weapon.get("name", {}).get("en_US"),
        "kill": member.get("kill"),
        "assist": member.get("assist"),
        "kill_or_assist": member.get("kill_or_assist"),
        "death": member.get("death"),
        "special": member.get("special"),
        "inked": member.get("inked"),
        "is_me": is_me,
        "team": team
    }

def flatten_battle(battle: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flatten a single battle record from stat.ink.
    """
    
    # Basic info
    flat = {
        "id": battle.get("uuid"),
        "url": battle.get("url"),
        "end_at": battle.get("end_at", {}).get("iso8601"),
        "result": battle.get("result"),
        "knockout": battle.get("knockout"),
        
        # Lobby/Rule/Stage
        "lobby": battle.get("lobby", {}).get("key"),
        "rule_key": battle.get("rule", {}).get("key"),
        "rule_name": battle.get("rule", {}).get("name", {}).get("en_US"),
        "stage_name": battle.get("stage", {}).get("name", {}).get("en_US"),
        
        # Main Player Stats (Legacy top-level keep for backward compat if needed, or primarily rely on nested)
        # keeping top level stats for easy dashboarding of "my" performance without nested queries
        "kill": battle.get("kill"),
        "assist": battle.get("assist"),
        "death": battle.get("death"),
        "special_count": battle.get("special"),
        "inked": battle.get("inked"),
        
        # Weapon
        "weapon_key": battle.get("weapon", {}).get("key"),
        "weapon_name": battle.get("weapon", {}).get("name", {}).get("en_US"),
        "sub_weapon": battle.get("weapon", {}).get("sub", {}).get("name", {}).get("en_US"),
        "special_weapon": battle.get("weapon", {}).get("special", {}).get("name", {}).get("en_US"),
        
        # Rank / Power (X Match specific)
        "x_power_before": battle.get("x_power_before"),
        "x_power_after": battle.get("x_power_after"),
        "rank_before": battle.get("rank_before"),
        "rank_after": battle.get("rank_after"),
        
        # Medals
        "medals": battle.get("medals", []),
    }

    # Consolidated Players List
    players = []
    
    # My Team
    for m in battle.get("our_team_members", []):
        players.append(extract_player_stats(m, is_me=m.get("me", False), team="my"))
        
    # Their Team
    for m in battle.get("their_team_members", []):
        players.append(extract_player_stats(m, is_me=False, team="their"))
        
    flat["players"] = players

    return flat

def flatten_battles(battles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Flatten a list of battles."""
    return [flatten_battle(b) for b in battles]
