# Project Architecture

```mermaid
graph TB
    subgraph Input
        Resume[Resume Text]
        JobDescription[Job Description]
        CSV[Job Listings CSV]
    end

    subgraph DataProcessing
        LoadCSV[load_jobs_from_csv]
        ProcessJobs[process_and_store_jobs]
        CleanData[Clean & Process Data]
    end

    subgraph Embeddings
        EMB[OpenAI Embeddings]
    end
    
    subgraph Database
        DB[(ChromaDB)]
    end


    subgraph ResumeProcessing
        LLM[ChatGPT LLM]
        ProcessResume[prompt for resume processing]
        ExtractInfo[Extract Resume Info]
        
    end

    subgraph JobCompatability
        LLM2[ChatGPT LLM]
        
    end

    subgraph Recommendation
        LLM3[ChatGPT LLM]
        ResumeSummary[Prompt to summarize the resume]
        CreateQuery[Create Search Query]
        GetRecs[get_job_recommendations]
        GenEmbed[Generate Query Embedding]
        QueryDB[Query ChromaDB]
    end

    subgraph Output
        ResumeReport[Resume Report]
    end
    subgraph Output
        ResumeJobMatch[Resume Job Compatability Report]
    end
    subgraph Output
        Recommendations[Job Recommendations]
    end

    Resume -->LLM2
    JobDescription -->LLM2
    LLM2-->ResumeJobMatch

    CSV --> LoadCSV
    LoadCSV --> ProcessJobs
    ProcessJobs --> CleanData
    CleanData --> EMB
    EMB --> DB

    Resume --> LLM
    LLM --> ProcessResume
    ProcessResume --> ExtractInfo
    ExtractInfo --> ResumeReport
    
    Resume --> LLM3
    LLM3 -->  ResumeSummary
    ResumeSummary --> GenEmbed
    GenEmbed --> CreateQuery
    CreateQuery --> QueryDB
    QueryDB --> DB
    DB --> GetRecs
    GetRecs --> Recommendations
    