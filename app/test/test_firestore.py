# GPT PROMPT
# I am using FastAPI to create an API app interacting with Google Firebase. Please help me to write a FastAPI test for this endpoint

from fastapi.testclient import TestClient
from app.main import app
from firebase_admin import firestore

client = TestClient(app)
db = firestore.client()

# Main Collection for testing
test_coll = "testing"

# Sub Collections Path Nodes
sub_colls_path_nodes = {
    "my_sub_collection": [
        {"type": "collection", "name": test_coll},
        {"type": "document", "name": "my_document"},
        {"type": "collection", "name": "my_sub_collection"}
    ],
    "test_coll": [
        {"type": "collection", "name": test_coll},
        {"type": "document", "name": "test_doc"},
        {"type": "collection", "name": "test_coll"}
    ]
}

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Firebridge!"}


def test_create_document_with_specific_name():
    path_nodes = sub_colls_path_nodes.my_sub_collection.append({"type": "document", "name": "a_deep_document"})
    document_data = {"foo": "bar"}
    payload = {"path_nodes": path_nodes, "document_data": document_data}
    response = client.post("/firestore/create_document", json=payload)
    print(response.text)
    assert response.status_code == 200
    assert response.json() == {"detail": "Document created successfully"}


def test_create_document_under_collection():
    path_nodes = sub_colls_path_nodes.my_sub_collection
    document_data = {"lore": "amet"}
    payload = {"path_nodes": path_nodes, "document_data": document_data}
    response = client.post("/firestore/create_document", json=payload)
    print(response.text)
    assert response.status_code == 200
    assert "document_id" in response.json()


def test_read_document():
    # Create a new document for testing
    city = {"name": "Tokyo", "country": "Japan"}
    city_ref = db.collection("testing").add(city)[1]

    # Send a request to read the document
    response = client.post(
        "/firestore/read_document",
        json={
            "path_nodes": [
                {"type": "collection", "name": test_coll},
                {"type": "document", "name": city_ref.id},
            ]
        },
    )

    # Check that the response is successful and contains the expected data
    assert response.status_code == 200
    assert response.json() == {"document_data": {"name": "Tokyo", "country": "Japan"}}


def test_update_document():
    # Create a new document for testing
    city = {"name": "Tokyo", "country": "Japan"}
    city_ref = db.collection("testing").add(city)[1]

    # Update the document with new data
    new_data = {"name": "New Tokyo", "population": 14000000}
    response = client.put(
        "/firestore/update_document",
        json={
            "path_nodes": [
                {"type": "collection", "name": test_coll},
                {"type": "document", "name": city_ref.id},
            ],
            "update_data": new_data,
        },
    )

    # Check that the response is successful and contains the expected data
    assert response.status_code == 200
    expected_data = {
        **city,
        **new_data,
    }  # Merge the original data with the updated fields
    assert response.json() == {"detail": "Document updated successfully"}
    updated_doc = db.collection("testing").document(city_ref.id).get()
    assert updated_doc.to_dict() == expected_data


# https://www.python-httpx.org/compatibility/#request-body-on-http-methods
def test_delete_document():
    # Create a new document for testing
    doc_ref = db.collection("testing").document("new_document")
    doc_ref.set({"name": "Test", "age": 42})

    # Send a request to delete the document
    response = client.request(
        method="DELETE",
        url="/firestore/delete_document",
        json={
            "path_nodes": [
                {"type": "collection", "name": test_coll},
                {"type": "document", "name": "new_document"},
            ]
        },
    )

    # Check that the response is successful and contains the expected message
    assert response.status_code == 200, f"Response: {response.text}"
    assert response.json() == {"detail": "Document deleted successfully"}

    # Check that the document was actually deleted from the database
    doc_snapshot = doc_ref.get()
    assert not doc_snapshot.exists


def test_delete_collection():
    # Create a new collection for testing
    for i in range(10):
        doc_ref = db.collection("testing").document(f"doc{i}")
        doc_ref.set({"name": f"Test Document {i}", "value": i})

    # Send a request to delete the collection
    response = client.request(
        method="DELETE",
        url="/firestore/delete_collection",
        json={
            "path_nodes": [
                {"type": "collection", "name": test_coll},
            ]
        },
    )

    # Check that the response is successful and contains the expected data
    assert response.status_code == 200, f"Response: {response.text}"
    assert response.json() == {"detail": "Collection deleted successfully"}

    # Check that the collection was deleted from Firestore
    docs = db.collection("testing").limit(1).get()
    assert len(list(docs)) == 0, "Length: {}".format(len(list(docs)))


def test_delete_collection_or_document():
    # Create a test document
    db = firestore.client()
    doc_ref = db.collection(test_coll).add({u'name': u'Test Document'})
    doc_id = doc_ref[1].id

    # Create a test collection with documents
    coll_ref = db.collection(test_coll).document(u'test_doc').collection(u'test_coll')
    for i in range(10):
        coll_ref.add({u'name': f'Test Document {i+1}'})

    # Delete the document using the new endpoint
    path_nodes = [
        {"type": "collection", "name": "testing"},
        {"type": "document", "name": doc_id},
    ]
    response = client.delete("/delete_collection_or_document", json={"path_nodes": path_nodes})
    assert response.status_code == 200

    # Check that the document is deleted
    docs = db.collection("testing").limit(1).get()
    assert len(list(docs)) == 0, "Length: {}".format(len(list(docs)))

    with pytest.raises(exceptions.NotFound):
        db.collection(test_coll).document(doc_id).get()

    # Delete the collection using the new endpoint
    path_nodes = sub_colls_path_nodes.test_coll
    response = client.delete("/delete_collection_or_document", json={"path_nodes": path_nodes})
    assert response.status_code == 200

    # Check that the collection is deleted
    with pytest.raises(exceptions.NotFound):
        db.collection(test_coll).document(u'test_doc').collection(u'test_coll').get()
