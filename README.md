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
- Web: Streamlit 
- Vector DB: Chroma DB
- Embedding : OpenAI
- LLM : OpenAI 4o Model
- 

## Setup
### Prerequisites

- Python 3.10 or 3.11
- Poetry (Follow this [Poetry installation tutorial](https://python-poetry.org/docs/#installation) to install Poetry on your system)

### Installation

1. Install dependencies using Poetry:

   ```bash
   poetry install --no-root
   ```

2. Set up your environment variables:

   - Rename the `.env.example` file to `.env` and update the variables inside with your own values. Example:

   ```bash
   mv examples/.env.example .env
   ```

3. Activate the Poetry shell to run the examples:

   ```bash
   poetry shell
   ```

4. Run the code examples:

   ```bash
    python resume_coach_main.py
   ```

## Release notes

### v0.1

- Store any example resume in 'resume.txt' and store any example job description in 'job_description.txt'
or use the examples provided as follows

   ```bash
   mv examples/job_description.txt.example job_description.txt
   mv examples/resume.txt.example resume.txt
   ```
- Run resume_coach_main.py


### Git Quick setup 

```bash
  https://github.com/B206423/REFRESH.git
```
	
- Get started by creating a new file or uploading an existing file. 
- We recommend every repository include a README, LICENSE, and .gitignore.

### …or create a new repository on the command line

1. echo "# REFRESH" >> README.md
2. git init
3. git add README.md
4. git commit -m "first commit"
5. git branch -M main
6. git remote add origin https://github.com/B206423/REFRESH.git
7. git push -u origin main

### …or push an existing repository from the command line

1. git remote add origin https://github.com/B206423/REFRESH.git
2. git branch -M main
3. git push -u origin main
