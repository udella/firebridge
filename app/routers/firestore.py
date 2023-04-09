# Give me an simple example to create a FastAPI router for "creating doc" in Firestore using Pydantic models and API documentation. Make sure there is doc along with function.

import traceback
from typing import Dict, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, constr
from firebase_admin import firestore, exceptions

router = APIRouter()

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
        db = firestore.client()
        path_node_str_list = []
        last_node_is_document = False
        for idx, node in enumerate(doc.path_nodes):
            path_node_str_list.append(f"{node.type}('{node.name}')")
            if idx + 1 == len(doc.path_nodes) and node.type == "collection":
                path_node_str_list.append("add(doc.document_data)")
            elif idx + 1 == len(doc.path_nodes) and node.type == "document":
                last_node_is_document = True
                path_node_str_list.append("set(doc.document_data)")
            
        path_str = ".".join(path_node_str_list)
        if last_node_is_document:
            eval(f"db.{path_str}")
            return {"detail": "Document created successfully"}
        else:
            doc_ref = eval(f"db.{path_str}")
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
        db = firestore.client()
        path_node_str_list = []
        for node in doc.path_nodes:
            path_node_str_list.append(f"{node.type}('{node.name}')")
            
        path_str = ".".join(path_node_str_list)
        doc_ref = eval(f"db.{path_str}")
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
        db = firestore.client()
        path_node_str_list = []
        for idx, node in enumerate(doc.path_nodes):
            path_node_str_list.append(f"{node.type}('{node.name}')")
        
        path_str = ".".join(path_node_str_list)
        doc_ref = eval(f"db.{path_str}")
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
        db = firestore.client()
        path_node_str_list = []
        for node in doc.path_nodes:
            path_node_str_list.append(f"{node.type}('{node.name}')")
            
        path_str = ".".join(path_node_str_list)
        eval(f"db.{path_str}").delete()
        
        return {"detail": "Document deleted successfully"}
    except exceptions.FirebaseError as e:
        raise HTTPException(status_code=400, detail=f"Error deleting document: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Unknown Error deleting document: {e}")

# TODO: Add support for delete a collection