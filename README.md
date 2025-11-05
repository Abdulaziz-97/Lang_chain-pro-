# Document Assistant - AI-Powered Document Processing System

## Project Description

The Document Assistant is an intelligent document processing system built with LangChain and LangGraph. It uses a multi-agent architecture to handle document-related tasks including question answering, summarization, and calculations on financial and healthcare documents. The system employs intent classification to route user requests to specialized agents, maintains conversation memory across sessions, and provides structured, traceable responses.

## Getting Started

These instructions will help you get a copy of the project running on your local machine for development and testing purposes.

### Dependencies

```
Python 3.9 or higher
langchain>=0.2.0
langgraph>=0.6.7
langchain-openai>=0.1.0
langchain-core>=0.2.0
pydantic>=2.0.0
python-dotenv>=1.0.0
openai>=1.0.0
print-color>=0.4.6
```

### Installation

Follow these steps to set up the development environment:

1. **Clone or download the repository**
   ```bash
   cd <repository_path>
   ```

2. **Create a virtual environment**
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate
   
   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Create .env file in the starter directory
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

5. **Verify installation**
   ```bash
   python test_implementation.py
   ```

## Architecture Overview

### Multi-Agent System

The Document Assistant implements a graph-based workflow with the following components:

```
User Input → Intent Classifier → [QA Agent | Summarization Agent | Calculation Agent] → Update Memory → Response
```

**Key Components:**

1. **Intent Classifier**: Analyzes user input and routes to appropriate agent
2. **QA Agent**: Answers questions using document retrieval
3. **Summarization Agent**: Creates summaries and extracts key points
4. **Calculation Agent**: Performs mathematical operations on document data
5. **Memory System**: Maintains conversation context across turns

### State Management

The system uses LangGraph's state management with the following key features:

**State Structure (`AgentState`):**
- `user_input`: Current user query
- `messages`: Conversation history (with `add_messages` reducer)
- `intent`: Classified user intent
- `next_step`: Next node to execute
- `conversation_summary`: Summary of recent conversation
- `active_documents`: Currently referenced document IDs
- `current_response`: Response being constructed
- `tools_used`: List of tools invoked
- `actions_taken`: Audit trail of executed nodes (with `operator.add` reducer)
- `session_id` and `user_id`: Session identifiers

**State Flow:**
1. Initial state created with user input
2. State flows through workflow nodes
3. Each node updates relevant fields
4. Reducers accumulate values (messages, actions_taken)
5. Final state contains complete response and audit trail

**Memory Persistence:**
- Uses `InMemorySaver` checkpointer for cross-turn persistence
- Each session has unique `thread_id` for state isolation
- Conversation summaries updated after each turn
- Active documents tracked throughout session

### Structured Output Enforcement

The system enforces structured outputs using Pydantic schemas with strict validation:

**Schema Validation Features:**

1. **Type Enforcement**: All fields have explicit type annotations
2. **Value Constraints**: 
   - `confidence` fields constrained to [0.0, 1.0] using `ge=0.0, le=1.0`
   - `intent_type` restricted to valid literals: "qa", "summarization", "calculation", "unknown"
3. **Required Fields**: Non-optional fields must be provided
4. **Default Values**: Fields like `timestamp` auto-populate with `default_factory`

**Implementation:**
```python
# LLM configured to return structured output
llm_with_structure = llm.with_structured_output(UserIntent)

# Pydantic validates all constraints automatically
result = llm_with_structure.invoke(prompt)  # Returns validated UserIntent object
```

**Response Schemas:**
- `AnswerResponse`: Q&A responses with sources and confidence
- `SummarizationResponse`: Summaries with key points and document IDs
- `CalculationResponse`: Calculation results with explanations
- `UserIntent`: Intent classification with reasoning
- `UpdateMemoryResponse`: Memory updates with conversation summary

## Testing

### Automated Testing

Run the comprehensive test suite to validate all components:

```bash
cd starter
python test_implementation.py
```

### Test Coverage

The test suite validates:

1. **Module Imports**: All required packages load correctly
2. **Schema Validation**: Pydantic models enforce constraints
3. **Prompt Templates**: All prompts format correctly
4. **Calculator Tool**: Math operations, security, and error handling
5. **State Reducers**: Action accumulation works properly
6. **Workflow Functions**: All nodes have correct signatures
7. **Graph Structure**: StateGraph properly configured
8. **Assistant Config**: Session and LLM configuration correct

### Automated Scenario Testing

Run the comprehensive scenario test suite:

```bash
cd starter
python test_scenarios.py
```

This will test:
- **Unit Tests** (no API key required):
  - Calculator tool functionality
  - Document retrieval system
  
- **Integration Tests** (requires OPENAI_API_KEY):
  - Scenario 1: Financial document analysis
  - Scenario 2: Contract summarization
  - Scenario 3: Multi-intent workflow

**Example Output:**
```
======================================================================
 DOCUMENT ASSISTANT - SCENARIO TESTS
======================================================================

[PASS] Calculator Tool
[PASS] Document Retrieval
[PASS] Scenario 1: Financial Analysis
[PASS] Scenario 2: Contract Summarization
[PASS] Scenario 3: Multi-Intent Workflow

Total Tests: 5
Passed: 5
Failed: 0
Pass Rate: 100.0%
```

### Manual Interactive Testing

Start the interactive assistant:

```bash
cd starter
python main.py
```

**Quick Test Examples:**

#### 1. Question Answering (QA Intent)
```
Input: What's the total amount in invoice INV-001?

Expected Output:
- Intent: qa
- Tools Used: document_search, document_reader
- Response includes: "$22,000" with breakdown
- Sources: ["INV-001"]
```

#### 2. Summarization Intent
```
Input: Summarize contract CON-001

Expected Output:
- Intent: summarization
- Tools Used: document_search, document_reader
- Response includes: Service Agreement details, parties, terms
- Documents: ["CON-001"]
```

#### 3. Calculation Intent
```
Input: Calculate 15% of 22000

Expected Output:
- Intent: calculation
- Tools Used: calculator
- Response: "Result: 3300.0"
```

#### 4. Multi-turn Conversation
```
Turn 1: What's the total in invoice INV-001?
Turn 2: Calculate 15% of that amount
Turn 3: What other invoices do we have?

Expected Behavior:
- System remembers context across turns
- Calculations reference previous answers
- Active documents list grows with each query
```

### Real Test Cases with Actual Documents

The system includes these sample documents for testing:

**Invoices:**
- INV-001: $22,000 (Acme Corporation, 2024-01-15)
- INV-002: $69,300 (TechStart Inc., 2024-02-20)
- INV-003: $214,500 (Global Corp, 2024-03-01)

**Contracts:**
- CON-001: $180,000 (Healthcare Partners LLC, 12-month service agreement)

**Claims:**
- CLM-001: $2,450 (Medical expense reimbursement)

**Test Commands to Try:**
```
# QA Tests
What's the total amount in invoice INV-001?
Who is the client for invoice INV-002?
What is the contract value for CON-001?
How much is the insurance claim CLM-001?

# Calculation Tests
Calculate 22000 * 0.15
What is 69300 + 214500?
Calculate (214500 - 69300) / 2

# Summarization Tests
Summarize contract CON-001
Summarize invoice INV-003
Give me a summary of all invoices

# Complex Multi-turn Tests
Find all invoices over $50,000
Calculate the total of these invoices
Summarize the higher value invoice
```

## Implementation Decisions

### 1. Why LangGraph Over Simple Chains?

**Decision**: Use LangGraph's stateful workflow instead of simple LangChain chains

**Reasoning**:
- **Complex Routing**: Need conditional logic based on intent classification
- **State Management**: Require persistent state across multiple turns
- **Audit Trail**: Need to track which agents execute and in what order
- **Extensibility**: Easy to add new agents or modify workflow
- **Memory**: Built-in checkpointing for conversation persistence

### 2. Multi-Agent Architecture

**Decision**: Separate specialized agents for each intent type

**Reasoning**:
- **Specialization**: Each agent optimized for specific task type
- **Prompt Engineering**: Different system prompts per intent
- **Tool Selection**: Agents can use different tool subsets
- **Maintainability**: Easier to update one agent without affecting others
- **Scalability**: Simple to add new intent types

### 3. Structured Output with Pydantic

**Decision**: Enforce structured outputs for all agent responses

**Reasoning**:
- **Reliability**: Guaranteed response format for downstream processing
- **Validation**: Automatic constraint checking (confidence scores, valid intents)
- **Type Safety**: Compile-time type checking with mypy
- **Documentation**: Schemas serve as API documentation
- **Error Prevention**: Invalid responses rejected before processing

### 4. Tool Security Design

**Decision**: Validate all calculator inputs with regex before evaluation

**Reasoning**:
- **Security**: Prevent code injection through malicious expressions
- **Sandboxing**: Only allow safe mathematical operations
- **Error Handling**: Graceful failures for invalid input
- **Logging**: Track all tool usage for audit purposes

### 5. Memory Management Strategy

**Decision**: Use InMemorySaver with conversation summaries

**Reasoning**:
- **Simplicity**: In-memory suitable for development and small deployments
- **Speed**: Fast access to conversation history
- **Context Limits**: Summaries prevent token overflow in long conversations
- **Document Tracking**: Active documents list maintains relevant context
- **Upgradeability**: Easy to switch to persistent storage (SQLite, Postgres)

### 6. Session-Based Architecture

**Decision**: Isolate conversations by session with unique thread_ids

**Reasoning**:
- **Privacy**: User conversations remain separate
- **Scalability**: Support multiple concurrent users
- **Testing**: Easy to create isolated test sessions
- **Persistence**: Sessions can be saved and resumed
- **Analytics**: Track usage patterns per session

## Example Conversations

**NOTE: These are REAL outputs captured from the live system using gpt-4o-mini**

### Example 1: Financial Document Analysis

```
Session: d9ca2ae2-cdd0-4029-8098-d0586d6d9932

[Turn 1]
User: What's the total amount in invoice INV-001?
Assistant: The total amount in invoice INV-001 is **$22,000**. 

This total is derived from the subtotal of $20,000 plus the tax of $2,000.
           
Intent: calculation
Tools Used: document_reader, calculator
Sources: ['INV-001']
Actions Taken: ['classify_intent', 'calculation_agent']
Confidence: 0.95

[Turn 2]
User: Calculate 15% of that amount
Assistant: To calculate 15% of the total amount of $22,000, we perform the following calculation:

1. **Calculate 15% of $22,000**:
   15% of 22000 = 0.15 × 22000

Using the calculator, we find that:
0.15 × 22000 = 3300

Thus, **15% of $22,000 is $3,300**.
           
Intent: calculation
Tools Used: document_reader, calculator, calculator
Sources: ['INV-001']
Actions Taken: ['classify_intent', 'calculation_agent', 'classify_intent', 'calculation_agent']
Confidence: 0.95

[Turn 3]
User: What other invoices do we have?
Assistant: Here are the invoices available:

1. **Invoice ID: INV-001**
   - **Title:** Invoice #12345
   - **Date:** 2024-01-15
   - **Client:** Acme Corporation
   - **Total Amount:** $22,000 (calculated from services rendered)

2. **Invoice ID: INV-002**
   - **Title:** Invoice #12346
   - **Date:** 2024-02-20
   - **Client:** TechStart Inc.
   - **Total Amount:** $69,300.00
   - **Preview:** Products include an Enterprise License (Annual) for $50,000.

3. **Invoice ID: INV-003**
   - **Title:** Invoice #12347
   - **Date:** 2024-03-01
   - **Client:** Global Corp
   - **Total Amount:** $214,500.00
   - **Preview:** Services include an Annual Subscription for $120,000.

If you need more details about any specific invoice, please let me know!
           
Intent: qa
Tools Used: document_reader, calculator, calculator, document_search
Sources: ['INV-001', 'INV-002', 'INV-003']
Actions Taken: ['classify_intent', 'calculation_agent', 'classify_intent', 'calculation_agent', 'classify_intent', 'qa_agent']
Confidence: 0.85

Conversation Summary: Multi-turn conversation querying invoice details, calculating percentages, 
                      and finding other invoices
Active Documents: ['INV-001', 'INV-002', 'INV-003']
```

### Example 2: Contract Summarization

```
Session: 1a5e08bc-7878-4829-9e28-f5f9d2a46e38

[Turn 1]
User: Summarize contract CON-001
Assistant: ### Contract Summary: CON-001

**Parties Involved:**
- **Provider:** DocDacity Solutions Inc.
- **Client:** Healthcare Partners LLC

**Contract Details:**
- **Amount:** $180,000.00
- **Effective Date:** January 1, 2024
- **Duration:** 12 months
- **Monthly Fee:** $15,000

**Services Provided:**
1. Document Processing Platform Access
2. 24/7 Technical Support
3. Monthly Data Analytics Reports
4. Compliance Monitoring

**Termination Clause:**
- Either party may terminate the agreement with 60 days written notice. 

This contract outlines the terms for the provision of services by DocDacity Solutions Inc. to 
Healthcare Partners LLC, with a total value of $180,000 over a one-year period.
           
Intent: summarization
Tools Used: document_reader
Sources: ['CON-001']
Actions Taken: ['classify_intent', 'summarization_agent']
Confidence: 0.95
```

### Example 3: Multi-Intent Workflow

```
Session: a6bb82cd-b927-4f01-9050-e7e2f86052d4

[Turn 1]
User: Find all invoices over $50,000
Assistant: I found 3 documents related to invoices over $50,000. Here are the details:

### Document 1
- **ID**: INV-003
- **Title**: Invoice #12347
- **Amount**: $214,500.00
- **Date**: 2024-03-01
- **Client**: Global Corp
- **Services**:
  - Annual Subscription: $120,000

### Document 2
- **ID**: INV-002
- **Title**: Invoice #12346
- **Amount**: $69,300.00
- **Date**: 2024-02-20
- **Client**: TechStart Inc.
- **Products**:
  - Enterprise License (Annual): $50,000

### Document 3
- **ID**: CON-001 (Note: This is a contract, not an invoice)
- **Title**: Service Agreement
- **Amount**: $180,000.00
- **Date**: January 1, 2024
- **Provider**: DocDacity Solutions Inc.

### Summary
- **Total Invoices Found**: 2 (INV-003 and INV-002)
- **Total Amount of Invoices**: 
  - Invoice #12347: $214,500.00
  - Invoice #12346: $69,300.00

If you need further calculations or details, please let me know!
           
Intent: calculation
Tools Used: document_search, document_search
Sources: ['INV-003', 'INV-002', 'CON-001']
Actions Taken: ['classify_intent', 'calculation_agent']
Confidence: 0.90

[Turn 2]
User: Calculate the total of these invoices
Assistant: To calculate the total of the invoices, I added the amounts of the two invoices found:

1. **Invoice #12347**: $214,500.00
2. **Invoice #12346**: $69,300.00

### Calculation Steps:
- **Step 1**: Add the amounts together:
  214500 + 69300 = 283800

### Total Amount:
- **Total of Invoices**: $283,800.00

Thus, the total amount of the invoices over $50,000 is **$283,800.00**.
           
Intent: calculation
Tools Used: document_search, document_search, calculator, calculator, calculator
Sources: ['INV-003', 'INV-002', 'CON-001']
Actions Taken: ['classify_intent', 'calculation_agent', 'classify_intent', 'calculation_agent']
Confidence: 0.95

[Turn 3]
User: Summarize the higher value invoice
Assistant: ### Summary of Higher Value Invoice

- **Document ID**: INV-003
- **Title**: Invoice #12347
- **Date**: March 1, 2024
- **Client**: Global Corp
- **Total Amount**: $214,500.00

#### Services Provided:
1. **Annual Subscription**: $120,000
2. **Premium Support**: $30,000
3. **Custom Development**: $45,000

#### Financial Breakdown:
- **Subtotal**: $195,000
- **Tax (10%)**: $19,500
- **Total Due**: $214,500

#### Payment Terms:
- **Net**: 60 days

This invoice represents a comprehensive service package provided to Global Corp, with a total due 
amount of $214,500.00, payable within 60 days.
           
Intent: summarization
Tools Used: document_search, document_search, calculator, calculator, calculator, document_reader
Sources: ['INV-003']
Actions Taken: ['classify_intent', 'calculation_agent', 'classify_intent', 'calculation_agent', 'classify_intent', 'summarization_agent']
Confidence: 0.90

Conversation Summary: Complex workflow demonstrating QA, calculation, and summarization
Active Documents: ['INV-002', 'INV-003', 'CON-001']
```

## Project Structure

```
starter/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── schemas.py            # Pydantic data models
│   ├── prompts.py            # LLM prompt templates
│   ├── tools.py              # Agent tools (@tool decorator)
│   ├── agent.py              # LangGraph workflow definition
│   ├── assistant.py          # Main assistant orchestrator
│   └── retrieval.py          # Document retrieval system
├── logs/                     # Auto-generated tool usage logs
├── sessions/                 # Auto-generated session history
├── main.py                   # Interactive CLI entry point
├── requirements.txt          # Python dependencies
├── TEST_RESULTS.md          # Automated test results
└── README.md                # This file
```

## Built With

* [LangChain](https://www.langchain.com/) - LLM application framework
* [LangGraph](https://langchain-ai.github.io/langgraph/) - Stateful multi-agent orchestration
* [OpenAI GPT-4](https://openai.com/gpt-4) - Large language model
* [Pydantic](https://docs.pydantic.dev/) - Data validation and settings management
* [Python 3.9+](https://www.python.org/) - Programming language

## Features

### Core Capabilities
- **Intent Classification**: Automatically routes requests to appropriate agent
- **Document Retrieval**: Search and read financial/healthcare documents
- **Question Answering**: Provides answers with source citations
- **Summarization**: Generates concise summaries with key points
- **Calculations**: Performs mathematical operations on document data
- **Conversation Memory**: Maintains context across multiple turns
- **Tool Logging**: Tracks all tool usage for debugging and audit
- **Session Management**: Isolates and persists user sessions

### Security Features
- Input validation for calculator tool (prevents code injection)
- Regex-based expression sanitization
- Error handling with graceful degradation
- Session isolation for multi-user environments

### Observability
- Comprehensive logging in `./logs` directory
- Session history in `./sessions` directory
- Action tracking with `actions_taken` reducer
- Tool usage audit trail
- Confidence scores on all responses

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'langchain'`
- **Solution**: Install dependencies: `pip install -r requirements.txt`

**Issue**: `Error: OPENAI_API_KEY not found`
- **Solution**: Create `.env` file with your OpenAI API key

**Issue**: Calculator rejects valid expression
- **Solution**: Ensure expression only contains digits, +, -, *, /, (), and spaces

**Issue**: Intent classification incorrect
- **Solution**: Provide more specific input or add context from previous turns

**Issue**: Session not persisting
- **Solution**: Verify `InMemorySaver` is properly initialized in workflow

## Performance Considerations

- **Token Usage**: Conversation summaries prevent context overflow
- **Caching**: Consider implementing response caching for repeated queries
- **Concurrent Users**: InMemorySaver suitable for development; use persistent storage for production
- **Rate Limiting**: Implement rate limits for OpenAI API calls in production

## License

[License](../LICENSE.md)

## Acknowledgments

- Built as part of LangChain/LangGraph learning curriculum
- Architecture inspired by multi-agent design patterns
- Test suite validates all critical components
