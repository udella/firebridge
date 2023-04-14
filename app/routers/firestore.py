# GPT PROMPT
# Give me an simple example to create a FastAPI router for "creating doc" in Firestore using Pydantic models and API documentation. Make sure there is doc along with function.

from typing import Dict, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, constr
from firebase_admin import exceptions
from app.init_firebase import db

router = APIRouter()
# db = db

class FireStorePathNode(BaseModel):
    type: constr(regex='^(collection|document)$')
    name: str

class DocumentCreateRequest(BaseModel):
    path_nodes: List[FireStorePathNode]
    document_data: Dict

class DocumentCreateResponse(BaseModel):
    document_id: str

@router.post(
    "/create_document",
    summary="Create a new document in Firestore",
    response_description="JSON object representing the newly created document ID"
)
async def create_document(doc: DocumentCreateRequest):
    """
    Create a new document in Firestore.

    :param doc: Pydantic model representing the document data to be created.
    :return: Pydantic model representing the newly created document ID.
    """
    try:
        

        base_path_str = get_db_ref_str(doc.path_nodes)
        if doc.path_nodes[-1].type == "document":
            db_ref_str = base_path_str + ".set(doc.document_data)"        
            eval(f"{db_ref_str}")
            return {"detail": "Document created successfully"}
        elif doc.path_nodes[-1].type == "collection":
            db_ref_str = base_path_str + ".add(doc.document_data)"        
            doc_ref = eval(f"{db_ref_str}")
            return DocumentCreateResponse(document_id=doc_ref[1].id)

    except exceptions.FirebaseError as e:
        raise HTTPException(status_code=400, detail=f"Error creating document: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Unknown Error creating document: {e}")
    

class DocumentReadRequest(BaseModel):
    path_nodes: List[FireStorePathNode]

class DocumentReadResponse(BaseModel):
    document_data: Dict

@router.post(
    "/read_document",
    summary="Read a document from Firestore",
    response_description="JSON object representing the document data"
)
async def read_document(doc: DocumentReadRequest):
    """
    Read a document from Firestore.

    :param doc: Pydantic model representing the document path to be read.
    :return: Pydantic model representing the document data.
    """
    try:
        
        db_ref_str = get_db_ref_str(doc.path_nodes)
        doc_ref = eval(f"{db_ref_str}")
        doc_data = doc_ref.get().to_dict()
        if not doc_data:
            raise HTTPException(status_code=404, detail="Document not found")
        return DocumentReadResponse(document_data=doc_data)
    except exceptions.FirebaseError as e:
        raise HTTPException(status_code=400, detail=f"Error reading document: {e}")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        else:
            raise HTTPException(status_code=400, detail=f"Unknown Error reading document: {e}")
        
class DocumentUpdateRequest(BaseModel):
    path_nodes: List[FireStorePathNode]
    update_data: Dict

class DocumentUpdateResponse(BaseModel):
    detail: str = "Document updated successfully"


@router.put(
    "/update_document",
    summary="Update an existing document in Firestore",
    response_description="JSON object representing the update status"
)
async def update_document(doc: DocumentUpdateRequest):
    """
    Update an existing document in Firestore.

    :param doc: Pydantic model representing the document data to be updated.
    :return: Pydantic model representing the update status.
    """
    try:
        
        db_ref_str = get_db_ref_str(doc.path_nodes)
        doc_ref = eval(f"{db_ref_str}")
        doc_ref.update(doc.update_data)
        return DocumentUpdateResponse()
    except exceptions.FirebaseError as e:
        raise HTTPException(status_code=400, detail=f"Error updating document: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Unknown Error updating document: {e}")


class DocumentDeleteRequest(BaseModel):
    path_nodes: List[FireStorePathNode]

@router.delete(
    "/delete_document",
    summary="Delete a document from Firestore",
    response_description="JSON object representing the success or failure of the delete operation"
)
async def delete_document(doc: DocumentDeleteRequest):
    """
    Delete a document from Firestore.

    :param doc: Pydantic model representing the document path to be deleted.
    :return: Pydantic model representing the success or failure of the delete operation.
    """
    try:
        

        if doc.path_nodes[-1].type == "collection":
            raise HTTPException(status_code=400, detail="Cannot delete a collection")

        db_ref_str = get_db_ref_str(doc.path_nodes)
        eval(f"{db_ref_str}").delete()

        return {"detail": "Document deleted successfully"}
    except exceptions.FirebaseError as e:
        raise HTTPException(status_code=400, detail=f"Error deleting document: {e}")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        else:
            raise HTTPException(status_code=400, detail=f"Unknown Error reading document: {e}")


class CollectionDeleteRequest(BaseModel):
    path_nodes: List[FireStorePathNode]

@router.delete(
    "/delete_collection",
    summary="Delete a collection from Firestore",
    response_description="JSON object representing the success or failure of the delete operation",
)
async def delete_collection(doc: CollectionDeleteRequest):
    """
    Delete a collection from Firestore.

    :param doc: Pydantic model representing the collection path to be deleted.
    :return: Pydantic model representing the success or failure of the delete operation.
    """
    try:
        

        if doc.path_nodes[-1].type == "document":
            raise HTTPException(status_code=400, detail="Cannot delete a document")
        
        db_ref_str = get_db_ref_str(doc.path_nodes)

        # docs = eval(f"{db_ref_str}").stream()
        collection_ref = eval(f"{db_ref_str}")
        batch_delete_docs_in_coll(collection_ref, 100)
        # for doc in docs:
        #     doc.reference.delete()

        return {"detail": "Collection deleted successfully"}
    except exceptions.FirebaseError as e:
        raise HTTPException(status_code=400, detail=f"Error deleting collection: {e}")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        else:
            raise HTTPException(status_code=400, detail=f"Unknown Error deleting document: {e}")

def batch_delete_docs_in_coll(collection_ref, batch_size):
    """
    Delete all documents in a collection and the collection itself.

    :param collection_ref: Reference to the collection to be deleted.
    :param batch_size: The batch size for deleting documents.
    """
    docs = collection_ref.limit(batch_size).stream()
    deleted = 0

    # Delete documents in batches
    for doc in docs:
        print(f"Deleting document {doc.id}...")
        doc.reference.delete()
        deleted += 1

    # Recurse on the next batch of documents
    if deleted >= batch_size:
        return delete_collection(collection_ref, batch_size)

    # # Delete the collection itself
    # print(f"Deleting collection {collection_ref.id}...")
    # collection_ref.delete()


class CollectionOrDocumentDeleteRequest(BaseModel):
    path_nodes: List[FireStorePathNode]


@router.delete(
    "/delete_collection_or_document",
    summary="Delete a collection or document from Firestore",
    response_description="JSON object representing the success or failure of the delete operation"
)
async def delete_collection_or_document(doc: CollectionOrDocumentDeleteRequest):
    """
    Delete a collection or document from Firestore.

    :param doc: Pydantic model representing the collection or document path to be deleted.
    :return: Pydantic model representing the success or failure of the delete operation.
    """
    try:
        

        db_ref_str = get_db_ref_str(doc.path_nodes)

        if doc.path_nodes[-1].type == "document":
            eval(f"{db_ref_str}").delete()
            return {"detail": "Document deleted successfully"}

        if doc.path_nodes[-1].type == "collection":
            collection_ref = eval(f"{db_ref_str}")
            batch_delete_docs_in_coll(collection_ref, 100)
            return {"detail": "Collection deleted successfully"}

        raise HTTPException(status_code=400, detail="Invalid path, must end with document or collection")
    except exceptions.FirebaseError as e:
        raise HTTPException(status_code=400, detail=f"Error deleting document/collection: {e}")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        else:
            raise HTTPException(status_code=400, detail=f"Unknown Error deleting document/collection: {e}")


def get_db_ref_str(path_nodes: List[FireStorePathNode]):

    path_node_str_list = []
    for node in path_nodes:
        if isinstance(node, FireStorePathNode):
            path_node_str_list.append(f"{node.type}('{node.name}')")
        elif isinstance(node, Dict):
            path_node_str_list.append(f"{node['type']}('{node['name']}')")
    return "db."+".".join(path_node_str_list)

def convert_to_path_nodes(path_list: List[Dict[str, str]]) -> List[FireStorePathNode]:
    """
    Converts a list of dictionaries with "type" and "name" keys to a list of FireStorePathNode instances.

    :param path_list: List of dictionaries with "type" and "name" keys.
    :return: List of FireStorePathNode instances.
    """
    path_nodes = []
    for node in path_list:
        path_nodes.append(FireStorePathNode(type=node["type"], name=node["name"]))
    return path_nodes
