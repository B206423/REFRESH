#Your Full Name : Subhra Ghosh
#Your Uplevel Email Address : b206423@gmail.com & sj_ghosh@yahoo.com
#Name of the Problem Statement of Submission : 
# Mini Project   
# Problem-01: AI-Assisted Learning for NVIDIA SDKs and Toolkits
#
#install these programs
#pip install streamlit langchain langchain-openai langchain_community beautifulsoup4 python-dotenv cromadb 

# Chat with website 
import streamlit as st 
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from dotenv import  load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

#executed if code is run as a program and not module                 
if __name__ == "__main__":
    #Load Enviroment 
    load_dotenv()

#Chat Debug using sidebar
def put_on_chat_sidebar(sidetxt):
    with st.sidebar:
        st.write(sidetxt)
    return()

#converts Website Page(s) into VectorStore (in chunks) - vectorization & embedding 
def get_vectorstore_from_url(url):

    #enter URL as https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html
    #website document to text form
    loader = WebBaseLoader(url)
    document = loader.load()
    
    #split document
    text_splitter = RecursiveCharacterTextSplitter() 
    document_chunk = text_splitter.split_documents(document)
    
    #For debugging 
    #put_on_chat_sidebar(document_chunk[0])
    
    #create vector store from chunks 
    url_vector_store = Chroma.from_documents(document_chunk, OpenAIEmbeddings()) 
    
    return(url_vector_store)

#Retrieve document chain using similarity search 
def get_context_retriever_chain(vector_stores):
    llm = ChatOpenAI()
    
    retriever = vector_stores.as_retriever()

    prompt = ChatPromptTemplate.from_messages([
      MessagesPlaceholder(variable_name="chat_history"),
      ("user", "{input}"),
      ("user", "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation")
    ])
    
    retriever_chain = create_history_aware_retriever(llm, retriever, prompt)
    
    st.write(retriever_chain)
    
    return retriever_chain

def get_conversational_rag_chain(retriever_chain):
    
    llm = ChatOpenAI()
    
    prompt = ChatPromptTemplate.from_messages([
      ("system", "Answer the user's questions based on the below context:\n\n{context}"),
      MessagesPlaceholder(variable_name="chat_history"),
      ("user", "{input}"),
    ])
    
    stuff_documents_chain = create_stuff_documents_chain(llm,prompt)
    
    return create_retrieval_chain(retriever_chain, stuff_documents_chain)

#get_response of user query function 
def get_response(user_input):
    
    #Wcreate conversational state
    retriever_chain = get_context_retriever_chain(st.session_state.vector_store)
    
    #create conversation
    conversational_rag_chain = get_conversational_rag_chain(retriever_chain) 
    
    response = conversational_rag_chain.invoke({
        "chat_history": st.session_state.chat_history,
        "input": user_input
    })
    
    return response['answer']

#Web App Config
st.set_page_config(page_title="Chat with websites", page_icon="🤖")
st.title("Chat with websites")

#Sidebar
with st.sidebar:
    st.header("Settings")
    website_url = st.text_area("Website URL")

#Process the Website URL    
if website_url is None or website_url == "":
    st.info("Please enter a website to use the Bot.")

else: 
    #intialize session state 
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
        AIMessage(content="Hello, I am a bot. How can I help you?"),
    ]
    
    #persistant vector store 
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = get_vectorstore_from_url(website_url)
               
    #User Input    
    user_query = st.chat_input("Type your message here ...")

    #Web Messaging 
    if user_query !="" and user_query is not None:
        response = get_response(user_query)
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        st.session_state.chat_history.append(AIMessage(content=response))
     
    #Chat Conversation
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.write(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.write(message.content)        
                
