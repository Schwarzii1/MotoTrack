import requests

response = requests.post("http://135.236.212.233:5000/add_fahrt", json={"FahrtName": "Testfahrt"})
print(response.status_code, response.text)
