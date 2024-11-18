import os
import json
import logging
import yaml
import uvicorn
import argparse
import gradio as gr
from pathlib import Path
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from routers.gui_chatbot import router


app = FastAPI()


@app.get("/actuator/health")
async def health_check():
    return {"status": "UP"}


@app.get("/actuator")
async def actuator():
    return {"status": "Not Implemented"}


class NoOptionsFilter(logging.Filter):
    def filter(self, record):
        """屏蔽/actuator/*类日志"""
        if "OPTIONS" in record.getMessage():
            return False
        if "/actuator/" in record.getMessage():
            return False
        return True


def check_filesystem_state(server_config: dict):
    """检查系统的必要文件挂载"""
    filesystem = server_config.get("mount") or []
    for filepath in filesystem:
        try:
            assert Path(filepath).exists(), f"{filepath} not exists!!!"
        except AssertionError as err:
            print(f"文件系统检测: {err}")
    os.environ["TIKTOKEN_CACHE_DIR"] = ".cache"


def load_config_settings(env, service_name):
    os.environ["env"] = env
    config_path = "./configs/service.yaml"
    with open(config_path, "r", encoding="utf-8") as file:
        server_config = yaml.safe_load(file).get(service_name)
        os.environ["service_name"] = service_name
        try:
            assert server_config is not None, f"config {service_name} cant be empty!!!"
        except AssertionError as err:
            print(f"配置检测: {err}")
    return server_config


def load_worker_from_config():
    """动态加载配置服务及路由"""
    gr.mount_gradio_app(app, router, "")


def set_logging_restriction():
    logging.getLogger().setLevel(logging.WARNING)
    restrict_items = ["apscheduler.executors", "apscheduler.scheduler", "nacos.client"]
    for log_item in restrict_items:
        logging.getLogger(log_item).setLevel(logging.CRITICAL)
    logging.getLogger("uvicorn.access").addFilter(NoOptionsFilter())


def set_app_corsmiddleware(server_config: dict):
    """跨域设置"""
    origins = server_config.get("origins") or ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )


def set_app_exception_handlers():
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """捕捉422报错并进行自定义处理"""
        error_json = await request.json()
        print("[422 Unprocessable Entity]: %s", json.dumps(error_json))
        return JSONResponse(
            status_code=422,
            content={"detail": jsonable_encoder(exc.errors())},
        )

    app.add_exception_handler(RequestValidationError, validation_exception_handler)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=str, required=False, help="environment name.")
    parser.add_argument("--address", type=str, default="0.0.0.0", help="server address")
    parser.add_argument("--port", type=str, default="8046", help="server port")
    args = parser.parse_args()
    set_logging_restriction()
    load_worker_from_config()
    uvicorn.run(app, host=args.address, port=int(args.port))
