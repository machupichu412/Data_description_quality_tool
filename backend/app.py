import os
import pandas as pd
import json
import logging
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
from database import add_descriptions, update_description_evaluation, \
    add_uploaded_file, update_file_statistics, get_recent_files, \
    get_descriptions_by_file, get_description_id, get_description_by_id, \
    add_description, check_for_processed, get_uploaded_file
# For testing
# from dummy_llm import DummyLLM

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
    Evaluate the following description carefully. If it violates any of these principles, label it as **Fail** Otherwise, label it **Pass**
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

llm = OllamaLLM(model=os.getenv('MODEL'))  # TODO change model

@app.route('/api/evaluate', methods=['POST'])
def evaluate_descriptions():
    if 'files[]' not in request.files:
        return jsonify({"error": "No files part"}), 400
    
    files = request.files.getlist('files[]')
    
    if not files or files[0].filename == '':
        return jsonify({"error": "No selected files"}), 400
    
    results = []
    file_records = []
    
    for file in files:
        if not file.filename.endswith('.csv'):
            continue  # Skip non-CSV files
        
        try:
            # Generate a unique filename
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            unique_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            
            # Save the file
            file.save(file_path)
            
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
            # Check if file already exists
            file_exists = get_uploaded_file(file.filename)
            if file_exists:
                file_records.append({
                    "filename": file.filename,
                    "error": "File already exists in database"
                })
                continue
            file_id = add_uploaded_file(file.filename, os.path.getsize(file_path))
            
            # Add descriptions to database
            descriptions = df['description'].tolist()
            add_descriptions(descriptions, file_id)
    
            # Get LLM chain
            initial_chain = initial_prompt | llm | parser
            
            followup_chain = followup_prompt | llm | parser
            
            file_results = []
            pass_count = 0
            fail_count = 0

            # seen = set()

            # Process each description
            for idx, row in df.iterrows():
                description = row['description']

                # Uncomment if you want to skip duplicates
                # if description in seen:
                #     continue
                # seen.add(description)

                # Skip empty descriptions
                if pd.isna(description) or description.strip() == '':
                    result = {
                        "description": "",
                        "decision": "FAIL",
                        "reasoning": "Empty description"
                    }
                    fail_count += 1
                else:
                    # Check if description has already been evaluated
                    processed, description_id = check_for_processed(description) # will find an id if it has been evaluated
                    desc_data = get_description_by_id(description_id)
                    if processed:
                        result = {
                            "description": description,
                            "decision": desc_data['decision'],
                            "reasoning": desc_data['reasoning'],
                        }
                        if result['decision'] == "PASS":
                            pass_count += 1
                        else:
                            fail_count += 1
                        file_results.append(result)
                        add_description(description, file_id, result['decision'], result['reasoning'], True)
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
                    if ("pass" in initial_decision.lower()):
                        decision = "PASS"
                    elif ("fail" in initial_decision.lower()):
                        decision = "FAIL"
                    else:
                        decision = "FAIL"

                    # Log the LLM decision
                    logger.info("LLM Decision: %s", initial_decision)

                    # Run followup prompt
                    reasoning = followup_chain.invoke({
                        "decision": decision,
                        "description": description,
                    })

                    # Log the LLM reasoning
                    logger.info("LLM Reasoning: %s", reasoning)

                    # Add to database
                    description_id = get_description_id(description, file_id)
                    if not description_id:
                        add_description(description, file_id, decision, reasoning, True)
                    else:
                        update_description_evaluation(description_id, decision, reasoning)

                    result = {
                        "description": description,
                        "decision": decision,
                        "reasoning": reasoning
                    }
                    
                    if decision == "PASS":
                        pass_count += 1
                    else:
                        fail_count += 1
                
                file_results.append(result)
            
            # Update file statistics
            if file_id:
                update_file_statistics(file_id, len(file_results), pass_count, fail_count)
            
            # Add to overall results
            results.extend(file_results)
            
            file_records.append({
                "filename": file.filename,
                "id": file_id,
                "count": len(file_results),
                "pass_count": pass_count,
                "fail_count": fail_count,
                "pass_rate": (pass_count / len(file_results)) * 100 if len(file_results) > 0 else 0
            })
            
        except Exception as e:
            logger.error("Error processing file %s: %s", file.filename, str(e))
            file_records.append({
                "filename": file.filename,
                "error": str(e)
            })
            remove_file(file_id)
    
    if not results:
        return jsonify({"error": "No valid files were processed", "file_records": file_records}), 400
    
    return jsonify({
        "results": results,
        "file_records": file_records
    }), 200

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
    """Get all descriptions from a specific file."""
    descriptions = get_descriptions_by_file(file_id)
    return jsonify({"descriptions": descriptions}), 200

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)
