import random
import string
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)


# generate a random email address
def random_email():
    return ''.join(random.choices(string.ascii_lowercase, k=8)) + '@example.com'

# test create user and delete user
def test_create_user():
    email = random_email()

    response = client.post(
        "/user/create_user",
        json={
            "email": email,
            "password": "123123"
        }
    )
    assert response.status_code == 200, "Response: {}".format(response.text)
    assert response.json()["email"] == email
    uid = response.json()["uid"]

    # delete the user
    delete_user_only(uid)



# test send verification email endpoint
def test_send_verification_email():
    # create a new user
    email = random_email()

    response = client.post(
        "/user/create_user",
        json={
            "email": email,
            "password": "123123"
        }
    )
    assert response.status_code == 200, "Response: {}".format(response.text)
    assert response.json()["email"] == email
    uid = response.json()["uid"]
    assert response.json()["email_verified"] == False

    # send verification email
    response = client.post(
        "/user/send_verification_email",
        json={
            "email": email
        }
    )
    assert response.status_code == 200, "Response: {}".format(response.text)
    assert response.json()["message"] == f"Verification email sent to {email}"

    # verify the user manually
    response = client.put(
        "/user/update_user",
        json={
            "uid": uid,
            "email": email,
            "password": "123123",
            "email_verified": True,        
        }
    )
    assert response.status_code == 200, "Response: {}".format(response.text)
    assert response.json()["email_verified"] == True, "Response: {}".format(response.text)

    # delete the user
    delete_user_only(uid)




# test create user and read user endpoints
def test_read_user():
    # create a new user
    email = random_email()
    password = "testpassword"
    response = client.post(
        "/user/create_user",
        json={
            "email": email,
            "password": password
        }
    )
    assert response.status_code == 200, "Response: {}".format(response.text)
    uid = response.json()["uid"]

    # read the created user
    response = client.post(
        "/user/read_user",
        json={
            "uid": uid
        }
    )
    assert response.status_code == 200, "Response: {}".format(response.text)
    # assert False, "Response: {}".format(response.text)
    assert response.json()["email"] == email, "Response: {}".format(response.text)
    assert response.json()["display_name"] is None

    # delete the user
    delete_user_only(uid)

    
def test_update_user():
    # create a new user
    email = random_email()
    response = client.post(
        "/user/create_user",
        json={
            "email": email,
            "password": "password123",
            "display_name": "Test User"
        }
    )
    assert response.status_code == 200, "Response: {}".format(response.text)
    uid = response.json()["uid"]

    # update the user
    updated_email = random_email()
    response = client.put(
        "/user/update_user",
        json={
            "uid": uid,
            "email": updated_email,
            "password": "newpassword123",
            "display_name": "Updated User"
        }
    )
    assert response.status_code == 200, "Response: {}".format(response.text)
    assert response.json()["email"] == updated_email
    assert response.json()["display_name"] == "Updated User"

    # delete the user
    delete_user_only(uid)
    
def test_delete_user():    
    # create a new user
    response = client.post(
        "/user/create_user",
        json={
            "email": random_email(),
            "password": "password123"
        }
    )
    assert response.status_code == 200, "Response: {}".format(response.text)
    uid = response.json()["uid"]
    
    delete_user_only(uid)

def delete_user_only(uid):
    # delete the user
    response = client.request(
        method="DELETE",
        url="/user/delete_user",
        json={
            "uid": uid
        }
    )
    assert response.status_code == 200, "Response: {}".format(response.text)
    assert response.json()["message"] == "User deleted successfully"

