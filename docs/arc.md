# Project Architecture

```mermaid
graph TB
    subgraph Input
        CSV[Job Listings CSV]
        Resume[Resume Text]
    end

    subgraph DataProcessing
        LoadCSV[load_jobs_from_csv]
        ProcessJobs[process_and_store_jobs]
        CleanData[Clean & Process Data]
    end

    subgraph Database
        DB[(ChromaDB)]
    end

    subgraph Embeddings
        EMB[OpenAI Embeddings]
    end

    subgraph LanguageModel
        LLM[ChatGPT LLM]
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
    end

    subgraph Output
        Recommendations[Job Recommendations]
    end

    CSV --> LoadCSV
    LoadCSV --> ProcessJobs
    ProcessJobs --> CleanData
    CleanData --> DB

    Resume --> ProcessResume
    ProcessResume --> ExtractInfo
    ExtractInfo --> CreateQuery
    CreateQuery --> GenEmbed
    GenEmbed --> EMB
    GenEmbed --> QueryDB
    QueryDB --> DB
    QueryDB --> GetRecs
    GetRecs --> Recommendations
    ```