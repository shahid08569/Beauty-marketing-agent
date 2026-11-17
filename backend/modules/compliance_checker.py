import os
import json

def check_compliance(script_data: dict) -> dict:
    rules_path = r"F:\Projects\beauty-marketing-agent\backend\config\rules.json"
    with open(rules_path, "r", encoding="utf-8") as f:
        rules = json.load(f)
        
    prohibited_words = rules.get("prohibited_words", [])
    
    # Text to check: hook + all voiceovers + on_screen_texts + caption
    text_corpus = script_data.get("hook", "") + " " + script_data.get("caption", "")
    for scene in script_data.get("scenes", []):
        text_corpus += " " + scene.get("voiceover", "") + " " + scene.get("on_screen_text", "")
        
    text_lower = text_corpus.lower()
    
    issues = []
    for word in prohibited_words:
        if word.lower() in text_lower:
            issues.append({
                "type": "ProhibitedWord",
                "severity": "Critical",
                "message": f"Banned marketing/medical claim found: '{word}'"
            })
            
    # Check AI disclosure
    caption = script_data.get("caption", "")
    if script_data.get("uses_ai_assets", False) and "#AI" not in caption:
        # Automatically append or flag
        script_data["caption"] += " #AI"
        
    passed = len(issues) == 0
    return {
        "passed": passed,
        "issues_count": len(issues),
        "issues": issues,
        "compliance_badge": "PASSED" if passed else "FAILED"
    }

if __name__ == "__main__":
    sample = {
        "hook": "Instant 100% cure for acne!",
        "caption": "Best product ever",
        "scenes": []
    }
    print(check_compliance(sample))
