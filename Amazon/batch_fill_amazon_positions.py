#!/usr/bin/env python3
"""
Batch fill Amazon search position info into Feishu Bitable
"""

import sys
import os
import time
import subprocess

# Get all records from bitable via openclaw tool output
# We'll call the script for each (keyword, asin)

def process_one(keyword, asin, record_id, app_token, table_id, field_name):
    """Process one record: search and update position"""
    print(f"\n{'='*60}")
    print(f"Processing: keyword='{keyword}', ASIN={asin}, field={field_name}")
    print(f"{'='*60}\n")
    
    # Call the search script
    cmd = f"python3 /root/.openclaw/workspace/Amazon/amazon_search_asin_screenshot.py '{keyword}' {asin}"
    return_code = os.system(cmd)
    
    # Parse the output to get position
    # We need to capture output, but for now let's just run and get info manually
    print(f"\n>>> Finished processing {keyword} - {asin}, return code: {return_code}")
    time.sleep(15)  # Wait between searches to avoid blocking

if __name__ == "__main__":
    print("Batch processing started...")
    print("This script will be called from OpenClaw with each record")
