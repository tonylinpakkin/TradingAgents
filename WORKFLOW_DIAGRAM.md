# TradingAgents Workflow Diagram

## System Architecture Overview

```mermaid
graph TB
    Start([User Input: Ticker + Date]) --> Init[Initialize TradingAgentsGraph]
    Init --> Phase1[Phase 1: Information Gathering]

    subgraph Phase1[" PHASE 1: Information Gathering "]
        MA[Market Analyst<br/>Technical Indicators]
        FA[Fundamentals Analyst<br/>Financial Statements]
        NA[News Analyst<br/>Macro News]
        SA[Social Media Analyst<br/>Sentiment Analysis]

        MA --> |Market Report| Reports
        FA --> |Fundamentals Report| Reports
        NA --> |News Report| Reports
        SA --> |Sentiment Report| Reports

        Reports[Consolidated Reports]
    end

    Phase1 --> Phase2

    subgraph Phase2[" PHASE 2: Investment Debate "]
        Reports --> Bull[Bull Researcher<br/>Pro-Investment Arguments]
        Reports --> Bear[Bear Researcher<br/>Risk Arguments]

        Bull <--> |Debate Round| Bear
        Bear <--> |Counter Arguments| Bull

        Bull --> RM[Research Manager<br/>Judge]
        Bear --> RM

        RM --> |Investment Plan| IPlan[Investment Plan<br/>BUY/SELL/HOLD Recommendation]
    end

    Phase2 --> Phase3

    subgraph Phase3[" PHASE 3: Trading Decision "]
        IPlan --> Trader[Trader Agent<br/>Proposes Action]
        Memory1[(ChromaDB Memory<br/>Past Decisions)] -.-> Trader
        Trader --> |Trading Plan| TradePlan[Trading Proposal<br/>FINAL TRANSACTION PROPOSAL]
    end

    Phase3 --> Phase4

    subgraph Phase4[" PHASE 4: Risk Assessment Debate "]
        TradePlan --> Risky[Risky Analyst<br/>High-Risk/High-Reward]
        TradePlan --> Safe[Safe Analyst<br/>Conservative/Stable]
        TradePlan --> Neutral[Neutral Analyst<br/>Balanced View]

        Risky <--> |3-Way Debate| Safe
        Safe <--> |Counter Arguments| Neutral
        Neutral <--> |Challenge Views| Risky

        Risky --> RiskMgr[Risk Manager<br/>Final Judge]
        Safe --> RiskMgr
        Neutral --> RiskMgr

        Memory2[(ChromaDB Memory<br/>Past Outcomes)] -.-> RiskMgr

        RiskMgr --> Final[Final Trade Decision<br/>BUY/SELL/HOLD]
    end

    Phase4 --> Reflect

    Reflect[Reflection Phase<br/>Learn from Outcome] --> Memory3[(Update ChromaDB<br/>Store Decision + Context)]

    Memory3 --> End([Return Decision to User])

    style Phase1 fill:#e1f5ff
    style Phase2 fill:#fff4e1
    style Phase3 fill:#e8f5e9
    style Phase4 fill:#fce4ec
    style Reflect fill:#f3e5f5
    style Final fill:#ffeb3b,stroke:#f57c00,stroke-width:3px
```

## Detailed Agent Flow

```mermaid
sequenceDiagram
    participant User
    participant Graph as LangGraph Orchestrator
    participant Analysts as Analyst Team (4 agents)
    participant Bull as Bull Researcher
    participant Bear as Bear Researcher
    participant RM as Research Manager
    participant Trader as Trader Agent
    participant Risk as Risk Analysts (3 agents)
    participant RiskMgr as Risk Manager
    participant Memory as ChromaDB Memory

    User->>Graph: Submit (Ticker, Date)
    Graph->>Analysts: Request Analysis

    par Parallel Analysis
        Analysts->>Analysts: Market Analysis (15+ indicators)
        Analysts->>Analysts: Fundamentals Analysis
        Analysts->>Analysts: News Analysis
        Analysts->>Analysts: Sentiment Analysis
    end

    Analysts->>Graph: Return 4 Reports
    Graph->>Memory: Query similar past situations
    Memory-->>Bull: Return relevant memories
    Memory-->>Bear: Return relevant memories

    Graph->>Bull: Start debate with reports
    Graph->>Bear: Start debate with reports

    loop Debate Rounds (configurable, default=1)
        Bull->>Bear: Pro-investment argument
        Bear->>Bull: Counter-argument with risks
    end

    Bull->>RM: Submit bull case
    Bear->>RM: Submit bear case
    RM->>Memory: Query past decisions
    Memory-->>RM: Return lessons learned
    RM->>Graph: Investment Plan (Buy/Sell/Hold)

    Graph->>Trader: Investment Plan + Reports
    Trader->>Memory: Query similar trades
    Memory-->>Trader: Return past outcomes
    Trader->>Graph: Trading Proposal

    Graph->>Risk: Trading Proposal + Reports

    par 3-Way Risk Debate
        Risk->>Risk: Risky: Advocate high-reward
        Risk->>Risk: Safe: Advocate low-risk
        Risk->>Risk: Neutral: Balanced view
    end

    loop Risk Debate Rounds
        Risk->>Risk: Counter each other's arguments
    end

    Risk->>RiskMgr: All 3 perspectives
    RiskMgr->>Memory: Query past mistakes
    Memory-->>RiskMgr: Return reflections
    RiskMgr->>Graph: Final Decision (Buy/Sell/Hold)

    Graph->>Memory: Store decision + context
    Graph->>User: Final Trade Decision
```

## Data Flow Architecture

```mermaid
graph LR
    subgraph "Data Sources"
        YF[yfinance<br/>Stock Data]
        AV[Alpha Vantage<br/>Fundamentals/News]
        OAI[OpenAI<br/>News/Fundamentals]
        GN[Google News<br/>News Data]
        Local[Local DB<br/>Offline Data]
    end

    subgraph "Abstraction Layer"
        Utils[agent_utils.py<br/>Abstract Tool Interface]
        Config[default_config.py<br/>Vendor Routing]
    end

    subgraph "Agent Tools"
        StockTools[Stock Data Tools]
        TechTools[Technical Indicators<br/>15+ indicators]
        FundTools[Fundamental Tools]
        NewsTools[News Tools]
    end

    subgraph "Agents"
        MA2[Market Analyst]
        FA2[Fundamentals Analyst]
        NA2[News Analyst]
        SA2[Social Media Analyst]
    end

    YF --> Utils
    AV --> Utils
    OAI --> Utils
    GN --> Utils
    Local --> Utils

    Utils --> Config
    Config --> StockTools
    Config --> TechTools
    Config --> FundTools
    Config --> NewsTools

    StockTools --> MA2
    TechTools --> MA2
    FundTools --> FA2
    NewsTools --> NA2
    NewsTools --> SA2

    style Utils fill:#4CAF50
    style Config fill:#2196F3
```

## Memory System Architecture

```mermaid
graph TB
    subgraph "ChromaDB Collections"
        BullMem[Bull Researcher<br/>Memory Collection]
        BearMem[Bear Researcher<br/>Memory Collection]
        TraderMem[Trader<br/>Memory Collection]
        RMMem[Research Manager<br/>Memory Collection]
        RiskMgrMem[Risk Manager<br/>Memory Collection]
    end

    subgraph "Embedding Models"
        OpenAIEmb[OpenAI<br/>text-embedding-ada-002]
        OllamaEmb[Ollama<br/>nomic-embed-text]
        GoogleEmb[Google<br/>Generative AI]
    end

    subgraph "Memory Operations"
        Store[Store Decision<br/>+ Context + Outcome]
        Query[Query Similar<br/>Situations (n=2)]
        Learn[Learn from<br/>Past Mistakes]
    end

    OpenAIEmb --> BullMem
    OllamaEmb --> BearMem
    GoogleEmb --> TraderMem

    Store --> BullMem
    Store --> BearMem
    Store --> TraderMem
    Store --> RMMem
    Store --> RiskMgrMem

    BullMem --> Query
    BearMem --> Query
    TraderMem --> Query
    RMMem --> Query
    RiskMgrMem --> Query

    Query --> Learn

    style Store fill:#FF9800
    style Query fill:#03A9F4
    style Learn fill:#9C27B0
```

## Decision Flow with Conditional Logic

```mermaid
flowchart TD
    Start([Start Analysis]) --> SelectAnalysts{Select Active<br/>Analysts}

    SelectAnalysts -->|User Choice| RunAnalysts[Run Selected Analysts]
    RunAnalysts --> CheckReports{All Reports<br/>Generated?}

    CheckReports -->|No| RunAnalysts
    CheckReports -->|Yes| StartDebate[Investment Debate Phase]

    StartDebate --> DebateRound{Debate Round<br/>< Max Rounds?}
    DebateRound -->|Yes| BullTurn[Bull Argues]
    BullTurn --> BearTurn[Bear Counters]
    BearTurn --> DebateRound

    DebateRound -->|No| Judge[Research Manager Judges]
    Judge --> InvestPlan[Generate Investment Plan]

    InvestPlan --> TraderDecision[Trader Proposes Action]
    TraderDecision --> RiskDebate[Risk Assessment Debate]

    RiskDebate --> RiskRound{Risk Debate<br/>Complete?}
    RiskRound -->|Continue| RiskyArg[Risky Argues]
    RiskyArg --> SafeArg[Safe Counters]
    SafeArg --> NeutralArg[Neutral Balances]
    NeutralArg --> RiskRound

    RiskRound -->|Yes| RiskJudge[Risk Manager Judges]
    RiskJudge --> ExtractSignal[Extract BUY/SELL/HOLD]

    ExtractSignal --> FinalDecision{Valid Signal?}
    FinalDecision -->|Yes| StoreMemory[Store in ChromaDB]
    FinalDecision -->|No| Error[Return Error]

    StoreMemory --> Return([Return Final Decision])

    style StartDebate fill:#FFD54F
    style RiskDebate fill:#E91E63
    style FinalDecision fill:#4CAF50,stroke:#2E7D32,stroke-width:3px
```

## Key Features

### Multi-Agent Collaboration
- **8-11 specialized agents** working in phases
- **LangGraph orchestration** manages state transitions
- **Structured debates** with adversarial collaboration

### Memory & Learning
- **ChromaDB** stores past decisions and outcomes
- **Semantic similarity search** retrieves relevant past experiences
- **Reflection mechanism** updates memory after each decision

### Flexible Configuration
- **38+ config options** in `default_config.py`
- **Multiple LLM providers**: OpenAI, Anthropic, Google, Ollama, LMStudio
- **Multiple data vendors**: yfinance, Alpha Vantage, OpenAI, Google, Local

### Technical Analysis
- **15+ technical indicators**: MACD, RSI, Bollinger Bands, Moving Averages, ATR, etc.
- **Fundamental analysis**: P/E ratio, debt, cash flow, income statements
- **Sentiment analysis**: Social media, news sentiment
- **Macro analysis**: Global news, economic indicators

---

*Generated for TradingAgents - Multi-Agent LLM Financial Trading Framework*
