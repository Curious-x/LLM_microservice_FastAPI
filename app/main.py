# from fydp_try1 import _get_chain, _get_chain_llm
# from langserve import add_routes

from time import sleep
from fastapi import FastAPI

from app.routers import v0_dummy, v2_RLenhanced_validate

app = FastAPI()


@app.get("/", tags=["Hello World"])
def read_root():
    # sleep(10)
    sleep(5)
    return {"Hello": "World"}


app.include_router(
    v0_dummy.router,
    prefix="/api/v0",
    tags=["V0"],
)

# app.include_router(
#     v1_basic.router,
#     prefix="/api/v1",
#     tags=["V1"],
# )

app.include_router(
    v2_RLenhanced_validate.router,
    prefix="/api/v2",
    tags=["V2"],
)


# LangServe
# chain = _get_chain_llm()
# add_routes(app, chain, path="/chain")

# Uncoment the following to debug code and then run the following command:
# py main.py
# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app)
