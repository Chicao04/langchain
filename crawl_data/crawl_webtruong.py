import requests

url = "https://tuyensinh.hnue.edu.vn/tin-tuc/643"

response = requests.get(
    url,
    timeout=20,
    headers={
        "User-Agent": "Mozilla/5.0"
    }
)

print(response.status_code)
print(response.text[:200])