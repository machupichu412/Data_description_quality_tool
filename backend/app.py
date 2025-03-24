import os
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import tempfile
from langchain_openai import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.document_loaders import TextLoader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Check if OpenAI API key is set
if not os.getenv("OPENAI_API_KEY"):
    print("Warning: OPENAI_API_KEY environment variable not set. LLM functionality will not work.")

# Initialize vector store with quality guidelines
def initialize_vector_store():
    try:
        # Load the quality guidelines
        loader = TextLoader("./data/quality_guidelines.md")
        documents = loader.load()
        
        # Split the documents into chunks
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        docs = text_splitter.split_documents(documents)
        
        # Create the vector store
        embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
        vector_store = FAISS.from_documents(docs, embeddings)
        
        print("Vector store initialized successfully")
        return vector_store
    except Exception as e:
        print(f"Error initializing vector store: {e}")
        return None

# Initialize the vector store
vector_store = initialize_vector_store()

# Create a prompt template for evaluating data descriptions
template = """
You are a data quality expert evaluating the quality of data descriptions.
Your task is to determine if a data description meets the quality guidelines.

Here are some relevant quality guidelines based on your query:
{context}

Based on these guidelines, evaluate the following data description:
"{description}"

Provide your evaluation in the following format:
- Decision: [PASS/FAIL]
- Reasoning: [Your detailed reasoning for the decision]

Remember to consider clarity, completeness, accuracy, consistency, and relevance in your evaluation.
"""

prompt = PromptTemplate(
    input_variables=["context", "description"],
    template=template,
)

# Create the LLM chain
def get_llm_chain():
    llm = OpenAI(temperature=0)
    return LLMChain(llm=llm, prompt=prompt)

@app.route('/api/evaluate', methods=['POST'])
def evaluate_descriptions():
    if not vector_store:
        return jsonify({"error": "Vector store not initialized. Check if OpenAI API key is set."}), 500
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({"error": "Only CSV files are supported"}), 400
    
    try:
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp:
            file.save(temp.name)
            # Read the CSV file
            df = pd.read_csv(temp.name)
        
        # Check if the CSV has a 'description' column
        if 'description' not in df.columns:
            return jsonify({"error": "CSV file must contain a 'description' column"}), 400
        
        # Initialize the LLM chain
        chain = get_llm_chain()
        
        results = []
        
        # Process each description
        for idx, row in df.iterrows():
            description = row['description']
            
            # Skip empty descriptions
            if pd.isna(description) or description.strip() == '':
                results.append({
                    "description": "",
                    "decision": "FAIL",
                    "reasoning": "Empty description"
                })
                continue
            
            # Get relevant context from the vector store
            docs = vector_store.similarity_search(description, k=3)
            context = "\n".join([doc.page_content for doc in docs])
            
            # Run the LLM chain
            response = chain.run(context=context, description=description)
            
            # Parse the response
            decision = "PASS" if "PASS" in response.split("Decision:")[1].split("\n")[0] else "FAIL"
            reasoning = response.split("Reasoning:")[1].strip()
            
            results.append({
                "description": description,
                "decision": decision,
                "reasoning": reasoning
            })
        
        return jsonify({"results": results}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)
