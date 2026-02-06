import os
import pickle

def save_data(data, filename=None):
    """Save data to filename"""
    if not filename:
        filename = "data.pkl"
    with open(filename, 'wb') as file:
        pickle.dump(data, file)
    print("CWD of mysave: ", os.getcwd())
