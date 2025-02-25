import requests
import json
import uuid
from datetime import datetime

# Base URL - replace with your actual server address
BASE_URL = "http://localhost:8123"  # Adjust as needed

def test_create_thread():
    """Test thread creation functionality"""
    print("=== Testing Thread Creation ===")
    
    # Case 1: Create a thread with auto-generated ID
    response = requests.post(
        f"{BASE_URL}/threads",
        json={
            "metadata": {"source": "test_script", "purpose": "testing"}
        }
    )
    if response.status_code == 200:
        thread1 = response.json()
        thread_id = thread1["thread_id"]
        print(f"✅ Successfully created thread with auto-generated ID: {thread_id}")
        print(f"  Created at: {thread1['created_at']}")
        print(f"  Status: {thread1['status']}")
    else:
        print(f"❌ Failed to create thread: {response.status_code} - {response.text}")
        return

    # Case 2: Create a thread with custom ID
    custom_id = str(uuid.uuid4())
    response = requests.post(
        f"{BASE_URL}/threads",
        json={
            "thread_id": custom_id,
            "metadata": {"source": "test_script", "purpose": "custom_id_test"}
        }
    )
    if response.status_code == 200:
        thread2 = response.json()
        print(f"✅ Successfully created thread with custom ID: {thread2['thread_id']}")
        assert thread2["thread_id"] == custom_id, "Custom ID doesn't match"
    else:
        print(f"❌ Failed to create thread with custom ID: {response.status_code} - {response.text}")

    # Case 3: Test duplicate handling with if_exists=raise
    response = requests.post(
        f"{BASE_URL}/threads",
        json={
            "thread_id": custom_id,
            "metadata": {"source": "test_script", "purpose": "duplicate_test"},
            "if_exists": "raise"
        }
    )
    if response.status_code == 409:
        print("✅ Correctly received 409 error for duplicate ID with if_exists=raise")
    else:
        print(f"❌ Expected 409 for duplicate with if_exists=raise, got: {response.status_code} - {response.text}")

    # Case 4: Test duplicate handling with if_exists=do_nothing
    response = requests.post(
        f"{BASE_URL}/threads",
        json={
            "thread_id": custom_id,
            "metadata": {"source": "test_script", "purpose": "do_nothing_test"},
            "if_exists": "do_nothing"
        }
    )
    if response.status_code == 200:
        thread3 = response.json()
        print("✅ Successfully handled duplicate with if_exists=do_nothing")
        # Verify it returned the existing thread without modifications
        assert thread3["metadata"]["purpose"] == "custom_id_test", "Metadata was modified when it shouldn't be"
    else:
        print(f"❌ Failed with if_exists=do_nothing: {response.status_code} - {response.text}")
        
    print("\n=== Test Summary ===")
    print("Thread creation tests completed. Check the results above.")


if __name__ == "__main__":
    test_create_thread()