# Resume AI Coach

Project Name: **REFRESH**

Resume Evaluation, Feedback, Revision, and Enhancement Service Hub


## Feature Set 

### 1. Preview Resume/CV
 - Preview the resume contents
   - If resume is in pdf format, parse the resume

### 2. Preview Job Description
 - Preview the Job Description
   - If Job Description is in pdf format, parse the document

### 3. Resume Report
 - Assess the resume and provide qualitative feedback - point out anything missing and suggest improvements in the following components
    1. Contact Information
    2. Resume Summary
    3. Education
    4. Work Experience
    5. Skills Section
    6. Awards and Certifications
    7. Formatting
    8. Overall Customization

### 4. Job Compatibility Report
  - Provide an overall compatibity score of the Resume with the Job Description
  - Provide specific feedback on the following with respect to how well they match, relevant strengths in the resume and suggest improvements if necessary
    1. Hard Skills
    2. Soft Skills
    3. Job Title Alignment
    4. Experience Relevance
    5. Degree Requirements


### 5. Job Recommendations Report
  - Provide other matching jobs for the given resume from a corpus of available jobs

### 6. Chat with Coach 
  - Ability to chat on anything the user wants while maintaining the context of the resume and job description

## Sequence diagram

![Sequence Diagram](./docs/sequencediagram.svg)

## Technolgy Stack 
- Web: jQuery, html 
- Vector DB: Chroma DB
- Embedding: OpenAI
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
   docker run --name=refresh --hostname=refresh -p 8001:8001 -e PORT=8001 -v "chromadb:/app/db/chroma_db_jobs" --rm -it refresh
   ```

3. Launch browser and go to http://localhost:$PORT/

## Release notes

### v2.1
  - UI support for changing LLM inference model (backend pending)

### v2.0
  - improve layout
  - add job recommendations to the web UI
  - changes to make it work with https
  - add support for multiple user sessions
  - fix issues with missing chat context
  - add pdf reader support
  - add documentation

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

- CLI support. Store any example resume in 'resume.txt' and store any example job description in 'job_description.txt'
or use the examples provided as follows

   ```bash
   mv examples/job_description.txt.example job_description.txt
   mv examples/resume.txt.example resume.txt
   ```
- Run resume_coach_main.py
