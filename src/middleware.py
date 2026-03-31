import time
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware


def register_middleware(app: FastAPI):
    @app.middleware("http")
    async def custom_logging(request: Request, call_next: Callable):
        print(f"--------------- {request.url} ---------------")
        print("--------------- headers ---------------")
        print(request.headers)
        print("--------------- method ---------------")
        print(request.method)
        print("--------------- body ---------------")
        print(request.body.__dict__)
        start_time = time.perf_counter()
        response: Response = await call_next(request)
        process_time = time.perf_counter() - start_time
        process_time_str = str(f"{process_time:.4f}s")
        print("--------------- time ---------------")
        print(process_time_str)
        response.headers["X-Process-Time"] = process_time_str
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=("*",),
        allow_methods=("*",),
        allow_headers=("*",),
        allow_credentials=True,
    )
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"],
        www_redirect=True,
    )
