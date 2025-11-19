"""
Standalone test to verify LangChain prompt templates structure.
Tests file loading and template formatting without API calls.
"""
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate


# Base directory for prompt templates
PROMPT_TEMPLATES_DIR = Path(__file__).parent / "app" / "services" / "prompt_templates"


def load_template_file(filename: str) -> str:
    """Load a prompt template from a text file."""
    template_path = PROMPT_TEMPLATES_DIR / filename
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def test_prompt_files():
    """Test that all required prompt template files exist and load correctly."""
    
    print("=" * 80)
    print("Testing LangChain Prompt Template Files")
    print("=" * 80)
    
    required_files = [
        "system_message.txt",
        "human_message.txt",
        "ai_example_message.txt",
        "similar_ticket_item.txt",
        "no_similar_tickets.txt"
    ]
    
    print("\n📁 Checking template files...")
    for filename in required_files:
        try:
            content = load_template_file(filename)
            preview = content[:80].replace('\n', ' ') + "..."
            print(f"   ✅ {filename}: {len(content)} chars")
            print(f"      Preview: {preview}")
        except FileNotFoundError:
            print(f"   ❌ {filename}: NOT FOUND")
            return False
    
    print("\n" + "=" * 80)
    print("Creating ChatPromptTemplate...")
    print("=" * 80)
    
    # Load templates
    system_msg = load_template_file("system_message.txt")
    human_msg = load_template_file("human_message.txt")
    ai_example_msg = load_template_file("ai_example_message.txt")
    
    # Create example human message for few-shot
    example_human = """### Current Incident Details:
**Title:** Test Ticket
**Description:** Test description
**Category:** Application
**Severity:** High
**Application:** test-app
**Environment:** production
**Affected Users:** 100

### Similar Past Cloud Application Issues (85%+ match confidence):
Test similar tickets...

### Your Task:
Provide analysis."""
    
    # Create ChatPromptTemplate with all messages
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", system_msg),
        ("human", example_human),
        ("ai", ai_example_msg),
        ("human", human_msg)
    ])
    
    print(f"\n✅ ChatPromptTemplate created successfully!")
    print(f"\n📝 Template structure:")
    print(f"   - Total messages: {len(chat_prompt.messages)}")
    for i, msg in enumerate(chat_prompt.messages):
        msg_type = msg.__class__.__name__
        print(f"   {i+1}. {msg_type}")
    
    # Test variable extraction
    print(f"\n📊 Input variables required:")
    for var in chat_prompt.input_variables:
        print(f"   - {var}")
    
    print("\n" + "=" * 80)
    print("✨ All prompt templates are configured correctly!")
    print("=" * 80)
    
    return True


def test_similar_tickets_formatting():
    """Test the similar tickets context formatting."""
    
    print("\n" + "=" * 80)
    print("Testing Similar Tickets Formatting")
    print("=" * 80)
    
    item_template = load_template_file("similar_ticket_item.txt")
    no_similar_template = load_template_file("no_similar_tickets.txt")
    
    # Test with sample ticket
    sample_ticket = {
        'number': 1,
        'similarity_percent': '92.5',
        'title': 'Database Connection Timeout',
        'description': 'Users experiencing timeout errors',
        'solution': 'Increased connection pool size',
        'reasoning': 'Connection pool was exhausted'
    }
    
    formatted = item_template.format(**sample_ticket)
    print(f"\n✅ Similar ticket item formatted:")
    print(formatted[:200] + "...")
    
    print(f"\n✅ No similar tickets message:")
    print(no_similar_template[:100] + "...")
    
    return True


if __name__ == "__main__":
    print("\n🚀 Starting LangChain Prompt Template Tests\n")
    
    success = test_prompt_files()
    if success:
        test_similar_tickets_formatting()
        print("\n✅ All tests passed! Ready to use with Groq API.\n")
    else:
        print("\n❌ Tests failed. Please check the template files.\n")
