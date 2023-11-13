import json

with open('currentOrder.json', 'r') as f:
        data = json.load(f)
        _dict = data[session["Table"]-1]
        for pizza in data[3-1]:
            print(f"We need {_dict[pizza]} {pizza}")
