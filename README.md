# Resume AI Coach

Project Name: **REFRESH**

Resume Evaluation, Feedback, Revision, and Enhancement Service Hub


## Feature Set 

### 1. Review Resume/CV
-

### 2. Check Resume's compatibility with Job Description
-

### 3. General Recommendations 
- Recommend changes to Resume based on similar Job Descriptions (JD) from JD history corpus

### 4. Chat with Coach 
-

### 5. MLOPS
-
-
-

## Technolgy Stack 
- Web: jQuery, html 
- Vector DB: Chroma DB
- Embedding : OpenAI
- LLM : OpenAI gpt4o-mini Model

## Setup
### Prerequisites

- Docker

### Installation

1. Build Docker image

   ```bash
   docker build -t refresh .
   ```

2. Run the Docker container

   ```bash
   docker run --name=refresh --hostname=refresh -p 8000:8000 -e PORT=8000 -v "<fullpath to chroma_db_jobs>:/app/db/chroma_db_jobs" --rm -it refresh
   ```

3. Launch browser and go to http://localhost:$PORT/

## Release notes

### v1.2
  - add chat

### v1.1
  - added job recommender (command line only)

### v1.0
  Working UI
  - Upload Resume, Job description
  - Preview Resume, Job Description
  - "Get Report" button to 
    - generate and display a Resume report
    - generate and display Job Compatibility report

### v0.3

  Run inside a Docker container
  Add Basic web UI to display the result

### v0.2

  Support for both resume report and job compatibility report

### v0.1

- Store any example resume in 'resume.txt' and store any example job description in 'job_description.txt'
or use the examples provided as follows

   ```bash
   mv examples/job_description.txt.example job_description.txt
   mv examples/resume.txt.example resume.txt
   ```
- Run resume_coach_main.py