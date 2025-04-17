import os
import sqlite3
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create the database directory if it doesn't exist
os.makedirs('data/db', exist_ok=True)

# Create the database engine
engine = create_engine('sqlite:///data/db/descriptions.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Description(Base):
    """Model for storing data descriptions and their evaluations."""
    __tablename__ = 'descriptions'
    
    id = Column(Integer, primary_key=True)
    description = Column(Text, nullable=False)
    file_id = Column(Integer, nullable=True)
    decision = Column(String(10), nullable=True)
    reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    processed = Column(Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'file_id': self.file_id,
            'decision': self.decision,
            'reasoning': self.reasoning,
            'created_at': self.created_at.isoformat(),
            'processed': self.processed
        }

class UploadedFile(Base):
    """Model for tracking uploaded files."""
    __tablename__ = 'uploaded_files'
    
    id = Column(Integer, primary_key=True)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_date = Column(DateTime, default=datetime.now)
    description_count = Column(Integer, default=0)
    pass_count = Column(Integer, default=0)
    fail_count = Column(Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'upload_date': self.upload_date.isoformat(),
            'description_count': self.description_count,
            'pass_count': self.pass_count,
            'fail_count': self.fail_count,
            'pass_rate': (self.pass_count / self.description_count) * 100 if self.description_count > 0 else 0
        }

def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(engine)
    print("Database initialized successfully")

def drop_db():
    """Drop the database by deleting all tables."""
    Base.metadata.drop_all(engine)
    print("Database dropped successfully")

def add_description(description, file_id=None, decision=None, reasoning=None, processed=False):
    session = Session()
    try:
        description = Description(
            description=description,
            file_id=file_id,
            decision=decision,
            reasoning=reasoning,
            processed=processed
        )
        session.add(description)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error adding description: {e}")
        return False
    finally:
        session.close()

def add_descriptions(descriptions, file_id=None):
    """Add multiple descriptions to the database."""
    session = Session()
    try:
        for desc in descriptions:
            description = Description(
                description=desc,
                file_id=file_id
            )
            session.add(description)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error adding descriptions: {e}")
        return False
    finally:
        session.close()

# Returns description ID of first exact text match
def get_description_id(description, file_id=None):
    session = Session()
    try:
        description = session.query(Description).filter_by(description=description, file_id=file_id).first()
        if description:
            return description.id
        return None
    except Exception as e:
        print(f"Error getting description ID: {e}")
        return None
    finally:
        session.close()

def get_description_by_id(description_id):
    session = Session()
    try:
        description = session.query(Description).filter_by(id=description_id).first()
        if description:
            return description.to_dict()
        return None
    except Exception as e:
        print(f"Error getting descriptions by ID: {e}")
        return None
    finally:
        session.close()

def check_for_processed(description):
    # check if a processed description exists
    session = Session()
    try:
        description = session.query(Description).filter_by(description=description, processed=True).first()
        if description:
            return True, description.id
        return False, None
    except Exception as e:
        print(f"Error checking for processed description: {e}")
        return False, None
    finally:
        session.close()

def update_description_evaluation(description_id, decision, reasoning):
    """Update a description with evaluation results."""
    session = Session()
    try:
        description = session.query(Description).filter_by(id=description_id).first()
        if description:
            description.decision = decision
            description.reasoning = reasoning
            description.processed = True
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        print(f"Error updating description: {e}")
        return False
    finally:
        session.close()

def add_uploaded_file(file_name, file_size):
    """Add a record of an uploaded file."""
    session = Session()
    try:
        file_record = UploadedFile(
            file_name=file_name,
            file_size=file_size
        )
        session.add(file_record)
        session.commit()
        return file_record.id
    except Exception as e:
        session.rollback()
        print(f"Error adding file record: {e}")
        return None
    finally:
        session.close()

def get_uploaded_file(file_name):
    """Get a file record by name."""
    session = Session()
    try:
        file_record = session.query(UploadedFile).filter_by(file_name=file_name).first()
        if file_record:
            return file_record
        return None
    except Exception as e:
        print(f"Error getting file record: {e}")
        return None
    finally:
        session.close()

def update_file_statistics(file_id, description_count, pass_count, fail_count):
    """Update statistics for a processed file."""
    session = Session()
    try:
        file_record = session.query(UploadedFile).filter_by(id=file_id).first()
        if file_record:
            file_record.description_count = description_count
            file_record.pass_count = pass_count
            file_record.fail_count = fail_count
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        print(f"Error updating file statistics: {e}")
        return False
    finally:
        session.close()

def get_recent_files(limit=5):
    """Get a list of recently uploaded files."""
    session = Session()
    try:
        files = session.query(UploadedFile).order_by(UploadedFile.upload_date.desc()).limit(limit).all()
        return [file.to_dict() for file in files]
    except Exception as e:
        print(f"Error getting recent files: {e}")
        return []
    finally:
        session.close()

def get_descriptions_by_file(file_id):
    """Get all descriptions from a specific file."""
    session = Session()
    try:
        file = session.query(UploadedFile).filter_by(id=file_id).first()
        if not file:
            return []
        
        descriptions = session.query(Description).filter_by(file_id=file.id).all()
        return [desc.to_dict() for desc in descriptions]
    except Exception as e:
        print(f"Error getting descriptions by file: {e}")
        return []
    finally:
        session.close()

def get_unprocessed_descriptions(limit=100):
    """Get descriptions that haven't been processed yet."""
    session = Session()
    try:
        descriptions = session.query(Description).filter_by(processed=False).limit(limit).all()
        return [desc.to_dict() for desc in descriptions]
    except Exception as e:
        print(f"Error getting unprocessed descriptions: {e}")
        return []
    finally:
        session.close()

def remove_file(file_id):
    session = Session()
    try:
        file = session.query(UploadedFile).filter_by(id=file_id).first()
        if not file:
            return False
        session.delete(file)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error removing file: {e}")
        return False
    finally:
        session.close()

# Initialize the database when this module is imported
init_db()
