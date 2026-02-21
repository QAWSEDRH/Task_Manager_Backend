import asyncio
import httpx

BASE = "http://localhost:8000"


async def sign_up(client):
    resp = await client.post(
        f"{BASE}/sign_up",
        json={
            "name": "Tewst",
            "surname": "Uswer",
            "email": "testwuser@example.com",
            "password": "12w345678"
        }
    )
    print("SIGN UP:", resp.status_code)
    return resp.json().get("access_token") if resp.status_code == 200 else None


async def login(client):
    resp = await client.post(
        f"{BASE}/login",
        json={
            "email": "testuser@example.com",
            "password": "12345678"
        }
    )
    print("LOGIN:", resp.status_code)
    return resp.json().get("access_token") if resp.status_code == 200 else None


async def create_nine_tasks(client, token):
    headers = {"Authorization": f"Bearer {token}"}

    tasks = [
        # 2026-03-03 (3 tasks)
        {
            "title": "March 3 - Task 1",
            "description": "First task on March 3",
            "created_at": "2026-03-03T08:00:00",
            "exp_time": "2026-03-03T12:00:00",
            "category": "school_task",
            "completed": False
        },
        {
            "title": "March 3 - Task 2",
            "description": "Second task on March 3",
            "created_at": "2026-03-03T14:00:00",
            "exp_time": "2026-03-03T18:00:00",
            "category": "house_task",
            "completed": False
        },
        {
            "title": "March 3 - Task 3",
            "description": "Third task on March 3",
            "created_at": "2026-03-03T20:00:00",
            "exp_time": "2026-03-04T10:00:00",
            "category": "own_bussiness_task",
            "completed": False
        },
        # 2026-03-04 (3 tasks)
        {
            "title": "March 4 - Task 1",
            "description": "First task on March 4",
            "created_at": "2026-03-04T09:00:00",
            "exp_time": "2026-03-04T13:00:00",
            "category": "school_task",
            "completed": False
        },
        {
            "title": "March 4 - Task 2",
            "description": "Second task on March 4",
            "created_at": "2026-03-04T15:00:00",
            "exp_time": "2026-03-04T19:00:00",
            "category": "house_task",
            "completed": False
        },
        {
            "title": "March 4 - Task 3",
            "description": "Third task on March 4",
            "created_at": "2026-03-04T21:00:00",
            "exp_time": "2026-03-05T11:00:00",
            "category": "own_bussiness_task",
            "completed": False
        },
        # 2026-03-05 (3 tasks)
        {
            "title": "March 5 - Task 1",
            "description": "First task on March 5",
            "created_at": "2026-03-05T07:30:00",
            "exp_time": "2026-03-05T11:30:00",
            "category": "school_task",
            "completed": False
        },
        {
            "title": "March 5 - Task 2",
            "description": "Second task on March 5",
            "created_at": "2026-03-05T13:30:00",
            "exp_time": "2026-03-05T17:30:00",
            "category": "house_task",
            "completed": False
        },
        {
            "title": "March 5 - Task 3",
            "description": "Third task on March 5",
            "created_at": "2026-03-05T19:30:00",
            "exp_time": "2026-03-06T09:30:00",
            "category": "own_bussiness_task",
            "completed": False
        }
    ]

    created_ids = []
    for task_data in tasks:
        resp = await client.post(
            f"{BASE}/task/create",
            json=task_data,
            headers=headers
        )
        print(f"CREATE '{task_data['title']}': {resp.status_code}")
        if resp.status_code == 200:
            created_ids.append(resp.json().get("task_id"))

    return created_ids


async def test_date_filter(client, token, date, skip, limit):
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get(
        f"{BASE}/task/{date}/{skip}/{limit}",
        headers=headers
    )

    print(f"\nGET /task/{date}/{skip}/{limit}:")
    print(f"Status: {resp.status_code}")

    if resp.status_code == 200:
        tasks = resp.json()
        print(f"Returned {len(tasks)} tasks:")
        for t in tasks:
            print(f"  - {t.get('title')} | created: {t.get('created_at')}")
    else:
        print(f"Error: {resp.text}")


async def main():
    async with httpx.AsyncClient() as client:

        print("=== SIGN UP ===")
        token = await sign_up(client)

        if not token:
            print("\n=== LOGIN ===")
            token = await login(client)

        if not token:
            print("❌ No token - stop")
            return

        print("\n=== CREATE 9 TASKS (3 per day) ===")
        task_ids = await create_nine_tasks(client, token)
        print(f"\nCreated {len(task_ids)} tasks")

        print("\n" + "=" * 50)
        print("TEST DATE FILTERING")
        print("=" * 50)

        # Test each date
        await test_date_filter(client, token, "2026-03-03", 0, 10)
        await test_date_filter(client, token, "2026-03-04", 0, 10)
        await test_date_filter(client, token, "2026-03-05", 0, 10)

        # Test pagination within a date
        print("\n" + "=" * 50)
        print("TEST PAGINATION WITHIN DATE")
        print("=" * 50)

        await test_date_filter(client, token, "2026-03-03", 0, 2)  # First 2
        await test_date_filter(client, token, "2026-03-03", 1, 2)  # Skip 1, get 2
        await test_date_filter(client, token, "2026-03-03", 2, 1)  # Last one


if __name__ == "__main__":
    asyncio.run(main())