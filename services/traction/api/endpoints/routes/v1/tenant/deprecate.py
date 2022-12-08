# HTTP Header Date format: Thu, 01 Dec 1994 16:00:00 GMT
# Let's deprecate this set of endpoints.
# messaging is handled in acapy plugins.
from fastapi.responses import JSONResponse
from starlette import status

sunset_str = "Thu, 08 Dec 2022 00:00:00 GMT"

# The HTTP_410_GONE will override whatever is in the route documentation
sunset_response = JSONResponse(
    status_code=status.HTTP_410_GONE,
    content={"message": "API method is deprecated"},
    headers={"sunset": sunset_str, "deprecated": "true"},
)
