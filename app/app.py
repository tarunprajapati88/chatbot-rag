import streamlit as st
import os
from utils.save_docs import save_docs_to_vectordb
from utils.session_state import initialize_session_state_variables
from utils.prepare_vectordb import get_vectorstore
from utils.chatbot import chat

class ChatApp:
    """
    A Streamlit application for chatting with PDF documents
    """
    def __init__(self):
        """
        Initializes the ChatApp class
        """
        # Ensure the docs folder exists
        if not os.path.exists("docs"):
            os.makedirs("docs")

        # Configurations and session state initialization
        st.set_page_config(page_title="RAG based Chatbot with PDF")
        st.title("Rag Chatbot with PDF 📄🤖")
        initialize_session_state_variables(st)
        self.docs_files = st.session_state.processed_documents

    def run(self):
        """
        Runs the Streamlit app for chatting with PDFs
        """
        upload_docs = os.listdir("docs")
        
        # Sidebar frontend for document upload
        with st.sidebar:
            st.subheader("Your documents")
            if upload_docs:
                st.write("📄 **Uploaded Documents:**")
                for doc in upload_docs:
                    st.write(f"• {doc}")
            else:
                st.info("No documents uploaded yet.")
            
            st.subheader("Upload PDF documents")
            pdf_docs = st.file_uploader(
                "Select PDF documents and click 'Process'", 
                type=['pdf'], 
                accept_multiple_files=True
            )
            
            if pdf_docs:
                with st.spinner("Processing documents..."):
                    save_docs_to_vectordb(pdf_docs, upload_docs)

        # Unlocks the chat when document is uploaded
        if self.docs_files or st.session_state.uploaded_pdfs:
            # Check if new documents were uploaded to update vectordb
            if len(upload_docs) > st.session_state.get('previous_upload_docs_length', 0):
                with st.spinner("Updating knowledge base..."):
                    st.session_state.vectordb = get_vectorstore(upload_docs, from_session_state=True)
                    st.session_state.previous_upload_docs_length = len(upload_docs)
                st.success("Knowledge base updated!")
            
            # ✅ Updated: Remove chat_history assignment since it's managed internally
            chat(st.session_state.vectordb)

        # Locks the chat until a document is uploaded
        else:
            st.info("📤 Upload a PDF file to start chatting with it. You can upload multiple files, and they'll be saved for future sessions!")
            
            # Optional: Add some helpful instructions
            with st.expander("ℹ️ How to use"):
                st.write("""
                1. **Upload PDFs**: Use the sidebar to upload one or more PDF documents
                2. **Wait for processing**: The system will process and index your documents
                3. **Start chatting**: Once processed, you can ask questions about your documents
                4. **View sources**: Check the sidebar during chat to see which parts of your documents were used to answer your questions
                """)

if __name__ == "__main__":
    app = ChatApp()
    app.run()
