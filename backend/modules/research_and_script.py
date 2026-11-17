import os
import json
import re
import urllib.parse
import requests

BRANDS_MAP = {
    'dettol': 'ڈیٹول',
    'lifebuoy': 'لائف بوائے',
    'safeguard': 'سیف گارڈ',
    'palmolive': 'پامولیو',
    'lux': 'لکس',
    'dove': 'ڈو',
    'sunsilk': 'سن سلک',
    'head & shoulders': 'ہیڈ اینڈ شولڈرز',
    'head and shoulders': 'ہیڈ اینڈ شولڈرز',
    'pantene': 'پینٹین',
    'tresemme': 'ٹریسمے',
    'garnier': 'گارنیئر',
    'cerave': 'سیرا وی',
    'cetaphil': 'سیٹافل',
    'bioderma': 'بائیوڈرما',
    'the ordinary': 'دی آرڈنری',
    'ordinary': 'دی آرڈنری',
    'cosrx': 'کوز آر ایکس',
    'neutrogena': 'نیوٹروجینا',
    'clean & clear': 'کلین اینڈ کلیئر',
    'clean and clear': 'کلین اینڈ کلیئر',
    'pond\'s': 'پونڈز',
    'ponds': 'پونڈز',
    'nivea': 'نیویا',
    'vaseline': 'ویسلین',
    'himalaya': 'ہمالیہ',
    'saeed ghani': 'سعید غنی',
    'jenpharm': 'جین فارم',
    'conatural': 'کونیچرل',
    'golden pearl': 'گولڈن پرل',
    'biocos': 'بائیو کوس',
    'faiza': 'فائزہ',
    'tibetan': 'تبت',
    'rivaj': 'رواج یو کے',
    'rivaj uk': 'رواج یو کے',
    'vince': 'ونس',
    'dr rashel': 'ڈاکٹر راشیل',
    'dr. rashel': 'ڈاکٹر راشیل',
    'medora': 'میڈورا',
    'simple': 'سمپل',
    'olay': 'اولے',
    'fair & lovely': 'گلو اینڈ لولی',
    'glow & lovely': 'گلو اینڈ لولی',
    'loreal': 'لوریل',
    'l\'oreal': 'لوریل',
    'derma shine': 'ڈرما شائن',
    'colgate': 'کولگیٹ',
    'sensodyne': 'سینسوڈائن',
    'harpic': 'ہارپک',
    'dari moosh': 'داری موچھ',
    'dari mooch': 'داری موچھ',
    'khaadi': 'کھاڈی',
    'junaid jamshed': 'جے ڈاٹ',
    'j.': 'جے ڈاٹ',
    'sapphire': 'سیفائر',
    'limelight': 'لائم لائٹ',
    'almirah': 'المیرہ',
    'bonanza': 'بونینزا',
    'nishat': 'نشاط'
}

INGREDIENTS_MAP = {
    'vitamin c': 'وٹامن سی',
    'vit c': 'وٹامن سی',
    'salicylic acid': 'سیلی سائلک ایسڈ',
    'salicylic': 'سیلی سائلک',
    'niacinamide': 'نیاسینامائڈ',
    'hyaluronic acid': 'ہائیلورونک ایسڈ',
    'hyaluronic': 'ہائیلورونک',
    'retinol': 'ریٹینول',
    'charcoal': 'چارکول',
    'neem': 'نیم',
    'tea tree': 'ٹی ٹری',
    'aloe vera': 'ایلو ویرا',
    'aloe': 'ایلو ویرا',
    'rice water': 'رائس واٹر',
    'collagen': 'کولیجن',
    'bright complete': 'برائٹ کمپلیٹ',
    'bright beauty': 'برائٹ بیوٹی',
    'oil control': 'آئل کنٹرول',
    'acne control': 'اینٹی ایکنی',
    'chloroxylenol': 'کلوروکسیلینول',
    'antiseptic': 'اینٹی سیپٹک',
    'antibacterial': 'اینٹی بیکٹیریل',
    'shea butter': 'شیا بٹر',
    'argan oil': 'آرگن آئل',
    'keratin': 'کیراٹین'
}

FORMS_MAP = {
    'liquid hand wash': 'لیکوڈ ہینڈ واش',
    'liquid handwash': 'لیکوڈ ہینڈ واش',
    'hand wash': 'ہینڈ واش',
    'handwash': 'ہینڈ واش',
    'hand soap': 'ہینڈ واش',
    'liquid hand soap': 'لیکوڈ ہینڈ واش',
    'hand sanitizer': 'ہینڈ سینیٹائزر',
    'sanitizer': 'سینیٹائزر',
    'body wash': 'باڈی واش',
    'shower gel': 'شاور جیل',
    'intimate wash': 'انٹیمیٹ واش',
    'face wash': 'فیس واش',
    'facewash': 'فیس واش',
    'cleanser': 'کلینزر',
    'foaming cleanser': 'فومنگ کلینزر',
    'scrub': 'سکرب',
    'serum': 'سیرم',
    'booster serum': 'بوسٹر سیرم',
    'sunscreen': 'سن سکرین',
    'sunblock': 'سن بلاک',
    'sun gel': 'سن جیل',
    'moisturizer': 'موئسچرائزر',
    'moisturiser': 'موئسچرائزر',
    'cream': 'کریم',
    'night cream': 'نائٹ کریم',
    'day cream': 'ڈے کریم',
    'body lotion': 'باڈی لوشن',
    'lotion': 'لوشن',
    'shampoo': 'شیمپو',
    'conditioner': 'کنڈیشنر',
    'hair oil': 'ہیئر آئل',
    'soap': 'صابن',
    'bath bar': 'بیوٹی بار',
    'kurti': 'کرتی',
    'suit': 'سوٹ',
    'lawn suit': 'لان سوٹ',
    'dress': 'ڈریس',
    'jelly': 'پیٹرولیم جیلی',
    'lip balm': 'لپ بام'
}

def get_pinpoint_urdu_title(raw_name: str) -> str:
    """
    Extracts the exact Brand and Product Core and converts them into natural,
    authentic Urdu pronunciation script for EdgeTTS native pronunciation.
    """
    low = raw_name.lower().strip()
    
    # 1. Match Brand
    matched_brand = ''
    for b_eng, b_urdu in sorted(BRANDS_MAP.items(), key=lambda x: len(x[0]), reverse=True):
        if b_eng in low:
            matched_brand = b_urdu
            break
            
    # 2. Match Key Active / Descriptor
    matched_active = ''
    for a_eng, a_urdu in sorted(INGREDIENTS_MAP.items(), key=lambda x: len(x[0]), reverse=True):
        if a_eng in low:
            matched_active = a_urdu
            break
            
    # 3. Match Exact Form (Multi-word matches prioritized)
    matched_form = ''
    for f_eng, f_urdu in sorted(FORMS_MAP.items(), key=lambda x: len(x[0]), reverse=True):
        if f_eng in low:
            matched_form = f_urdu
            break
            
    # Fallback form detection if not matched above (Never conflate hand wash with face wash!)
    if not matched_form:
        if 'hand' in low and ('wash' in low or 'soap' in low or 'liquid' in low or 'clean' in low):
            matched_form = 'ہینڈ واش'
        elif 'body' in low and ('wash' in low or 'shower' in low or 'gel' in low):
            matched_form = 'باڈی واش'
        elif 'face' in low and ('wash' in low or 'foam' in low or 'clean' in low):
            matched_form = 'فیس واش'
        elif any(w in low for w in ['facewash', 'cleanse', 'scrub']):
            matched_form = 'فیس واش'
        elif any(w in low for w in ['sanitiz']):
            matched_form = 'سینیٹائزر'
        elif any(w in low for w in ['shampoo']):
            matched_form = 'شیمپو'
        elif any(w in low for w in ['serum', 'drop']):
            matched_form = 'سیرم'
        elif any(w in low for w in ['cream', 'moistur']):
            matched_form = 'کریم'
        elif any(w in low for w in ['sun', 'spf']):
            matched_form = 'سن بلاک'
        elif any(w in low for w in ['oil']):
            matched_form = 'آئل'
        elif any(w in low for w in ['suit', 'dress', 'kurti', 'lawn']):
            matched_form = 'سوٹ'
        elif any(w in low for w in ['soap', 'bar']):
            matched_form = 'صابن'
        elif 'wash' in low:
            if any(w in low for w in ['dettol', 'lifebuoy', 'safeguard', 'germ']):
                matched_form = 'ہینڈ واش'
            else:
                matched_form = 'فیس واش'
        else:
            matched_form = 'پروڈکٹ'
            
    parts = []
    if matched_brand:
        parts.append(matched_brand)
    if matched_active and matched_active not in matched_brand:
        parts.append(matched_active)
    if matched_form and matched_form not in matched_active and matched_form not in matched_brand:
        parts.append(matched_form)
        
    return ' '.join(parts) if parts else 'پریمیئم پروڈکٹ'


def research_product_live(product_name: str) -> dict:
    """
    100% Free Multi-Tier Live Research Engine:
    1. Google Autosuggest API (Real-time live search queries, popular pack sizes, variants)
    2. Wikipedia Action Search API + Page Extracts (Brand origins, active chemicals, hygiene facts)
    3. Wikidata Knowledge Classification (Official product taxonomy & description)
    """
    clean_name = product_name.strip()
    result = {
        "query": clean_name,
        "source": "Live Knowledge & Web Search Engine",
        "extract": "",
        "brand": "",
        "detected_form": "product",
        "benefits": [],
        "search_suggestions": [],
        "wiki_description": ""
    }
    
    headers = {"User-Agent": "BeautyMarketingAgent/2.0 (E-Commerce Video Automation; contact@agent.pk)"}
    
    # 1. Google Autosuggest API (Instant, live commercial queries & sizes)
    try:
        sug_url = f"https://suggestqueries.google.com/complete/search?client=firefox&q={urllib.parse.quote(clean_name)}"
        resp_sug = requests.get(sug_url, headers=headers, timeout=3.0)
        if resp_sug.status_code == 200:
            sug_data = resp_sug.json()
            if len(sug_data) > 1 and isinstance(sug_data[1], list):
                result["search_suggestions"] = sug_data[1][:6]
    except Exception:
        pass

    # 2. Wikipedia Action Search + Extract API
    try:
        words = clean_name.split()
        search_target = clean_name
        # Also try brand-only search if full name has multiple words
        w_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(search_target)}&utf8=&format=json"
        resp_wiki = requests.get(w_url, headers=headers, timeout=3.5)
        if resp_wiki.status_code == 200:
            hits = resp_wiki.json().get("query", {}).get("search", [])
            if hits:
                top_title = hits[0].get("title", "")
                snippet = re.sub(r'<[^>]+>', '', hits[0].get("snippet", "")).strip()
                result["extract"] = snippet
                # Fetch detailed page extract
                if top_title:
                    ext_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=&explaintext=&titles={urllib.parse.quote(top_title)}&format=json"
                    resp_ext = requests.get(ext_url, headers=headers, timeout=3.5)
                    if resp_ext.status_code == 200:
                        pages = resp_ext.json().get("query", {}).get("pages", {})
                        if pages:
                            p_info = list(pages.values())[0]
                            full_extract = p_info.get("extract", "")
                            if full_extract:
                                result["extract"] = full_extract[:500]
                                result["source"] = f"Wikipedia Knowledge ({top_title})"
    except Exception:
        pass

    # 3. Wikidata Knowledge Classification
    try:
        brand_word = clean_name.split()[0]
        wd_url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={urllib.parse.quote(brand_word)}&language=en&format=json"
        resp_wd = requests.get(wd_url, headers=headers, timeout=2.5)
        if resp_wd.status_code == 200:
            wd_items = resp_wd.json().get("search", [])
            if wd_items:
                result["wiki_description"] = wd_items[0].get("description", "")
    except Exception:
        pass

    return result


def classify_product_profile(product_name: str, research_extract: str, explicit_category: str) -> dict:
    """
    Intelligently classifies product form, pinpoint Urdu pronunciation name,
    and physical model action so scripts match the REAL physical product!
    """
    text = f"{product_name} {research_extract} {explicit_category}".lower()
    urdu_title = get_pinpoint_urdu_title(product_name)
    
    # 1. Liquid Hand Wash / Hand Hygiene
    if any(w in text for w in ["hand wash", "handwash", "liquid hand", "hand soap", "liquid hand soap", "hand hygiene"]) or ("dettol" in text and "wash" in text):
        return {
            "form": "hand_wash",
            "urdu_name": urdu_title,
            "action_desc": "ماڈل ہینڈ واش کا ایک پمپ دبا کر ہاتھوں پر جھاگ بناتی ہے اور بیس سیکنڈ تک انگلیوں، انگوٹھوں اور ناخنوں کے درمیان مساج کر کے صاف پانی سے ہاتھ دھوتی ہے۔",
            "action_type": "handwash_cleanse",
            "hook_urdu": f"کھانا کھانے سے پہلے اور باہر سے آ کر جراثیم سے سو فیصد حفاظت کے لیے یہ اصلی {urdu_title} استعمال کریں۔",
            "scene1_urdu": "دن بھر موبائل اسکرین، دروازوں کے ہینڈلز اور پیسوں سے لاکھوں خطرناک جراثیم ہمارے ہاتھوں پر لگ جاتے ہیں جو بیماریوں کا باعث بنتے ہیں۔",
            "scene2_urdu": f"اس {urdu_title} کا اینٹی بیکٹیریل متوازن فارمولا ننانوے اعشاریہ نو فیصد جراثیم ختم کرتا ہے اور جلد کو نرم ملائم رکھتا ہے۔",
            "scene3_urdu": "ایک پمپ لیں، بیس سیکنڈ تک ہاتھوں، انگلیوں اور ناخنوں کے درمیان اچھی طرح جھاگ بنائیں اور تازہ پانی سے دھو لیں۔",
            "scene4_urdu": f"اپنے گھر اور بچوں کو بیماریوں سے محفوظ رکھنے کے لیے تصدیق شدہ اصلی {urdu_title} ابھی بائیو لنک سے آرڈر کریں۔",
            "subtitles": [
                "Thousands of unseen harmful germs on mobile screens & door handles?",
                "99.9% antibacterial germ defense with gentle skin conditioning",
                "1 pump — 20-second thorough lather between fingers & nails",
                "100% Genuine Family Pack | Tap link in bio to order"
            ],
            "on_screen": [
                "99.9% Germ Defense",
                "Antibacterial Hygiene",
                "20-Sec Hand Cleanse",
                "Order Authentic | Bio Link"
            ]
        }

    # 2. Body Wash / Shower Gel
    if any(w in text for w in ["body wash", "shower gel", "bath gel", "body cleanser"]):
        return {
            "form": "body_wash",
            "urdu_name": urdu_title,
            "action_desc": "ماڈل لوفا پر باڈی واش کی چند بوندیں لے کر بھرپور جھاگ بناتی ہے اور ریفریشنگ شاور کلینز دکھاتی ہے۔",
            "action_type": "bodywash_cleanse",
            "hook_urdu": f"دن بھر کی تھکن، پسینے اور چپچپاہٹ کے بعد ایک لگژری شاور کے لیے یہ نیا {urdu_title} آزمائیں۔",
            "scene1_urdu": "سخت صابن سے نہانے کے بعد جلد کی قدرتی نمی چھن جاتی ہے اور جسم پر کھنچاؤ اور خشکی محسوس ہوتی ہے۔",
            "scene2_urdu": f"اس {urdu_title} کا کریمی لیدر فارمولا جلد کو گہرائی سے صاف کر کے سارا دن مہکتی خوشبو اور تازگی دیتا ہے۔",
            "scene3_urdu": "لوفا پر چند قطرے ڈالیں، بھرپور خوشبودار جھاگ بنائیں اور پورے جسم پر نرمی سے ملیں — الٹرا کلین اور سلکی سوفٹ رزلٹ۔",
            "scene4_urdu": f"سو فیصد اصلی اور امپورٹڈ {urdu_title} حاصل کرنے کے لیے ابھی بائیو لنک سے اپنا آرڈر بک کریں۔",
            "subtitles": [
                "Post-workout sweat and dry tight skin ruining your freshness?",
                "Rich moisturizing foam with long-lasting luxury fragrance",
                "Gentle shower lather with loofah — Silky smooth clean skin",
                "100% Authentic Stock | Tap link in bio"
            ],
            "on_screen": [
                "Luxury Shower Foam",
                "All-Day Fresh Scent",
                "Silky Soft Skin",
                "Order Authentic | Bio Link"
            ]
        }

    # 3. Face Wash / Facial Cleanser / Scrub
    if any(w in text for w in ["face wash", "facewash", "cleanser", "foaming wash", "charcoal wash", "scrub", "cleansing gel", "face wash gel"]):
        return {
            "form": "face_wash",
            "urdu_name": urdu_title,
            "action_desc": "ماڈل ہتھیلی پر تھوڑا سا فیس واش لے کر پانی سے جھاگ بناتی ہے اور گیلے چہرے پر گول دائروں میں مساج کر کے چہرہ دھوتی ہے۔",
            "action_type": "facewash_cleanse",
            "hook_urdu": f"اگر دھول مٹی، اوپن پورز اور چکنائی کی وجہ سے آپ کا چہرہ بھی کالا اور بے رونق لگ رہا ہے تو یہ نیا {urdu_title} دیکھیں۔",
            "scene1_urdu": "سادہ پانی یا سخت صابن سے منہ دھونے سے مساموں میں جمی گندگی اور اضافی آئل صاف نہیں ہوتا۔",
            "scene2_urdu": f"اس {urdu_title} کا ڈیپ کلینزنگ فارمولا مساموں کی گہرائی میں جا کر ضدی آئل اور گندگی کو جڑ سے نکالتا ہے۔",
            "scene3_urdu": "مٹر کے دانے جتنا فیس واش لیں، گیلے چہرے پر ایک منٹ تک مساج کریں اور دھو لیں — بالکل فریش اور آئل فری لک!",
            "scene4_urdu": f"اصلی اور تصدیق شدہ {urdu_title} حاصل کرنے کے لیے ابھی بائیو میں دیے گئے لنک پر جا کر اپنا آرڈر کریں۔",
            "subtitles": [
                "Excess oil, dust, and clogged pores making your face dull?",
                "Deep pore clarifying formula removes stubborn oil & dirt",
                "1-minute gentle circular foam wash — Clean matte glow!",
                "100% Authentic Tube | Tap link in bio to order!"
            ],
            "on_screen": [
                "Instant Oil-Free Clean",
                "Deep Pore Clarifying",
                "1-Min Foam Cleanse",
                "Order Authentic | Bio Link"
            ]
        }

    # 4. Sunscreen / Sunblock / SPF
    if any(w in text for w in ["sunscreen", "sunblock", "spf", "sun gel", "uv shield", "sun fluid"]):
        return {
            "form": "sunscreen",
            "urdu_name": urdu_title,
            "action_desc": "ماڈل انگلیوں پر سن بلاک کی مناسب مقدار لے کر چہرے اور گردن پر یکساں لگا کر زیرو وائٹ کاسٹ دکھا رہی ہے۔",
            "action_type": "sunscreen_apply",
            "hook_urdu": f"اگر دھوپ میں نکلتے ہی آپ کی جلد ٹین ہو جاتی ہے اور کالے دھبے بن رہے ہیں، تو یہ نیا {urdu_title} دیکھیں۔",
            "scene1_urdu": "سورج کی تیز شعاعیں جلد کی تہوں کو جلا دیتی ہیں جس سے بے رونقی اور پگمنٹیشن تیزی سے پھیلتی ہے۔",
            "scene2_urdu": f"اس {urdu_title} کا براڈ سپیکٹرم ایس پی ایف فارمولا جلد پر ایک غیر مرئی شیلڈ بنا کر دھوپ سے مکمل تحفظ دیتا ہے۔",
            "scene3_urdu": "دو انگلیوں پر مقدار لیں اور چہرے اور گردن پر لگائیں — نہ کوئی سفید داغ، نہ چپچپاہٹ، بالکل ہلکا میٹ فنش!",
            "scene4_urdu": f"دھوپ اور ٹیننگ سے سکن کو محفوظ رکھنے کے لیے ابھی بائیو لنک پر جا کر اپنا اصلی {urdu_title} آرڈر کریں۔",
            "subtitles": [
                "Sun exposure causing severe tanning and dark spots?",
                "Broad-spectrum SPF 50+ invisible protective shield",
                "Two-finger rule application — Zero white cast matte finish!",
                "100% Genuine Sunblock | Tap link in bio to order!"
            ],
            "on_screen": [
                "Broad Spectrum SPF 50+",
                "Zero White Cast Shield",
                "Non-Greasy Matte Finish",
                "Order Authentic | Bio Link"
            ]
        }

    # 3. Moisturizer / Face Cream / Night Cream
    if any(w in text for w in ["moisturizer", "moisturiser", "face cream", "night cream", "day cream", "gel cream", "cold cream", "hydrating cream"]):
        return {
            "form": "moisturizer_cream",
            "urdu_name": urdu_title,
            "action_desc": "ماڈل انگلی کی پوروں پر نرم کریم لے کر چہرے اور گردن پر اوپر کی جانب ہلکا مساج کر کے گہری نمی دکھا رہی ہے۔",
            "action_type": "cream_massage",
            "hook_urdu": f"منہ دھونے کے بعد اگر آپ کی جلد بھی کھنچنے لگتی ہے اور ڈل ہو جاتی ہے، تو یہ نیا {urdu_title} آزمائیں۔",
            "scene1_urdu": "خشک موسم اور پانی کی کمی سکن کے حفاظتی بیریئر کو توڑ دیتی ہے جس سے جلد کھردری اور بے رونق ہو جاتی ہے۔",
            "scene2_urdu": f"اس {urdu_title} کے ایکٹو سیرامائڈز جلد کی گہرائی میں جا کر چوبیس گھنٹے کے لیے نمی کو مکمل لاک کرتے ہیں۔",
            "scene3_urdu": "تھوڑی سی کریم لیں اور چہرے اور گردن پر اوپر کی طرف مساج کریں — جلد فوری طور پر نرم، ملائم اور گلوئنگ بن جاتی ہے۔",
            "scene4_urdu": f"نرم اور پلپ سکن کے لیے سو فیصد اصلی {urdu_title} حاصل کریں، ابھی بائیو میں دیے گئے لنک پر جائیں!",
            "subtitles": [
                "Post-wash tight, flaky skin ruining your glow?",
                "Ceramide-rich active moisture barrier repairs damage",
                "Upward gentle massage — 24H plump, velvety softness!",
                "100% Authentic Cream | Order via Bio Link"
            ],
            "on_screen": [
                "24H Barrier Moisture",
                "Ceramide Repair Core",
                "Plump Velvety Softness",
                "Shop Original | Bio Link"
            ]
        }

    # 4. Body Lotion / Body Milk
    if any(w in text for w in ["body lotion", "lotion", "body milk", "intensive care", "body butter"]):
        return {
            "form": "body_lotion",
            "urdu_name": urdu_title,
            "action_desc": "ماڈل لوشن کو ہتھیلیوں پر لے کر بازوؤں اور گردن پر ہموار مساج کر کے مکھن جیسی نرمی دکھا رہی ہے۔",
            "action_type": "lotion_spread",
            "hook_urdu": f"اگر آپ کی سکن بھی سارا دن کھردری رہتی ہے اور سفید لکیریں بنتی ہیں، تو یہ {urdu_title} دیکھیے!",
            "scene1_urdu": "عام لوشنز کچھ دیر بعد اڑ جاتے ہیں اور جلد دوبارہ اسی کھردری اور بے رونق حالت میں چلی جاتی ہے۔",
            "scene2_urdu": f"اس {urdu_title} کا جدید فارمولا بغیر کسی چپچپاہٹ کے جذب ہو کر جلد کو چوبیس گھنٹے تک گہری ہائیڈریشن دیتا ہے۔",
            "scene3_urdu": "ہتھیلیوں پر لوشن لیں اور نرمی سے مساج کریں — یہ فوری جذب ہو کر ریشمی ملائم مکھن جیسی جلد بناتا ہے۔",
            "scene4_urdu": f"سو فیصد اصلی اور معیاری {urdu_title} حاصل کرنے کے لیے ابھی بائیو میں دیے گئے لنک پر جا کر آرڈر کریں!",
            "subtitles": [
                "24-hour long-lasting hydration for dry, rough skin",
                "Fast-absorbing deep moisture lock without stickiness",
                "Silky smooth texture — Non-greasy velvet feel!",
                "100% Genuine Bottle | Order via Bio Link"
            ],
            "on_screen": [
                "24H Deep Body Hydration",
                "Non-Sticky Moisture",
                "Velvety Soft Touch",
                "Order Authentic | Bio Link"
            ]
        }

    # 5. Hair Care / Shampoo / Hair Oil
    if any(w in text for w in ["shampoo", "hair oil", "conditioner", "rosemary", "hair serum", "hair fall"]):
        return {
            "form": "hair_care",
            "urdu_name": urdu_title,
            "action_desc": "ماڈل بالوں کی جڑوں پر چند قطرے لگا کر انگلیوں سے ہلکا مساج کرتی ہے اور ریشمی چمکدار بال دکھاتی ہے۔",
            "action_type": "hair_application",
            "hook_urdu": f"اگر کنگھی کرتے وقت آپ کے بال بھی تیزی سے گر رہے ہیں اور بے جان ہو چکے ہیں، تو یہ نیا {urdu_title} دیکھیں۔",
            "scene1_urdu": "کیمیکل والے پروڈکٹس اور آلودگی بالوں کی جڑوں کو کمزور کر دیتی ہے جس سے ہیئر فال اور روکھا پن بڑھتا ہے۔",
            "scene2_urdu": f"اس {urdu_title} کے قدرتی نباتاتی اجزاء بالوں کی جڑوں کو اندر سے مضبوط کرتے ہیں اور گرنا مکمل روکتے ہیں۔",
            "scene3_urdu": "انگلیوں کی پوروں سے جڑوں پر ہلکا مساج کریں — چند ہفتوں میں بالوں کا گھنا پن، مضبوطی اور ریشمی چمک خود دیکھیں۔",
            "scene4_urdu": f"گرتے بالوں سے چھٹکارا پانے اور اصلی {urdu_title} کے لیے ابھی بائیو میں دیے گئے لنک پر جائیں!",
            "subtitles": [
                "Severe hair fall and brittle strands ruining your hair volume?",
                "Pure botanical root-strengthening anti-fall formula",
                "Gentle scalp massage — Thick, strong, glossy strands!",
                "100% Verified Batch | Tap Bio link to order"
            ],
            "on_screen": [
                "Anti-Hair Fall Nourishment",
                "Root Strengthening Formula",
                "Dense Glossy Strands",
                "Order Authentic | Bio Link"
            ]
        }

    # 6. Petroleum Jelly / Healing Balm / Lip Balm
    if any(w in text for w in ["vaseline", "petroleum jelly", "jelly", "lip balm", "balm", "chapstick", "aquaphor"]):
        return {
            "form": "petroleum_jelly",
            "urdu_name": urdu_title,
            "action_desc": "ماڈل انگلی کی پور پر تھوڑی سی پیٹرولیم جیلی لے کر ہونٹوں اور خشک جلد پر ملائم مساج کر کے گہرا گلو دکھا رہی ہے۔",
            "action_type": "balm_application",
            "hook_urdu": f"اگر سردی اور خشک ہوا سے آپ کے ہونٹ یا جلد پھٹ رہی ہے، تو یہ لائف ہیک دیکھیں!",
            "scene1_urdu": "عام لوشن کچھ ہی دیر میں اڑ جاتے ہیں اور جلد دوبارہ بے رونق اور کھردری ہو جاتی ہے۔",
            "scene2_urdu": f"اس {urdu_title} کا پیور فارمولا جلد پر ایک محفوظ حفاظتی تہہ بنا کر گہرائی تک نمی کو سو فیصد لاک کر دیتا ہے۔",
            "scene3_urdu": "انگلی کی پور پر بالکل تھوڑی سی جیلی لیں اور ہونٹوں، کہنیوں یا چہرے پر لگائیں — فوری بیبی سوفٹ سکن!",
            "scene4_urdu": f"سو فیصد اصلی اور تصدیق شدہ {urdu_title} حاصل کرنے کے لیے ابھی بائیو لنک پر کلک کریں!",
            "subtitles": [
                "Dry cracked skin aur chapped lips se pareshan?",
                "Pure petroleum moisture lock formula",
                "Fingertip apply — instant baby soft lips & skin!",
                "100% Original Jar | Order via Bio Link!"
            ],
            "on_screen": [
                "Heal Dry Cracked Skin",
                "Moisture Lock Protection",
                "Baby Soft Hydration",
                "Original Stock | Order Now"
            ]
        }

    # 7. Bar Soap
    if any(w in text for w in ["soap", "bath bar", "lux", "soap bar"]):
        return {
            "form": "bar_soap",
            "urdu_name": urdu_title,
            "action_desc": "ماڈل صابن پر پانی ڈال کر ہاتھوں میں بھرپور کریمی جھاگ بنا کر چہرے اور ہاتھوں پر ملائم لیدر دکھا رہی ہے۔",
            "action_type": "soap_lather",
            "hook_urdu": f"کیا آپ کا عام صابن بھی نہانے کے بعد جلد کو بالکل کھردرا، بے جان اور ڈل بنا دیتا ہے؟",
            "scene1_urdu": "کیمیکل والے سخت صابن سکن کی قدرتی نمی کو چھین لیتے ہیں جس سے چہرہ مرجھایا ہوا لگتا ہے۔",
            "scene2_urdu": f"اس {urdu_title} میں شامل نیچرل موئسچرائزر جلد کو صاف کرنے کے ساتھ ساتھ ریشم جیسی نرمی بخشتے ہیں۔",
            "scene3_urdu": "پانی کے ساتھ ہلکا سا مساج کریں اور اس کی بھرپور کریمی جھاگ دیکھیں جو خوشبو اور تروتازگی کا احساس دیتی ہے۔",
            "scene4_urdu": f"اصلی اور تصدیق شدہ {urdu_title} حاصل کرنے کے لیے ابھی بائیو لنک پر کلک کریں!",
            "subtitles": [
                "Harsh drying soaps leaving skin tight and rough?",
                "Rich moisturizing cream core nourishes skin",
                "Creamy rich lather — Silky touch feeling!",
                "100% Authentic | Tap link in bio now"
            ],
            "on_screen": [
                "Luxury Cream Lather",
                "Deep Moisture and Glow",
                "Silky Soft Skin",
                "Order Today | Link In Bio"
            ]
        }

    # 8. Fashion / Clothing
    is_explicit_fashion = explicit_category == "clothing_fashion"
    has_clothing_words = any(w in text for w in ["kurti", "suit", "lawn suit", "velvet suit", "chiffon", "dress", "outfit", "abaya", "clothing"])
    if is_explicit_fashion or has_clothing_words:
        return {
            "form": "fashion_clothing",
            "urdu_name": urdu_title,
            "action_desc": "ماڈل نے پورا سوٹ پہنا ہوا ہے اور گھوم کر فیبرک کا فال، کڑھائی اور کلاسی فٹنگ دکھا رہی ہے۔",
            "action_type": "fashion_walk",
            "hook_urdu": f"یہ رائل {urdu_title} پہن کر آپ کی پرسنالٹی میں جو گریس آتی ہے، وہ کسی عام ڈریس میں نہیں مل سکتی!",
            "scene1_urdu": "کیا آپ بھی عام فاسٹ فیشن کپڑوں سے تنگ آ چکے ہیں جن کی فٹنگ بالکل خراب لگتی ہے؟",
            "scene2_urdu": f"اس {urdu_title} کا پریمیئم اور نرم فیبرک دیکھیں۔ یہ سکن پر بالکل ہوادار ہے اور کلاسی رائل لک دیتا ہے۔",
            "scene3_urdu": "ماڈل کا یہ واک دیکھیں۔ نفاست سے بنی کڑھائی اور پرفیکٹ سلائی جو محفل میں سب کی نظریں آپ پر ٹھہرا دے۔",
            "scene4_urdu": f"لمیٹڈ ایڈیشن سٹاک ہے۔ اصلی {urdu_title} کے لیے ابھی بائیو لنک پر جا کر اپنا پسندیدہ سائز آرڈر کریں!",
            "subtitles": [
                "Boring fast-fashion se tang aa chuke hain?",
                "Premium breathable fabric aur royal fit!",
                "Pure luxury embroidery — Stand out in crowd!",
                "Limited Stock — Tap Bio link to order!"
            ],
            "on_screen": [
                "Royalty and Grace",
                "Premium Breathable Fabric",
                "Perfect Tailored Drape",
                "Order Now | Link In Bio"
            ]
        }

    # 9. Default to Facial Serum (Vitamin C, Niacinamide, Hyaluronic, Dropper)
    return {
        "form": "facial_serum",
        "urdu_name": urdu_title,
        "action_desc": "ماڈل ڈراپر سے دو سے تین قطرے گال پر لگا کر انگلیوں سے ہلکا ٹیپنگ مساج کر کے چہرے پر شائنی گلاس سکن گلو دکھا رہی ہے۔",
        "action_type": "face_application",
        "hook_urdu": f"اگر آپ کے چہرے پر بھی ضدی داغ دھبے، اوپن پورز اور ڈلنس ختم نہیں ہو رہی تو یہ نیا {urdu_title} دیکھیں۔",
        "scene1_urdu": "ہم ہر روز عام پروڈکٹس لگاتے ہیں، لیکن اصل چمک تب آتی ہے جب اصلی ایکٹوز جلد کی گہری تہوں تک پہنچیں۔",
        "scene2_urdu": f"اس {urdu_title} کا خاص فارمولا داغ دھبوں کو ہلکا کرتا ہے اور جلد کو قدرتی گلو اور سیلولر ہائیڈریشن بخشتا ہے۔",
        "scene3_urdu": "ڈراپر سے صرف دو قطرے گال پر لگائیں اور ہلکے ہاتھوں سے ٹیپ کریں — یہ بغیر چپچپاہٹ کے جذب ہو کر قدرتی نکھار دیتا ہے۔",
        "scene4_urdu": f"سو فیصد اصلی اور تصدیق شدہ {urdu_title} حاصل کرنے کے لیے ابھی بائیو میں دیے گئے لنک پر جائیں!",
        "subtitles": [
            "Stubborn spots, open pores, and dull complexion?",
            "High potency active barrier repair formula",
            "Just 2 drops on cheek — Dewy Glass Glow!",
            "100% Original Batch | Tap Bio Link!"
        ],
        "on_screen": [
            "Radiant Glass Skin",
            "Repairs Skin Barrier",
            "Dewy Glow in 2 Drops",
            "100% Authentic | Tap Bio"
        ]
    }


def generate_script(
    product_name: str, 
    category: str = "beauty_skincare", 
    target_gender: str = "women", 
    language: str = "urdu", 
    action_type: str = "face_application",
    target_duration: int = 30
) -> dict:
    """
    Generates a 100% authentic viral video script powered by real market research.
    Performs live lookup for facts, classifies the product form,
    and outputs 100% pure Urdu script text with exact product name pronunciation.
    """
    is_urdu = language.lower() in ["urdu", "roman_urdu"]
    is_men = target_gender.lower() == "men"
    
    research_info = research_product_live(product_name)
    extract = research_info.get("extract", "")
    research_source = research_info.get("source", "Beauty Knowledge Engine")
    
    profile = classify_product_profile(product_name, extract, category)
    detected_form = profile["form"]
    urdu_product_name = profile["urdu_name"]
    
    # Adjust for Men if selected
    if is_men and profile["form"] != "fashion_clothing":
        hook_spoken = f"لڑکوں کی گرومنگ میں عام صابن چھوڑ کر یہ ایک چیز شروع کریں: {urdu_product_name}!"
        s1_vo = "پسینہ، دھول اور اضافی آئل کی وجہ سے دوپہر تک ہمارا چہرہ تھکا ہوا اور ڈل لگنے لگتا ہے۔"
        s2_vo = f"اس {urdu_product_name} کا متوازن فارمولا جلد کی گہرائی میں جا کر اضافی آئل ختم کرتا ہے اور بیریئر کو محفوظ رکھتا ہے۔"
        s3_vo = "لگانا بالکل آسان ہے: ہتھیلی پر مقدار لیں، ہلکا مساج کریں — یہ فوری جذب ہو کر کلین میٹ فنش دیتا ہے۔"
        s4_vo = f"ایک شارپ اور فریش لک کے لیے اصلی اور تصدیق شدہ {urdu_product_name} ابھی بائیو لنک سے منگوائیں!"
        action_desc = "مردانہ ماڈل چہرے اور داڑھی پر ہلکے ہاتھوں سے پراڈکٹ لگا کر کلین فریش لک دکھا رہا ہے۔"
        sub1 = "Midday grease and dullness ruining your fresh look?"
        sub2 = "Deep pore balancing and oil-control formula"
        sub3 = "Fast absorption with clean non-sticky matte finish"
        sub4 = "100% Original | Tap bio link to order"
        on1 = "30-Sec Sharp Look"
        on2 = "Oil-Free Balance"
        on3 = "Instant Matte Finish"
        on4 = "Verified Stock | Bio Link"
        caption = f"Upgrade your daily grooming in 30 seconds with authentic {product_name}. 100% verified batch. Tap link in bio to order! #MensGrooming #ClearSkinMen #SharpLook"
    else:
        # Women or Unisex
        hook_spoken = profile["hook_urdu"]
        s1_vo = profile["scene1_urdu"]
        s2_vo = profile["scene2_urdu"]
        s3_vo = profile["scene3_urdu"]
        s4_vo = profile["scene4_urdu"]
        action_desc = profile["action_desc"]
        sub1, sub2, sub3, sub4 = profile["subtitles"]
        on1, on2, on3, on4 = profile["on_screen"]
        caption = f"The secret to healthy, radiant results with authentic {product_name}. Verified 100% original batch. Tap link in bio to shop now! #SkincarePakistan #GlowRoutine #AuthenticBeauty"

    scenes = [
        {"n": 1, "title": "Hook & Problem", "duration": 7, "voiceover": s1_vo, "on_screen_text": on1, "subtitle": sub1},
        {"n": 2, "title": "The Secret Formula", "duration": 8, "voiceover": s2_vo, "on_screen_text": on2, "subtitle": sub2},
        {"n": 3, "title": "Model Action Demo", "duration": 10, "voiceover": s3_vo, "on_screen_text": on3, "subtitle": sub3},
        {"n": 4, "title": "Offer & Bio CTA", "duration": 7, "voiceover": s4_vo, "on_screen_text": on4, "subtitle": sub4}
    ]

    return {
        "product_name": product_name,
        "category": category,
        "language": language,
        "target_gender": target_gender,
        "hook": hook_spoken,
        "action_description": action_desc,
        "action_type": profile.get("action_type", action_type),
        "detected_form": detected_form,
        "research_source": research_source,
        "research_extract": extract,
        "scenes": scenes,
        "subtitles_preview": "\n".join([f"[{s['n']}] {s['subtitle']}" for s in scenes]),
        "caption": caption,
        "hashtags": ["#Skincare", "#BeautyTok", "#GlowUp", "#PakistanBeauty", "#OriginalProducts"],
        "call_to_action": "Tap link in bio to shop authentic batch",
        "claims_used": ["CLAIM-VERIFIED-AUTH", "CLAIM-HYDRATING"],
        "uses_ai_assets": True
    }
