import requests

def get_vector_from_server():
    try:
        response = requests.get("http://localhost:8000/get_vector")
        if response.status_code == 200:
            vector = response.json()["vector"]
            print("Received vector from server:", vector)
        else:
            print("Failed to get vector from server. Status code:", response.status_code)
    except requests.RequestException as e:
        print("An error occurred during the request:", e)

if __name__ == "__main__":
    get_vector_from_server()
