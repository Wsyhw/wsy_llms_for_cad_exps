import json 

import os


data_save = [
    {
        "instruction": "Give three tips for staying healthy.",
        "input": "",
        "output": "1.Eat a balanced diet and make sure to include plenty of fruits and vegetables. \n2. Exercise regularly to keep your body active and strong. \n3. Get enough sleep and maintain a consistent sleep schedule."
    },
    {
        "instruction": "What are the three primary colors?",
        "input": "",
        "output": "The three primary colors are red, blue, and yellow."
    }
]
with open('/home/hj2/wsy/deepcad/generate_data_wsy/data.json', 'w') as file:
    # json_data = json.dumps(data_save)
    # file.write(json_data)
    json.dump(data_save, file, indent=4)
