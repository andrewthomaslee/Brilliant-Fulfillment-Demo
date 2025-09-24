from fastapi import HTTPException, status
from beanie import Document


async def check_document_exists(document: Document | None) -> Document:
    if document:
        try:
            result: Document | None = await document.get(document.id)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document not found: {e}")
    if result:
        return result
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
