import pickle

def save_to_pickle(database, filename='threads_db.pkl'):
    with open(filename, 'wb') as f:
        pickle.dump(database, f)
    print(f"Data saved to {filename}")

def load_from_pickle(filename='threads_db.pkl'):
    try:
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        print(f"Data loaded from {filename}")
        return data
    except FileNotFoundError:
        print(f"{filename} not found. Returning an empty dictionary.")
        return {}
    except pickle.UnpicklingError:
        print(f"Error while unpickling {filename}. Returning an empty dictionary.")
        return {}
