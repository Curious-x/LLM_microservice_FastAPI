from fastapi import APIRouter
from fastapi import Request
from time import sleep
from app.lib.schemas import PolicyTranslationRequest, PolicyTranslationResponse

router = APIRouter()

from langsmith import Client

client = Client(api_key="LANGSMITH_KEY")
prompt = client.pull_prompt("fydp_v_0_1", include_model=True)


@router.post("/validate")
def translate_policy(
    request: Request, req: PolicyTranslationRequest
) -> PolicyTranslationResponse:
    res = PolicyTranslationResponse(policy=get_response(req.kyvernoPolicy))
    sleep(3)
    return res


def get_response(kevernoPolicy) -> str:

    return prompt.invoke({"Kyverno Policy": kevernoPolicy}).content
