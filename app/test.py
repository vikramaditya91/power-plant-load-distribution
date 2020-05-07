import json
import pathlib
import unittest
from parameterized import parameterized
from app.main.service import load_calculations
from app.main.utils.general_utils import PowerPlantConfigurationError


class Testing(unittest.TestCase):
    @parameterized.expand([
        ("payload1.json", [{'name': 'windpark1', 'p': 90.0}, {'name': 'windpark2', 'p': 21.6}, {'name': 'gasfiredbig1', 'p': 368.4}, {'name': 'gasfiredbig2', 'p': 0}, {'name': 'gasfiredsomewhatsmaller', 'p': 0}, {'name': 'tj1', 'p': 0}]),
        ("payload2.json", [{'name': 'windpark1', 'p': 0.0}, {'name': 'windpark2', 'p': 0.0}, {'name': 'gasfiredbig1', 'p': 380.0}, {'name': 'gasfiredbig2', 'p': 100}, {'name': 'gasfiredsomewhatsmaller', 'p': 0}, {'name': 'tj1', 'p': 0}]),
        ("payload3.json", [{'name': 'windpark1', 'p': 90.0}, {'name': 'windpark2', 'p': 21.6}, {'name': 'gasfiredbig1', 'p': 460}, {'name': 'gasfiredbig2', 'p': 338.4}, {'name': 'gasfiredsomewhatsmaller', 'p': 0}, {'name': 'tj1', 'p': 0}]),
    ])
    def test_response_from_example(self, file_name, expected_output):
        path_to_example_dir = pathlib.Path.cwd().parent / "example_payloads"
        with open(path_to_example_dir / file_name, "r") as fp:
            example_content = json.load(fp)
            output_received = load_calculations.load_distributor(example_content)
            self.assertEqual(expected_output, output_received)
            # print(requests.post("http://0.0.0.0:5001/powerplant/", json=example_content).content)

    @parameterized.expand([
        ("payload1.json", 10000, PowerPlantConfigurationError),
        ("payload2.json", -1, ValueError),
        ("payload3.json", 5000, PowerPlantConfigurationError),
    ])
    def test_response_strange_inputs(self, file_name, new_load, raised_error):
        path_to_example_dir = pathlib.Path.cwd().parent / "example_payloads"
        with open(path_to_example_dir / file_name, "r") as fp:
            example_content = json.load(fp)
            example_content['load'] = new_load
            with self.assertRaises(raised_error):
                load_calculations.load_distributor(example_content)

if __name__=="__main__":
    unittest.main()