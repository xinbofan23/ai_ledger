from google.adk.agents import Agent
from .new_record_agent import new_record_agent
from .modify_record_agent import modify_record_agent
from .report_agent import report_agent

MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

root_agent = Agent(
    name="root_agent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Classifies a free-form ledger query into one of: NEW, MODIFY, REPORT.",
    instruction=
        "You are the main Ledger Agent coordinating a team. Your primary responsibility is to classify the user's query to exactly one intent. "
        "You have specialized sub-agents: "
        "1. 'new_record_agent': Handles creating a new record query like 'Starbucks $5', 'Bought a new dress for $60'. Delegate to it for these. "
        "2. 'modify_record_agent': Handles modifying an existing record like 'Change today's last record to yesterday', 'The starbucks today was 5, not 6'. Delegate to it for these. "
        "3. 'report_agent': Handles making a report like 'How much did I spend on coffee this week', 'Report the last three months'. Delegate to it for these. "
        "Analyze the user's query. If it's a creation, delegate to 'new_record_agent'. If it's a modification, delegate to 'modify_record_agent'. "
        "If it's a report request, delegate to 'report_agent'."
        "If the operation was canceled by modify_record_agent, ask if there is anything else you can help with."
        "For anything else, respond appropriately or state you cannot handle it.",
    
    tools=[],
    sub_agents=[new_record_agent, modify_record_agent, report_agent],
)

