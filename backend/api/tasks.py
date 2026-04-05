from celery import shared_task
from django.contrib.auth.models import User
from .models import Ticket, TicketComment
from .agents import ticket_agent_graph

@shared_task
def process_new_ticket_task(ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        
        # Initialize internal state for LangGraph
        initial_state = {
            "ticket_id": ticket.id,
            "title": ticket.title,
            "description": ticket.description,
            "category": "",
            "context": "",
            "draft_response": "",
            "escalate": False
        }
        
        # Invoke LangGraph Multi-Agent Pipeline
        # NOTE: State mutations happen within the StateGraph nodes
        final_state = ticket_agent_graph.invoke(initial_state)
        
        # Save Draft to Comments
        system_user, _ = User.objects.get_or_create(username='ai_agent', email='ai@system.local')
        
        prefix = "[AI DRAFT]" if not final_state.get('escalate') else "[ESCALATION REVIEW NEEDED]"
        
        TicketComment.objects.create(
            ticket=ticket,
            user=system_user,
            comment_text=f"{prefix} {final_state.get('draft_response')}"
        )
        print(f"AI workflow completed for ticket {ticket_id}")
    except Exception as e:
        print(f"Error processing ticket {ticket_id}: {str(e)}")
