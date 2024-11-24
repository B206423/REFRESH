# AI-powered Chatbot Extracts Information and Answers

# Questions about NVIDIA CUDA SDK & other websites

This document outlines a Python application that utilizes artificial intelligence to extract
information from websites and answer user queries based on that information.

**Core Functionalities:**

- **Website Exploration**: The application leverages Beautiful Soup, a Python library, to
parse the HTML structure of a website and extract relevant content.
- **Understanding Through Langchain**: Langchain, a powerful NLP (Natural Language
Processing) library, plays a crucial role in enabling the application to comprehend the
extracted website content. Langchain facilitates the creation of applications that can
interact with and understand natural language.
- **Conversational Retrieval Chains**: This application employs Langchain's
Conversational Retrieval Chains to tailor responses to the user's specific questions and
conversation history. By considering both the website content and the conversation flow,
the application generates contextually relevant answers.
- **User Interface with Streamlit**: Streamlit, a user-friendly Python library, streamlines the
development of the application's front-end. This allows users to interact with the
application through a clear and intuitive interface.

**Libraries:** Several key Python libraries contribute to the application's functionality

- **Beautiful Soup (Web Scraping)**: Parses the HTML structure of a website, allowing the
application to extract relevant text and information.
- **Langchain (Natural Language Processing)**: Plays a crucial role in enabling the
application to understand the extracted website content and user queries. Langchain
facilitates the creation of applications that can interact with and understand natural
language.
- **Langchain OpenAI (Optional)**: Integrates with OpenAI's powerful language models for
potentially more advanced chatbot capabilities (not covered in this example).
- **python-dotenv (Environment Variables)**: Securely manages environment variables
used by the application.
- **Streamlit (Front-End Development)**: Streamlines the development of the user
interface, creating a clear and intuitive experience for users to interact with the
application.
-  **Chroma (Vector Store)**: (Optional, but recommended) Stores the extracted website text
as mathematical vectors. These vectors capture the semantic meaning of the text, 
allowing for efficient comparison and retrieval of relevant information.

**How it Works:**


![NV_RAG_Approach](https://github.com/user-attachments/assets/84457814-f29d-4543-8408-2b3d8229a7cc)

1. **User Input:** Users provide the URL of a website they want to explore through the
    Streamlit interface.
2. **Website Exploration:** The application utilizes Beautiful Soup to parse the website's
    HTML, extracting relevant text and information.
3. **Understanding and Retrieval:** Langchain steps in to analyze the extracted information.
    Here, the application employs a **vector store** like Chroma to represent the extracted text
    as mathematical vectors. These vectors capture the semantic meaning of the text,
    allowing for efficient comparison and retrieval. Langchain then uses these vectors to
    identify the most pertinent sections that align with the user's potential queries.
4. **Conversational Response:** When a user enters a question, the application utilizes
    Langchain's Conversational Retrieval Chains. These chains consider both the user's
    query (also converted into a vector) and the relevant website content vectors to generate
    an informative and contextually appropriate response.
5. **Response Generation:** Based on the retrieved website content, the application doesn't
    necessarily create entirely new content. Instead, it utilizes the retrieved information to
    formulate a response that addresses the user's question directly. This response may
    involve summarizing relevant sections of the website, providing paraphrased
    explanations, or highlighting key points directly from the source material.
6. **Refinement and Improvement:** The application undergoes continuous testing with
    various websites and user queries. This testing helps identify and address any bugs,
    ultimately enhancing the application's accuracy and effectiveness.

**Beyond NVIDIA:**

While the writeup uses the NVIDIA CUDA SDK website as an example, the application
technology can be used to explore and answer user questions about many websites, making
information retrieval and exploration more efficient and user-friendly.
