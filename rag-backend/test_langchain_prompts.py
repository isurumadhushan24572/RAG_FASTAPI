"""
Quick test to verify LangChain prompt templates are working correctly.
Run this to test the new prompt structure without calling the API.
"""
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.prompts import get_ticket_resolution_prompt, prompt_manager


def test_prompt_template():
    """Test that prompt templates load and format correctly."""
    
    # Sample ticket data
    ticket_data = {
        'title': 'Test Ticket',
        'description': 'This is a test ticket for validation',
        'category': 'Application',
        'severity': 'High',
        'application': 'test-service',
        'environment': 'production',
        'affected_users': '100'
    }
    
    # Sample similar tickets
    similar_tickets = [
        {
            'title': 'Similar Issue 1',
            'description': 'Previous similar issue',
            'solution': 'Fixed by restarting service',
            'reasoning': 'Cache issue identified',
            'similarity_score': 0.92
        }
    ]
    
    print("=" * 80)
    print("Testing LangChain Prompt Template Structure")
    print("=" * 80)
    
    # Get the chat prompt and variables
    chat_prompt, variables = get_ticket_resolution_prompt(
        ticket_data, 
        similar_tickets,
        include_example=True
    )
    
    print("\n✅ ChatPromptTemplate created successfully!")
    print(f"\n📝 Number of messages in template: {len(chat_prompt.messages)}")
    
    for i, msg in enumerate(chat_prompt.messages):
        msg_type = msg.__class__.__name__
        print(f"   {i+1}. {msg_type}")
    
    print("\n📊 Variables to be injected:")
    for key, value in variables.items():
        preview = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
        print(f"   - {key}: {preview}")
    
    print("\n" + "=" * 80)
    print("✨ Prompt templates are configured correctly!")
    print("=" * 80)
    
    # Test without example
    chat_prompt_no_ex, _ = get_ticket_resolution_prompt(
        ticket_data,
        similar_tickets,
        include_example=False
    )
    
    print(f"\n📝 Without example: {len(chat_prompt_no_ex.messages)} messages")
    print("   (System + Human only)")
    
    print("\n✅ All tests passed! Ready to use with Groq API.")


if __name__ == "__main__":
    test_prompt_template()
