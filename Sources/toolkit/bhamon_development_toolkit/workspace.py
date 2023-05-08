import json
import os


def load_results(result_file_path):
    results = {}

    if os.path.isfile(result_file_path):
        with open(result_file_path, "r") as result_file:
            results = json.load(result_file)

    return results


def save_results(result_file_path, results):
    if os.path.dirname(result_file_path):
        os.makedirs(os.path.dirname(result_file_path), exist_ok = True)
    with open(result_file_path + ".tmp", "w") as result_file:
        json.dump(results, result_file, indent = 4)
    if os.path.isfile(result_file_path):
        os.remove(result_file_path)
    os.replace(result_file_path + ".tmp", result_file_path)
