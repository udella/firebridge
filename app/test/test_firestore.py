# GPT PROMPT
# I am using FastAPI to create an API app interacting with Google Firebase. Please help me to write a FastAPI test for this endpoint

from fastapi.testclient import TestClient
from app.main import app
from app.routers.firestore import get_db_ref_str
from app.init_firebase import db

client = TestClient(app)

# Main Collection for testing
main_test_coll_name = "testing"

# Sub Collections Path Nodes
collection_path_nodes = {
    "my_sub_collection": [
        {"type": "collection", "name": main_test_coll_name},
        {"type": "document", "name": "my_document"},
        {"type": "collection", "name": "my_sub_collection"},
    ],
    "test_coll": [
        {"type": "collection", "name": main_test_coll_name},
        {"type": "document", "name": "test_doc"},
        {"type": "collection", "name": "main_test_coll_name"},
    ],
    "main_test_coll": [
        {"type": "collection", "name": main_test_coll_name},
    ],
}
# def test_1():
#     theType = type(collection_path_nodes["my_sub_collection"])
#     coll = collection_path_nodes["my_sub_collection"]
#     assert False, f"{coll}, type: {theType}"


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Firebridge!"}


def test_create_document_with_specific_name():
    path_nodes = collection_path_nodes["my_sub_collection"]+[
        {"type": "document", "name": "a_deep_document"}
    ]
    document_data = {"foo": "bar"}
    payload = {"path_nodes": path_nodes, "document_data": document_data}
    response = client.post("/firestore/create_document", json=payload)
    assert response.status_code == 200, "Response: {}, payload: {}".format(response.text, path_nodes)
    assert response.json() == {"detail": "Document created successfully"}


def test_create_document_under_collection():
    path_nodes = collection_path_nodes["my_sub_collection"]
    document_data = {"lore": "amet"}
    payload = {"path_nodes": path_nodes, "document_data": document_data}
    response = client.post("/firestore/create_document", json=payload)
    assert response.status_code == 200
    assert "document_id" in response.json()


def test_read_document():
    # Create a new document for testing
    city = {"name": "Tokyo", "country": "Japan"}
    city_ref = eval(get_db_ref_str(collection_path_nodes["main_test_coll"])).add(city)[1]

    # Send a request to read the document
    response = client.post(
        "/firestore/read_document",
        json={
            "path_nodes": collection_path_nodes["main_test_coll"]+[
                {"type": "document", "name": city_ref.id}
            ]
        },
    )

    # Check that the response is successful and contains the expected data
    assert response.status_code == 200
    assert response.json() == {"document_data": city}


def test_update_document():
    # Create a new document for testing
    city = {"name": "Tokyo", "country": "Japan"}
    city_ref = eval(get_db_ref_str(collection_path_nodes["main_test_coll"])).add(city)[1]

    # Update the document with new data
    new_data = {"name": "New Tokyo", "population": 14000000}
    response = client.put(
        "/firestore/update_document",
        json={
            "path_nodes": collection_path_nodes["main_test_coll"]+[
                {"type": "document", "name": city_ref.id}
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
    updated_doc = (
        eval(get_db_ref_str(collection_path_nodes["main_test_coll"]))
        .document(city_ref.id)
        .get()
    )
    assert updated_doc.to_dict() == expected_data


# https://www.python-httpx.org/compatibility/#request-body-on-http-methods
def test_delete_document():
    # Create a new document for testing
    doc_ref = eval(get_db_ref_str(collection_path_nodes["main_test_coll"])).document(
        "new_document"
    )
    doc_ref.set({"name": "Test", "age": 42})

    # Send a request to delete the document
    response = client.request(
        method="DELETE",
        url="/firestore/delete_document",
        json={
            "path_nodes": collection_path_nodes["main_test_coll"]+[
                {"type": "document", "name": "new_document"}
            ],
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
        doc_ref = eval(get_db_ref_str(collection_path_nodes["main_test_coll"])).document(
            f"doc{i}"
        )
        doc_ref.set({"name": f"Test Document {i}", "value": i})

    # Send a request to delete the collection
    response = client.request(
        method="DELETE",
        url="/firestore/delete_collection",
        json={
            "path_nodes": collection_path_nodes["main_test_coll"]
        },
    )

    # Check that the response is successful and contains the expected data
    assert response.status_code == 200, f"Response: {response.text}"
    assert response.json() == {"detail": "Collection deleted successfully"}

    # Check that the collection was deleted from Firestore
    docs = eval(get_db_ref_str(collection_path_nodes["main_test_coll"])).limit(1).get()
    assert len(list(docs)) == 0, "Length: {}".format(len(list(docs)))


def test_delete_collection_or_document():
    # Create a test document
    doc_ref = eval(get_db_ref_str(collection_path_nodes["main_test_coll"])).add({"name": "Test Document"})
    doc_id = doc_ref[1].id

    # Create a test collection with documents
    coll_ref = eval(get_db_ref_str(collection_path_nodes["test_coll"]))
    for i in range(10):
        coll_ref.add({"name": f"Test Document {i+1}"})

    # Delete the document using the new endpoint
    path_nodes = collection_path_nodes["main_test_coll"]+[{"type": "document", "name": doc_id}]
        
    response = client.request(
        method="DELETE",
        url="/firestore/delete_collection_or_document",
        json={"path_nodes": path_nodes},
    )
    assert response.status_code == 200, "Response: {}".format(response.text)

    # # Check that the document is deleted
    # docs = eval(get_db_ref_str(collection_path_nodes["main_test_coll"])).limit(1).get()
    # assert len(list(docs)) == 0, "Length: {}".format(len(list(docs)))
            
    # Check that the document was actually deleted from the database
    doc_snapshot = eval(get_db_ref_str(collection_path_nodes["main_test_coll"])).document(doc_id).get()
    assert not doc_snapshot.exists


    # Delete the collection using the new endpoint
    path_nodes = collection_path_nodes["test_coll"]
    response = client.request(
        method="DELETE",
        url="/firestore/delete_collection_or_document",
        json={"path_nodes": path_nodes},
    )
    assert response.status_code == 200, "Response: {}".format(response.text)

    # # Check that the collection is deleted
    # with pytest.raises(exceptions.NotFoundError):
    #     eval(get_db_ref_str(collection_path_nodes["test_coll"])).limit(1).get()

    # Check that the collection was deleted from Firestore
    docs = eval(get_db_ref_str(collection_path_nodes["test_coll"])).limit(1).get()
    assert len(list(docs)) == 0, "Length: {}".format(len(list(docs)))


def test_clean_up_firestore_testing():
    for key, value in collection_path_nodes.items():
        print(key, value)

        # Delete the collection using the new endpoint
        path_nodes = value
        response = client.request(
            method="DELETE",
            url="/firestore/delete_collection_or_document",
            json={"path_nodes": path_nodes},
        )
        assert response.status_code == 200, "Response: {}".format(response.text)

        # Check that the collection was deleted from Firestore
        docs = eval(get_db_ref_str(value)).limit(1).get()
        assert len(list(docs)) == 0, "Length: {}".format(len(list(docs)))
