import json

with open('currentOrder.json', 'r') as f:
        data = json.load(f)
        
for table in range(len(data)):
        #print(data[table])
        _dict = data[table]
        for pizza in data[table]:
                while _dict[pizza] != 0:
                        print(f"We need {pizza} for table {table + 1}")
                        _dict[pizza] = _dict[pizza] - 1