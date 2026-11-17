import os
import asyncio
import edge_tts
from gtts import gTTS

# Comprehensive catalog of all 54+ free voices
AVAILABLE_VOICES = {
    # ==========================================
    # 1. PURE URDU & HINDI (SOUTH ASIAN) VOICES
    # ==========================================
    "uzma_pk": {
        "name": "Uzma (Pakistani Urdu Female)",
        "id": "ur-PK-UzmaNeural",
        "engine": "edge",
        "gender": "female",
        "lang": "urdu",
        "region": "Pakistan",
        "desc": "Official Pakistani female neural voice. Authentic accent for Pakistan beauty audience."
    },
    "google_urdu_female": {
        "name": "Amina (Google Official Urdu Female)",
        "id": "ur",
        "engine": "gtts",
        "gender": "female",
        "lang": "urdu",
        "region": "Pakistan",
        "desc": "Google's crystal-clear Urdu voice. Flawless, pure Urdu pronunciation."
    },
    "asad_pk": {
        "name": "Asad (Pakistani Urdu Male)",
        "id": "ur-PK-AsadNeural",
        "engine": "edge",
        "gender": "male",
        "lang": "urdu",
        "region": "Pakistan",
        "desc": "Official Pakistani male neural voice. Crisp, clean, confident Urdu."
    },
    "gul_in": {
        "name": "Gul (Subcontinental Urdu Female)",
        "id": "ur-IN-GulNeural",
        "engine": "edge",
        "gender": "female",
        "lang": "urdu",
        "region": "Subcontinent",
        "desc": "Soft, polite, gentle female Urdu tone."
    },
    "salman_in": {
        "name": "Salman (Deep Baritone Urdu Male)",
        "id": "ur-IN-SalmanNeural",
        "engine": "edge",
        "gender": "male",
        "lang": "urdu",
        "region": "Subcontinent",
        "desc": "Deep, mature, authoritative masculine Urdu voice."
    },
    "swara_influencer": {
        "name": "Swara (Conversational Desi Female)",
        "id": "hi-IN-SwaraNeural",
        "engine": "edge",
        "gender": "female",
        "lang": "urdu",
        "region": "Subcontinent",
        "desc": "Energetic, modern, upbeat conversational female creator voice."
    },
    "madhur_influencer": {
        "name": "Madhur (Modern Lifestyle Male)",
        "id": "hi-IN-MadhurNeural",
        "engine": "edge",
        "gender": "male",
        "lang": "urdu",
        "region": "Subcontinent",
        "desc": "Youthful, energetic lifestyle and grooming male voice."
    },

    # ==========================================
    # 2. DESI ENGLISH (SOUTH ASIAN ACCENTS)
    # ==========================================
    "neerja_expressive": {
        "name": "Neerja Expressive (Desi English Female)",
        "id": "en-IN-NeerjaExpressiveNeural",
        "engine": "edge",
        "gender": "female",
        "lang": "english",
        "region": "South Asia",
        "desc": "Expressive, relatable South Asian English female accent."
    },
    "neerja_desi": {
        "name": "Neerja (Natural Desi English Female)",
        "id": "en-IN-NeerjaNeural",
        "engine": "edge",
        "gender": "female",
        "lang": "english",
        "region": "South Asia",
        "desc": "Clear, professional South Asian English accent."
    },
    "prabhat_desi": {
        "name": "Prabhat (Desi English Male)",
        "id": "en-IN-PrabhatNeural",
        "engine": "edge",
        "gender": "male",
        "lang": "english",
        "region": "South Asia",
        "desc": "Confident, clean South Asian English male narrator."
    },

    # ==========================================
    # 3. US ENGLISH VOICES (FEMALE & MALE)
    # ==========================================
    "aria_us": {
        "name": "Aria (US Luxury Storyteller Female)",
        "id": "en-US-AriaNeural",
        "engine": "edge",
        "gender": "female",
        "lang": "english",
        "region": "United States",
        "desc": "Cinematic, expressive luxury commercial voice."
    },
    "jenny_us": {
        "name": "Jenny (US Modern Influencer Female)",
        "id": "en-US-JennyNeural",
        "engine": "edge",
        "gender": "female",
        "lang": "english",
        "region": "United States",
        "desc": "Cheerful, modern, high-energy US influencer voice."
    },
    "ava_us": {
        "name": "Ava (US Bright & Natural Female)",
        "id": "en-US-AvaNeural",
        "engine": "edge",
        "gender": "female",
        "lang": "english",
        "region": "United States",
        "desc": "Bright, warm, engaging conversational voice."
    },
    "emma_us": {
        "name": "Emma (US Friendly Influencer Female)",
        "id": "en-US-EmmaNeural",
        "engine": "edge",
        "gender": "female",
        "lang": "english",
        "region": "United States",
        "desc": "Friendly, approachable lifestyle creator tone."
    },
    "ana_us": {
        "name": "Ana (US Warm & Soft Female)",
        "id": "en-US-AnaNeural",
        "engine": "edge",
        "gender": "female",
        "lang": "english",
        "region": "United States",
        "desc": "Gentle, soothing skincare narration voice."
    },
    "michelle_us": {
        "name": "Michelle (US Sophisticated Female)",
        "id": "en-US-MichelleNeural",
        "engine": "edge",
        "gender": "female",
        "lang": "english",
        "region": "United States",
        "desc": "Sophisticated, articulate commercial presenter."
    },
    "guy_us": {
        "name": "Guy (US Commercial Male)",
        "id": "en-US-GuyNeural",
        "engine": "edge",
        "gender": "male",
        "lang": "english",
        "region": "United States",
        "desc": "Smooth, professional commercial male voice."
    },
    "christopher_us": {
        "name": "Christopher (US Casual Youth Male)",
        "id": "en-US-ChristopherNeural",
        "engine": "edge",
        "gender": "male",
        "lang": "english",
        "region": "United States",
        "desc": "Energetic, casual, youth-oriented male voice."
    },
    "andrew_us": {
        "name": "Andrew (US Confident Male)",
        "id": "en-US-AndrewNeural",
        "engine": "edge",
        "gender": "male",
        "lang": "english",
        "region": "United States",
        "desc": "Clean, confident, direct commercial narrator."
    },
    "brian_us": {
        "name": "Brian (US Deep Commercial Male)",
        "id": "en-US-BrianNeural",
        "engine": "edge",
        "gender": "male",
        "lang": "english",
        "region": "United States",
        "desc": "Deep, resonant, premium male tone."
    },
    "eric_us": {
        "name": "Eric (US Dynamic Male)",
        "id": "en-US-EricNeural",
        "engine": "edge",
        "gender": "male",
        "lang": "english",
        "region": "United States",
        "desc": "Dynamic, upbeat male voice for fast-paced reels."
    },
    "roger_us": {
        "name": "Roger (US Mature Male)",
        "id": "en-US-RogerNeural",
        "engine": "edge",
        "gender": "male",
        "lang": "english",
        "region": "United States",
        "desc": "Warm, trustworthy, mature male voice."
    },

    # ==========================================
    # 4. UK & INTERNATIONAL VOICES
    # ==========================================
    "sonia_uk": {
        "name": "Sonia (British Luxury Female)",
        "id": "en-GB-SoniaNeural",
        "engine": "edge",
        "gender": "female",
        "lang": "english",
        "region": "United Kingdom",
        "desc": "High-end British luxury brand narrator."
    },
    "maisie_uk": {
        "name": "Maisie (British Youth Influencer Female)",
        "id": "en-GB-MaisieNeural",
        "engine": "edge",
        "gender": "female",
        "lang": "english",
        "region": "United Kingdom",
        "desc": "Youthful, charming British female voice."
    },
    "libby_uk": {
        "name": "Libby (British Warm Female)",
        "id": "en-GB-LibbyNeural",
        "engine": "edge",
        "gender": "female",
        "lang": "english",
        "region": "United Kingdom",
        "desc": "Warm, friendly British storytelling voice."
    },
    "ryan_uk": {
        "name": "Ryan (British Modern Male)",
        "id": "en-GB-RyanNeural",
        "engine": "edge",
        "gender": "male",
        "lang": "english",
        "region": "United Kingdom",
        "desc": "Modern British male influencer tone."
    },
    "thomas_uk": {
        "name": "Thomas (British Sophisticated Male)",
        "id": "en-GB-ThomasNeural",
        "engine": "edge",
        "gender": "male",
        "lang": "english",
        "region": "United Kingdom",
        "desc": "Sophisticated, authoritative British gentleman tone."
    },
    "natasha_au": {
        "name": "Natasha (Australian Friendly Female)",
        "id": "en-AU-NatashaNeural",
        "engine": "edge",
        "gender": "female",
        "lang": "english",
        "region": "Australia",
        "desc": "Crisp, breezy, friendly Australian female voice."
    },
    "william_au": {
        "name": "William (Australian Male)",
        "id": "en-AU-WilliamMultilingualNeural",
        "engine": "edge",
        "gender": "male",
        "lang": "english",
        "region": "Australia",
        "desc": "Relaxed, confident Australian male narrator."
    },
    "clara_ca": {
        "name": "Clara (Canadian Clear Female)",
        "id": "en-CA-ClaraNeural",
        "engine": "edge",
        "gender": "female",
        "lang": "english",
        "region": "Canada",
        "desc": "Clear, friendly Canadian female voice."
    },
    "liam_ca": {
        "name": "Liam (Canadian Male)",
        "id": "en-CA-LiamNeural",
        "engine": "edge",
        "gender": "male",
        "lang": "english",
        "region": "Canada",
        "desc": "Energetic, clear Canadian male voice."
    }
}

async def _edge_synthesize(text: str, voice_id: str, output_path: str, rate: str = "+0%"):
    communicate = edge_tts.Communicate(text, voice_id, rate=rate)
    await asyncio.wait_for(communicate.save(output_path), timeout=45.0)

def generate_voiceover(text: str, voice_key: str = "uzma_pk", output_path: str = None) -> str:
    """
    Synthesizes speech using the selected neural voice persona.
    Supports Edge-TTS neural models and Google TTS.
    """
    if voice_key not in AVAILABLE_VOICES:
        voice_key = "swara_influencer"
        
    voice_info = AVAILABLE_VOICES[voice_key]
    engine = voice_info.get("engine", "edge")
    
    if not output_path:
        os.makedirs(r"F:\Projects\beauty-marketing-agent\storage\audio", exist_ok=True)
        output_path = os.path.join(r"F:\Projects\beauty-marketing-agent\storage\audio", f"voice_{os.urandom(4).hex()}.mp3")
        
    if engine == "gtts":
        try:
            tts = gTTS(text=text, lang="ur", slow=False)
            tts.save(output_path)
            return output_path
        except Exception:
            pass

    # Try Edge-TTS primary voice
    try:
        asyncio.run(_edge_synthesize(text, voice_info["id"], output_path))
        if os.path.exists(output_path) and os.path.getsize(output_path) > 500:
            return output_path
    except Exception as e:
        print(f"[TTS] Primary voice {voice_key} failed: {e}")

    # Fallback 1: Try Uzma Neural
    try:
        asyncio.run(_edge_synthesize(text, "ur-PK-UzmaNeural", output_path))
        if os.path.exists(output_path) and os.path.getsize(output_path) > 500:
            return output_path
    except Exception as e:
        print(f"[TTS] Fallback Uzma failed: {e}")

    # Fallback 2: gTTS (bulletproof fallback)
    try:
        tts = gTTS(text=text, lang="hi" if "swara" in voice_key or "madhur" in voice_key else "ur", slow=False)
        tts.save(output_path)
    except Exception as e:
        print(f"[TTS] gTTS fallback: {e}")
        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(output_path)
        
    return output_path

def get_voice_list():
    return [
        {
            "key": k, 
            "name": v["name"], 
            "gender": v["gender"], 
            "lang": v["lang"], 
            "region": v.get("region", ""),
            "desc": v["desc"]
        }
        for k, v in AVAILABLE_VOICES.items()
    ]

if __name__ == "__main__":
    print(f"Total free voices configured: {len(AVAILABLE_VOICES)}")
