# Fix the load_dataframe function in analysis.py

import re

# Read the file
with open('app/routes/analysis.py', 'r') as f:
    content = f.read()

# Find and replace the load_dataframe function
load_dataframe_pattern = r'async def load_dataframe\(dataset_id: str\) -> pd\.DataFrame:.*?(?=async def|\Z)'

new_load_dataframe = '''async def load_dataframe(dataset_id: str) -> pd.DataFrame:
    """Helper function to load DataFrame from dataset - ADAPTER VERSION"""
    import logging
    logger = logging.getLogger(__name__)
    
    db_adapter = get_db()
    dataset = await db_adapter.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(404, "Dataset not found")
    
    logger.info(f"Loading dataset {dataset_id}, storage_type: {dataset.get('storage_type', 'direct')}")
    
    # Load data based on storage type
    if dataset.get("storage_type") == "gridfs":
        gridfs_file_id = dataset.get("gridfs_file_id")
        if gridfs_file_id:
            try:
                data = await db_adapter.retrieve_file(gridfs_file_id)
                logger.info(f"GridFS data loaded, size: {len(data)} bytes")
                
                # Parse JSON data
                import json
                data_dict = json.loads(data.decode('utf-8'))
                df = pd.DataFrame(data_dict)
                
                logger.info(f"DataFrame created: {df.shape}")
                return df
                
            except Exception as e:
                logger.error(f"Error loading GridFS data: {str(e)}")
                raise HTTPException(500, f"Error loading dataset from GridFS: {str(e)}")
        else:
            raise HTTPException(500, "GridFS file ID not found")
    else:
        # Load from inline data
        data = dataset.get("data", [])
        if not data:
            raise HTTPException(500, "No data found in dataset")
        
        df = pd.DataFrame(data)
        logger.info(f"DataFrame loaded from inline data: {df.shape}")
        return df


'''

# Replace the function
content = re.sub(load_dataframe_pattern, new_load_dataframe, content, flags=re.DOTALL)

# Write back
with open('app/routes/analysis.py', 'w') as f:
    f.write(content)

print("Fixed load_dataframe function in analysis.py")
