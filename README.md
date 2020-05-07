# Powerplant-load-requirement

A REST API that exposes a POST request method to cost-effectively distribute load on power plants.

## Usage

To run the application, ensure that you have [docker](https://docs.docker.com/get-docker/) installed
```bash
sudo docker build -t engie-test .
sudo docker run -p 5001:5001 engie-test
```

The application responds to POST requests    
```
curl -H "Content-Type: application/json" --data @payload1.json http://0.0.0.0:5001/powerplant/
```

## Algorithm of load distribution

1. The power plants are sorted in an ascending order based on the cost in euros per MWh of electricity generated.
2. The load is first distributed on the power plants with the lowest cost of operation. While setting the load 
on each plant, it is checked:
-  Is the total-load less than Pmin of the powerplant? skip it
- Is the remaining-load more than the Pmax, fill the powerplants's load with Pmax
- Is the remaining-load less than Pmax, but more than Pmin, fill the powerplant's load by remaining-load
- Is the remaining-load less than Pmax and also less than Pmin, check if it is worth reducing load on a 
cheaper plan to get the load on the current plant to Pmin 

## Features
1. Type/field validation is done on the POST request
2. CO2 is accounted for on the gas turbine power plant
3. Contains basic test cases in test.py

## Limitations
1. Currently it only accepts the unites in MWh, euros, ton of CO2
2. It runs on debug mode

## Author
[Vikramaditya Gaonkar](https://github.com/vikramaditya91)