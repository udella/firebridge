# Give me a simple example to create a FastAPI router for "creating doc" in Firestore using Pydantic models and API documentation. Make sure there is doc along with function.

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, constr
from firebase_admin import firestore, exceptions

router = APIRouter()

class FireStorePathNode(BaseModel):
    type: constr(regex='^(collection|document)$')
    name: str

class DocumentCreateRequest(BaseModel):
    path_nodes: list[FireStorePathNode]
    document_data: dict

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
        # print(path_str)
        # collection_ref = db.eval(path_str)
        # doc_ref = collection_ref.add(doc.document_data)
        doc_ref = eval(f"db.{path_str}")
        if last_node_is_document:
            return {"detail": "Document created successfully"}
        else:
            return DocumentCreateResponse(document_id=doc_ref.id)
            # return DocumentCreateResponse(document_id=doc_ref[1].id)
    except exceptions.FirebaseError as e:
        raise HTTPException(status_code=400, detail=f"Error creating document: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Unknown Error creating document: {e}")
    
