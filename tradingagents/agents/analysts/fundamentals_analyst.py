from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.agent_utils import get_fundamentals, get_balance_sheet, get_cashflow, get_income_statement, get_insider_sentiment, get_insider_transactions
from tradingagents.dataflows.config import get_config


def create_fundamentals_analyst(llm):
    def fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        tools = [
            get_fundamentals,
            get_balance_sheet,
            get_cashflow,
            get_income_statement,
        ]

        system_message = (
            "You are a researcher tasked with analyzing fundamental information over the past week about a company. Please write a comprehensive report of the company's fundamental information such as financial documents, company profile, basic company financials, and company financial history to gain a full view of the company's fundamental information to inform traders. Make sure to include as much detail as possible. Do not simply state the trends are mixed, provide detailed and finegrained analysis and insights that may help traders make decisions."
            + "\n\n**Economic Moat Analysis**: As part of your fundamental analysis, conduct a thorough evaluation of the company's economic moat (sustainable competitive advantages). Assess the following:"
            + "\n- **Moat Width**: Classify the moat as Wide (durable advantages lasting 20+ years), Narrow (advantages lasting 10+ years), or None (limited competitive advantages)"
            + "\n- **Moat Sources**: Identify and analyze specific competitive advantages from the following categories:"
            + "\n  * **Intangible Assets**: Brand strength, patents, regulatory licenses, proprietary technology"
            + "\n  * **Switching Costs**: Customer lock-in due to high costs or difficulty of switching to competitors"
            + "\n  * **Network Effects**: Product/service value increases with more users (e.g., platforms, marketplaces)"
            + "\n  * **Cost Advantages**: Economies of scale, unique access to resources, process advantages, superior locations"
            + "\n  * **Efficient Scale**: Operating in markets where additional competitors would be economically irrational"
            + "\n  * **Monopolistic Profitability and Market Share Concentration**: Dominant market position leading to superior margins, pricing power, and market share concentration that creates barriers to entry"
            + "\n  * **Dominant Ecosystem and Competitive Exclusion**: Control of critical platforms, standards, or ecosystems that create competitive barriers and exclude rivals from key markets or customer segments"
            + "\n  * **Scalability and Asset-Light Model**: Ability to grow revenue with minimal incremental capital investment, enabling high return on invested capital and rapid expansion without proportional cost increases"
            + "\n- **Moat Durability**: Evaluate the sustainability of these advantages over time, considering technological disruption, regulatory changes, and competitive threats"
            + "\n- **Moat Trends**: Assess whether the moat is widening, stable, or narrowing based on recent developments"
            + "\n- **Investment Implications**: Explain how the moat analysis impacts long-term value creation, pricing power, and investment attractiveness"
            + "\n\nMake sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read. The table should include a dedicated row or section for Moat Analysis summary."
            + " Use the available tools: `get_fundamentals` for comprehensive company analysis, `get_balance_sheet`, `get_cashflow`, and `get_income_statement` for specific financial statements.",
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    "For your reference, the current date is {current_date}. The company we want to look at is {ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "fundamentals_report": report,
        }

    return fundamentals_analyst_node
