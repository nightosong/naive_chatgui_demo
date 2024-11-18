import yaml
import gradio as gr
from typing import Dict
from workers.ragbase_image_analysis import (
    EXTRACTION_METHODS,
    extract_text_from_image,
    load_extraction_models,
)


current_lang = "zh"


def load_translations() -> Dict[str, Dict]:
    with open("configs/translations.yaml", "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def translate(key):
    return load_translations()[current_lang].get(key, key)


def switch_language():
    global current_lang


def update_extraction_models(method):
    choices = load_extraction_models(method)
    return gr.update(value=choices and choices[0] or None, choices=choices)


def setup_tab_image_analysis():
    with gr.Blocks(analytics_enabled=False), gr.Row(equal_height=True):
        with gr.Accordion(translate("image-text-extraction"), open=True):
            extract_method_dlst = gr.Dropdown(
                label=translate("image-text-extract-methods"),
                choices=EXTRACTION_METHODS,
                value=EXTRACTION_METHODS[0],
                interactive=True,
            )
            extract_model_dlst = gr.Dropdown(
                label=translate("image-text-extract-models"),
                choices=load_extraction_models(EXTRACTION_METHODS[0]),
                interactive=True,
            )
            extract_method_dlst.change(
                fn=update_extraction_models,
                inputs=extract_method_dlst,
                outputs=extract_model_dlst,
            )
            gr.Interface(
                fn=extract_text_from_image,
                inputs=[
                    extract_method_dlst,
                    extract_model_dlst,
                    gr.Image(type="filepath"),
                ],
                outputs=gr.TextArea(show_copy_button=True),
                flagging_mode="never",
            )


def setup_ui():
    with gr.Blocks() as client:
        gr.Markdown("Chat Bot Title")
        with gr.Tab("图片分析"):
            setup_tab_image_analysis()
        with gr.Tab("对话问答"):
            gr.Markdown("...")
        with gr.Tab("代码分析"):
            gr.Markdown("...")
        with gr.Tab("使用说明"):
            gr.Markdown("...")
        client.queue()
        # client.startup_events()
    return client


router = setup_ui()
