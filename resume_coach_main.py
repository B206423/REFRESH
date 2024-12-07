import os

from dotenv import load_dotenv
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Load environment variables from .env
load_dotenv()

# Define the persistent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
persistent_directory = os.path.join(current_dir, "db", "chroma_db_with_metadata")

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

# Create a ChatOpenAI model
llm = ChatOpenAI(model="gpt-4o-mini")

# Answer question prompt
# This system prompt helps the AI understand that it should provide concise answers
# based on the retrieved context and indicates what to do if the answer is unknown
qa_system_prompt_compatibility = (
    "You are an assistant for reviewing the resume and providing guidance."
    "I will provide a job description and a resume as 2 fields 'resume', 'job_description' in a json format. Please analyze their compatibility by:"
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
    "Provide a clear, structured response that helps understand how closely the resume matches the job description."    
    " Use the following pieces of retrieved context to answer the "
    "question. If you don't know the answer, just say that you "
    "don't know. Use three sentences maximum and keep the answer "
    "concise."
    "\n\n"
    "{context}"
)

qa_system_prompt_proofread = (
    "Please analyze the following resume and provide feedback on its completeness and effectiveness. Specifically, evaluate these key elements:"
    "Contact Information: Is it complete and professional?"
    "Resume Summary: Does it effectively highlight relevant skills and career goals?"
    "Education: Is it clearly presented with relevant details?"
    "Work Experience: Are job titles, companies, dates, and achievements clearly stated?"
    "Skills Section: Are both hard and soft skills adequately represented?"
    "Awards and Certifications: Are relevant ones included?"
    "Formatting: Is it consistent, readable, and ideally one to two pages long?"
    "Overall customization: Does it appear tailored to a specific job or industry?"
    "For each element, provide a brief assessment and suggest improvements if needed. Also, identify any missing crucial components"
    "\n\n"
    "{context}"
)

def create_rag_chain(qa_system_prompt):
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

  # Create a prompt template for answering questions
  qa_prompt = ChatPromptTemplate.from_messages(
      [
          ("system", qa_system_prompt),
          MessagesPlaceholder("chat_history"),
          ("human", "{input}"),
      ]
  )

  # Create a chain to combine documents for question answering
  # `create_stuff_documents_chain` feeds all retrieved context into the LLM
  question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

  # Create a retrieval chain that combines the history-aware retriever and the question answering chain
  rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
  return rag_chain


# Function to simulate a continual chat
def continual_chat():
    print("Step 1. Loading Reading resume and job description")
    chat_history = []  # Collect chat history here (a sequence of messages)

    initial_query = {}

    #TODO: read from user input
    with open('resume.txt', 'r') as file:
      initial_query["resume"] = file.read()

    initial_query["job_description"] = ""

    #TODO: read from user input
    with open('job_description.txt', 'r') as file:
      initial_query["job_description"] = file.read()

    option = input("Select option 1 for 'Resume Report' or 2 for 'Job Compatibility Report': ")
    if option.strip()  == '1':
       qa_system_prompt = qa_system_prompt_proofread
       option_string = 'Resume Report'
    else:
       qa_system_prompt = qa_system_prompt_compatibility
       option_string = 'Job Compatibility Report'

    # Process the initial query through the retrieval chain
    print(f"Step 2. Creating rag chain for {option_string}")
    rag_chain = create_rag_chain(qa_system_prompt)
    result = rag_chain.invoke({"input": str(initial_query), "chat_history": chat_history})
    # Display the AI's response
    print(f"Step 3. Result of {option_string}")
    print(f"AI: {result['answer']}")
    # Update the chat history
    chat_history.append(HumanMessage(content=str(initial_query)))
    chat_history.append(SystemMessage(content=result["answer"]))

    print("Start chatting with the AI! Type 'exit' to end the conversation.")

    while True:
        query = input("You: ")
        if query.lower() == "exit":
            break
        # Process the user's query through the retrieval chain
        result = rag_chain.invoke({"input": query, "chat_history": chat_history})
        # Display the AI's response
        print(f"AI: {result['answer']}")
        # Update the chat history
        chat_history.append(HumanMessage(content=query))
        chat_history.append(SystemMessage(content=result["answer"]))


# Main function to start the continual chat
if __name__ == "__main__":
    continual_chat()
