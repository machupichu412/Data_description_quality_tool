import os
import pandas as pd
import re
import threading
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
import tempfile
from datetime import datetime
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from database import (
    add_description, add_descriptions_and_file_entries, add_file_entries_batch,
    add_processed_description, add_uploaded_file, check_for_processed,
    get_description_id, get_description_by_id, get_uploaded_file,
    get_recent_files, get_descriptions_by_file, update_file_statistics,
    update_file_processing_status, get_or_create_uploaded_file,
    get_file_descriptions_with_results
)

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure CORS explicitly
CORS(app, 
    resources={r"/*": {"origins": "http://localhost:3000"}},
    supports_credentials=True,
    allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
    expose_headers=['Content-Length', 'X-CSRFToken'],
    methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD']
)

@app.before_request
def before_request():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS,HEAD')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Max-Age', '86400')  # 24 hours
    return response

# Global queue to track file processing
processing_queue = []

# Lock for thread-safe operations on the queue
queue_lock = threading.Lock()

# Create upload directory if it doesn't exist
UPLOAD_FOLDER = os.path.join('data', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Create a prompt template for evaluating data descriptions
initial_prompt = PromptTemplate(
    input_variables=["description"],
    template="""<|system|>You are a data quality evaluator. Your task is to classify data descriptions as 'Pass' or 'Fail' based on best practices for clarity, precision, and consistency.
    A high-quality ('Pass') data description should:
    1. Avoid self-referencing or circular definitions.
    2. Clarify the meaning of outliers using business-specific distinctions.
    3. Use singular tense unless referring to a naturally plural concept.
    4. Define what something is, not what it is not.
    5. Use clear, descriptive sentences to avoid ambiguity.
    6. Expand uncommon abbreviations at first use.
    7. Be precise and allow only one interpretation.
    8. Be self-contained and not rely on references to other fields.
    9. Optionally include example values to improve clarity and consistency.
    10. Explicitly define decode or derivation logic.
    Evaluate the following description carefully. If it violates any of these principles, label it as 'Fail' Otherwise, label it 'Pass'.
    DESCRIPTION:
    {description}
    END DESCRIPTION
    Your response should be a single word: 'Pass' or 'Fail'.<|end|><|assistant|>
    """
)

followup_prompt = PromptTemplate(
    input_variables=["decision", "description"],
    template="""
    You are a data quality evaluator. Your task is to justify why a data description is classified as 'Pass' or 'Fail'.
    A high-quality ('Pass') data description should:
    1. Avoid self-referencing or circular definitions.
    2. Clarify the meaning of outliers using business-specific distinctions.
    3. Use singular tense unless referring to a naturally plural concept.
    4. Define what something is, not what it is not.
    5. Use clear, descriptive sentences to avoid ambiguity.
    6. Expand uncommon abbreviations at first use.
    7. Be precise and allow only one interpretation.
    8. Be self-contained and not rely on references to other fields.
    9. Optionally include example values to improve clarity and consistency.
    10. Explicitly define decode or derivation logic.
    'Pass' means the description passes all the principles listed above.
    'Fail' means the description fails to meet any of the principles listed above.
    The following description has been classified as {decision}:
    {description}
    Justify the decision with a clear explanation.
    If the description is classified as 'Fail', suggest a revised version that adheres to the principles.
    """
)

parser = StrOutputParser()

phi_llm = OllamaLLM(model=os.getenv('CLASSIFY_MODEL'), temperature=0.0)

deepseek_llm = OllamaLLM(model=os.getenv('REASON_MODEL'))

# Helper function to process files in background
def process_file_in_background(file_id, file_path, filename):
    try:
        # Update status to processing
        with queue_lock:
            for item in processing_queue:
                if item['id'] == file_id:
                    item['status'] = 'processing'
                    item['progress'] = 0
                    break
        
        # Get the uploaded file entry
        uploaded_file = get_or_create_uploaded_file(file_id)
        
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Check if the CSV has a 'description' column
        if 'description' not in df.columns:
            with queue_lock:
                for item in processing_queue:
                    if item['id'] == file_id:
                        item['status'] = 'error'
                        item['error'] = "CSV file must contain a 'description' column"
                        break
            return

        # Get LLM chains
        initial_chain = initial_prompt | phi_llm | parser
        followup_chain = followup_prompt | deepseek_llm | parser
        
        file_results = []
        pass_count = 0
        total_rows = len(df)
        
        # Process each description
        for idx, row in df.iterrows():
            description = row['description']
            
            # Update progress
            progress = int((idx / total_rows) * 100)
            with queue_lock:
                for item in processing_queue:
                    if item['id'] == file_id:
                        item['progress'] = progress
                        break
            
            # Skip empty descriptions
            if pd.isna(description) or description.strip() == '':
                result = {
                    "description": "",
                    "decision": "FAIL",
                    "reasoning": "Empty description"
                }
                file_results.append(result)
                continue
            
            # Check cache for existing processed description
            processed, desc_id = check_for_processed(description)
            if processed:
                desc = get_description_by_id(desc_id)
                processed_desc = get_description_by_id(desc.processed_id)
                result = {
                    "description": description,
                    "decision": "PASS" if processed_desc.pass_ else "FAIL",
                    "reasoning": processed_desc.reasoning
                }
                if processed_desc.pass_:
                    pass_count += 1
            else:
                # Run the LLM chain
                initial_decision = initial_chain.invoke({
                    "description": description,
                })
                
                # Ensure valid decision
                attempts = 0
                while ("pass" not in initial_decision.lower() and "fail" not in initial_decision.lower()) and attempts < 3:
                    initial_decision = initial_chain.invoke({
                        "description": description,
                    })
                    attempts += 1
                
                # Parse the response
                decision = "PASS" if "pass" in initial_decision.lower() else "FAIL"
                
                # Run followup prompt
                reasoning = followup_chain.invoke({
                    "decision": decision,
                    "description": description,
                })
                
                # Remove content within <think> and </think>
                stripped_reasoning = re.sub(r'<think>.*?</think>', '', reasoning, flags=re.DOTALL).strip()
                
                # Add processed description
                processed_desc_id = add_processed_description(decision == "PASS", stripped_reasoning)
                if not processed_desc_id:
                    raise Exception("Failed to add processed description")
                
                # Add description and link to processed description
                desc_id = add_description(description, processed_desc_id)
                if not desc_id:
                    raise Exception("Failed to add description")
                
                # Add file entry
                add_file_entries_batch([desc_id], file_id)
                
                result = {
                    "description": description,
                    "decision": decision,
                    "reasoning": stripped_reasoning
                }
                
                if decision == "PASS":
                    pass_count += 1
            
            file_results.append(result)
            
        # Update file statistics
        update_file_statistics(file_id, len(file_results), pass_count)
        
        # Update processing status to completed
        update_file_processing_status(file_id, "completed")
        
        with queue_lock:
            for item in processing_queue:
                if item['id'] == file_id:
                    item['status'] = 'completed'
                    item['progress'] = 100
                    break
        
    except Exception as e:
        error_msg = f"Error processing file: {str(e)}"
        
        # Update error status
        update_file_processing_status(file_id, "error", error_msg)
        
        with queue_lock:
            for item in processing_queue:
                if item['id'] == file_id:
                    item['status'] = 'error'
                    item['error'] = error_msg
                    break

@app.route('/api/health', methods=['GET'])
@cross_origin()
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/files', methods=['GET'])
@cross_origin()
def get_files():
    """Get a list of recently uploaded files."""
    files = get_recent_files(limit=20)
    return jsonify({"files": files}), 200

@app.route('/api/files/descriptions/<int:file_id>', methods=['GET'])
@cross_origin()
def get_file_descriptions(file_id):
    """Get all descriptions from a specific file."""
    descriptions = get_descriptions_by_file(file_id)
    return jsonify(descriptions), 200

@app.route('/api/queue', methods=['GET'])
@cross_origin()
def get_processing_queue():
    """Get the current processing queue status."""
    with queue_lock:
        # Get queue items from database
        new_queue_items = load_existing_files_to_queue()
        
        # Add new items to the queue if they're not already present
        for item in new_queue_items:
            if not any(q['id'] == item['id'] for q in processing_queue):
                processing_queue.append(item)
        
        # Return a copy of the queue to avoid race conditions
        queue_copy = [item.copy() for item in processing_queue]
        
        # Clean up completed items older than 1 hour
        current_time = datetime.now()
        for item in processing_queue.copy():
            if item['status'] in ['completed', 'error']:
                upload_time = datetime.fromisoformat(item['upload_date'])
                time_diff = (current_time - upload_time).total_seconds() / 3600
                if time_diff > 1:  # Remove if older than 1 hour
                    processing_queue.remove(item)
        
        return jsonify({'queue': queue_copy}), 200

@app.route('/api/download/<int:file_id>', methods=['GET'])
@cross_origin()
def download_results(file_id):
    """Generate and download results for a specific file."""
    descriptions = get_descriptions_by_file(file_id)
    
    if not descriptions:
        return jsonify({"error": "File not found or no descriptions available"}), 404
    
    # Convert to DataFrame
    df = pd.DataFrame(descriptions)
    
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
    df.to_csv(temp_file.name, index=False)
    
    return send_file(
        temp_file.name,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'evaluation_results_{file_id}.csv'
    )

@app.route('/api/files/<int:file_id>/delete', methods=['DELETE'])
@cross_origin()
def delete_file(file_id):
    try:
        success = remove_file(file_id)
        if success:
            return jsonify({'message': 'File deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete file'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/<int:file_id>/download', methods=['GET'])
@cross_origin()
def download_file_results(file_id):
    try:
        # Get the file from database
        descriptions = get_file_descriptions_with_results(file_id)
        if not descriptions:
            return jsonify({'error': 'File not found'}), 404
        
        # Convert to DataFrame
        df = pd.DataFrame(descriptions)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            df.to_csv(temp_file.name, index=False)
            return send_file(temp_file.name, as_attachment=True, 
                           download_name=f"evaluation_results_{file_id}.csv")
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/upload', methods=['POST'])
@cross_origin()
def upload_files():
    """Upload one or more CSV files."""
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files[]')
    uploaded_files = []

    for file in files:
        if file.filename == '':
            continue

        if not file.filename.endswith('.csv'):
            continue

        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        try:
            # Save the file
            file.save(file_path)
            
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Check if the CSV has a 'description' column
            if 'description' not in df.columns:
                return jsonify({'error': 'CSV file must contain a \'description\' column'}), 400
                
            # Check if file already exists in database
            # file_exists = get_uploaded_file(file.filename)
            # if file_exists:
            #     return jsonify({'error': 'File already exists in database'}), 400
                
            # Add file record to database
            uploaded_file = add_uploaded_file(file.filename, os.path.getsize(file_path))
            
            # Add file to processing queue
            with queue_lock:
                processing_queue.append({
                    'id': uploaded_file,
                    'file_name': file.filename,
                    'status': 'waiting',
                    'progress': None,
                    'upload_date': datetime.now().isoformat(),
                    'error': None
                })
            
            # Add descriptions to database
            descriptions = df['description'].tolist()
            add_descriptions_and_file_entries(descriptions, uploaded_file)
            
            # Start background processing
            threading.Thread(
                target=process_file_in_background,
                args=(uploaded_file, file_path, filename)
            ).start()

            uploaded_files.append({
                'id': uploaded_file,
                'filename': filename,
                'file_size': os.path.getsize(file_path),
                'upload_date': datetime.now().isoformat()
            })

        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500

    response = jsonify({'files': uploaded_files})
    return response, 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)
