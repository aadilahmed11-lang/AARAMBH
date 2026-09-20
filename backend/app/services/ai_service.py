import json
import httpx
from ..config import GROQ_API_KEY, GROQ_MODEL

async def extract_profile_with_ai(text: str):
    if not GROQ_API_KEY:
        return fallback_profile(text)
    prompt = """Extract an entrepreneur profile from the user's speech/text.
Return ONLY JSON with these keys:
category, annual_income, occupation, business_type, business_stage,
loan_amount, state, district, city.
Use null when unknown. Do not invent values.
Input:
""" + text
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json={"model": GROQ_MODEL, "temperature": 0,
                      "messages":[{"role":"user","content":prompt}]}
            )
            r.raise_for_status()
            content = r.json()["choices"][0]["message"]["content"]
            content = content.replace("```json","").replace("```","").strip()
            return json.loads(content)
    except Exception:
        return fallback_profile(text)

def fallback_profile(text: str):
    t = text.lower()
    p = {}
    categories = {"sc":"SC", "scheduled caste":"SC", "dalit":"SC"}
    for k,v in categories.items():
        if k in t: p["category"] = v
    for k,v in [("tailor","Tailoring"),("dairy","Dairy"),("shop","Retail"),("farming","Agriculture"),
                ("food","Food Business"),("transport","Transport"),("mobile","Mobile Repair")]:
        if k in t: p["business_type"] = v
    import re
    nums = re.findall(r"\d+(?:\.\d+)?", t.replace(",",""))
    if nums:
        # Heuristic only; user can edit the result before saving.
        p["loan_amount"] = float(nums[-1])
    return p
