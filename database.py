import os
import json
import uuid
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGO_DB", "quiz_db")
FALLBACK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db_fallback.json")

class FallbackCollection:
    def __init__(self, db_path, collection_name):
        self.db_path = db_path
        self.collection_name = collection_name
        
    def _load_data(self):
        if not os.path.exists(self.db_path):
            return []
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get(self.collection_name, [])
        except Exception:
            return []
            
    def _save_data(self, docs):
        data = {}
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception:
                pass
        data[self.collection_name] = docs
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, default=str)
        except Exception as e:
            print(f"Error saving fallback database: {e}")
            
    def _match(self, doc, query):
        if not query:
            return True
        for key, val in query.items():
            if key == '_id':
                # MongoDB query can be string or ObjectId or query dict like {'$in': [...]}
                doc_id = str(doc.get('_id', ''))
                if isinstance(val, dict):
                    if '$in' in val:
                        query_ids = [str(x) for x in val['$in']]
                        if doc_id not in query_ids:
                            return False
                        continue
                else:
                    if doc_id != str(val):
                        return False
                continue
            
            # Simple direct match
            if doc.get(key) != val:
                return False
        return True

    def find(self, query=None, sort=None):
        docs = self._load_data()
        query = query or {}
        matched = [doc for doc in docs if self._match(doc, query)]
        if sort:
            # Sort format: list of (field, direction), e.g. [('score', -1)]
            for field, direction in reversed(sort):
                matched.sort(key=lambda x: x.get(field) or 0, reverse=(direction == -1))
        return matched

    def find_one(self, query=None):
        docs = self.find(query)
        return docs[0] if docs else None

    def insert_one(self, doc):
        docs = self._load_data()
        if '_id' not in doc:
            doc['_id'] = str(uuid.uuid4())
        # Make a copy to avoid mutating original dictionary
        new_doc = dict(doc)
        new_doc['_id'] = str(new_doc['_id'])
        docs.append(new_doc)
        self._save_data(docs)
        
        class InsertResult:
            def __init__(self, inserted_id):
                self.inserted_id = inserted_id
        return InsertResult(new_doc['_id'])

    def update_one(self, query, update_data):
        docs = self._load_data()
        updated = False
        for doc in docs:
            if self._match(doc, query):
                # Apply $set
                if '$set' in update_data:
                    for k, v in update_data['$set'].items():
                        doc[k] = v
                # Apply $push
                if '$push' in update_data:
                    for k, v in update_data['$push'].items():
                        if k not in doc:
                            doc[k] = []
                        doc[k].append(v)
                updated = True
                break
        if updated:
            self._save_data(docs)
            
        class UpdateResult:
            def __init__(self, matched, modified):
                self.matched_count = matched
                self.modified_count = modified
        return UpdateResult(1 if updated else 0, 1 if updated else 0)

    def delete_one(self, query):
        docs = self._load_data()
        deleted = False
        new_docs = []
        for doc in docs:
            if not deleted and self._match(doc, query):
                deleted = True
            else:
                new_docs.append(doc)
        if deleted:
            self._save_data(new_docs)
            
        class DeleteResult:
            def __init__(self, count):
                self.deleted_count = count
        return DeleteResult(1 if deleted else 0)

    def count_documents(self, query):
        return len(self.find(query))

class FallbackDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.collections = {}

    def __getattr__(self, name):
        if name not in self.collections:
            self.collections[name] = FallbackCollection(self.db_path, name)
        return self.collections[name]
        
    def __getitem__(self, name):
        return getattr(self, name)

# Attempt to initialize MongoDB client
db = None
is_fallback = False

try:
    # Set a short timeout (2 seconds) so it doesn't hang if Mongo isn't running
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    # Trigger connection check
    client.server_info()
    db = client[DB_NAME]
    is_fallback = False
    print("Database: Connected successfully to MongoDB server.")
except (ConnectionFailure, ServerSelectionTimeoutError) as e:
    print(f"Database Warning: Could not connect to MongoDB server. Falling back to local JSON database. Error: {e}")
    db = FallbackDatabase(FALLBACK_FILE)
    is_fallback = True

def get_db():
    return db

def get_db_status():
    return {
        "is_fallback": is_fallback,
        "type": "JSON Fallback File" if is_fallback else "MongoDB Server",
        "path_or_uri": FALLBACK_FILE if is_fallback else MONGO_URI
    }
