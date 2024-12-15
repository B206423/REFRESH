import os

from dotenv import load_dotenv
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from flask import jsonify
import uuid
from job_recommender import JobRecommender

# Load environment variables from .env
load_dotenv()

# Define the persistent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
persistent_directory = os.path.join(current_dir, "db", "chroma_db_with_metadata")
persistent_jobs_directory  = os.path.join(current_dir, "db", "chroma_db_jobs")

# Define the embedding model
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Load the existing vector store with the embedding function
db = Chroma(persist_directory=persistent_directory, embedding_function=embeddings)

# Create a retriever for querying the vector store
# `search_type` specifies the type of search (e.g., similarity)
# `search_kwargs` contains additional arguments for the search (e.g., number of results to return)
retriever = db.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3},
)

# TODO: support alternate models
#inference: llama-3.2, text embedding: nomic-embed-text

# Create a ChatOpenAI model
llm = ChatOpenAI(model="gpt-4o-mini")

# From https://python.langchain.com/v0.1/docs/use_cases/question_answering/chat_history/#contextualizing-the-question
# Contextualize question prompt
# This system prompt helps the AI understand that it should reformulate the question
# based on the chat history to make it a standalone question
contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, just "
    "reformulate it if needed and otherwise return it as is."
)

# Create a prompt template for contextualizing questions
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

# Create a history-aware retriever
# This uses the LLM to help reformulate the question based on chat history
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

# Answer question prompt
# This system prompt helps the AI understand that it should provide concise answers
# based on the retrieved context and indicates what to do if the answer is unknown
qa_system_prompt = (
    "You are an assistant for reviewing the resume and providing guidance."
    "The context is the resume and job description which will be provided in the following prompt"
    "Use the context to answer the question. "
    "If you don't know the answer, just say that you "
    "don't know. Use ten sentences maximum and keep the answer "
    "concise."
    "{context}"
)

# Create a prompt template for answering questions
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

# TODO: move this to DB but keep the interface the same
chat_histories = {}
def get_chat_history(session_id):
   chat_history = chat_histories.get(session_id)
   if chat_history is None:
      print(f"[DEBUG] no chat_history found for session_id {session_id}")
      chat_history = []
      chat_histories[session_id] = chat_history
   print(f"[DEBUG] get-Chat history count for session_id {session_id} is {len(chat_history)}")
   print(f"[DEBUG] get-Chat history:\n{chat_history}")
   return chat_history

# Create a chain to combine documents for question answering
# `create_stuff_documents_chain` feeds all retrieved context into the LLM
question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

# Create a retrieval chain that combines the history-aware retriever and the question answering chain
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
recommender = JobRecommender(str(persistent_jobs_directory))

def q_and_a(session_id, question, rag_chain=rag_chain):
  chat_history = get_chat_history(session_id)
  result = rag_chain.invoke({"input": question, "chat_history": chat_history})
  chat_history.append(HumanMessage(content=question))
  chat_history.append(SystemMessage(content=result["answer"]))
  print(f"[DEBUG] qa-Chat history count for session_id {session_id} is {len(chat_history)}")
  print(f"[DEBUG] qa-Chat history:\n{chat_history}")
  return result["answer"]

# Function to simulate a continual chat
def main_method(from_browser = False):
    print("Step 1. Loading Reading resume and job description")
    chat_history = []  # Collect chat history here (a sequence of messages)

    user_input = {}
    session_id = "localhost" + str(uuid.uuid4())

    # read from user input, this is just for example
    with open('examples/resume.txt', 'r') as file:
      resume_file_content = file.read()

    # read from user input, this is just for example
    with open('examples/job_description.txt', 'r') as file:
      jd_file_content = file.read()

    resume_rpt= resume_report(session_id, resume_file_content)
    jd_rpt = jd_compatibility_report(session_id, jd_file_content)

    print(f"Resume Report\n{resume_rpt[0]}")
    print(f"Job Compatibility Report\n{jd_rpt[0]}")

    print(f"Step3.1 Starting Job Compatibility Report\n")
    print(f"Step3.2 Initiazed recommendor with needs_data_load = {recommender.needs_data_load}\n")
    jobs_recommendations = recommender.get_job_recommendations(resume_file_content)
    
    #Print results
    print("\nTop Job Recommendations:")
    for i, job in enumerate(jobs_recommendations, 1):
        print(f"\n{i}. {job['title']}")
        print(f"Similarity Score: {job['similarity_score']:.2f}")
        print(f"Description Preview: {job['description']}")
        print("-" * 80)

def jobs_report(session_id, resume):
  print(f"Step 3.1 Creating jobs report for {session_id}")
  recommendations = recommender.get_job_recommendations(resume)
  print(f"Step 3.2 Response \n{recommendations}")
  return recommendations
   
def resume_report(session_id, resume):
    print(f"Step 2.1 Creating resume report for {session_id}")
    prompt_resume_report =  ("Please provide feedback on the resume provided below in terms of completeness and effectiveness by:"
    "1. Breaking down the match in these specific areas:"
    "   - Contact Information: Is it complete and professional?"
    "   - Resume Summary: Does it effectively highlight relevant skills and career goals?"
    "   - Education: Is it clearly presented with relevant details?"
    "   - Work Experience: Are job titles, companies, dates, and achievements clearly stated?"
    "   - Skills Section: Are both hard and soft skills adequately represented?"
    "   - Awards and Certifications: Are relevant ones included?"
    "   - Formatting: Is it consistent, readable, and ideally one to two pages long?"
    "   - Overall customization: Does it appear tailored to a specific job or industry?"
    ""
    "For each area, please:"
    "- Provide a brief assessment"
    "- Suggest improvements if needed"
    "- Identify any missing crucial components"
    ""
    "Provide a clear, structured response that helps understand how good the resume is.\n"
    "The response must be in a structured markdown format\n"
    ""
    "Resume\n\n" +
    resume)

    result = q_and_a(rag_chain=rag_chain, session_id=session_id, question=prompt_resume_report)
    print(f"Step 2.2 Response \n{result}")
    return [result]

def jd_compatibility_report(session_id, jd):
    print(f"Step 3.1 Creating job compatibility report for {session_id}")
    prompt_job_compatibility =  ("Please analyze the compatibility of the resume provided earlier "
    "with the job description provided below by:"
    "1. Calculating an overall compatibility score (0-100%)"
    "2. Breaking down the match in these specific areas:"
    "   - Hard Skills Match"
    "   - Soft Skills Match"
    "   - Job Title Alignment"
    "   - Experience Relevance"
    "   - Degree Requirements"
    ""
    "For each area, please:"
    "- Explain the match/mismatch"
    "- Highlight specific strengths"
    "- Suggest potential improvements for the candidate"
    ""
    "Job Description\n\n" +
    jd +
    "\n\nProvide a clear, structured response that helps understand how closely the resume matches the job description.\n"
    "The response must be in a structured markdown format\n")

    result = q_and_a(rag_chain=rag_chain, session_id=session_id, question=prompt_job_compatibility)
 
    print(f"Step 3.2 Response {result}")
    return [result]

# Starting point
if __name__ == "__main__":
    main_method()