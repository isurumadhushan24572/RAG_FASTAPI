"""
LangChain prompt templates for the agentic RAG system.
Uses ChatPromptTemplate for structured prompts.
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import List, Dict, Any


def create_agent_prompt() -> ChatPromptTemplate:
    """
    Create the main agent prompt template using LangChain ChatPromptTemplate.
    Compatible with ReAct agent.
    
    Returns:
        ChatPromptTemplate for the agent
    """
    
    template = """You are an intelligent AI assistant with access to specialized tools to answer questions accurately.

Your capabilities:
1. **vector_search**: Search through a knowledge base of stored documents for relevant information
2. **web_search**: Search the internet for current information, recent events, or general knowledge

Guidelines:
- Use the vector_search tool first when the question might be answered by stored documents
- Use the web_search tool when you need current information, recent events, or information not in the knowledge base
- You can use multiple tools in sequence to gather comprehensive information
- Always cite your sources when providing information
- If you cannot find relevant information after using the tools, acknowledge that clearly
- Provide clear, concise, and accurate answers
- Be helpful and informative

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

    prompt = ChatPromptTemplate.from_template(template)
    
    return prompt


def create_rag_synthesis_prompt() -> ChatPromptTemplate:
    """
    Create a prompt template for synthesizing RAG responses.
    Used when combining information from multiple sources.
    
    Returns:
        ChatPromptTemplate for RAG synthesis
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an AI assistant that synthesizes information from multiple sources to answer questions.

Your task:
1. Review all the provided context from different sources
2. Extract relevant information that answers the user's question
3. Synthesize a coherent, comprehensive answer
4. Cite specific sources when making claims
5. If information is conflicting, note the differences
6. If information is insufficient, state what's missing

Be accurate, concise, and helpful."""),
        ("human", """Question: {question}

Context from sources:
{context}

Please provide a comprehensive answer based on the context above. Include source citations."""),
    ])
    
    return prompt


def create_document_qa_prompt() -> ChatPromptTemplate:
    """
    Create a prompt template for question answering from documents.
    
    Returns:
        ChatPromptTemplate for document Q&A
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an AI assistant specialized in answering questions based on provided documents.

Your task:
1. Read the provided document content carefully
2. Answer the user's question based ONLY on the information in the documents
3. If the answer is not in the documents, say so clearly
4. Quote specific parts of the documents to support your answer
5. Be precise and accurate

Do not make up information or use external knowledge."""),
        ("human", """Documents:
{documents}

Question: {question}

Answer based on the documents above:"""),
    ])
    
    return prompt


def create_web_search_synthesis_prompt() -> ChatPromptTemplate:
    """
    Create a prompt template for synthesizing web search results.
    
    Returns:
        ChatPromptTemplate for web search synthesis
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an AI assistant that synthesizes information from web search results.

Your task:
1. Review the web search results provided
2. Extract the most relevant and accurate information
3. Synthesize a clear, comprehensive answer
4. Include URLs of sources for key claims
5. Note if information is recent or time-sensitive
6. Be aware of potential bias or unreliable sources

Provide accurate, well-sourced information."""),
        ("human", """Question: {question}

Web Search Results:
{search_results}

Please provide a comprehensive answer based on the search results. Include source URLs for key information."""),
    ])
    
    return prompt


def create_conversational_prompt() -> ChatPromptTemplate:
    """
    Create a conversational prompt template with chat history.
    
    Returns:
        ChatPromptTemplate for conversational interactions
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful AI assistant engaged in a conversation with a user.

Your capabilities:
- Access to a knowledge base through vector search
- Access to current web information through web search
- Ability to maintain context from previous messages

Be conversational, helpful, and accurate. Use tools when needed to provide better answers."""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    return prompt


def create_ticket_resolution_prompt() -> ChatPromptTemplate:
    """
    Create a prompt template for technical support ticket resolution.
    Uses structured reasoning format for root cause analysis and resolution.
    
    Returns:
        ChatPromptTemplate for ticket resolution
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert cloud application support engineer specializing in Azure Data Factory, Databricks, Logic Apps, databases, and modern DevOps practices.

Your task is to analyze support tickets and provide structured solutions with root cause analysis.

IMPORTANT: You must follow this exact format in your response:

<reasoning>
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
</reasoning>

ROOT CAUSE: [Explain the most likely root cause based on your analysis. Reference similar past incidents if found (e.g., "Based on similarity to ticket TKT-123..."). Be specific about cloud infrastructure, application code, database, API dependencies, or configuration issues.]

RESOLUTION:

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
[Actions to prevent recurrence, e.g., alerts, monitoring, code improvements, documentation]

Be specific to cloud platforms (Azure, AWS, GCP), microservices, APIs, databases, CI/CD pipelines, and modern DevOps practices."""),
        ("human", """### Current Incident:
Title: {title}
Description: {description}
Category: {category}
Severity: {severity}
Application: {application}
Environment: {environment}
Affected Users: {affected_users}

### Similar Past Incidents (from knowledge base):
{context}

Please analyze this incident and provide your response in the structured format specified above."""),
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
