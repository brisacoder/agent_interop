import requests
import uuid

# Base URL - replace with your actual server address
BASE_URL = "http://localhost:8123"  # Adjust as needed

def test_get_latest_thread_state(thread_id: str):
    """Test retrieving the latest state of a thread"""
    print(f"=== Testing Get Latest Thread State for Thread ID: {thread_id} ===")
    thread_id = uuid.UUID(thread_id)
    response = requests.get(f"{BASE_URL}/threads/{thread_id}/state")

    if response.status_code == 200:
        thread_state = response.json()
        print(f"✅ Successfully retrieved thread state for ID: {thread_id}")
        print(f"  State: {thread_state}")
    elif response.status_code == 422:
        print(f"❌ Failed to retrieve thread state: Invalid Thread ID (422)")
    else:
        print(f"❌ Failed to retrieve thread state: {response.status_code} - {response.text}")

if __name__ == "__main__":
    # Replace with an existing thread ID or test after creating one
    
    test_thread_id: str = input("\nTo fetch latest State of a given Thread, enter it's ThreadID: ")
    test_get_latest_thread_state(test_thread_id)