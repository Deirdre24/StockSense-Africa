from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

def run_procurement_agent(inventory_df, suppliers: list, business_name: str) -> dict:
    """
    Autonomous procurement agent:
    - Perceives stock levels
    - Reasons about risks
    - Acts with decisions and order messages
    """

    # ---- STEP 1: CLASSIFY STOCK ----
    critical = []
    warning = []
    healthy = []

    for _, row in inventory_df.iterrows():
        if row["days_left"] < 5:
            critical.append(row["product"])
        elif row["days_left"] < 10:
            warning.append(row["product"])
        else:
            healthy.append(row["product"])

    # ---- STEP 2: FORMAT SUPPLIERS ----
    supplier_text = "\n".join([
        f"{s['name']} - {s['product']}: P{s['price']}"
        for s in suppliers
    ]) if suppliers else "No supplier data available."

    # ---- STEP 3: BUILD PROMPT ----
    prompt = f"""
You are an autonomous procurement decision agent for {business_name}, a retail shop in Botswana.

IMPORTANT RULES:
- Do NOT repeat inventory numbers
- Do NOT restate dashboard data
- Do NOT describe stock levels
- ONLY focus on decisions and actions

Your job:
1. Decide what must be ordered TODAY
2. Identify supply risks or gaps
3. Choose best supplier options if available
4. Draft WhatsApp-ready order messages
5. Give a business health score (1-10)

CRITICAL ITEMS:
{', '.join(critical) if critical else 'None'}

WARNING ITEMS:
{', '.join(warning) if warning else 'None'}

AVAILABLE SUPPLIERS:
{supplier_text}

Respond EXACTLY in this format:

🧠 REASONING:
(Only insights + decisions, no repetition of data)

⚡ ACTIONS:
- bullet list of decisions only

📋 ORDER MESSAGE:
(WhatsApp-ready message or "No urgent orders needed today.")

📊 SCORE:
(number / 10 + one sentence explanation)
"""

    # ---- STEP 4: CALL GROQ ----
    client = Groq(api_key=os.getenv("GROQ_API_KEY") or "your_actual_key_here")

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    result = response.choices[0].message.content

    # ---- STEP 5: RETURN ----
    return {
        "output": result,
        "critical": critical,
        "warning": warning,
        "healthy": healthy,
        "ran": True
    }