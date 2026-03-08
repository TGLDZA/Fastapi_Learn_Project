from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

def success_response(message: str = "success", data=None):

    content = {
        "code": 200,
        "message": message,
        "data": data
    }

    # jsonable_encoder 可以把任何的 fastapi， pydantic， orm对象都转成正常响应 -> code, message, data
    return JSONResponse(content=jsonable_encoder(content))