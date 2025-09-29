#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-01-22 01:21:11 (ywatanabe)"
# File: _OpenAI.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/ai/_gen_ai/_OpenAI.py"


"""Imports"""
import os
from openai import OpenAI as _OpenAI
from ._BaseGenAI import BaseGenAI

"""Functions & Classes"""


class OpenAI(BaseGenAI):
    def __init__(
        self,
        system_setting="",
        model="",
        api_key=os.getenv("OPENAI_API_KEY"),
        stream=False,
        seed=None,
        n_keep=1,
        temperature=1.0,
        chat_history=None,
        max_tokens=None,
    ):
        self.passed_model = model

        # import scitex
        # scitex.str.print_debug()
        # scitex.gen.printc(model)

        if model.startswith("o"):
            for reasoning_effort in ["low", "midium", "high"]:
                model = model.replace(f"-{reasoning_effort}", "")

        # Set max_tokens based on model
        if max_tokens is None:
            if "gpt-4-turbo" in model:
                max_tokens = 128_000
            elif "gpt-4" in model:
                max_tokens = 8_192
            elif "gpt-3.5-turbo-16k" in model:
                max_tokens = 16_384
            elif "gpt-3.5" in model:
                max_tokens = 4_096
            else:
                max_tokens = 4_096

        super().__init__(
            system_setting=system_setting,
            model=model,
            api_key=api_key,
            stream=stream,
            n_keep=n_keep,
            temperature=temperature,
            provider="OpenAI",
            chat_history=chat_history,
            max_tokens=max_tokens,
        )

    def _init_client(
        self,
    ):
        client = _OpenAI(api_key=self.api_key)
        return client

    def _api_call_static(self):
        kwargs = dict(
            model=self.passed_model,
            messages=self.history,
            seed=self.seed,
            stream=False,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        # # o models adjustment
        # import scitex
        # scitex.str.print_debug()
        # scitex.gen.printc(kwargs.get("model"))

        if kwargs.get("model").startswith("o"):
            kwargs.pop("max_tokens")
            for reasoning_effort in ["low", "midium", "high"]:
                if reasoning_effort in kwargs["model"]:
                    kwargs["reasoning_effort"] = reasoning_effort
                    kwargs["model"] = kwargs["model"].replace(
                        f"-{reasoning_effort}", ""
                    )
        # import scitex
        # scitex.str.print_debug()
        # scitex.gen.printc(kwargs.get("model"))
        # scitex.gen.printc(kwargs.get("reasoning_effort"))
        # scitex.str.print_debug()

        output = self.client.chat.completions.create(**kwargs)
        self.input_tokens += output.usage.prompt_tokens
        self.output_tokens += output.usage.completion_tokens

        out_text = output.choices[0].message.content

        return out_text

    def _api_call_stream(self):
        kwargs = dict(
            model=self.model,
            messages=self.history,
            max_tokens=self.max_tokens,
            n=1,
            stream=self.stream,
            seed=self.seed,
            temperature=self.temperature,
            stream_options={"include_usage": True},
        )

        if kwargs.get("model").startswith("o"):
            for reasoning_effort in ["low", "midium", "high"]:
                kwargs["reasoning_effort"] = reasoning_effort
                kwargs["model"] = kwargs["model"].replace(f"-{reasoning_effort}", "")
            full_response = self._api_call_static()
            for char in full_response:
                yield char
            return

        stream = self.client.chat.completions.create(**kwargs)
        buffer = ""

        for chunk in stream:
            if chunk:
                try:
                    self.input_tokens += chunk.usage.prompt_tokens
                except:
                    pass
                try:
                    self.output_tokens += chunk.usage.completion_tokens
                except:
                    pass

                try:
                    current_text = chunk.choices[0].delta.content
                    if current_text:
                        buffer += current_text
                        # Yield complete sentences or words
                        if any(char in ".!?\n " for char in current_text):
                            yield buffer
                            buffer = ""
                except Exception as e:
                    pass

        # Yield any remaining text
        if buffer:
            yield buffer

    def _api_format_history(self, history):
        formatted_history = []
        for msg in history:
            if isinstance(msg["content"], list):
                content = []
                for item in msg["content"]:
                    if item["type"] == "text":
                        content.append({"type": "text", "text": item["text"]})
                    elif item["type"] == "_image":
                        content.append(
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{item['_image']}"
                                },
                            }
                        )
                formatted_msg = {"role": msg["role"], "content": content}
            else:
                formatted_msg = {
                    "role": msg["role"],
                    "content": msg["content"],
                }
            formatted_history.append(formatted_msg)
        return formatted_history


def main() -> None:
    import scitex

    ai = scitex.ai.GenAI(
        model="o1-low",
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    print(ai("hi, could you tell me what is in the pic?"))

    # print(
    #     ai(
    #         "hi, could you tell me what is in the pic?",
    #         images=[
    #             "/home/ywatanabe/Downloads/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
    #         ],
    #     )
    # )
    pass


# def main():
#     model = "o1-mini"
#     # model = "o1-preview"
#     # model = "gpt-4o"
#     stream = True
#     max_tokens = 4906
#     m = scitex.ai.GenAI(model, stream=stream, max_tokens=max_tokens)
#     m("hi")

if __name__ == "__main__":
    import sys

    import matplotlib.pyplot as plt
    import scitex

    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.session.start(sys, plt, verbose=False)
    main()
    scitex.session.close(CONFIG, verbose=False, notify=False)

# EOF
"""
python -m scitex.ai._gen_ai._OpenAI
"""

# EOF
