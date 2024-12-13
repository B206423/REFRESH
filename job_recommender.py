import os
import pandas as pd
from typing import List, Dict, Any
from pathlib import Path

from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import chromadb
from chromadb.config import Settings, DEFAULT_TENANT, DEFAULT_DATABASE
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

# Load environment variables
load_dotenv()

class ResumeInfo(BaseModel):
    skills: List[str] = Field(description="List of technical and soft skills")
    experience_level: str = Field(description="Years of experience")
    job_titles: List[str] = Field(description="List of previous job titles")
    domains: List[str] = Field(description="List of industry domains")

class JobRecommender:
    def __init__(self, db_path: str):
        """
        Initialize the JobRecommender with the path to the ChromaDB database.
        Checks if database exists and has data before creating new one.
        
        Args:
            db_path (str): Path to the ChromaDB database
        """
        self.db_path = db_path
        self.embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
        self.chroma_client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(),
            tenant=DEFAULT_TENANT,
            database=DEFAULT_DATABASE,
        )
        self.collection_name = "job_descriptions"
        
        # Check if collection exists and has data
        existing_collections = self.chroma_client.list_collections()
        collection_exists = any(col.name == self.collection_name for col in existing_collections)
        
        if collection_exists:
            #print(f"Using existing collection: {self.collection_name}")
            self.job_collection = self.chroma_client.get_collection(name=self.collection_name)
            # Check if collection has data
            collection_data_count = self.job_collection.count()
            if collection_data_count > 0:
                #print(f"Found {len(collection_data['ids'])} existing job records")
                #print("Collection Data count: ", collection_data_count)
                self.needs_data_load = False
            else:
                print("Collection exists but is empty. Will load data.")
                self.needs_data_load = True
        else:
            print(f"Creating new collection: {self.collection_name}")
            self.job_collection = self.chroma_client.create_collection(name=self.collection_name)
            self.needs_data_load = True
        
        self.llm = ChatOpenAI(temperature=0)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    def process_and_store_jobs(self, jobs_df: pd.DataFrame) -> None:
        """Process job data from DataFrame and store in ChromaDB."""
        cleaned_data = jobs_df.dropna(subset=['job_id', 'title', 'description'])
        processed_data = cleaned_data[['job_id', 'title', 'description']].fillna('')

        print(f"Processing {len(processed_data)} jobs...")
        processed_count = 0

        for _, row in processed_data.iterrows():
            try:
                job_id = str(row['job_id'])
                title = row['title']
                description = row['description']

                # Generate embedding for the full description
                embedding = self.embedding_model.embed_documents([description])[0]
                
                # Store the complete job
                self.job_collection.add(
                    ids=[job_id],
                    embeddings=[embedding],
                    metadatas=[{
                        "title": title,
                        "description": description
                    }],
                    documents=[description]
                )
                
                processed_count += 1
                print(f"Processed job {processed_count}: {title}")

            except Exception as e:
                print(f"Error processing job {row['job_id']}: {e}")
                continue

        print(f"Successfully processed {processed_count} jobs")
    
    def load_jobs_from_csv(self, file_path: str) -> None:
        """
        Load jobs from a CSV file and store in ChromaDB if needed.
        Skips loading if database already exists with data.
        
        Args:
            file_path (str): Path to the CSV file containing job data
        """
        if not self.needs_data_load:
            print("Database already exists with data. Skipping data load.")
            return
            
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"CSV file not found at: {file_path}")

            df = pd.read_csv(file_path)
            required_columns = ['job_id', 'title', 'description']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            os.makedirs(self.db_path, exist_ok=True)
            self.process_and_store_jobs(df)
            print("Successfully loaded data into database.")
            
        except Exception as e:
            print(f"Error loading jobs from CSV: {e}")
            raise


    def process_resume(self, resume_text: str) -> Dict[str, Any]:
        """Process a resume and extract key information."""
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "Extract key information from the resume."),
                ("human", """
                Extract key information from this resume:
                {resume}
                
                Response should include:
                1. Skills (both technical and soft skills)
                2. Experience level (in years if mentioned)
                3. Job titles/roles
                4. Industry domains/fields
                
                Keep it focused on the most important elements.
                """)
            ])
            
            chain = prompt | self.llm
            response = chain.invoke({"resume": resume_text})
            
            # Create a simpler query from the response
            query = f"{resume_text} {response.content}"
            return {"query": query}
            
        except Exception as e:
            print(f"Error parsing resume: {e}")
            return {"query": resume_text}

    def get_job_recommendations(self, resume_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Get job recommendations based on a resume."""
        try:
            # Process resume
            resume_info = self.process_resume(resume_text)
            query = resume_info["query"]
            
            # Generate embedding for the query
            query_embedding = self.embedding_model.embed_documents([query])[0]
            
            # Get recommendations
            results = self.job_collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=['metadatas', 'distances'] # type: ignore
            )
            
            recommendations = []
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    metadata = results['metadatas'][0][i] # type: ignore
                    similarity_score = 1 / (1 + results['distances'][0][i]) # type: ignore
                    
                    job = {
                        'job_id': results['ids'][0][i],
                        'title': metadata['title'],
                        'description': metadata['description'][:200] + "...",  # Preview # type: ignore
                        'similarity_score': similarity_score
                    }
                    recommendations.append(job)
            
            return sorted(recommendations, key=lambda x: x['similarity_score'], reverse=True)
            
        except Exception as e:
            print(f"Error getting job recommendations: {e}")
            return []
