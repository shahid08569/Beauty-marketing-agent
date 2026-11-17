import re
from typing import Dict, Any

def generate_roman_urdu_script(
    product_name: str,
    category: str = "beauty_skincare",
    target_gender: str = "women",
    tone: str = "emotional_hook",
    target_duration: int = 30
) -> Dict[str, Any]:
    """
    Generates a high-converting, authentic Roman Urdu script tailored to Pakistani beauty and grooming consumers.
    Divided into 4 clear reviewable scenes.
    """
    is_men = target_gender.lower() == "men"
    p_lower = product_name.lower()
    
    # 1. Product Context Detection
    if any(k in p_lower for k in ["dove", "soap", "bar", "cleanser", "body wash"]):
        prod_type = "moisture_bar"
    elif any(k in p_lower for k in ["serum", "niacinamide", "vitamin c", "retinol", "hyaluronic", "salicylic"]):
        prod_type = "serum"
    elif any(k in p_lower for k in ["cream", "lotion", "moisturizer", "cold cream", "glow cream"]):
        prod_type = "cream"
    elif any(k in p_lower for k in ["beard", "oil", "shave", "charcoal", "hair wax"]):
        prod_type = "men_care"
    else:
        prod_type = "general_skincare"

    # 2. Build High-Impact Scenes in Roman Urdu
    if is_men or prod_type == "men_care":
        hook = f"Agar aapke chehre par bhi dhoop aur pollution se dullness rehti hai, to {product_name} zaroor try karein!"
        problem = f"Aam soaps skin ko sakht aur dry bana dete hain. {product_name} ka advanced formula pores ko deep clean karta hai bina natural moisture chheeney."
        action = f"Sirf thori si quantity lein, halka circular massage karein - yeh foran skin ko clean, fresh aur sharp matte look deta hai."
        cta = f"100% verified original batch bio link par available hai. Cash on Delivery ke sath abhi order karein!"
        action_desc = "Men's grooming model applies product with fingertips, demonstrating fresh clean matte finish."
    elif prod_type == "moisture_bar":
        hook = f"Agar aapki skin bhi har face wash ke baad khinchi khinchi aur dry lagti hai, to yeh secret dekhein!"
        problem = f"Aam sabun skin ka natural protective barrier tabah kar dete hain. {product_name} me shamil ultra-moisturizing cream skin ko 24 ghantay hydrated rakhti hai."
        action = f"Iski rich creamy foam lather skin par gentle hai - dhoney ke baad milta hai soft, dewy glass-skin glow bina kisi chipchipahat ke."
        cta = f"Original authentic {product_name} abhi bio link se order karein, pure Pakistan me Cash on Delivery available hai!"
        action_desc = "Model demonstrates creamy lather application on cheek, revealing hydrated radiant glow."
    elif prod_type == "serum":
        hook = f"Chehre ke stubborn spots aur open pores se pareshan hain? To {product_name} se behtar kuch nahi!"
        problem = f"Sirf moisturizers lagane se spots khatam nahi hotay. {product_name} ke active ingredients skin ki deep layers me penetrate ho kar repair karte hain."
        action = f"Dropper se sirf do se teen drops cheeks par lagayein aur ungliyon se halka tap karein - yeh foran absorb ho kar instant dewy shine deta hai."
        cta = f"Tasdeeq shuda asli {product_name} حاصل karne ke liye bio me diye gaye link par tap karein!"
        action_desc = "Model releases 2-3 drops of serum onto cheekbone, gently tapping to demonstrate instant glass-skin radiance."
    else:
        hook = f"Kya aap bhi radiant, glowing skin chahtay hain? To yeh 1-minute daily routine dekhein!"
        problem = f"Daily stress aur dhool ki wajah se skin dull ho jati hai. {product_name} ka balanced formula skin ko naturally revitalize karta hai."
        action = f"Halka sa apply karein aur circular motion me massage karein - yeh foran skin ko soothing aur fresh look deta hai."
        cta = f"100% verified authentic stock bio link par available hai, Cash on Delivery ke sath abhi apna pack mangwayein!"
        action_desc = "Model massages product smoothly into skin, displaying vibrant refreshed complexion."

    full_text = f"{hook} {problem} {action} {cta}"
    
    caption = f"The secret to radiant skin with authentic {product_name}. 100% verified batch. Cash on Delivery across Pakistan. Link in Bio! #SkincarePakistan #GlowRoutine #{re.sub(r'[^a-zA-Z0-9]', '', product_name)} #AuthenticBeauty"
    
    hashtags = [
        f"#{re.sub(r'[^a-zA-Z0-9]', '', product_name)}",
        "#SkincarePakistan",
        "#BeautyHacks",
        "#ViralReels",
        "#GlowUpRoutine"
    ]

    scenes = [
        {
            "scene_num": 1,
            "title": "Scene 1: Hook & Attention",
            "type": "hook",
            "voiceover": hook,
            "on_screen_text": "Dry & Dull Skin Secret",
            "subtitle": hook,
            "duration": 7
        },
        {
            "scene_num": 2,
            "title": "Scene 2: Problem & Active Formula",
            "type": "problem",
            "voiceover": problem,
            "on_screen_text": "Deep Barrier Repair",
            "subtitle": problem,
            "duration": 8
        },
        {
            "scene_num": 3,
            "title": "Scene 3: Live Application & Glow",
            "type": "action",
            "voiceover": action,
            "on_screen_text": "Dewy Glass-Skin Finish",
            "subtitle": action,
            "duration": 8
        },
        {
            "scene_num": 4,
            "title": "Scene 4: Call to Action & COD",
            "type": "cta",
            "voiceover": cta,
            "on_screen_text": "Order Authentic | Link in Bio",
            "subtitle": cta,
            "duration": 7
        }
    ]

    return {
        "product_name": product_name,
        "language": "roman_urdu",
        "category": category,
        "target_gender": target_gender,
        "hook": hook,
        "problem": problem,
        "solution": action,
        "action": action,
        "cta": cta,
        "action_description": action_desc,
        "full_text": full_text,
        "scenes": scenes,
        "caption": caption,
        "hashtags": hashtags,
        "target_duration": target_duration
    }
