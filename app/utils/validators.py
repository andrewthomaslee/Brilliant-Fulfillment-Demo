from fastapi import HTTPException, status, Request
from beanie import Document


async def check_document_exists(document: Document | None) -> Document:
    if document:
        try:
            result: Document | None = await document.get(document.id)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document not found: {e}")
    if result:
        return document
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")


def get_current_user(request: Request) -> tuple[str, str, bool]:
    username: str | None = request.session.get("username")
    user_id: str | None = request.session.get("user_id")
    admin: bool | None = request.session.get("admin")
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if admin is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return (username, user_id, admin)
