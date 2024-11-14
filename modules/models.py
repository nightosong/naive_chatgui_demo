from typing import Dict, Tuple, Union
from llama_index.core.base.llms.types import (
    CompletionResponseAsyncGen,
    ChatResponseAsyncGen,
    CompletionResponseGen,
    ChatResponseGen,
)
from llama_index.core.base.response.schema import (
    StreamingResponse,
    AsyncStreamingResponse,
)
from llama_index.core.llms.utils import LLMType
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.embeddings.siliconflow import SiliconFlowEmbedding
from llama_index.embeddings.xinference import XinferenceEmbedding
from llama_index.embeddings.zhipuai import ZhipuAIEmbedding
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI
from llama_index.llms.siliconflow import SiliconFlow
from llama_index.llms.zhipuai import ZhipuAI
from llama_index.postprocessor.siliconflow_rerank import SiliconFlowRerank
from llama_index.postprocessor.xinference_rerank import XinferenceRerank


class LlamaChatModelManager:
    _reference = {
        "azure": AzureOpenAI,
        "deepseek": OpenAI,
        "ollama": Ollama,
        "siliconflow": SiliconFlow,
        "zhipuai": ZhipuAI,
    }

    def __init__(self, model_configs):
        self._links: Dict[str, Tuple[Union[AzureOpenAI, Ollama], Dict]] = {}
        self._configs = model_configs
        self.link_models(model_configs)

    def link_models(self, configs):
        for config in configs:
            model_type = config["model_type"].split("-")[0]
            model_args = config["model_args"] or {}
            model_cls = self._reference.get(model_type)
            for model_cfg in config["model_list"]:
                if not model_cfg["model_ready"]:
                    continue
                self._links[model_cfg["model_show"]] = [
                    model_cls,
                    dict(model_cfg["extra_args"] or {}, **model_args),
                ]

    def choices(self):
        return list(self._links.keys())

    def load(self, model_name=None, **kwargs) -> Union[AzureOpenAI, Ollama]:
        if not model_name and self._links:
            model_name = next(iter(self._links.keys()))
        if model_name not in self._links:
            raise ValueError(f"Invalid chat model name: {model_name}")
        model_cls, model_args = self._links.get(model_name)
        return model_cls(**model_args, **kwargs)

    @staticmethod
    def generator(
        response: Union[StreamingResponse, CompletionResponseGen, ChatResponseGen],
    ):
        try:
            if isinstance(response, StreamingResponse):
                response_gen = response.response_gen
            else:
                response_gen = response
            for text_gen in response_gen:
                token_gen = (
                    text_gen
                    if isinstance(response, StreamingResponse)
                    else text_gen.delta
                )
                yield token_gen
        except AttributeError as err:
            print("llm generator error: ", err)

    @staticmethod
    async def generator_async(
        response: Union[
            AsyncStreamingResponse, CompletionResponseAsyncGen, ChatResponseAsyncGen
        ]
    ):
        try:
            if isinstance(response, AsyncStreamingResponse):
                response_gen = response.async_response_gen()
            else:
                response_gen = response
            async for text_gen in response_gen:
                yield text_gen
        except AttributeError as err:
            print("llm generator async error: ", err)


class LlamaEmbeddingsManager:
    reference = {
        "azure": AzureOpenAIEmbedding,
        "siliconflow": SiliconFlowEmbedding,
        "xinference": XinferenceEmbedding,
        "zhipuai": ZhipuAIEmbedding,
    }

    def __init__(self, model_configs):
        self.links = {}
        self.link_models(model_configs)

    def link_models(self, configs):
        for config in configs:
            model_type = config["model_type"].split("-")[0]
            model_args = config["model_args"] or {}
            model_cls = self.reference.get(model_type)
            for model_cfg in config["model_list"]:
                if not model_cfg["model_ready"]:
                    continue
                self.links[model_cfg["model_show"]] = [
                    model_cls,
                    dict(model_cfg["extra_args"] or {}, **model_args),
                ]

    def choices(self):
        return list(self.links.keys())

    def load(
        self, model_name, **kwargs
    ) -> Union[AzureOpenAIEmbedding, XinferenceEmbedding]:
        if model_name not in self.links:
            raise ValueError(f"Invalid embedding model name: {model_name}")
        model_cls, model_args = self.links.get(model_name)
        return model_cls(**model_args, **kwargs)


class LlamaRerankManager:
    reference = {
        "siliconflow": SiliconFlowRerank,
        "xinference": XinferenceRerank,
    }

    def __init__(self, model_configs):
        self.links = {}
        self.configs = model_configs
        self.link_models(model_configs)

    def link_models(self, configs):
        for config in configs:
            model_cls = self.reference.get(config["model_type"])
            model_args = config["model_args"] or {}
            for model_cfg in config["model_list"]:
                if not model_cfg["model_ready"]:
                    continue
                self.links[model_cfg["model_show"]] = [
                    model_cls,
                    dict(model_cfg["extra_args"] or {}, **model_args),
                ]

    def choices(self):
        return list(self.links.keys())

    def load(self, model_name, **kwargs) -> Union[SiliconFlowRerank, XinferenceRerank]:
        if model_name not in self.links:
            raise ValueError(f"Invalid rerank model name: {model_name}")
        model_cls, model_args = self.links.get(model_name)
        return model_cls(**model_args, **kwargs)
