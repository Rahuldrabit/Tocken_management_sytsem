"""
AI Agent Orchestration — Hybrid Pipeline
=========================================
Architecture:
  - OpenAI (gpt-4o-mini)       → Ticket classification + language detection
  - OpenAI (text-embedding-3)  → Semantic embedding for pgvector RAG search
  - OpenAI (gpt-4o)            → High-quality multilingual response drafting

LangGraph StateGraph nodes:
  1. classifier_node    — OpenAI extracts category + language as JSON
  2. router_node        — Determines escalation flag based on category & keywords
  3. retriever_node     — pgvector L2Distance similarity search over KnowledgeBase
  4. draft_sales_node   — OpenAI: upbeat, sales-focused reply (multilingual)
  5. draft_technical_node — OpenAI: step-by-step technical reply (multilingual)
  6. draft_billing_node — OpenAI: precise, empathetic billing reply (multilingual)
  7. draft_general_node — OpenAI: friendly general reply (multilingual)
  8. draft_escalation_node — OpenAI: internal human-agent handoff summary
"""

import os
import json
import logging
from typing import TypedDict

from dotenv import load_dotenv
from pathlib import Path

# Load .env from backend root
load_dotenv(Path(__file__).resolve().parent.parent / '.env')

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from .models import KnowledgeBase

logger = logging.getLogger(__name__)

_DB_ENGINE = os.environ.get('DB_ENGINE', 'postgresql')
if _DB_ENGINE != 'sqlite3':
    from pgvector.django import L2Distance

# ──────────────────────────────────────────────────────────────
# Model Configuration (all from .env)
# ──────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
OPENAI_CLASSIFIER_MODEL = os.environ.get('OPENAI_CLASSIFIER_MODEL', 'gpt-4o-mini')
OPENAI_EMBED_MODEL = os.environ.get('OPENAI_EMBED_MODEL', 'text-embedding-3-small')
OPENAI_DRAFT_MODEL = os.environ.get('OPENAI_DRAFT_MODEL', 'gpt-4o')

# ──────────────────────────────────────────────────────────────
# State Definition
# ──────────────────────────────────────────────────────────────
class TicketState(TypedDict):
    ticket_id: int
    title: str
    description: str
    # Filled by classifier_node
    category: str        # e.g. "Technical", "Sales", "Billing", "General", "Urgent"
    language: str        # e.g. "English", "Spanish", "French", "Arabic"
    sentiment: str       # e.g. "Positive", "Neutral", "Frustrated", "Angry"
    # Filled by router_node
    escalate: bool
    # Filled by retriever_node
    context: str         # RAG context from KnowledgeBase
    # Filled by draft node
    draft_response: str
    draft_node_used: str # Which specialized node produced the draft


# ──────────────────────────────────────────────────────────────
# Model Instances
# ──────────────────────────────────────────────────────────────
# OPENAI — for classification
openai_classifier = ChatOpenAI(
    model=OPENAI_CLASSIFIER_MODEL,
    api_key=OPENAI_API_KEY,
    temperature=0.0,  # deterministic for classification
)

# EMBEDDINGS — OpenAI embeddings
openai_embeddings = OpenAIEmbeddings(
    model=OPENAI_EMBED_MODEL,
    api_key=OPENAI_API_KEY,
)

# CHATGPT — high-quality generative drafting (cloud)
chatgpt_drafter = ChatOpenAI(
    model=OPENAI_DRAFT_MODEL,
    api_key=OPENAI_API_KEY,
    temperature=0.7,
)


# ──────────────────────────────────────────────────────────────
# Helper
# ──────────────────────────────────────────────────────────────
def get_embedding(text: str) -> list[float]:
    """Generate a semantic embedding vector using OpenAI."""
    return openai_embeddings.embed_query(text)


# ──────────────────────────────────────────────────────────────
# NODE 1: Classifier (OpenAI — fast, reliable)
# ──────────────────────────────────────────────────────────────
def classifier_node(state: TicketState) -> dict:
    """
    Uses OpenAI (gpt-4o-mini or gpt-4o) to extract:
      - category: Billing | Technical | Sales | General | Urgent
      - language: the language the customer is writing in
      - sentiment: Positive | Neutral | Frustrated | Angry
    Returns strict JSON so the router can act on it.
    """
    prompt = PromptTemplate(
        input_variables=["title", "description"],
        template="""You are an intelligent support ticket classifier.
Analyze the ticket below and respond ONLY with a valid JSON object — no explanation, no markdown.

Ticket Title: {title}
Ticket Description: {description}

JSON format (choose exactly one value for each key):
{{
  "category": "Billing" | "Technical" | "Sales" | "General" | "Urgent",
  "language": "<the language the customer is writing in, e.g. English, Spanish, French, Arabic, German>",
  "sentiment": "Positive" | "Neutral" | "Frustrated" | "Angry"
}}"""
    )
    try:
        chain = prompt | openai_classifier
        raw = chain.invoke({"title": state["title"], "description": state["description"]}).content.strip()
        # Strip markdown fences if model wraps the output
        clean = raw[raw.find("{"):raw.rfind("}") + 1]
        data = json.loads(clean)
        logger.info(f"[Classifier] ticket_id={state['ticket_id']} → {data}")
        return {
            "category": data.get("category", "General"),
            "language": data.get("language", "English"),
            "sentiment": data.get("sentiment", "Neutral"),
        }
    except Exception as e:
        logger.error(f"[Classifier] failed: {e}")
        return {"category": "General", "language": "English", "sentiment": "Neutral"}


# ──────────────────────────────────────────────────────────────
# NODE 2: Router (fast rule-based, no LLM needed)
# ──────────────────────────────────────────────────────────────
def router_node(state: TicketState) -> dict:
    """
    Determines if the ticket should be escalated to a human agent.
    Escalation triggers:
      - Category is Urgent
      - Sentiment is Angry
      - Description contains angry keywords
    """
    angry_keywords = ["angry", "furious", "lawsuit", "unacceptable", "terrible", "disgusting", "refund immediately"]
    desc_lower = state["description"].lower()
    should_escalate = (
        state["category"] == "Urgent"
        or state["sentiment"] == "Angry"
        or any(kw in desc_lower for kw in angry_keywords)
    )
    logger.info(f"[Router] ticket_id={state['ticket_id']} escalate={should_escalate}")
    return {"escalate": should_escalate}


# ──────────────────────────────────────────────────────────────
# NODE 3: Retriever — pgvector RAG (OpenAI embeddings)
# ──────────────────────────────────────────────────────────────
def retriever_node(state: TicketState) -> dict:
    """
    Generates a semantic embedding using OpenAI (text-embedding-3-small),
    then performs an L2 distance vector search against KnowledgeBase.
    Top-3 articles below the distance threshold form the RAG context.
    """
    query_text = f"{state['title']} {state['description']}"
    try:
        embedding = get_embedding(query_text)
        
        if _DB_ENGINE == 'sqlite3':
            # pgvector is not available on sqlite3.
            # Just return some dummy context or grab basic matches using python
            logger.warning("[Retriever] Using sqlite3. pgvector similarity search skipped. Returning first 3 articles.")
            articles = KnowledgeBase.objects.all()[:3]
            contexts = [
                f"[Article: {a.title}]\n{a.content}"
                for a in articles
            ]
        else:
            articles = (
                KnowledgeBase.objects
                .annotate(distance=L2Distance('embedding', embedding))
                .order_by('distance')[:3]
            )
            # Only include articles within a meaningful similarity threshold
            contexts = [
                f"[Article: {a.title}]\n{a.content}"
                for a in articles
                if a.embedding is not None and a.distance < 0.85
            ]
        context_str = "\n\n".join(contexts) if contexts else "No relevant knowledge base articles found."
        logger.info(f"[Retriever] ticket_id={state['ticket_id']} found {len(contexts)} relevant articles")
    except Exception as e:
        logger.error(f"[Retriever] vector search failed: {e}")
        context_str = "Knowledge base unavailable."
    return {"context": context_str}


# ──────────────────────────────────────────────────────────────
# NODE 4–8: Specialized Draft Nodes (ChatGPT — cloud, generative)
# ──────────────────────────────────────────────────────────────
_COMMON_RULES = """
CRITICAL RULES:
1. Write your ENTIRE response in {language}. Do NOT use English if the language is different.
2. Base your answer ONLY on the Knowledge Base provided. Do not invent facts.
3. If the Knowledge Base is insufficient, say so politely and promise a follow-up.
4. Be concise, warm, and professional.
"""

def _run_chatgpt_draft(system_persona: str, state: TicketState) -> str:
    """Shared helper that invokes ChatGPT with a given persona prompt."""
    prompt = PromptTemplate(
        input_variables=["persona", "description", "context", "language"],
        template="""{persona}

Customer Message:
{description}

Knowledge Base Context:
{context}
""" + _COMMON_RULES
    )
    try:
        chain = prompt | chatgpt_drafter
        result = chain.invoke({
            "persona": system_persona,
            "description": state["description"],
            "context": state["context"],
            "language": state["language"],
        })
        return result.content
    except Exception as e:
        logger.error(f"[Draft] ChatGPT call failed: {e}")
        return f"We received your request and our team will respond shortly. (AI drafting unavailable: {e})"


def draft_technical_node(state: TicketState) -> dict:
    persona = ("You are a precise, analytical Technical Support Engineer. "
               "Provide clear, step-by-step troubleshooting instructions.")
    draft = _run_chatgpt_draft(persona, state)
    logger.info(f"[Draft/Technical] ticket_id={state['ticket_id']}")
    return {"draft_response": draft, "draft_node_used": "Technical (ChatGPT)"}


def draft_sales_node(state: TicketState) -> dict:
    persona = ("You are an enthusiastic, customer-first Sales Associate. "
               "Address the customer's sales enquiry warmly and highlight value.")
    draft = _run_chatgpt_draft(persona, state)
    logger.info(f"[Draft/Sales] ticket_id={state['ticket_id']}")
    return {"draft_response": draft, "draft_node_used": "Sales (ChatGPT)"}


def draft_billing_node(state: TicketState) -> dict:
    persona = ("You are a meticulous and empathetic Billing Specialist. "
               "Explain billing details clearly and offer concrete next steps.")
    draft = _run_chatgpt_draft(persona, state)
    logger.info(f"[Draft/Billing] ticket_id={state['ticket_id']}")
    return {"draft_response": draft, "draft_node_used": "Billing (ChatGPT)"}


def draft_general_node(state: TicketState) -> dict:
    persona = ("You are a friendly, helpful Customer Support Representative. "
               "Answer the customer's general question politely and helpfully.")
    draft = _run_chatgpt_draft(persona, state)
    logger.info(f"[Draft/General] ticket_id={state['ticket_id']}")
    return {"draft_response": draft, "draft_node_used": "General (ChatGPT)"}


def draft_escalation_node(state: TicketState) -> dict:
    """
    For escalated tickets, ChatGPT writes an internal handoff summary
    for the human agent — NOT a customer-facing reply.
    """
    prompt = PromptTemplate(
        input_variables=["title", "description", "category", "sentiment", "language"],
        template="""You are a support supervisor AI preparing a handoff note for a human agent.

Ticket Title: {title}
Category: {category}
Detected Language: {language}
Customer Sentiment: {sentiment}
Customer Message:
{description}

Write a concise INTERNAL HANDOFF NOTE (3-5 bullet points) for the human agent that:
- Summarises the core issue
- Flags the urgency and sentiment
- Suggests what the agent should address first
- Notes the customer's language so the agent can respond appropriately

Do NOT write a customer-facing reply."""
    )
    try:
        chain = prompt | chatgpt_drafter
        result = chain.invoke({
            "title": state["title"],
            "description": state["description"],
            "category": state["category"],
            "sentiment": state["sentiment"],
            "language": state["language"],
        })
        draft = result.content
    except Exception as e:
        logger.error(f"[Draft/Escalation] ChatGPT call failed: {e}")
        draft = f"ESCALATION REQUIRED — Ticket #{state['ticket_id']}: {state['title']}"
    logger.info(f"[Draft/Escalation] ticket_id={state['ticket_id']}")
    return {"draft_response": draft, "draft_node_used": "Escalation Handoff (ChatGPT)"}


# ──────────────────────────────────────────────────────────────
# Conditional Edge — Route to specialist after retriever
# ──────────────────────────────────────────────────────────────
def route_to_specialist(state: TicketState) -> str:
    if state["escalate"]:
        return "draft_escalation_node"
    category = state["category"].lower()
    if "technical" in category:
        return "draft_technical_node"
    if "sales" in category:
        return "draft_sales_node"
    if "billing" in category:
        return "draft_billing_node"
    return "draft_general_node"


# ──────────────────────────────────────────────────────────────
# Build & Compile the LangGraph StateGraph
# ──────────────────────────────────────────────────────────────
workflow = StateGraph(TicketState)

workflow.add_node("classifier_node", classifier_node)
workflow.add_node("router_node", router_node)
workflow.add_node("retriever_node", retriever_node)
workflow.add_node("draft_technical_node", draft_technical_node)
workflow.add_node("draft_sales_node", draft_sales_node)
workflow.add_node("draft_billing_node", draft_billing_node)
workflow.add_node("draft_general_node", draft_general_node)
workflow.add_node("draft_escalation_node", draft_escalation_node)

# Entry point → sequence
workflow.set_entry_point("classifier_node")
workflow.add_edge("classifier_node", "router_node")
workflow.add_edge("router_node", "retriever_node")

# Conditional routing to the right specialist after retrieval
workflow.add_conditional_edges(
    "retriever_node",
    route_to_specialist,
    {
        "draft_technical_node": "draft_technical_node",
        "draft_sales_node": "draft_sales_node",
        "draft_billing_node": "draft_billing_node",
        "draft_general_node": "draft_general_node",
        "draft_escalation_node": "draft_escalation_node",
    }
)

# All draft nodes lead to END
for node in [
    "draft_technical_node",
    "draft_sales_node",
    "draft_billing_node",
    "draft_general_node",
    "draft_escalation_node",
]:
    workflow.add_edge(node, END)

# Compile once at import time
ticket_agent_graph = workflow.compile()
