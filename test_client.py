import asyncio
import httpx

BASE = "http://localhost:8000"


async def login(client):
    resp = await client.post(
        f"{BASE}/login",
        json={
            "email": "test@example.com",
            "password": "12345678"
        }
    )
    print("LOGIN:", resp.status_code, resp.text)
    return resp.json().get("access_token") if resp.status_code == 200 else None


async def create_task(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    task_data = {
        "title": "Task to delete",
        "description": "This task will be deleted",
        "created_at": "02/08/2026",
        "exp_time": "06/02/2026",
        "category": "school_task",
        "completed": False
    }

    resp = await client.post(
        f"{BASE}/task/create",
        json=task_data,
        headers=headers
    )

    print("CREATE:", resp.status_code, resp.text)

    if resp.status_code == 200:
        return resp.json().get("task_id")
    return None


async def delete_task(client, token, task_id):
    headers = {"Authorization": f"Bearer {token}"}
    delete_data = {"task_id": task_id}

    resp = await client.request(
        "DELETE",
        f"{BASE}/task/delete",
        json=delete_data,
        headers=headers
    )

    print("\n" + "=" * 50)
    print("DELETE TASK:")
    print("=" * 50)
    print(f"Status Code: {resp.status_code}")
    print(f"Task ID: {task_id}")
    print(f"Response: {resp.text}")


async def main():
    async with httpx.AsyncClient() as client:
        print("=== LOGIN ===")
        token = await login(client)

        if not token:
            print("❌ NO TOKEN — STOP")
            return

        print("\n=== CREATE TASK ===")
        task_id = await create_task(client, token)

        if not task_id:
            print("❌ NO TASK ID — STOP")
            return

        print("\n=== DELETE TASK ===")
        await delete_task(client, token, task_id)


if __name__ == "__main__":
    asyncio.run(main())