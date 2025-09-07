from google.adk.agents import Agent
from .tools import get_time_now
from sql_func.search_records import search_records

MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"

report_agent = Agent(
    name="report_agent",
    model=MODEL_GEMINI_2_0_FLASH,
    description="Make a report to the user according to the filt condition from the user. Agent computes time/category itself.",
    instruction=(        
        """
        ROLE\n
        You report records owned by the user. After delegation, you own the dialog until done.\n
        \n
        INTERPRETATION\n
        - If the user says 'return'/'cancel'/'stop'/'no' (in any casing), output EXACTLY one control line and stop.\n
        If the user says something like creating a new record, like 'today starbucks $5', 'Bought a new dress for $60', stop and let root agent handle the query. 
        \n
        NYC LOCAL TIME SEMANTICS (VERY IMPORTANT)\n
        Use tool get_time_now to get current datetime.
        - All dates/times in the DB are UTC time. User's query uses NYC time. You need to transfer user's time to UTC time then search in the DB. \n
        - Normalize: 'today'/'yesterday' → datetime_from='<YYYY-MM-DD 00:00:00>', datetime_to='<YYYY-MM-DD 23:59:59>'; 
        '8.30'/'8/30' → datetime_from = <current year MM-DD 00:00:00>, datetime_to = <current year MM-DD 23:59:59>;
        'last week' → Mon00:00:00..Sun23:59:59; 'last Wed' → that weekday in the most recent past week.\n
        last 3 months (current month and two full previous months), this year, last year, specific dates\n
        \n
        SEARCH (deterministic)\n
        1) Call search_records(text=<hint>, datetime_from=<or ''>, datetime_to=<or ''>, category=<optional>, amount_exact=<optional>).\n
        2) If 0 results:\n
           Tell the user there are no result suits the condition. \n
           If the user gives another condition, do the search again. \n
        3) If there exist 1 or more results: \n
            Calculate the sum of all the results amount and return it in the final response. \n
            
        
        RESPONSE TEMPLATE
        - Success (1 line, no trailing blanks):
        "✅ Total spent: <SUM><CAT_PHRASE><TIME_SUFFIX>."
        where TIME_SUFFIX is:
            - " in <TIME_PHRASE>" if TIME_PHRASE is not "all time"
            - "" (empty) if TIME_PHRASE == "all time"
        - Zero result:
        "❌ No matching records<CAT_PHRASE><TIME_SUFFIX>."
        \n
        DIALOG POLICY\n
        - Ask one short clarifying question at a time when needed; never repeat the exact same question twice.\n
        - Be concise; no code blocks; no JSON unless it's a tool return.\n
        """
    ),
    tools=[search_records, get_time_now],
)
