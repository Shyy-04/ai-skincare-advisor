import json
from groq import Groq, APIStatusError, APIConnectionError, APITimeoutError
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MODEL = "llama-3.3-70b-versatile"

# Create one shared client
_client = Groq(api_key=GROQ_API_KEY)

# INTERNAL HELPERS

def _call(messages: list, temperature: float = 0.7, max_tokens: int = 600) -> str:
    """
    Send messages to Groq and return the reply text.
    'messages' must be a list of dicts: [{"role": "system"|"user"|"assistant", "content": "..."}]
    """
    try:
        response = _client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()

    except APIStatusError as e:
        # e.status_code and e.message give the exact Groq error
        if e.status_code == 401:
            return "❌ Invalid API key. Open agent.py and replace GROQ_API_KEY with your key from console.groq.com"
        return f"❌ Groq error {e.status_code}: {e.message}"

    except APIConnectionError:
        return "❌ Could not connect to Groq. Check your internet connection."

    except APITimeoutError:
        return "❌ Request timed out. Please try again."

    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"


def _clean_history(history: list) -> list:
    """
    Prepare chat history for the API:
    - Keep only 'user' and 'assistant' roles
    - Drop messages with empty content
    - Fix strict alternation (no two consecutive same roles)
    - Limit to last 10 messages to stay within token limits
    """
    # Step 1: filter valid messages
    valid = [
        {"role": m["role"], "content": m["content"].strip()}
        for m in history
        if m.get("role") in ("user", "assistant")
        and isinstance(m.get("content"), str)
        and m["content"].strip()
    ]

    # Step 2: enforce alternation — when two consecutive same roles appear,
    # keep only the last one
    alternated = []
    for msg in valid:
        if alternated and alternated[-1]["role"] == msg["role"]:
            alternated[-1] = msg   # replace, don't append
        else:
            alternated.append(msg)

    # Step 3: history must start with a user message (Groq requirement)
    while alternated and alternated[0]["role"] != "user":
        alternated.pop(0)

    # Step 4: keep last 10 messages
    return alternated[-10:]


# SKIN ANALYSIS

def analyze_skin(skin_type: str, concerns: str, lifestyle: str) -> dict:
    """
    Analyze the user's skin and return a structured dict.
    Falls back to safe defaults if the model returns malformed JSON.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are a dermatologist AI. Respond ONLY with a JSON object — "
                "no markdown, no code fences, no explanation. Pure JSON only."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Skin type: {skin_type}\n"
                f"Concerns: {concerns}\n"
                f"Lifestyle: {lifestyle}\n\n"
                "Return exactly this JSON structure with real values:\n"
                '{"skin_type":"' + skin_type + '",'
                '"oil_level":"Low or Medium or High",'
                '"sensitivity":"Low or Medium or High",'
                '"acne_risk":"Low or Medium or High",'
                '"hydration":"Low or Adequate or High",'
                '"top_concerns":["concern1","concern2"],'
                '"advice":["tip1","tip2","tip3"],'
                '"confidence":80}'
            ),
        },
    ]

    raw = _call(messages, temperature=0.3, max_tokens=400)

    # Strip any accidental markdown fences and parse
    try:
        clean = raw.replace("```json", "").replace("```", "").strip()
        # Sometimes the model wraps in extra text — extract just the JSON object
        start = clean.find("{")
        end   = clean.rfind("}") + 1
        if start != -1 and end > start:
            clean = clean[start:end]
        return json.loads(clean)
    except (json.JSONDecodeError, ValueError):
        # Safe fallback — never crash the app
        return {
            "skin_type":    skin_type,
            "oil_level":    "Medium",
            "sensitivity":  "Medium",
            "acne_risk":    "Medium",
            "hydration":    "Adequate",
            "top_concerns": ["General skin health", "Hydration balance"],
            "advice": [
                "Cleanse twice daily with a gentle cleanser",
                "Apply SPF 30+ every morning",
                "Stay hydrated — at least 8 glasses of water daily",
            ],
            "confidence": 70,
        }


# CHATBOT

_SYSTEM = (
    "You are GlowBot, a professional skincare advisor. "
    "Provide clear, structured, and science-based skincare guidance. "
    
    "Always tailor advice based on skin type, concerns, and sensitivity. "
    
    "When suggesting routines, ALWAYS include: "
    "1) Cleanser, 2) Treatment (active ingredients), 3) Moisturizer, 4) Sunscreen (daytime). "
    
    "Prioritize correct ingredient logic: "
    "- Oily/acne-prone: salicylic acid, niacinamide "
    "- Dry skin: hyaluronic acid, ceramides "
    "- Sensitive skin: gentle, fragrance-free, low-actives "
    
    "Avoid misinformation: "
    "- Do NOT recommend unsuitable products for the skin type "
    "- Do NOT include makeup products (e.g., primers) unless explicitly asked "
    
    "Keep recommendations realistic and safe: "
    "- Warn against over-exfoliation "
    "- Suggest patch testing when introducing new products "
    
    "If giving product examples, ensure they match the skin type correctly. "
    
    "Keep responses under 200 words, clear and practical. Use at most 2 emojis. "
    
    "For serious or persistent skin issues, recommend consulting a dermatologist."
)

def chat_with_bot(user_message: str, chat_history: list, skin_context: dict) -> str:
    """
    Reply to one user message.

    Args:
        user_message  — the NEW message (do NOT include it in chat_history)
        chat_history  — previous turns only [{"role":..., "content":...}, ...]
        skin_context  — analysis dict (may be empty {})
    """
    # Build system prompt — attach skin context if available
    system = _SYSTEM
    if skin_context:
        system += (
            "\n\nThis user's skin profile (use it to personalise your answers):\n"
            f"• Skin type:  {skin_context.get('skin_type', 'Unknown')}\n"
            f"• Oil level:  {skin_context.get('oil_level', 'Unknown')}\n"
            f"• Sensitivity:{skin_context.get('sensitivity', 'Unknown')}\n"
            f"• Acne risk:  {skin_context.get('acne_risk', 'Unknown')}\n"
            f"• Concerns:   {', '.join(skin_context.get('top_concerns', []))}"
        )

    # Clean and trim history, then append the new user message
    history = _clean_history(chat_history)

    messages = (
        [{"role": "system", "content": system}]
        + history
        + [{"role": "user", "content": user_message.strip()}]
    )

    return _call(messages, temperature=0.7, max_tokens=350)
