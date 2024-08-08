"""
This module defines FastAPI endpoints for suggestion.
"""

from fastapi import (status,
                     Depends,
                     APIRouter,
                     HTTPException,
                     Response)

from src.services.service import Service
from src.api.dependencies.dependency import get_service


test_router = APIRouter(
    tags=["Test"],
    prefix="/test",
)


@test_router.post(
    "/testPreprocessing",
    status_code=status.HTTP_200_OK,
)
async def get_all_suggestion(
    text: str,
    service: Service = Depends(get_service)
) -> Response:
    """
    """
    try:
        result = service.get_preprocess_engine.preprocess_text(
            text_input=text
        )
        if not result:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="No result not found"
            )
        print(result)
        return Response(
            status_code=status.HTTP_201_CREATED,
            content="Success"
        )
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e
