import requests
import json
import pathlib

if __name__ == "__main__":
    path_to_example_dir = pathlib.Path.cwd().parent / "example_payloads"
    for example in path_to_example_dir.glob('*.json'):
        with open(example, "r") as fp:
            example_content = json.load(fp)
            output_from_call = requests.post("http://127.0.0.1:5000/powerplant/", json=example_content)
            a=1
