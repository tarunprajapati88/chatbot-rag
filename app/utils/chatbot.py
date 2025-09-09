import streamlit as st
from collections import defaultdict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from dotenv import load_dotenv

def get_context_retriever_chain(vectordb):
    """
    Create a context retriever chain for generating responses based on the chat history and vector database
    """
    load_dotenv()
    # ✅ Fixed model name
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", 
        temperature=0.2, 
        convert_system_message_to_human=True
    )
    retriever = vectordb.as_retriever()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful chatbot. Use the provided context to answer questions accurately. If you don't know the answer or lack sufficient context, ask for more details. Don't invent answers. Context: {context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])
    
    chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
    retrieval_chain = create_retrieval_chain(retriever, chain)
    return retrieval_chain

def get_response(question, chat_history, vectordb):
    """
    Generate a response with limited chat history to prevent context overflow
    """
    chain = get_context_retriever_chain(vectordb)
    # ✅ Limit chat history to prevent token overflow
    limited_history = chat_history[-10:] if len(chat_history) > 10 else chat_history
    response = chain.invoke({"input": question, "chat_history": limited_history})
    return response["answer"], response["context"]

def chat(vectordb):
    """
    Handle the chat functionality with proper session state management
    """
    # ✅ Initialize chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display existing chat history
    for message in st.session_state.chat_history:
        with st.chat_message("assistant" if isinstance(message, AIMessage) else "user"):
            st.write(message.content)
    
    # Handle new user input
    user_query = st.chat_input("Ask a question:")
    if user_query:
        # Add user message to chat history
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_query)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response, context = get_response(user_query, st.session_state.chat_history[:-1], vectordb)
                st.write(response)
        
        # Add assistant response to chat history
        st.session_state.chat_history.append(AIMessage(content=response))
        
        # ✅ Improved source display
        with st.sidebar:
            st.subheader("📚 Sources")
            metadata_dict = defaultdict(list)
            for doc in context:
                source = doc.metadata.get('source', 'Unknown')
                page = doc.metadata.get('page', 'N/A')
                metadata_dict[source].append(page)
            
            for source, pages in metadata_dict.items():
                st.write(f"**Source:** {source}")
                st.write(f"**Pages:** {', '.join(map(str, pages))}")
                st.write("---")
