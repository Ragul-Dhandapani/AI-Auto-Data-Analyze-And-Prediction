# This script will help replace MongoDB calls with adapter calls
import re

# Read the file
with open('app/routes/datasource.py', 'r') as f:
    content = f.read()

# Replace patterns
replacements = [
    # Basic dataset operations
    (r'await db\.datasets\.find_one\(\{"id": ([^}]+)\}\)', r'db_adapter = get_db(); dataset = await db_adapter.get_dataset(\1); dataset'),
    (r'await db\.datasets\.find_one\(\{"name": ([^}]+)\}\)', r'db_adapter = get_db(); existing = await db_adapter.db.datasets.find_one({"name": \1}) if hasattr(db_adapter, "db") else None; existing'),
    (r'await db\.datasets\.insert_one\(([^)]+)\)', r'db_adapter = get_db(); await db_adapter.create_dataset(\1)'),
    (r'await db\.datasets\.delete_one\(\{"id": ([^}]+)\}\)', r'db_adapter = get_db(); await db_adapter.delete_dataset(\1)'),
    (r'await db\.datasets\.update_one\(\{"id": ([^}]+)\}, \{"\\$set": ([^}]+)\}\)', r'db_adapter = get_db(); await db_adapter.update_dataset(\1, \2)'),
    
    # GridFS operations
    (r'await fs\.upload_from_stream\(([^,]+), ([^,]+), metadata=([^)]+)\)', r'db_adapter = get_db(); file_id = await db_adapter.store_file(\1, \2, \3); file_id'),
    (r'await fs\.upload_from_stream\(([^,]+), ([^)]+)\)', r'db_adapter = get_db(); file_id = await db_adapter.store_file(\1, \2, {}); file_id'),
    (r'await fs\.open_download_stream\(ObjectId\(([^)]+)\)\)', r'db_adapter = get_db(); data = await db_adapter.retrieve_file(\1); io.BytesIO(data)'),
    (r'await fs\.delete\(ObjectId\(([^)]+)\)\)', r'db_adapter = get_db(); await db_adapter.delete_file(\1)'),
    
    # Collection operations that need MongoDB adapter access
    (r'await db\.saved_states\.delete_many\(\{"dataset_id": ([^}]+)\}\)', r'db_adapter = get_db(); await db_adapter.db.saved_states.delete_many({"dataset_id": \1}) if hasattr(db_adapter, "db") else None'),
    (r'await db\.command\(\'ping\'\)', r'db_adapter = get_db(); await db_adapter.db.command("ping") if hasattr(db_adapter, "db") else {"ok": 1}'),
    (r'await db\.list_collection_names\(\)', r'db_adapter = get_db(); collections = await db_adapter.db.list_collection_names() if hasattr(db_adapter, "db") else []; collections'),
]

# Apply replacements
for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

# Write back
with open('app/routes/datasource.py', 'w') as f:
    f.write(content)

print("Replacements applied to datasource.py")
