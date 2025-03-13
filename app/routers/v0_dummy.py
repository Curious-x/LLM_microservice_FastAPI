from fastapi import APIRouter
from fastapi import Request
from time import sleep
from app.lib.schemas import PolicyTranslationRequest, PolicyTranslationResponse

router = APIRouter()


@router.post("/validate")
def translate_policy(
    request: Request, req: PolicyTranslationRequest
) -> PolicyTranslationResponse:
    res = PolicyTranslationResponse(policy=get_dummy_response())
    sleep(3)
    return res


def get_dummy_response() -> str:
    return """
package example

default allow = false

# Allow if the request is a GET request and the path is "/allowed"

allow if {
    input.method == "GET"
    input.path == "/allowed"
}
    """
