"""
"""

from fastapi import (status,
                     Depends,
                     APIRouter,
                     HTTPException,
                     Response)

from src.services.service import Service
from src.api.dependencies.dependency import get_service
from src.api.schemas.suggestion import (ResponseSuggestion,
                                        ResponseSuggestionList,
                                        Suggestion)

suggestion_router = APIRouter(
    tags=["Suggestion"],
    prefix="/suggestion",
)


@suggestion_router.get("/getAllSuggestion", status_code=status.HTTP_200_OK, response_model=ResponseSuggestionList)
async def get_all_suggestion(
    service: Service = Depends(get_service)
) -> ResponseSuggestionList:
    """
    """
    try:
        suggestion_records = service.suggestion_repository.load_all_data()
        return ResponseSuggestionList(data=[ResponseSuggestion(**record) for record in suggestion_records])
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@suggestion_router.get("/getSuggestion", status_code=status.HTTP_200_OK)
async def get_suggestion(
    suggestion_question: str,
    service: Service = Depends(get_service)
) -> Suggestion:
    """
    """
    try:
        suggestion_record = service.suggestion_repository.get_suggestion_by_question(
            suggestion_question)
        if not suggestion_record:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Suggestion not found"
            )
        return Suggestion(**suggestion_record)
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@suggestion_router.post("/addSuggestion", status_code=status.HTTP_200_OK, response_model=Response)
async def add_suggestion(
    question: str,
    service: Service = Depends(get_service)
) -> Response:
    """
    """
    try:
        reponse, _ = await service.retrieve_chat_engine.retrieve_chat(
            query=question
        )
        service.suggestion_repository.add_suggestion(
            question=question,
            answer=reponse
        )
        return Response(
            status_code=status.HTTP_201_CREATED,
            content="Adding suggestion successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)) from e
