import os
import pandas as pd
import json
import logging
import re
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import tempfile
from datetime import datetime
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM

# Import custom modules
<<<<<<< HEAD
from database import add_description, add_processed_description, update_description_processing, get_processed_description, add_uploaded_file, update_file_statistics, get_recent_files, get_descriptions_by_file, get_uploaded_file, get_or_create_uploaded_file, update_file_processing_status, check_for_processed, get_description_by_id, add_file_entries_batch, get_file_descriptions_with_results
import threading
import re
=======
from database import add_descriptions_and_file_entries, update_description_evaluation, \
    add_uploaded_file, update_file_statistics, get_recent_files, \
    get_descriptions_by_file, get_description_id, get_description_by_id, \
    add_description, check_for_processed, get_uploaded_file, \
    get_file_descriptions_with_results, add_processed_description, \
    add_file_entries_batch, load_existing_files_to_queue, update_file_processing_status, remove_file,\
    get_uploaded_file_by_id
# For testing
# from dummy_llm import DummyLLM
>>>>>>> ad7d3da (UI refresh with new fonts, updated dummy_llm)

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Create upload directory if it doesn't exist
UPLOAD_FOLDER = os.path.join('data', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,  # or DEBUG, INFO, WARNING, ERROR, CRITICAL
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("server.log"),     # Log to server.log
        logging.StreamHandler()                # Log to console
    ]
)

logger = logging.getLogger(__name__)

# Create a prompt template for evaluating data descriptions
initial_prompt = PromptTemplate(
    input_variables=["description"],
    template="""You are a data quality evaluator. Your task is to classify data descriptions as 'Pass' or 'Fail' based on best practices for clarity, precision, and consistency.
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
    Evaluate the following description carefully. If it violates any of these principles, label it as 'Fail' Otherwise, label it 'Pass'.
    {description} 
    Output only 'Pass' or 'Fail' without any additional text.
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
    'Pass' means the description passes all the principles listed above.
    'Fail' means the description fails to meet any of the principles listed above.
    The following description has been classified as {decision}:
    {description}
    Justify the decision with a clear explanation.
    Output only the reasoning without any additional text.
    """
)

parser = StrOutputParser()

phi_llm = OllamaLLM(model=os.getenv('CLASSIFY_MODEL'), temperature=0.0)

deepseek_llm = OllamaLLM(model=os.getenv('REASON_MODEL'))
<<<<<<< HEAD

# Global processing queue and lock
processing_queue = []
queue_lock = threading.Lock()
=======
>>>>>>> ad7d3da (UI refresh with new fonts, updated dummy_llm)

@app.route('/api/evaluate', methods=['POST'])
def evaluate_descriptions():
    if 'files[]' not in request.files:
        return jsonify({"error": "No files provided"}), 400

    files = request.files.getlist('files[]')
    results = []
    file_records = []

    for file in files:
        try:
            # Save the file
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)
            
<<<<<<< HEAD
            # Add file record to database
            file_exists = get_uploaded_file(file.filename)
            if file_exists:
                file_records.append({
                    "filename": file.filename,
                    "error": "File already exists in database"
                })
                continue
            
            file_id = add_uploaded_file(file.filename, os.path.getsize(file_path))
            
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
                return jsonify({"error": "CSV file must contain a 'description' column"}), 400

            # Get LLM chains
            initial_chain = initial_prompt | phi_llm | parser
            followup_chain = followup_prompt | deepseek_llm | parser
=======
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Check if the CSV has a 'description' column
            if 'description' not in df.columns:
                file_records.append({
                    "filename": file.filename,
                    "error": "CSV file must contain a 'description' column"
                })
                continue

            # Add file record to database
            file_exists = get_uploaded_file(file.filename)
            # if file_exists:
            #     file_records.append({
            #         "filename": file.filename,
            #         "error": "File already exists in database"
            #     })
            #     continue

            file_id = add_uploaded_file(file.filename, os.path.getsize(file_path))
            
            # Add descriptions to database
            descriptions = df['description'].tolist()
>>>>>>> ad7d3da (UI refresh with new fonts, updated dummy_llm)
            
            # Get LLM chains
            initial_chain = initial_prompt | phi_llm | parser
            followup_chain = followup_prompt | deepseek_llm | parser

            file_results = []
            pass_count = 0
<<<<<<< HEAD
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
                
=======
            fail_count = 0
            total_count = len(descriptions)

            # Process each description
            for idx, description in enumerate(descriptions):
>>>>>>> ad7d3da (UI refresh with new fonts, updated dummy_llm)
                # Skip empty descriptions
                if pd.isna(description) or description.strip() == '':
                    result = {
                        "description": description,
                        "decision": "FAIL",
                        "reasoning": "Empty description"
                    }
<<<<<<< HEAD
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
=======
                    fail_count += 1
                    file_results.append(result)
                    continue

                # Check cache for existing processed description
                processed, description_id = check_for_processed(description)
                if processed:
                    desc_data = get_description_by_id(description_id)
                    processed_data = get_description_by_id(desc_data.processed_id)
                    result = {
                        "description": description,
                        "decision": "PASS" if processed_data.pass_ else "FAIL",
                        "reasoning": processed_data.reasoning
>>>>>>> ad7d3da (UI refresh with new fonts, updated dummy_llm)
                    }
                    if result['decision'] == "PASS":
                        pass_count += 1
<<<<<<< HEAD
=======
                    else:
                        fail_count += 1
                    file_results.append(result)
                    continue

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
                desc_id = add_description(description, file_id=file_id, processed_id=processed_desc_id, is_processed=True)
                if not desc_id:
                    raise Exception("Failed to add description")

                result = {
                    "description": description,
                    "decision": decision,
                    "reasoning": stripped_reasoning
                }
                
                if decision == "PASS":
                    pass_count += 1
                else:
                    fail_count += 1
>>>>>>> ad7d3da (UI refresh with new fonts, updated dummy_llm)
                
                file_results.append(result)

            # Update file statistics
<<<<<<< HEAD
            update_file_statistics(file_id, len(file_results), pass_count)
            
            # Update processing status to completed
            update_file_processing_status(file_id, "completed")
            
            file_records.append({
                "filename": file.filename,
                "total_descriptions": len(file_results),
                "pass_count": pass_count,
                "fail_count": len(file_results) - pass_count,
                "pass_rate": (pass_count / len(file_results)) * 100 if len(file_results) > 0 else 0,
                "results": file_results
            })
            
            results.extend(file_results)
            
=======
            update_file_statistics(file_id, total_count, pass_count)
            
            # Update processing status
            update_file_processing_status(file_id, "completed")

            file_records.append({
                "filename": file.filename,
                "id": file_id,
                "count": total_count,
                "pass_count": pass_count,
                "fail_count": fail_count,
                "pass_rate": (pass_count / total_count) * 100 if total_count > 0 else 0
            })
            
            results.extend(file_results)
            
>>>>>>> ad7d3da (UI refresh with new fonts, updated dummy_llm)
        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {str(e)}")
            file_records.append({
                "filename": file.filename,
                "error": f"Error processing file: {str(e)}"
            })
<<<<<<< HEAD
            # Update processing status to error
            update_file_processing_status(file_id, "error", str(e))
            continue

=======
            # Remove the file if it was created
            if file_id:
                remove_file(file_id)
            continue

    if not results:
        return jsonify({"error": "No valid files were processed", "file_records": file_records}), 400

>>>>>>> ad7d3da (UI refresh with new fonts, updated dummy_llm)
    return jsonify({
        "files": file_records,
        "total_results": len(results),
        "pass_count": sum(1 for r in results if r['decision'] == 'PASS'),
        "fail_count": sum(1 for r in results if r['decision'] == 'FAIL')
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/files', methods=['GET'])
def get_files():
    """Get a list of recently uploaded files."""
    files = get_recent_files(limit=20)
    return jsonify({"files": files}), 200

@app.route('/api/files/<int:file_id>/descriptions', methods=['GET'])
def get_file_descriptions(file_id):
<<<<<<< HEAD
    """Get all descriptions and their results from a specific file."""
    descriptions = get_file_descriptions_with_results(file_id)
    
    # Convert to list of dictionaries with expected format
    descriptions_list = []
    for desc, processed_desc in descriptions:
        descriptions_list.append({
            "description": desc.description,
            "decision": processed_desc.decision,
            "reasoning": processed_desc.reasoning
        })
    
    return jsonify({
        "file": {
            "id": file_id,
            "fname": desc.file_entry.uploaded_file.fname
        },
        "descriptions": descriptions_list
    }), 200
=======
    """Get all descriptions from a specific file."""
    try:
        result = get_descriptions_by_file(file_id)
        if not result or not result.get('file'):
            return jsonify({"error": "File not found or no descriptions available"}), 404
            
        return jsonify({
            "file": result["file"],
            "descriptions": result["descriptions"] or []
        }), 200
    except Exception as e:
        logger.error(f"Error getting file descriptions: {e}")
        return jsonify({"error": "Failed to fetch descriptions"}), 500
>>>>>>> ad7d3da (UI refresh with new fonts, updated dummy_llm)

@app.route('/api/download/<int:file_id>', methods=['GET'])
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

@app.route('/api/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Delete a file and its associated descriptions."""
    try:
        success = remove_file(file_id)
        if not success:
            return jsonify({"error": "File not found"}), 404
        return jsonify({"message": "File deleted successfully"}), 200
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        return jsonify({"error": "Failed to delete file"}), 500

@app.route('/api/files/<int:file_id>/download', methods=['GET'])
def download_file(file_id):
    """Download the original uploaded file."""
    try:
        file = get_uploaded_file_by_id(file_id)
        if not file:
            return jsonify({"error": "File not found"}), 404

        # Get the file path
        file_path = os.path.join(UPLOAD_FOLDER, file.fname)
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found on disk"}), 404

        return send_file(
            file_path,
            as_attachment=True,
            download_name=file.fname
        )
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return jsonify({"error": "Failed to download file"}), 500

@app.route('/api/files/<int:file_id>/descriptions/download', methods=['GET'])
def download_descriptions(file_id):
    """Download the processed descriptions for a file."""
    try:
        descriptions = get_descriptions_by_file(file_id)
        if not descriptions or not descriptions.get('descriptions'):
            return jsonify({"error": "No descriptions found"}), 404

        # Create a DataFrame with the descriptions
        df = pd.DataFrame(descriptions['descriptions'])
        
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        df.to_csv(temp_file.name, index=False)
        
        return send_file(
            temp_file.name,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'processed_descriptions_{file_id}.csv'
        )
    except Exception as e:
        logger.error(f"Error downloading descriptions: {e}")
        return jsonify({"error": "Failed to download descriptions"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)