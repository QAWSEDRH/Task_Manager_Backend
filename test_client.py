import httpx

URL = "http://127.0.0.1:8000"

login_data = {
    "email": "seva@example.com",
    "password": "12345678"
}

# 1. Авторизация
resp = httpx.post(f"{URL}/login", json=login_data)
print("LOGIN STATUS:", resp.status_code)
print("LOGIN RESPONSE:", resp.json())

token = resp.json()["access_token"]
print("TOKEN:", token)

# 2. Создание задачи
task_data = {
    "title": "Test task",
    "description": "Created from test client"
}

headers = {
    "Authorization": f"Bearer {token}"
}

create_resp = httpx.post(
    f"{URL}/task/create",
    json=task_data,
    headers=headers
)

print("TASK CREATE STATUS:", create_resp.status_code)
print("TASK CREATE RESPONSE:", create_resp.json())
