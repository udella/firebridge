import json
from fastapi.testclient import TestClient
from .main import app
from firebase_admin import firestore

client = TestClient(app)
db = firestore.client()

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Firebridge!"}

def test_create_document_with_specific_name():
    path_nodes = [{"type": "collection", "name": "testing"}, {"type": "document", "name": "my_document"}, {"type": "collection", "name": "my_sub_collection"}, {"type": "document", "name": "a_deep_document"}]
    document_data = {"foo": "bar"}
    payload = {"path_nodes": path_nodes, "document_data": document_data}
    response = client.post("/firestore/create_document", json=payload)
    print(response.text)
    assert response.status_code == 200
    assert response.json() == {'detail': 'Document created successfully'}

def test_create_document_under_collection():
    path_nodes = [{"type": "collection", "name": "testing"}, {"type": "document", "name": "my_document"}, {"type": "collection", "name": "my_sub_collection"}]
    document_data = {"lore": "amet"}
    payload = {"path_nodes": path_nodes, "document_data": document_data}
    response = client.post("/firestore/create_document", json=payload)
    print(response.text)
    assert response.status_code == 200
    assert "document_id" in response.json()

def test_read_document():
    # Create a new document for testing
    city = {
        u'name': u'Tokyo',
        u'country': u'Japan'
    }
    city_ref = db.collection(u'testing').add(city)[1]

    # Send a request to read the document
    response = client.post(
        "/firestore/read_document",
        json={
            "path_nodes": [
                {
                    "type": "collection",
                    "name": "testing"
                },
                {
                    "type": "document",
                    "name": city_ref.id
                }
            ]
        }
    )

    # Check that the response is successful and contains the expected data
    assert response.status_code == 200
    assert response.json() == {
        "document_data": {
            "name": "Tokyo",
            "country": "Japan"
        }
    }

def test_update_document():
    # Create a new document for testing
    city = {
        u'name': u'Tokyo',
        u'country': u'Japan'
    }
    city_ref = db.collection(u'testing').add(city)[1]

    # Update the document with new data
    new_data = {
        "name": "New Tokyo",
        "population": 14000000
    }
    response = client.put(
        "/firestore/update_document",
        json={
            "path_nodes": [
                {
                    "type": "collection",
                    "name": "testing"
                },
                {
                    "type": "document",
                    "name": city_ref.id
                }
            ],
            "update_data": new_data
        }
    )

    # Check that the response is successful and contains the expected data
    assert response.status_code == 200
    expected_data = {**city, **new_data}  # Merge the original data with the updated fields
    assert response.json() == {
        "detail": "Document updated successfully"
    }
    updated_doc = db.collection(u'testing').document(city_ref.id).get()
    assert updated_doc.to_dict() == expected_data

# TODO: Add tests for "/delete_document"
# TODO: Add tests for "/delete_collection"