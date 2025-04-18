# Data Description Quality Tool

A tool that uses an LLM to rank the quality of data descriptions, outputting "pass" or "fail" and the reasoning behind its decision.

## Features

- Next.js frontend with an upload screen for CSV files
- Flask backend that processes descriptions using LangChain
- References data quality review guidelines
- Displays results in a tabular format showing description, pass/fail status, and reasoning

## Project Structure

- `/frontend` - Next.js frontend application
- `/backend` - Flask backend application
  - `/backend/data` - Directory for storing data quality guidelines and uploaded files

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the Flask server:
   ```
   python app.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Run the development server:
   ```
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.
