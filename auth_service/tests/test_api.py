import pytest

class TestAuthAPI:
    """Интеграционные тесты через HTTP."""

    @pytest.mark.asyncio
    async def test_register_and_login_and_me(self, client):
        # Регистрация
        register_resp = await client.post("/auth/register", json={
            "email": "user@example.com",
            "password": "secret123"
        })
        assert register_resp.status_code == 201
        user_data = register_resp.json()
        assert user_data["email"] == "user@example.com"
        assert "id" in user_data

        # Логин (form-data)
        login_resp = await client.post("/auth/login", data={
            "username": "user@example.com",   # OAuth2 форма использует username
            "password": "secret123"
        })
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]

        # Получение профиля с токеном
        me_resp = await client.get("/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert me_resp.status_code == 200
        me_data = me_resp.json()
        assert me_data["email"] == "user@example.com"
        assert me_data["role"] == "user"

    @pytest.mark.asyncio
    async def test_duplicate_registration_returns_409(self, client):
        # Первая регистрация
        await client.post("/auth/register", json={
            "email": "dup@example.com",
            "password": "password1"
        })
        # Повтор с тем же email
        resp = await client.post("/auth/register", json={
            "email": "dup@example.com",
            "password": "password2"
        })
        assert resp.status_code == 409
        assert resp.json()["detail"] == "User already exists"

    @pytest.mark.asyncio
    async def test_login_wrong_password_returns_401(self, client):
        await client.post("/auth/register", json={
            "email": "test@example.com",
            "password": "rightpass"
        })
        resp = await client.post("/auth/login", data={
            "username": "test@example.com",
            "password": "wrongpass"
        })
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid credentials"

    @pytest.mark.asyncio
    async def test_me_without_token_returns_401(self, client):
        resp = await client.get("/auth/me")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_me_with_invalid_token_returns_401(self, client):
        resp = await client.get("/auth/me", headers={
            "Authorization": "Bearer invalidtoken"
        })
        assert resp.status_code == 401