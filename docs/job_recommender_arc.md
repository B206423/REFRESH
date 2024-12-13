# job_reccomender Architecture

```mermaid
graph TB
    subgraph Input
        CSV[Job Listings CSV]
        Resume[Resume Text]
    end

    subgraph JobRecommender
        direction TB
        Init[Initialization]
        DB[(ChromaDB)]
        EMB[OpenAI Embeddings]
        LLM[ChatGPT LLM]
        
        subgraph DataProcessing
            LoadCSV[load_jobs_from_csv]
            ProcessJobs[process_and_store_jobs]
            CleanData[Clean & Process Data]
        end
        
        subgraph ResumeProcessing
            ProcessResume[process_resume]
            ExtractInfo[Extract Key Information]
            CreateQuery[Create Search Query]
        end
        
        subgraph Recommendation
            GetRecs[get_job_recommendations]
            GenEmbed[Generate Query Embedding]
            QueryDB[Query ChromaDB]
            RankResults[Rank Results]
        end
    end

    subgraph Output
        JobRecs[Job Recommendations]
    end

    %% Data Flow
    CSV --> LoadCSV
    LoadCSV --> ProcessJobs
    ProcessJobs --> CleanData
    CleanData --> |Store Jobs| DB
    EMB --> ProcessJobs

    Resume --> ProcessResume
    ProcessResume --> ExtractInfo
    LLM --> ExtractInfo
    ExtractInfo --> CreateQuery
    
    CreateQuery --> GetRecs
    GetRecs --> GenEmbed
    EMB --> GenEmbed
    GenEmbed --> QueryDB
    DB --> QueryDB
    QueryDB --> RankResults
    RankResults --> JobRecs

    %% Styling with lighter colors for better readability
    classDef storage fill:#e0e0ff,stroke:#333,stroke-width:2px
    classDef process fill:#f0f0ff,stroke:#333,stroke-width:1px
    classDef input fill:#e0ffe0,stroke:#333,stroke-width:1px
    classDef output fill:#fff0e0,stroke:#333,stroke-width:1px
    
    class DB storage
    class CSV,Resume input
    class JobRecs output
    class LoadCSV,ProcessJobs,CleanData,ProcessResume,ExtractInfo,CreateQuery,GetRecs,GenEmbed,QueryDB,RankResults process
    ```