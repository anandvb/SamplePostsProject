from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from app.models.generic_response import GenericResponseModel
from app.utils.logger import logger


def build_response_model(response_model: GenericResponseModel) -> JSONResponse:
    """Build response for controller APIs with generic response"""
    try:
        response_json = jsonable_encoder(response_model)
        response = JSONResponse(
            status_code=response_model.status_code, content=response_json
        )
        return response
    except Exception as e:
        logger.error(e)
        return JSONResponse(
            status_code=response_model.status_code, content=response_model.error
        )
