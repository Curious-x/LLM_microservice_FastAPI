from fastapi import APIRouter
from app.lib.schemas import PolicyTranslationRequest, PolicyTranslationResponse
from app.lib.prompt_declarations import (
    system_msg_base,
    example_00,
    test_input_kyverno_policy,
)

from typing import Optional
from pydantic import BaseModel, Field

from langchain.chat_models import init_chat_model

from langchain_core.documents import Document

from app.routers import v2_setup


router = APIRouter()
vector_store = v2_setup.setUpChromaDB()


class RegoPolicyExplanation(BaseModel):
    """The equivalent Rego policy for the given Kyverno policy"""

    rego_policy: str = Field(..., description="The equivalent Rego policy")
    rego_policy_explanation: str = Field(
        ..., description="Explanation of the Rego Policy."
    )
    conversion_explanation: Optional[str] = Field(
        ..., description="Explanation of the conversion process."
    )


class SampleRegoPolicyTranslation(BaseModel):
    rego_policy: str = Field(..., description="The equivalent Rego policy")
    kyverno_policy: str = Field(..., description="The equivalent Rego policy")


@router.post("/uploadSample")
def upload_sample(
    req: SampleRegoPolicyTranslation,
):
    """Upload a sample Rego policy translation to the database"""
    # Create a document from the sample
    doc = Document(
        page_content=req.kyverno_policy,
        metadata={
            "translation": req.rego_policy,
        },
    )
    # Add the document to the vector store
    vector_store.add_documents([doc])

    return {"message": "Sample uploaded successfully"}


@router.post("/validate")
def translate_policy(req: PolicyTranslationRequest) -> PolicyTranslationResponse:
    regoPolicy = get_response(req.kyvernoPolicy)
    res = PolicyTranslationResponse(policy=regoPolicy.rego_policy)
    res.metadata = {
        "rego_policy_explanation": regoPolicy.rego_policy_explanation,
        "conversion_explanation": regoPolicy.conversion_explanation,
    }
    return res


@router.get("/test")
def test() -> PolicyTranslationResponse:
    """Test the API"""
    return translate_policy(
        PolicyTranslationRequest(kyvernoPolicy=test_input_kyverno_policy)
    )


def get_relevant_samples(
    kevernoPolicy, k=2, score_threshold=0.5
) -> list[tuple[Document, float]]:

    res = vector_store.similarity_search_with_relevance_scores(
        kevernoPolicy,
        k=k,
        score_threshold=score_threshold,
    )


def generate_example(example_kyverno: str, example_rego: str) -> str:
    e = """Here's another example of a Kyverno policy and its equivalent Rego policy:

Convert the following Kyverno policy to Rego:

```yaml
"""
    e += example_kyverno + "\n```\n\n"
    e += """Here's the equivalent Rego policy for the given Kyverno policy:
```rego
"""
    e += example_rego + "\n```\n\n"
    return e


def get_response(kevernoPolicy, dynamicFewShotPrompting=False) -> RegoPolicyExplanation:

    chatModel = structured_llm()

    system_msg = system_msg_base + example_00

    if dynamicFewShotPrompting:
        relevant_samples = get_relevant_samples(kevernoPolicy, k=1, score_threshold=0.6)
        if len(relevant_samples) > 0:
            example_kyverno = relevant_samples[0][0].page_content
            example_rego = relevant_samples[0][0].metadata["translation"]
            dynamic_example = generate_example(
                example_kyverno=example_kyverno, example_rego=example_rego
            )
            system_msg += dynamic_example
            print("Dynamic Few Shot Prompting:")
            print(dynamic_example)

    structured_res = chatModel.invoke(
        [
            {"role": "system", "content": system_msg},
            {
                "role": "user",
                "content": f"Convert the following Kyverno policy to Rego: \n {kevernoPolicy}",
            },
        ]
    )

    res = RegoPolicyExplanation(
        rego_policy=structured_res.rego_policy,
        rego_policy_explanation=structured_res.rego_policy_explanation,
        conversion_explanation=structured_res.conversion_explanation,
    )

    return res


def structured_llm():
    llm = init_chat_model(
        "llama-3.3-70b-versatile", model_provider="groq", temperature=0.0
    )
    return llm.with_structured_output(RegoPolicyExplanation)
