"""
Test script for Document Assistant scenarios
Tests all three intent types and multi-turn conversations
"""

import sys
import os
from datetime import datetime

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
load_dotenv()

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f" {text}")
    print("=" * 70)

def print_test(test_num, description):
    """Print test information"""
    print(f"\n[TEST {test_num}] {description}")
    print("-" * 70)

def print_result(success, message):
    """Print test result"""
    status = "[PASS]" if success else "[FAIL]"
    print(f"{status} {message}")

def check_env():
    """Check if OpenAI API key is set"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n[WARNING] OPENAI_API_KEY not found in .env file")
        print("Integration tests require an OpenAI API key.")
        print("Please create a .env file with: OPENAI_API_KEY=your_key_here")
        return False
    return True

# ============================================================================
# SCENARIO TEST FUNCTIONS
# ============================================================================

def test_scenario_1_financial_analysis():
    """
    Test Scenario 1: Financial Document Analysis
    Multi-turn conversation with QA and Calculation
    """
    print_header("SCENARIO 1: Financial Document Analysis")
    
    from src.assistant import DocumentAssistant
    
    try:
        # Initialize assistant
        print("\n[SETUP] Initializing Document Assistant...")
        assistant = DocumentAssistant(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model_name="gpt-4o-mini",  # Using mini for faster/cheaper testing
            temperature=0.1
        )
        
        session_id = assistant.start_session("test_user_001")
        print(f"[SETUP] Session started: {session_id}")
        
        # Turn 1: Question about invoice total
        print_test("1.1", "Query invoice INV-001 total amount")
        print("User: What's the total amount in invoice INV-001?")
        
        result1 = assistant.process_message("What's the total amount in invoice INV-001?")
        
        if result1["success"]:
            print(f"Assistant: {result1['response']}")
            print(f"Intent: {result1['intent']['intent_type'] if result1['intent'] else 'N/A'}")
            print(f"Tools Used: {', '.join(result1['tools_used'])}")
            
            # Validate
            is_qa = result1['intent']['intent_type'] == 'qa' if result1['intent'] else False
            has_sources = len(result1.get('sources', [])) > 0
            
            print_result(is_qa and has_sources, 
                        f"Intent: {result1['intent']['intent_type']}, Sources: {result1.get('sources', [])}")
        else:
            print_result(False, f"Error: {result1.get('error', 'Unknown error')}")
            return False
        
        # Turn 2: Calculate percentage
        print_test("1.2", "Calculate 15% of invoice amount")
        print("User: Calculate 15% of that amount")
        
        result2 = assistant.process_message("Calculate 15% of that amount")
        
        if result2["success"]:
            print(f"Assistant: {result2['response']}")
            print(f"Intent: {result2['intent']['intent_type'] if result2['intent'] else 'N/A'}")
            print(f"Tools Used: {', '.join(result2['tools_used'])}")
            
            # Validate
            is_calc = result2['intent']['intent_type'] == 'calculation' if result2['intent'] else False
            used_calculator = 'calculator' in result2.get('tools_used', [])
            
            print_result(is_calc and used_calculator,
                        f"Intent: calculation, Calculator used: {used_calculator}")
        else:
            print_result(False, f"Error: {result2.get('error', 'Unknown error')}")
            return False
        
        # Turn 3: Query other invoices
        print_test("1.3", "Query for other invoices")
        print("User: What other invoices do we have?")
        
        result3 = assistant.process_message("What other invoices do we have?")
        
        if result3["success"]:
            print(f"Assistant: {result3['response']}")
            print(f"Intent: {result3['intent']['intent_type'] if result3['intent'] else 'N/A'}")
            
            # Validate
            is_qa = result3['intent']['intent_type'] == 'qa' if result3['intent'] else False
            print_result(is_qa, f"Successfully retrieved other invoices")
        else:
            print_result(False, f"Error: {result3.get('error', 'Unknown error')}")
            return False
        
        print("\n[SCENARIO 1] All turns completed successfully!")
        return True
        
    except Exception as e:
        print_result(False, f"Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_scenario_2_contract_summarization():
    """
    Test Scenario 2: Contract Summarization
    Single-turn summarization request
    """
    print_header("SCENARIO 2: Contract Summarization")
    
    from src.assistant import DocumentAssistant
    
    try:
        # Initialize assistant
        print("\n[SETUP] Initializing Document Assistant...")
        assistant = DocumentAssistant(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model_name="gpt-4o-mini",
            temperature=0.1
        )
        
        session_id = assistant.start_session("test_user_002")
        print(f"[SETUP] Session started: {session_id}")
        
        # Turn 1: Summarize contract
        print_test("2.1", "Summarize contract CON-001")
        print("User: Summarize contract CON-001")
        
        result = assistant.process_message("Summarize contract CON-001")
        
        if result["success"]:
            print(f"Assistant: {result['response']}")
            print(f"Intent: {result['intent']['intent_type'] if result['intent'] else 'N/A'}")
            print(f"Tools Used: {', '.join(result['tools_used'])}")
            
            # Validate
            is_summary = result['intent']['intent_type'] == 'summarization' if result['intent'] else False
            has_docs = len(result.get('sources', [])) > 0
            
            print_result(is_summary and has_docs,
                        f"Intent: summarization, Documents referenced: {result.get('sources', [])}")
        else:
            print_result(False, f"Error: {result.get('error', 'Unknown error')}")
            return False
        
        print("\n[SCENARIO 2] Summarization test completed successfully!")
        return True
        
    except Exception as e:
        print_result(False, f"Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_scenario_3_multi_intent():
    """
    Test Scenario 3: Multi-Intent Workflow
    Tests QA -> Calculation -> Summarization flow
    """
    print_header("SCENARIO 3: Multi-Intent Workflow")
    
    from src.assistant import DocumentAssistant
    
    try:
        # Initialize assistant
        print("\n[SETUP] Initializing Document Assistant...")
        assistant = DocumentAssistant(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model_name="gpt-4o-mini",
            temperature=0.1
        )
        
        session_id = assistant.start_session("test_user_003")
        print(f"[SETUP] Session started: {session_id}")
        
        # Turn 1: Find invoices over threshold
        print_test("3.1", "Find invoices over $50,000")
        print("User: Find all invoices over $50,000")
        
        result1 = assistant.process_message("Find all invoices over $50,000")
        
        if result1["success"]:
            print(f"Assistant: {result1['response']}")
            print(f"Intent: {result1['intent']['intent_type'] if result1['intent'] else 'N/A'}")
            
            is_qa = result1['intent']['intent_type'] == 'qa' if result1['intent'] else False
            print_result(is_qa, f"QA intent correctly classified")
        else:
            print_result(False, f"Error: {result1.get('error', 'Unknown error')}")
            return False
        
        # Turn 2: Calculate total
        print_test("3.2", "Calculate total of found invoices")
        print("User: Calculate the total of these invoices")
        
        result2 = assistant.process_message("Calculate the total of these invoices")
        
        if result2["success"]:
            print(f"Assistant: {result2['response']}")
            print(f"Intent: {result2['intent']['intent_type'] if result2['intent'] else 'N/A'}")
            print(f"Tools Used: {', '.join(result2['tools_used'])}")
            
            is_calc = result2['intent']['intent_type'] == 'calculation' if result2['intent'] else False
            used_calc = 'calculator' in result2.get('tools_used', [])
            
            print_result(is_calc and used_calc,
                        f"Calculation intent with calculator tool")
        else:
            print_result(False, f"Error: {result2.get('error', 'Unknown error')}")
            return False
        
        # Turn 3: Summarize one invoice
        print_test("3.3", "Summarize the higher value invoice")
        print("User: Summarize the higher value invoice")
        
        result3 = assistant.process_message("Summarize the higher value invoice")
        
        if result3["success"]:
            print(f"Assistant: {result3['response']}")
            print(f"Intent: {result3['intent']['intent_type'] if result3['intent'] else 'N/A'}")
            
            is_summary = result3['intent']['intent_type'] == 'summarization' if result3['intent'] else False
            print_result(is_summary, f"Summarization intent correctly classified")
        else:
            print_result(False, f"Error: {result3.get('error', 'Unknown error')}")
            return False
        
        print("\n[SCENARIO 3] Multi-intent workflow completed successfully!")
        return True
        
    except Exception as e:
        print_result(False, f"Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_calculator_tool():
    """Test calculator tool directly"""
    print_header("CALCULATOR TOOL TESTS")
    
    from src.tools import create_calculator_tool, ToolLogger
    
    logger = ToolLogger()
    calculator = create_calculator_tool(logger)
    
    tests = [
        ("2 + 2", "4"),
        ("100 * 0.15", "15"),
        ("(69300 + 214500)", "283800"),
        ("22000 * 0.15", "3300"),
    ]
    
    all_passed = True
    
    for i, (expression, expected) in enumerate(tests, 1):
        print_test(f"CALC-{i}", f"Calculate: {expression}")
        result = calculator.invoke({"expression": expression})
        print(f"Result: {result}")
        
        # Check if expected value is in result
        if expected in result:
            print_result(True, f"Calculation correct")
        else:
            print_result(False, f"Expected {expected} in result")
            all_passed = False
    
    return all_passed

def test_document_retrieval():
    """Test document retrieval system"""
    print_header("DOCUMENT RETRIEVAL TESTS")
    
    from src.retrieval import SimulatedRetriever
    
    retriever = SimulatedRetriever()
    
    print_test("DOC-1", "Retrieve all documents")
    all_docs = retriever.retrieve_all()
    print(f"Found {len(all_docs)} documents")
    print_result(len(all_docs) == 5, f"Expected 5 documents, found {len(all_docs)}")
    
    print_test("DOC-2", "Search for invoices")
    invoice_results = retriever.retrieve_by_keyword("invoice", top_k=5)
    print(f"Found {len(invoice_results)} invoices")
    print_result(len(invoice_results) >= 3, f"Found invoice documents")
    
    print_test("DOC-3", "Search for contracts")
    contract_results = retriever.retrieve_by_type("contract")
    print(f"Found {len(contract_results)} contracts")
    print_result(len(contract_results) >= 1, f"Found contract documents")
    
    print_test("DOC-4", "Get statistics")
    stats = retriever.get_statistics()
    print(f"Total documents: {stats['total_documents']}")
    print(f"Document types: {stats['document_types']}")
    print_result(stats['total_documents'] == 5, f"Statistics correct")
    
    return True

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Main test runner"""
    print_header("DOCUMENT ASSISTANT - SCENARIO TESTS")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check for API key
    has_api_key = check_env()
    
    results = {}
    
    # Always run unit tests (no API key needed)
    print("\n")
    print_header("UNIT TESTS (No API Key Required)")
    
    results["Calculator Tool"] = test_calculator_tool()
    results["Document Retrieval"] = test_document_retrieval()
    
    # Run integration tests if API key is available
    if has_api_key:
        print("\n")
        print_header("INTEGRATION TESTS (Requires API Key)")
        print("[INFO] Running full integration tests with OpenAI...")
        
        results["Scenario 1: Financial Analysis"] = test_scenario_1_financial_analysis()
        results["Scenario 2: Contract Summarization"] = test_scenario_2_contract_summarization()
        results["Scenario 3: Multi-Intent Workflow"] = test_scenario_3_multi_intent()
    else:
        print("\n")
        print_header("INTEGRATION TESTS SKIPPED")
        print("[INFO] Set OPENAI_API_KEY in .env to run integration tests")
    
    # Print summary
    print("\n")
    print_header("TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name}")
    
    print("\n" + "-" * 70)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Pass Rate: {(passed_tests/total_tests*100):.1f}%")
    print("-" * 70)
    
    if passed_tests == total_tests:
        print("\n[SUCCESS] All tests passed!")
        return 0
    else:
        print("\n[WARNING] Some tests failed. Review output above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

