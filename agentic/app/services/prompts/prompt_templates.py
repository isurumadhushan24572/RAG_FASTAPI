"""
LangChain prompt templates for the agentic RAG system.
Uses ChatPromptTemplate for structured prompts.
Prompts are broken down into modular parts for easy updates.
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import List, Dict, Any


# ============================================================================
# AGENT PROMPT COMPONENTS - Easily editable parts
# ============================================================================

AGENT_ROLE = "You are an intelligent AI assistant with access to specialized tools to answer questions accurately."

AGENT_CAPABILITIES = """Your capabilities:
1. **vector_search**: Search through a knowledge base of stored documents for relevant information
2. **web_search**: Search the internet for current information, recent events, or general knowledge"""

AGENT_GUIDELINES = """Guidelines:
- Use the vector_search tool first when the question might be answered by stored documents
- Use the web_search tool when you need current information, recent events, or information not in the knowledge base and give high priority for latest ones
- You can use multiple tools in sequence to gather comprehensive information
- Always cite your sources when providing information
- If you cannot find relevant information after using the tools, acknowledge that clearly
- Provide clear, concise, and accurate answers
- Be helpful and informative"""

AGENT_TOOLS_SECTION = """You have access to the following tools:

{tools}"""

AGENT_FORMAT = """Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question"""

AGENT_BEGIN = """Begin!

Question: {input}
Thought: {agent_scratchpad}"""


# ============================================================================
# RAG SYNTHESIS PROMPT COMPONENTS
# ============================================================================

RAG_SYNTHESIS_SYSTEM_ROLE = "You are an AI assistant that synthesizes information from multiple sources to answer questions."

RAG_SYNTHESIS_TASKS = """Your task:
1. Review all the provided context from different sources
2. Extract relevant information that answers the user's question
3. Synthesize a coherent, comprehensive answer
4. Cite specific sources when making claims
5. If information is conflicting, note the differences
6. If information is insufficient, state what's missing"""

RAG_SYNTHESIS_BEHAVIOR = "Be accurate, concise, and helpful."

RAG_SYNTHESIS_HUMAN_TEMPLATE = """Question: {question}

Context from sources:
{context}

Please provide a comprehensive answer based on the context above. Include source citations."""


# ============================================================================
# DOCUMENT Q&A PROMPT COMPONENTS
# ============================================================================

DOCUMENT_QA_SYSTEM_ROLE = "You are an AI assistant specialized in answering questions based on provided documents."

DOCUMENT_QA_TASKS = """Your task:
1. Read the provided document content carefully
2. Answer the user's question based ONLY on the information in the documents
3. If the answer is not in the documents, say so clearly
4. Quote specific parts of the documents to support your answer
5. Be precise and accurate"""

DOCUMENT_QA_RESTRICTION = "Do not make up information or use external knowledge."

DOCUMENT_QA_HUMAN_TEMPLATE = """Documents:
{documents}

Question: {question}

Answer based on the documents above:"""


# ============================================================================
# WEB SEARCH SYNTHESIS PROMPT COMPONENTS
# ============================================================================

WEB_SEARCH_SYSTEM_ROLE = "You are an AI assistant that synthesizes information from web search results."

WEB_SEARCH_TASKS = """Your task:
1. Review the web search results provided
2. Extract the most relevant and accurate information
3. Synthesize a clear, comprehensive answer
4. Include URLs of sources for key claims
5. Note if information is recent or time-sensitive
6. Be aware of potential bias or unreliable sources"""

WEB_SEARCH_BEHAVIOR = "Provide accurate, well-sourced information."

WEB_SEARCH_HUMAN_TEMPLATE = """Question: {question}

Web Search Results:
{search_results}

Please provide a comprehensive answer based on the search results. Include source URLs for key information."""


# ============================================================================
# CONVERSATIONAL PROMPT COMPONENTS
# ============================================================================

CONVERSATIONAL_SYSTEM_ROLE = "You are a helpful AI assistant engaged in a conversation with a user."

CONVERSATIONAL_CAPABILITIES = """Your capabilities:
- Access to a knowledge base through vector search
- Access to current web information through web search
- Ability to maintain context from previous messages"""

CONVERSATIONAL_BEHAVIOR = "Be conversational, helpful, and accurate. Use tools when needed to provide better answers."


# ============================================================================
# TICKET RESOLUTION PROMPT COMPONENTS
# ============================================================================

TICKET_SYSTEM_ROLE = "You are an expert cloud application support engineer specializing in Azure Data Factory, Databricks, Logic Apps, databases, and modern DevOps practices."

TICKET_TASK_DESCRIPTION = "Your task is to analyze support tickets and provide structured solutions with root cause analysis."

TICKET_FORMAT_INSTRUCTION = "IMPORTANT: You must follow this exact format in your response:"

TICKET_REASONING_FORMAT = """<reasoning>
1. Deconstruct Current Incident:
   * What are the key symptoms, keywords, and error messages in the ticket?
   * What specific services, environments, and components are affected?

2. Correlate with Past Incidents:
   * Review similar past tickets from the knowledge base
   * Identify patterns and commonalities with current incident
   * Note relevant ticket IDs and their root causes/resolutions

3. Formulate Hypothesis:
   * Based on correlations, what is the most likely root cause?
   * What are the critical diagnostic steps needed?
   * Which past incident solutions are most applicable?
</reasoning>"""

TICKET_ROOT_CAUSE_INSTRUCTION = """ROOT CAUSE: [Explain the most likely root cause based on your analysis. Reference similar past incidents if found (e.g., "Based on similarity to ticket TKT-123..."). Be specific about cloud infrastructure, application code, database, API dependencies, or configuration issues.]"""

TICKET_RESOLUTION_FORMAT = """RESOLUTION:

**Immediate Mitigation:**
[Quick actions to restore service, e.g., "Restart service", "Roll back deployment", "Increase resource limits"]

**Diagnostic Steps:**
1. [Specific log files to check]
2. [Monitoring queries to run]
3. [Configuration settings to verify]
4. [Azure portal checks to perform]

**Fix Implementation:**
[Step-by-step instructions to resolve the root cause, with specific commands, portal actions, or code changes]

**Verification:**
1. [How to confirm the fix worked]
2. [Metrics or logs to monitor]
3. [User acceptance testing steps]

**Preventive Measures:**
[Actions to prevent recurrence, e.g., alerts, monitoring, code improvements, documentation]"""

TICKET_CONTEXT_REQUIREMENT = "Be specific to cloud platforms (Azure, AWS, GCP), microservices, APIs, databases, CI/CD pipelines, and modern DevOps practices."

TICKET_HUMAN_TEMPLATE = """### Current Incident:
Title: {title}
Description: {description}
Category: {category}
Severity: {severity}
Application: {application}
Environment: {environment}
Affected Users: {affected_users}

### Similar Past Incidents (from knowledge base):
{context}

Please analyze this incident and provide your response in the structured format specified above."""


# ============================================================================
# PROMPT TEMPLATE BUILDERS - Combine components into full prompts
# ============================================================================

def create_agent_prompt() -> ChatPromptTemplate:
    """
    Create the main agent prompt template using LangChain ChatPromptTemplate.
    Compatible with ReAct agent. Built from modular components.
    
    Returns:
        ChatPromptTemplate for the agent
    """
    # Combine all agent prompt components
    template = f"""{AGENT_ROLE}

{AGENT_CAPABILITIES}

{AGENT_GUIDELINES}

{AGENT_TOOLS_SECTION}

{AGENT_FORMAT}

{AGENT_BEGIN}"""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    return prompt


def create_rag_synthesis_prompt() -> ChatPromptTemplate:
    """
    Create a prompt template for synthesizing RAG responses.
    Used when combining information from multiple sources.
    Built from modular components.
    
    Returns:
        ChatPromptTemplate for RAG synthesis
    """
    # Combine RAG synthesis system message components
    system_message = f"""{RAG_SYNTHESIS_SYSTEM_ROLE}

{RAG_SYNTHESIS_TASKS}

{RAG_SYNTHESIS_BEHAVIOR}"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", RAG_SYNTHESIS_HUMAN_TEMPLATE),
    ])
    
    return prompt


def create_document_qa_prompt() -> ChatPromptTemplate:
    """
    Create a prompt template for question answering from documents.
    Built from modular components.
    
    Returns:
        ChatPromptTemplate for document Q&A
    """
    # Combine document Q&A system message components
    system_message = f"""{DOCUMENT_QA_SYSTEM_ROLE}

{DOCUMENT_QA_TASKS}

{DOCUMENT_QA_RESTRICTION}"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", DOCUMENT_QA_HUMAN_TEMPLATE),
    ])
    
    return prompt


def create_web_search_synthesis_prompt() -> ChatPromptTemplate:
    """
    Create a prompt template for synthesizing web search results.
    Built from modular components.
    
    Returns:
        ChatPromptTemplate for web search synthesis
    """
    # Combine web search system message components
    system_message = f"""{WEB_SEARCH_SYSTEM_ROLE}

{WEB_SEARCH_TASKS}

{WEB_SEARCH_BEHAVIOR}"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", WEB_SEARCH_HUMAN_TEMPLATE),
    ])
    
    return prompt


def create_conversational_prompt() -> ChatPromptTemplate:
    """
    Create a conversational prompt template with chat history.
    Built from modular components.
    
    Returns:
        ChatPromptTemplate for conversational interactions
    """
    # Combine conversational system message components
    system_message = f"""{CONVERSATIONAL_SYSTEM_ROLE}

{CONVERSATIONAL_CAPABILITIES}

{CONVERSATIONAL_BEHAVIOR}"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    return prompt


def create_ticket_resolution_prompt() -> ChatPromptTemplate:
    """
    Create a prompt template for technical support ticket resolution.
    Uses structured reasoning format for root cause analysis and resolution.
    Built from modular components.
    
    Returns:
        ChatPromptTemplate for ticket resolution
    """
    # Combine ticket resolution system message components
    system_message = f"""{TICKET_SYSTEM_ROLE}

{TICKET_TASK_DESCRIPTION}

{TICKET_FORMAT_INSTRUCTION}

{TICKET_REASONING_FORMAT}

{TICKET_ROOT_CAUSE_INSTRUCTION}

{TICKET_RESOLUTION_FORMAT}

{TICKET_CONTEXT_REQUIREMENT}"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", TICKET_HUMAN_TEMPLATE),
    ])
    
    return prompt


# Prompt template registry
PROMPT_TEMPLATES = {
    "agent": create_agent_prompt,
    "rag_synthesis": create_rag_synthesis_prompt,
    "document_qa": create_document_qa_prompt,
    "web_search_synthesis": create_web_search_synthesis_prompt,
    "conversational": create_conversational_prompt,
    "ticket_resolution": create_ticket_resolution_prompt,
}


def get_prompt_template(template_name: str) -> ChatPromptTemplate:
    """
    Get a prompt template by name.
    
    Args:
        template_name: Name of the template
        
    Returns:
        ChatPromptTemplate instance
    """
    if template_name not in PROMPT_TEMPLATES:
        raise ValueError(f"Unknown template: {template_name}. Available: {list(PROMPT_TEMPLATES.keys())}")
    
    return PROMPT_TEMPLATES[template_name]()
