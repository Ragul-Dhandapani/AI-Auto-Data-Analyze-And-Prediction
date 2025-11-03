# Helper to update analysis.py with adapter pattern

import re

# Read the file
with open('app/routes/analysis.py', 'r') as f:
    content = f.read()

# Key replacements for analysis.py
replacements = [
    # Dataset loading
    (r'dataset = await db\.datasets\.find_one\(\{"id": ([^}]+)\}[^)]*\)', r'db_adapter = get_db(); dataset = await db_adapter.get_dataset(\1)'),
    
    # Update operations
    (r'await db\.datasets\.update_one\(\{"id": ([^}]+)\}, \{"\\$inc": \{"training_count": 1\}\}\)', r'db_adapter = get_db(); await db_adapter.increment_training_count(\1)'),
    (r'await db\.datasets\.update_one\(\{"id": ([^}]+)\}, \{"\\$set": ([^}]+)\}\)', r'db_adapter = get_db(); await db_adapter.update_dataset(\1, \2)'),
    
    # GridFS operations
    (r'grid_out = await fs\.open_download_stream\(ObjectId\(([^)]+)\)\)', r'db_adapter = get_db(); data = await db_adapter.retrieve_file(\1)'),
    (r'data = await grid_out\.read\(\)', r'# data already loaded from adapter'),
    (r'file_id = await fs\.upload_from_stream\(([^,]+), ([^,]+), metadata=([^)]+)\)', r'db_adapter = get_db(); file_id = await db_adapter.store_file(\1, \2, \3)'),
    (r'await fs\.delete\(ObjectId\(([^)]+)\)\)', r'db_adapter = get_db(); await db_adapter.delete_file(\1)'),
    
    # Workspace operations
    (r'await db\.saved_states\.insert_one\(([^)]+)\)', r'db_adapter = get_db(); await db_adapter.save_workspace(\1)'),
    (r'state = await db\.saved_states\.find_one\(\{"id": ([^}]+)\}[^)]*\)', r'db_adapter = get_db(); state = await db_adapter.get_workspace(\1)'),
    (r'cursor = db\.saved_states\.find\(\{"dataset_id": ([^}]+)\}[^)]*\)', r'db_adapter = get_db(); states = await db_adapter.list_workspaces(\1); cursor = states'),
    (r'states = await cursor\.to_list\([^)]+\)', r'states = cursor  # already a list from adapter'),
    (r'result = await db\.saved_states\.delete_one\(\{"id": ([^}]+)\}\)', r'db_adapter = get_db(); success = await db_adapter.delete_workspace(\1); result = type("Result", (), {"deleted_count": 1 if success else 0})()'),
    
    # Dataset creation
    (r'await db\.datasets\.insert_one\(([^)]+)\)', r'db_adapter = get_db(); await db_adapter.create_dataset(\1)'),
]

# Apply replacements
for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

# Write back
with open('app/routes/analysis.py', 'w') as f:
    f.write(content)

print("Applied adapter pattern replacements to analysis.py")
