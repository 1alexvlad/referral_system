from httpx import AsyncClient
import pytest


@pytest.mark.parametrize("email, password, status_code, referral_code, expected_cookie", [
    ('kot@pes.com', 'kotopes', 200, None, True),
    ('kot@pes.com', 'sdfsdf', 409, None, False),
    ('sdfl@sdf3.com', 'sdfsdf', 200, None, True),
    ('code@link.com', 'sdfsdf', 400, 'qazwsxedcrfvtgbyhnuj', False),
    ('sd242om', 'sdfsdf', 422, None, False),
])
async def test_register_user(
    email: str, 
    password: str, 
    status_code: int, 
    referral_code: str,
    expected_cookie: bool, 
    ac: AsyncClient):

    response = await ac.post("/auth/register", json={
        "email": email,
        'password': password,
        "referral_code": referral_code,
    })

    assert response.status_code == status_code

    if expected_cookie:
        assert "user_access_token" in response.cookies
    else:
        assert "user_access_token" not in response.cookies



@pytest.mark.parametrize("email, password, status_code, has_cookie", [
    ('test1@example.com', 'password1', 200, True),
    ('test2@example.com', 'password2', 200, True),
    ('newsdf@example.com', 'password2', 401, False),
])
async def test_login_user(
    email: str, 
    password: str, 
    status_code: int, 
    has_cookie: bool,
    ac: AsyncClient):

    login_response = await ac.post("/auth/login", json={
        "email": email,
        "password": password
    })

    assert login_response.status_code == status_code
    
    if has_cookie:
        access_token = login_response.cookies.get("user_access_token")
        assert access_token is not None


    else:
        assert "user_access_token" not in login_response.cookies    

@pytest.mark.parametrize("email, password, expected_creation_status", [
    ('test3@example.com', 'password3', 200),
    ('test1@example.com', 'password1', 400),
])
@pytest.mark.asyncio
async def test_create_referral_code_success(
    email: str, 
    password: str, 
    expected_creation_status: int, 
    ac: AsyncClient):

    login_response = await ac.post("/auth/login", json={
        "email": email,
        "password": password,
    })

    assert login_response.status_code == 200
    access_token = login_response.cookies.get("user_access_token")
    assert access_token is not None

    create_code_response = await ac.post(
        "/referral/create-link",
        json={"expiration_date": 20},
        cookies={"user_access_token": access_token}
    )
    assert create_code_response.status_code == expected_creation_status

    if expected_creation_status == 400:
        assert create_code_response.json()["detail"] == "У вас уже есть активный реферальный код"
    else:
        assert "message" in create_code_response.json()


@pytest.mark.parametrize("email, password, expected_creation_status", [
    ('test3@example.com', 'password3', 400),
    ('test1@example.com', 'password1', 200),
])
@pytest.mark.asyncio
async def test_delete_referral_code_success(
    email: str, 
    password: str, 
    expected_creation_status: int, 
    ac: AsyncClient):

    login_response = await ac.post("/auth/login", json={
        "email": email,
        "password": password,
    })

    access_token = login_response.cookies.get("user_access_token")

    create_code_response = await ac.delete(
        "/referral/delete-link",
        cookies={"user_access_token": access_token}
    )
    assert create_code_response.status_code == expected_creation_status

    if expected_creation_status == 400:
        assert create_code_response.json()["detail"] == "У вас нет реферального кода"
    else:
        assert "message" in create_code_response.json()


@pytest.mark.parametrize("email, password, login_status_code, logout_status_code", [
    ('test1@example.com', 'password1', 200, 200),
    ('newsdf@example.com', 'password2', 401, None),
])
async def test_logout_user(
    email: str,
    password: str,
    login_status_code: int,
    logout_status_code: int,
    ac: AsyncClient
):
    login_response = await ac.post("/auth/login", json={
        "email": email,
        "password": password
    })

    assert login_response.status_code == login_status_code

    if login_status_code == 200:
        user_access_token = login_response.cookies.get("user_access_token")
        assert user_access_token is not None

        logout_response = await ac.post("/auth/logout")

        assert logout_response.status_code == logout_status_code


@pytest.mark.asyncio
async def test_get_referral_count(ac: AsyncClient):
    """Тест: возвращает количество привлеченных пользователей для данного реферала."""
    login_response = await ac.post("/auth/login", json={
        "email": "test1@example.com",
        "password": "password1",
    })
    assert login_response.status_code == 200
    access_token = login_response.cookies.get("user_access_token")
    assert access_token is not None

    referral_count_response = await ac.get(
        "/referral/1",
        cookies={"user_access_token": access_token})

    response_data = referral_count_response.json()
    assert len(response_data) == 1  


@pytest.mark.asyncio
async def test_get_referral_code_by_email(ac: AsyncClient):
    """Тест: возвращает реферальный код по email адресу реферера."""

    referral_code_response = await ac.get(
        "/referral/get-code-by-email",
        params={"email": "test2@example.com"},
    )

    response_data = referral_code_response.json()
    assert "Реферальный код" in response_data  
