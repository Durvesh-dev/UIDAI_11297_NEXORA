import os
import json
from google.genai import Client

# Try to create client, but handle if API key is missing or quota exceeded
try:
    client = Client(api_key=os.getenv("GEMINI_API_KEY"))
except:
    client = None

# Flag to track if API is working
API_AVAILABLE = True

def is_aadhaar_related(question: str) -> bool:
    """Check if question is related to Aadhaar/UIDAI only"""
    aadhaar_keywords = [
        "aadhaar", "aadhar", "uidai", "enrol", "enrollment", "update",
        "demographic", "biometric", "state", "district", "activity",
        "trend", "predict", "forecast", "age", "child", "adult",
        "bank", "link", "mobile", "address", "document", "card",
        "pan", "verification", "authentication", "otp", "maadhaar",
        "e-aadhaar", "pvc", "center", "centre", "seva kendra"
    ]
    
    # Non-Aadhaar keywords that should be rejected
    non_aadhaar = [
        "ice cream", "movie", "game", "sport", "music", "food",
        "recipe", "weather", "cricket", "football", "python",
        "java", "programming", "coding", "machine learning", "ai",
        "artificial intelligence", "deep learning", "neural"
    ]
    
    q_lower = question.lower()
    
    # Reject if contains non-Aadhaar topics
    for term in non_aadhaar:
        if term in q_lower and "aadhaar" not in q_lower and "aadhar" not in q_lower:
            return False
    
    # Accept if contains Aadhaar keywords
    return any(kw in q_lower for kw in aadhaar_keywords)

def get_rejection_response():
    """Return rejection message for non-Aadhaar questions"""
    return "❌ This question is not related to Aadhaar or UIDAI services. Please ask questions about Aadhaar enrollment, updates, state-wise trends, linking Aadhaar to bank/mobile, or UIDAI policies."

def get_simple_answer(data_summary: dict, prediction_summary: dict = None, question: str = "") -> str:
    """
    Generate a simple, direct answer for chat questions.
    """
    global API_AVAILABLE
    
    # Check if question is Aadhaar related
    if question and not is_aadhaar_related(question):
        return get_rejection_response()
    
    # Try Gemini API first if available
    if API_AVAILABLE and client:
        try:
            context_parts = build_context(data_summary, prediction_summary, question)
            context = "\n".join(context_parts)
            
            prompt = f"""
You are an Aadhaar expert assistant for UIDAI.

{context}

User Question: {question}

Provide a clear, concise, and direct answer to the question. Use the data provided above.
- Be specific and include numbers where relevant
- Keep the answer focused and easy to understand
- Do not use Finding/Impact/Recommendation format
- Just give a straightforward answer
"""
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"Gemini API error: {e}")
            API_AVAILABLE = False
    
    # Fallback: Generate simple answer from data
    return generate_simple_answer_fallback(data_summary, prediction_summary, question)

def generate_simple_answer_fallback(data_summary: dict, prediction_summary: dict = None, question: str = "") -> str:
    """Generate simple answer without API"""
    q_lower = question.lower() if question else ""
    
    # State-related questions
    if any(kw in q_lower for kw in ['state', 'highest', 'lowest', 'most', 'least']):
        highest = data_summary.get('highest_state', 'N/A')
        lowest = data_summary.get('lowest_state', 'N/A')
        top_states = data_summary.get('top_5_states', {})
        
        if top_states:
            top_list = ", ".join([f"**{s}** ({v:,.0f})" for s, v in list(top_states.items())[:5]])
            return f"📊 **Top States by Aadhaar Activity:**\n\n{top_list}\n\n**Highest:** {highest}\n**Lowest:** {lowest}"
        return f"**Highest activity:** {highest}\n**Lowest activity:** {lowest}"
    
    # Age-related questions
    if any(kw in q_lower for kw in ['age', 'child', 'adult', 'demographic', 'young']):
        age_data = data_summary.get('age_groups', {})
        if age_data:
            age_info = "\n".join([f"- **{k.replace('_', '-')}**: {v:,}" for k, v in age_data.items()])
            return f"📊 **Age Group Distribution:**\n\n{age_info}"
        return "Age group data not available in the current dataset."
    
    # Bank/Link questions
    if any(kw in q_lower for kw in ['bank', 'link', 'connect', 'mobile', 'pan']):
        return """🔗 **How to Link Aadhaar:**

- **Bank:** Visit branch with Aadhaar OR use net banking
- **Mobile:** Call 14546 or visit operator store  
- **PAN:** Use Income Tax e-filing portal (incometax.gov.in)

Always use official UIDAI channels: **uidai.gov.in** or **1947** helpline"""
    
    # Update questions
    if any(kw in q_lower for kw in ['update', 'change', 'correction']):
        return """📝 **Aadhaar Update Options:**

- **Online:** myaadhaar.uidai.gov.in (address, mobile, email)
- **Offline:** Visit nearest Aadhaar Seva Kendra

**Documents needed:** Proof of identity/address for changes
**Free updates:** One free update allowed; Rs.50 for additional changes"""
    
    # Total/Overall questions
    total = data_summary.get('total_activity', 0)
    total_rows = data_summary.get('total_rows', 0)
    highest = data_summary.get('highest_state', 'N/A')
    
    return f"""📊 **Data Summary:**

- **Total Records:** {total_rows:,}
- **Total Activity:** {total:,}
- **Top State:** {highest}
- **States Covered:** {data_summary.get('total_states', 0)}"""

def generate_insight_from_data(data_summary: dict, prediction_summary: dict = None, question: str = "") -> str:
    """
    Generate insights from data statistics.
    Uses Gemini API if available, otherwise uses template-based responses.
    """
    global API_AVAILABLE
    
    # Check if question is Aadhaar related
    if question and not is_aadhaar_related(question):
        return get_rejection_response()
    
    # Try Gemini API first if available
    if API_AVAILABLE and client:
        try:
            context_parts = build_context(data_summary, prediction_summary, question)
            context = "\n".join(context_parts)
            
            prompt = f"""
You are a senior policy analyst for UIDAI (Unique Identification Authority of India).

Analyze the following Aadhaar data and provide actionable insights.

{context}

Answer the user's question if provided, using the data above.

Provide your response using EXACTLY this format:

Finding:
[Clear, data-driven statement about what the analysis reveals. Include specific numbers from the data.]

Impact:
[Explain the operational, policy, or strategic implications of these findings]

Recommendation:
[Specific, actionable recommendations for UIDAI based on the data]

Be specific and use actual numbers from the data provided.
"""
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"Gemini API error: {e}")
            API_AVAILABLE = False  # Disable for future calls
    
    # Fallback: Generate response from data without API
    return generate_data_insight_fallback(data_summary, prediction_summary, question)

def build_context(data_summary, prediction_summary, question):
    """Build context string from data"""
    context_parts = []
    
    if question:
        context_parts.append(f"User Question: {question}\n")
    
    context_parts.append("=== ACTUAL DATA STATISTICS ===")
    context_parts.append(f"Total Records: {data_summary.get('total_rows', 0):,}")
    
    if 'total_activity' in data_summary:
        context_parts.append(f"Total Aadhaar Activity: {data_summary.get('total_activity', 0):,}")
        context_parts.append(f"Average Activity per Record: {data_summary.get('avg_activity', 0):,.1f}")
    
    if 'highest_state' in data_summary:
        context_parts.append(f"\nHighest Activity State: {data_summary.get('highest_state')}")
        context_parts.append(f"Lowest Activity State: {data_summary.get('lowest_state')}")
        context_parts.append(f"Total States: {data_summary.get('total_states', 0)}")
    
    if 'top_5_states' in data_summary:
        context_parts.append("\nTop 5 States by Activity:")
        for state, activity in data_summary['top_5_states'].items():
            context_parts.append(f"  - {state}: {activity:,.0f}")
    
    if 'age_groups' in data_summary:
        context_parts.append("\nAge Group Distribution:")
        for age, count in data_summary['age_groups'].items():
            age_label = age.replace('_', '-').replace('age-', '')
            context_parts.append(f"  - {age_label}: {count:,}")
    
    if prediction_summary:
        context_parts.append("\n=== MODEL PREDICTIONS ===")
        context_parts.append(f"Total Predicted Activity: {prediction_summary.get('total_predicted', 0):,.0f}")
    
    return context_parts

def generate_data_insight_fallback(data_summary: dict, prediction_summary: dict = None, question: str = "") -> str:
    """Generate insight without API using data templates"""
    
    q_lower = question.lower() if question else ""
    
    # State-related questions
    if any(kw in q_lower for kw in ['state', 'highest', 'lowest', 'most', 'least']):
        highest = data_summary.get('highest_state', 'N/A')
        lowest = data_summary.get('lowest_state', 'N/A')
        total_states = data_summary.get('total_states', 0)
        
        top_states = ""
        if 'top_5_states' in data_summary:
            top_states = ", ".join([f"{s} ({v:,.0f})" for s, v in list(data_summary['top_5_states'].items())[:3]])
        
        return f"""
Finding:
{highest} has the highest Aadhaar activity among {total_states} states. Top states: {top_states}. {lowest} has the lowest activity.

Impact:
High-activity states require more enrollment centers and staff. Low-activity states may need awareness campaigns or better accessibility.

Recommendation:
Allocate additional resources to {highest} and other high-demand states. Investigate barriers in {lowest} and implement targeted outreach programs.
""".strip()
    
    # Age-related questions
    if any(kw in q_lower for kw in ['age', 'child', 'adult', 'demographic', '18', 'young']):
        age_data = data_summary.get('age_groups', {})
        if age_data:
            highest_age = max(age_data, key=age_data.get) if age_data else 'N/A'
            highest_age_label = highest_age.replace('_', '-').replace('age-', '')
            return f"""
Finding:
Age group {highest_age_label} contributes the highest share of Aadhaar activity with {age_data.get(highest_age, 0):,} records.

Impact:
{highest_age_label} age group drives most enrollment/update activity, suggesting focus on child enrollment or adult updates depending on the pattern.

Recommendation:
Ensure adequate child-friendly enrollment facilities if 0-5 dominates, or streamline adult update processes if 18+ is highest.
""".strip()
    
    # Bank/Link questions
    if any(kw in q_lower for kw in ['bank', 'link', 'connect', 'mobile', 'pan']):
        return """
Finding:
Aadhaar can be linked to bank accounts, mobile numbers, and PAN through multiple official channels.

Impact:
Linking Aadhaar enables direct benefit transfers (DBT), simplified KYC, and reduces fraud in government schemes.

Recommendation:
To link Aadhaar:
- Bank: Visit branch with Aadhaar or use net banking
- Mobile: Call 14546 or visit operator store
- PAN: Use Income Tax e-filing portal
Always use official UIDAI channels (uidai.gov.in) for security.
""".strip()
    
    # Update questions
    if any(kw in q_lower for kw in ['update', 'change', 'correction', 'address', 'name', 'photo']):
        return """
Finding:
Aadhaar updates can be done for demographic data (name, address, DOB) and biometric data (fingerprints, iris, photo).

Impact:
Regular updates ensure accurate records for service delivery and prevent authentication failures.

Recommendation:
- Online updates: Visit myaadhaar.uidai.gov.in (limited changes)
- Offline updates: Visit nearest Aadhaar Seva Kendra with supporting documents
- Biometric update: Must be done at enrollment center
Free updates available once; nominal fee for subsequent changes.
""".strip()
    
    # General/Overview questions
    total = data_summary.get('total_activity', 0)
    total_rows = data_summary.get('total_rows', 0)
    highest = data_summary.get('highest_state', 'N/A')
    
    return f"""
Finding:
Analysis of {total_rows:,} records shows total Aadhaar activity of {total:,}. {highest} leads in activity volume across all states.

Impact:
This data reveals geographic distribution of Aadhaar operations and helps identify resource allocation priorities.

Recommendation:
Focus operational resources on high-activity regions like {highest}. Monitor trends to optimize enrollment center capacity and staffing.
""".strip()

def answer_general_question(question: str, data_summary: dict = None) -> str:
    """Answer general Aadhaar-related questions"""
    global API_AVAILABLE
    
    # Check if Aadhaar related
    if not is_aadhaar_related(question):
        return get_rejection_response()
    
    # Try API first
    if API_AVAILABLE and client:
        try:
            prompt = f"""
You are an Aadhaar expert assistant for UIDAI.

User Question: {question}

Provide a helpful answer about Aadhaar services using this format:

Finding:
[Direct answer to the question]

Impact:
[Why this is important]

Recommendation:
[Practical next steps]
"""
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return response.text.strip()
        except:
            API_AVAILABLE = False
    
    # Fallback for common questions
    return generate_data_insight_fallback(data_summary or {}, None, question)

def generate_suggestions_from_insight(insight: str, data_summary: dict = None) -> str:
    """Generate suggestions based on insights"""
    global API_AVAILABLE
    
    # Try API first
    if API_AVAILABLE and client:
        try:
            prompt = f"""
Based on this insight, provide 3-5 actionable suggestions:

{insight}

Format:
Suggestions:
1. [Action 1]
2. [Action 2]
...
"""
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return response.text.strip()
        except:
            API_AVAILABLE = False
    
    # Fallback suggestions based on data
    highest = data_summary.get('highest_state', 'high-activity states') if data_summary else 'high-activity states'
    lowest = data_summary.get('lowest_state', 'low-activity states') if data_summary else 'low-activity states'
    
    return f"""
Suggestions:
1. Increase enrollment center capacity in {highest} to handle high demand
2. Launch awareness campaigns in {lowest} to improve Aadhaar adoption
3. Deploy mobile enrollment units in rural and underserved areas
4. Implement real-time monitoring dashboard for state-wise activity tracking
5. Train additional operators to reduce wait times at busy centers
""".strip()

# Legacy functions
def classify_intent(question: str) -> bool:
    return is_aadhaar_related(question)

def generate_human_insight(context: str) -> str:
    return generate_data_insight_fallback({'context': context}, None, "")
