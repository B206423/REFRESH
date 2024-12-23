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
        print(f"[DEBUG] Collections list is {existing_collections}")
        collection_exists = any(col.name == self.collection_name for col in existing_collections)
        
        if collection_exists:
            print(f"[DEBUG] Using existing collection: {self.collection_name}")
            self.job_collection = self.chroma_client.get_collection(name=self.collection_name)
            # Check if collection has data
            collection_data_count = self.job_collection.count()
            if collection_data_count > 0:
                print("[DEBUG] Collection Data count: ", collection_data_count)
                self.needs_data_load = False
            else:
                print("[DEBUG] Collection exists but is empty. Will load data.")
                self.needs_data_load = True
        else:
            print(f"[DEBUG] No collection by name {self.collection_name} exists, no job recommendations will be provided")
            #self.job_collection = self.chroma_client.create_collection(name=self.collection_name)
            #self.needs_data_load = True
        
        self.llm = ChatOpenAI(temperature=0)
        # unused, remove?
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
                print(f"[DEBUG] Processed job {processed_count}: {title}")

            except Exception as e:
                print(f"[ERROR] Error processing job {row['job_id']}: {e}")
                continue

        print(f"[DEBUG] Successfully processed {processed_count} jobs")
    
    def load_jobs_from_csv(self, file_path: str) -> None:
        """
        Load jobs from a CSV file and store in ChromaDB if needed.
        Skips loading if database already exists with data.
        
        Args:
            file_path (str): Path to the CSV file containing job data
        """
        if not self.needs_data_load:
            print("[DEBUG] Database already exists with data. Skipping data load.")
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
            print("[DEBUG] Successfully loaded data into database.")
            
        except Exception as e:
            print(f"[ERROR] Error loading jobs from CSV: {e}")
            raise