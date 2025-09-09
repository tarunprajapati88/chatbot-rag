import os
from utils.prepare_vectordb import get_vectorstore

def initialize_session_state_variables(st):
    """
    Initialize session state variables for the Streamlit application
    
    Parameters:
    - st (streamlit.delta_generator.DeltaGenerator): Streamlit's DeltaGenerator object used for rendering elements
    """
    # Ensure docs directory exists
    if not os.path.exists("docs"):
        os.makedirs("docs")
    
    # Get the list of uploaded documents
    upload_docs = os.listdir("docs")
    
    # List of session state variables to initialize
    variables_to_initialize = [
        "chat_history", 
        "uploaded_pdfs", 
        "processed_documents", 
        "vectordb", 
        "previous_upload_docs_length"
    ]
    
    # Iterate over the variables and initialize them if not present in the session state 
    for variable in variables_to_initialize:
        if variable not in st.session_state:
            if variable == "processed_documents":
                # Set to the name of the files present in the docs folder
                st.session_state.processed_documents = upload_docs
            elif variable == "vectordb":
                # Handle case when no documents exist yet
                if upload_docs:
                    # Set to vector database if documents exist
                    st.session_state.vectordb = get_vectorstore(upload_docs, from_session_state=True)
                else:
                    # Set to None if no documents exist
                    st.session_state.vectordb = None
            elif variable == "previous_upload_docs_length":
                # Set to the quantity of documents in the docs folder during app startup
                st.session_state.previous_upload_docs_length = len(upload_docs)
            else:
                # Initialize other variables as empty lists
                st.session_state[variable] = []
