import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Create the database directory if it doesn't exist
os.makedirs('data/db', exist_ok=True)

# Create the database engine
engine = create_engine('sqlite:///data/db/descriptions_demo.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Description(Base):
    __tablename__ = 'descriptions'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    description = Column(Text, nullable=False)
    is_processed = Column(Boolean, default=False)
    processed_id = Column(Integer, ForeignKey('processed_descriptions.id'), nullable=True)

    entries = relationship("FileEntry", back_populates="description")
    processed_description = relationship("ProcessedDescription", back_populates="description")

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'is_processed': self.is_processed,
            'processed_id': self.processed_id
        }

class FileEntry(Base):
    __tablename__ = 'file_entry'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    file_id = Column(Integer, ForeignKey('uploaded_files.id'), nullable=False)
    desc_id = Column(Integer, ForeignKey('descriptions.id'), nullable=False)

    uploaded_file = relationship("UploadedFile", back_populates="entries")
    description = relationship("Description", back_populates="entries")

class UploadedFile(Base):
    """Model for tracking uploaded files."""
    __tablename__ = 'uploaded_files'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    fname = Column(String(150), nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_date = Column(DateTime, default=datetime.now)
    num_processed = Column(Integer, default=0)
    total_descs = Column(Integer, default=0)
    pass_count = Column(Integer, default=0)
    processing_status = Column(String(20), default='waiting')  # waiting, processing, completed, error
    error_message = Column(Text, nullable=True)

    entries = relationship("FileEntry", back_populates="uploaded_file")
    
    def to_dict(self):
        return {
            'id': self.id,
            'fname': self.fname,
            'file_size': self.file_size,
            'upload_date': self.upload_date.isoformat(),
            'num_processed': self.num_processed,
            'total_descs': self.total_descs,
            'pass_count': self.pass_count,
            'fail_count': self.total_descs - self.pass_count,
            'pass_rate': (self.pass_count / self.total_descs) * 100 if self.total_descs > 0 else 0,
            'processing_status': self.processing_status,
            'error_message': self.error_message
        }

class ProcessedDescription(Base):
    __tablename__ = 'processed_descriptions'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    description_id = Column(Integer, ForeignKey('descriptions.id'), nullable=False)
    decision = Column(String(4), nullable=False)  # 'PASS' or 'FAIL'
    reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    description = relationship("Description", back_populates="processed_description")

    def to_dict(self):
        return {
            'id': self.id,
            'description_id': self.description_id,
            'decision': self.decision,
            'reasoning': self.reasoning,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(engine)
    print("Database initialized successfully")

def drop_db():
    """Drop the database by deleting all tables."""
    Base.metadata.drop_all(engine)
    print("Database dropped successfully")

# DESCRIPTION FUNCTIONS
def add_description(description_text, file_id=None, is_processed=False):
    session = Session()
    try:
        # Check if description already exists
        existing_desc = session.query(Description).filter_by(description=description_text).first()
        if existing_desc:
            return existing_desc.id
            
        desc = Description(
            description=description_text,
            is_processed=is_processed
        )
        session.add(desc)
        session.flush()  # Get ID before committing
        
        if file_id:
            file_entry = FileEntry(
                file_id=file_id,
                desc_id=desc.id
            )
            session.add(file_entry)
            
        session.commit()
        return desc.id
    except Exception as e:
        session.rollback()
        print(f"Error adding description: {e}")
        return None
    finally:
        session.close()


def add_descriptions_and_file_entries(descriptions, file_id):
    """Allow adding descriptions and file entries in batch.
    Args:
        descriptions (list of str): List of description texts to add.
        file_id (int): ID of the file entry to associate with the descriptions.

    Cache check: see if any of the descriptions are already in the database.
    If so, use the existing description ID for the given file entry.
    """
    session = Session()
    try:
        # First create all descriptions
        description_records = []
        for desc_text in descriptions:
            # Check if description already exists
            existing_desc = session.query(Description).filter_by(description=desc_text).first()
            if existing_desc:
                description_records.append(existing_desc)
            else:
                new_desc = Description(description=desc_text)
                session.add(new_desc)
                session.flush()  # Get the ID before committing
                description_records.append(new_desc)
        
        # Now create file entries with the description IDs
        for desc in description_records:
            file_entry = FileEntry(
                file_id=file_id,
                desc_id=desc.id
            )
            session.add(file_entry)
        
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error adding description and file entries: {e}")
        return False
    finally:
        session.close()

def add_processed_description(description_id, decision, reasoning):
    session = Session()
    try:
        processed_desc = ProcessedDescription(
            description_id=description_id,
            decision=decision.upper(),
            reasoning=reasoning
        )
        session.add(processed_desc)
        session.commit()
        return processed_desc.id
    except Exception as e:
        session.rollback()
        print(f"Error adding processed description: {e}")
        return None
    finally:
        session.close()


def get_description_id(description_text, file_entry_id=None):
    session = Session()
    try:
        desc = session.query(Description).filter_by(
            description=description_text,
            file_entry_id=file_entry_id
        ).first()
        return desc.id if desc else None
    except Exception as e:
        print(f"Error getting description ID: {e}")
        return None
    finally:
        session.close()


def get_description_by_id(description_id):
    session = Session()
    try:
        desc = session.query(Description).filter_by(id=description_id).first()
        return desc.to_dict() if desc else None
    except Exception as e:
        print(f"Error getting descriptions by ID: {e}")
        return None
    finally:
        session.close()


def check_for_processed(description_text):
    session = Session()
    try:
        desc = session.query(Description).filter_by(description=description_text, is_processed=True).first()
        return (True, desc.id) if desc else (False, None)
    except Exception as e:
        print(f"Error checking for processed description: {e}")
        return False, None
    finally:
        session.close()


def update_description_processing(description_id, processed_id):
    session = Session()
    try:
        desc = session.query(Description).filter_by(id=description_id).first()
        if desc:
            desc.is_processed = True
            desc.processed_id = processed_id
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        print(f"Error updating description: {e}")
        return False
    finally:
        session.close()


def get_unprocessed_descriptions(limit=100):
    session = Session()
    try:
        descs = session.query(Description).filter_by(is_processed=False).limit(limit).all()
        return [desc.to_dict() for desc in descs]
    except Exception as e:
        print(f"Error getting unprocessed descriptions: {e}")
        return []
    finally:
        session.close()

def get_processed_description(description_id):
    session = Session()
    try:
        processed_desc = session.query(ProcessedDescription).filter_by(description_id=description_id).first()
        return processed_desc.to_dict() if processed_desc else None
    except Exception as e:
        print(f"Error getting processed description: {e}")
        return None
    finally:
        session.close()

# FILE FUNCTIONS
def add_file_entries_batch(file_entries_data, uploaded_file_id):
    """
    Add multiple FileEntry records and optional Description records in batch.
    
    Args:
        file_entries_data (list of dict): Each dict should have:
            - 'text': (str) the raw file entry text (required)
            - 'descriptions': (list of str) optional list of descriptions associated with the entry
        uploaded_file_id (int): ID of the UploadedFile these entries belong to.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    session = Session()
    try:
        for entry_data in file_entries_data:
            entry_text = entry_data.get("text")
            descriptions = entry_data.get("descriptions", [])

            file_entry = FileEntry(
                file_id=uploaded_file_id,
                desc_id=None  # Assuming you'll handle the desc_id after creation if necessary
            )
            session.add(file_entry)
            session.flush()  # Assigns ID to file_entry without committing yet

            for desc_text in descriptions:
                description = Description(
                    desc_id=file_entry.id,
                    description=desc_text
                )
                session.add(description)

        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error adding file entries batch: {e}")
        return False
    finally:
        session.close()

def add_uploaded_file(fname, file_size):
    session = Session()
    try:
        file_record = UploadedFile(fname=fname, file_size=file_size)
        session.add(file_record)
        session.commit()
        return file_record.id
    except Exception as e:
        session.rollback()
        print(f"Error adding file record: {e}")
        return None
    finally:
        session.close()


def get_uploaded_file(fname):
    session = Session()
    try:
        return session.query(UploadedFile).filter_by(fname=fname).first()
    except Exception as e:
        print(f"Error getting file record: {e}")
        return None
    finally:
        session.close()


def update_file_statistics(uploaded_file_id, num_processed, pass_count):
    session = Session()
    try:
        file = session.query(UploadedFile).filter_by(id=uploaded_file_id).first()
        if file:
            file.num_processed = num_processed
            file.pass_count = pass_count
            file.total_descs = num_processed + pass_count
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        print(f"Error updating file statistics: {e}")
        return False
    finally:
        session.close()


def update_file_processing_status(uploaded_file_id, status, error_message=None):
    session = Session()
    try:
        file = session.query(UploadedFile).filter_by(id=uploaded_file_id).first()
        if file:
            file.processing_status = status
            file.error_message = error_message
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        print(f"Error updating file processing status: {e}")
        return False
    finally:
        session.close()


def get_recent_files(limit: int = 20):
    """Get recent uploaded files with their statistics."""
    session = Session()
    try:
        # Get files with their statistics
        files = session.query(UploadedFile).order_by(UploadedFile.upload_date.desc()).limit(limit).all()
        
        # Calculate statistics for each file
        file_stats = []
        for file in files:
            total_descs = session.query(FileEntry).filter_by(file_id=file.id).count()
            processed_descs = session.query(FileEntry).join(Description).filter(
                FileEntry.file_id == file.id,
                Description.is_processed == True
            ).count()
            
            pass_count = session.query(FileEntry).join(Description).filter(
                FileEntry.file_id == file.id,
                Description.is_processed == True,
                Description.processed_id.isnot(None)
            ).count()
            
            fail_count = processed_descs - pass_count
            pass_rate = (pass_count / processed_descs * 100) if processed_descs > 0 else 0
            
            # Calculate progress percentage
            progress = (processed_descs / total_descs * 100) if total_descs > 0 else 0
            
            file_stats.append({
                'id': file.id,
                'filename': file.fname,
                'count': total_descs,
                'processed': processed_descs,
                'pass_count': pass_count,
                'fail_count': fail_count,
                'pass_rate': pass_rate,
                'status': file.processing_status,
                'progress': progress,
                'timestamp': file.upload_date.isoformat(),
                'error': file.error_message
            })
        
        return file_stats
        
    except Exception as e:
        print(f"Error getting recent files: {e}")
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

# FILE ENTRY AND DESCRIPTION RETRIEVAL FUNCTION

def get_descriptions_by_file(file_id):
    session = Session()
    try:
        uploaded_file = session.query(UploadedFile).filter_by(id=file_id).first()
        if not uploaded_file:
            return {"file": None, "descriptions": []}

        file_entries = session.query(FileEntry).filter_by(file_id=file_id).all()
        descriptions = []
        for entry in file_entries:
            descriptions.extend(entry.description)

        return {
            "file": uploaded_file.to_dict(),
            "descriptions": [desc.to_dict() for desc in descriptions]
        }
    except Exception as e:
        print(f"Error getting descriptions by file: {e}")
        return {"file": None, "descriptions": []}
    finally:
        session.close()


def load_existing_files_to_queue():
    """Load all non-processed files from the database into the processing queue.
    
    Returns:
        list: List of queue items that were added
    """
    session = Session()
    try:
        # Get all files that haven't been fully processed
        files = session.query(UploadedFile).filter(
            UploadedFile.num_processed < UploadedFile.total_descs
        ).all()

        queue_items = []
        for file in files:
            queue_items.append({
                'id': file.id,
                'file_name': file.fname,
                'status': file.processing_status,
                'progress': None,
                'upload_date': file.upload_date.isoformat(),
                'error': file.error_message
            })
        
        return queue_items
    except Exception as e:
        print(f"Error loading existing files to queue: {e}")
        return []
    finally:
        session.close()

def get_or_create_uploaded_file(file_id):
    """Get or create an uploaded file entry.
    
    Args:
        file_id (int): ID of the uploaded file
        
    Returns:
        UploadedFile: The file entry object
    """
    session = Session()
    try:
        uploaded_file = session.query(UploadedFile).filter_by(id=file_id).first()
        if not uploaded_file:
            raise ValueError(f"File with ID {file_id} not found")
        return uploaded_file
    except Exception as e:
        print(f"Error getting uploaded file: {e}")
        raise
    finally:
        session.close()


def get_file_descriptions_with_results(file_id):
    """Get all descriptions and their results for a specific file.
    
    Args:
        file_id (int): ID of the uploaded file
        
    Returns:
        list: List of tuples containing (FileEntry, Description, ProcessedDescription)
    """
    session = Session()
    try:
        descriptions = session.query(FileEntry, Description, ProcessedDescription) \
            .join(Description, FileEntry.desc_id == Description.id) \
            .join(ProcessedDescription, Description.processed_id == ProcessedDescription.id) \
            .filter(FileEntry.file_id == file_id) \
            .all()
        return descriptions
    except Exception as e:
        print(f"Error getting file descriptions: {e}")
        raise
    finally:
        session.close()

init_db()