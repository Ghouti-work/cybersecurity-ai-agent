# Copyright (c) OpenAI
#
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""
Unit tests for the internal `_Converter` class defined in
`agents.models.openai_chatcompletions`. The converter is responsible for
translating between internal "item" structures (e.g., `ResponseOutputMessage`
and related types from `openai.types.responses`) and the ChatCompletion message
structures defined by the OpenAI client library.

These tests exercise both conversion directions:

- `_Converter.message_to_output_items` turns a `ChatCompletionMessage` (as
  returned by the OpenAI API) into a list of `ResponseOutputItem` instances.

- `_Converter.items_to_messages` takes in either a simple string prompt, or a
  list of input/output items such as `ResponseOutputMessage` and
  `ResponseFunctionToolCallParam` dicts, and constructs a list of
  `ChatCompletionMessageParam` dicts suitable for sending back to the API.
"""

from __future__ import annotations

from typing import Literal, cast

import pytest
from openai.types.chat import ChatCompletionMessage, ChatCompletionMessageToolCall
from openai.types.chat.chat_completion_message_tool_call import Function
from openai.types.responses import (
    ResponseFunctionToolCall,
    ResponseFunctionToolCallParam,
    ResponseInputTextParam,
    ResponseOutputMessage,
    ResponseOutputRefusal,
    ResponseOutputText,
)
from openai.types.responses.response_input_item_param import FunctionCallOutput

from cai.sdk.agents.agent_output import AgentOutputSchema
from cai.sdk.agents.exceptions import UserError
from cai.sdk.agents.items import TResponseInputItem
from cai.sdk.agents.models.fake_id import FAKE_RESPONSES_ID
from cai.sdk.agents.models.openai_chatcompletions import _Converter


@pytest.fixture
def converter():
    """Create a _Converter instance for testing."""
    return _Converter()


def test_message_to_output_items_with_text_only(converter):
    """
    Make sure a simple ChatCompletionMessage with string content is converted
    into a single ResponseOutputMessage containing one ResponseOutputText.
    """
    msg = ChatCompletionMessage(role="assistant", content="Hello")
    items = converter.message_to_output_items(msg)
    # Expect exactly one output item (the message)
    assert len(items) == 1
    message_item = cast(ResponseOutputMessage, items[0])
    assert message_item.id == FAKE_RESPONSES_ID
    assert message_item.role == "assistant"
    assert message_item.type == "message"
    assert message_item.status == "completed"
    # Message content should have exactly one text part with the same text.
    assert len(message_item.content) == 1
    text_part = cast(ResponseOutputText, message_item.content[0])
    assert text_part.type == "output_text"
    assert text_part.text == "Hello"


def test_message_to_output_items_with_refusal(converter):
    """
    Make sure a message with a refusal string produces a ResponseOutputMessage
    with a ResponseOutputRefusal content part.
    """
    msg = ChatCompletionMessage(role="assistant", refusal="I'm sorry")
    items = converter.message_to_output_items(msg)
    assert len(items) == 1
    message_item = cast(ResponseOutputMessage, items[0])
    assert len(message_item.content) == 1
    refusal_part = cast(ResponseOutputRefusal, message_item.content[0])
    assert refusal_part.type == "refusal"
    assert refusal_part.refusal == "I'm sorry"


def test_message_to_output_items_with_tool_call(converter):
    """
    If the ChatCompletionMessage contains one or more tool_calls, they should
    be reflected as separate `ResponseFunctionToolCall` items appended after
    the message item.
    """
    tool_call = ChatCompletionMessageToolCall(
        id="tool1",
        type="function",
        function=Function(name="myfn", arguments='{"x":1}'),
    )
    msg = ChatCompletionMessage(role="assistant", content="Hi", tool_calls=[tool_call])
    items = converter.message_to_output_items(msg)
    # Should produce a message item followed by one function tool call item
    assert len(items) == 2
    message_item = cast(ResponseOutputMessage, items[0])
    assert isinstance(message_item, ResponseOutputMessage)
    fn_call_item = cast(ResponseFunctionToolCall, items[1])
    assert fn_call_item.id == FAKE_RESPONSES_ID
    assert fn_call_item.call_id == tool_call.id
    assert fn_call_item.name == tool_call.function.name
    assert fn_call_item.arguments == tool_call.function.arguments
    assert fn_call_item.type == "function_call"


def test_items_to_messages_with_string_user_content(converter):
    """
    A simple string as the items argument should be converted into a user
    message param dict with the same content.
    """
    result = converter.items_to_messages("Ask me anything")
    assert isinstance(result, list)
    assert len(result) == 1
    msg = result[0]
    assert msg["role"] == "user"
    assert msg["content"] == "Ask me anything"


def test_items_to_messages_with_easy_input_message(converter):
    """
    Given an easy input message dict (just role/content), the converter should
    produce the appropriate ChatCompletionMessageParam with the same content.
    """
    items: list[TResponseInputItem] = [
        {
            "role": "user",
            "content": "How are you?",
        }
    ]
    messages = converter.items_to_messages(items)
    assert len(messages) == 1
    out = messages[0]
    assert out["role"] == "user"
    # For simple string inputs, the converter returns the content as a bare string
    assert out["content"] == "How are you?"


def test_items_to_messages_with_output_message_and_function_call(converter):
    """
    Given a sequence of one ResponseOutputMessageParam followed by a
    ResponseFunctionToolCallParam, the converter should produce a single
    ChatCompletionAssistantMessageParam that includes both the assistant's
    textual content and a populated `tool_calls` reflecting the function call.
    """
    # Construct output message param dict with two content parts.
    output_text: ResponseOutputText = ResponseOutputText(
        text="Part 1",
        type="output_text",
        annotations=[],
    )
    refusal: ResponseOutputRefusal = ResponseOutputRefusal(
        refusal="won't do that",
        type="refusal",
    )
    resp_msg: ResponseOutputMessage = ResponseOutputMessage(
        id="42",
        type="message",
        role="assistant",
        status="completed",
        content=[output_text, refusal],
    )
    # Construct a function call item dict (as if returned from model)
    func_item: ResponseFunctionToolCallParam = {
        "id": "99",
        "call_id": "abc",
        "name": "math",
        "arguments": "{}",
        "type": "function_call",
    }
    items: list[TResponseInputItem] = [
        resp_msg.model_dump(),  # type:ignore
        func_item,
    ]
    messages = converter.items_to_messages(items)
    # Should return a single assistant message
    assert len(messages) == 1
    assistant = messages[0]
    assert assistant["role"] == "assistant"
    # Content combines text portions of the output message
    assert "content" in assistant
    assert assistant["content"] == "Part 1"
    # Refusal in output message should be represented in assistant message
    assert "refusal" in assistant
    assert assistant["refusal"] == refusal.refusal
    # Tool calls list should contain one ChatCompletionMessageToolCall dict
    tool_calls = assistant.get("tool_calls")
    assert isinstance(tool_calls, list)
    assert len(tool_calls) == 1
    tool_call = tool_calls[0]
    assert tool_call["type"] == "function"
    assert tool_call["function"]["name"] == "math"
    assert tool_call["function"]["arguments"] == "{}"


def test_convert_tool_choice_handles_standard_and_named_options(converter) -> None:
    """
    The `_Converter.convert_tool_choice` method should return NOT_GIVEN
    if no choice is provided, pass through values like "auto", "required",
    or "none" unchanged, and translate any other string into a function
    selection dict.
    """
    assert converter.convert_tool_choice(None).__class__.__name__ == "str"
    assert converter.convert_tool_choice("auto") == "auto"
    assert converter.convert_tool_choice("required") == "required"
    assert converter.convert_tool_choice("none") == "none"
    tool_choice_dict = converter.convert_tool_choice("mytool")
    assert isinstance(tool_choice_dict, dict)
    assert tool_choice_dict["type"] == "function"
    assert tool_choice_dict["function"]["name"] == "mytool"


def test_convert_response_format_returns_not_given_for_plain_text_and_dict_for_schemas(converter) -> None:
    """
    The `_Converter.convert_response_format` method should return NOT_GIVEN
    when no output schema is provided or if the output schema indicates
    plain text. For structured output schemas, it should return a dict
    with type `json_schema` and include the generated JSON schema and
    strict flag from the provided `AgentOutputSchema`.
    """
    # when output is plain text (schema None or output_type str), do not include response_format
    assert converter.convert_response_format(None).__class__.__name__ == "NoneType"
    assert (
        converter.convert_response_format(AgentOutputSchema(str)).__class__.__name__ == "NoneType"
    )
    # For e.g. integer output, we expect a response_format dict
    schema = AgentOutputSchema(int)
    resp_format = converter.convert_response_format(schema)
    assert isinstance(resp_format, dict)
    assert resp_format["type"] == "json_schema"
    assert resp_format["json_schema"]["name"] == "final_output"
    assert "strict" in resp_format["json_schema"]
    assert resp_format["json_schema"]["strict"] == schema.strict_json_schema
    assert "schema" in resp_format["json_schema"]
    assert resp_format["json_schema"]["schema"] == schema.json_schema()


def test_items_to_messages_with_function_output_item(converter):
    """
    A function call output item should be converted into a tool role message
    dict with the appropriate tool_call_id and content.
    """
    func_output_item: FunctionCallOutput = {
        "type": "function_call_output",
        "call_id": "somecall",
        "output": '{"foo": "bar"}',
    }
    messages = converter.items_to_messages([func_output_item])
    assert len(messages) == 1
    tool_msg = messages[0]
    assert tool_msg["role"] == "tool"
    assert tool_msg["tool_call_id"] == func_output_item["call_id"]
    assert tool_msg["content"] == func_output_item["output"]


def test_extract_all_and_text_content_for_strings_and_lists(converter):
    """
    The converter provides helpers for extracting user-supplied message content
    either as a simple string or as a list of `input_text` dictionaries.
    When passed a bare string, both `extract_all_content` and
    `extract_text_content` should return the string unchanged.
    When passed a list of input dictionaries, `extract_all_content` should
    produce a list of `ChatCompletionContentPart` dicts, and `extract_text_content`
    should filter to only the textual parts.
    """
    prompt = "just text"
    assert converter.extract_all_content(prompt) == prompt
    assert converter.extract_text_content(prompt) == prompt
    text1: ResponseInputTextParam = {"type": "input_text", "text": "one"}
    text2: ResponseInputTextParam = {"type": "input_text", "text": "two"}
    all_parts = converter.extract_all_content([text1, text2])
    assert isinstance(all_parts, list)
    assert len(all_parts) == 2
    assert all_parts[0]["type"] == "text" and all_parts[0]["text"] == "one"
    assert all_parts[1]["type"] == "text" and all_parts[1]["text"] == "two"
    text_parts = converter.extract_text_content([text1, text2])
    assert isinstance(text_parts, list)
    assert all(p["type"] == "text" for p in text_parts)
    assert [p["text"] for p in text_parts] == ["one", "two"]


def test_items_to_messages_handles_system_and_developer_roles(converter):
    """
    Roles other than `user` (e.g. `system` and `developer`) need to be
    converted appropriately whether provided as simple dicts or as full
    `message` typed dicts.
    """
    sys_items: list[TResponseInputItem] = [{"role": "system", "content": "setup"}]
    sys_msgs = converter.items_to_messages(sys_items)
    assert len(sys_msgs) == 1
    assert sys_msgs[0]["role"] == "system"
    assert sys_msgs[0]["content"] == "setup"
    dev_items: list[TResponseInputItem] = [{"role": "developer", "content": "debug"}]
    dev_msgs = converter.items_to_messages(dev_items)
    assert len(dev_msgs) == 1
    assert dev_msgs[0]["role"] == "developer"
    assert dev_msgs[0]["content"] == "debug"


def test_maybe_input_message_allows_message_typed_dict(converter):
    """
    The `_Converter.maybe_input_message` should recognize a dict with
    "type": "message" and a supported role as an input message. Ensure
    that such dicts are passed through by `items_to_messages`.
    """
    # Construct a dict with the proper required keys for a ResponseInputParam.Message
    message_dict: TResponseInputItem = {
        "type": "message",
        "role": "user",
        "content": "hi",
    }
    assert converter.maybe_input_message(message_dict) is not None
    # items_to_messages should process this correctly
    msgs = converter.items_to_messages([message_dict])
    assert len(msgs) == 1
    assert msgs[0]["role"] == "user"
    assert msgs[0]["content"] == "hi"


def test_tool_call_conversion(converter):
    """
    Test that tool calls are converted correctly.
    """
    function_call = ResponseFunctionToolCallParam(
        id="tool1",
        call_id="abc",
        name="math",
        arguments="{}",
        type="function_call",
    )

    messages = converter.items_to_messages([function_call])
    assert len(messages) == 1
    tool_msg = messages[0]
    assert tool_msg["role"] == "assistant"
    assert tool_msg.get("content") is None
    tool_calls = list(tool_msg.get("tool_calls", []))
    assert len(tool_calls) == 1

    tool_call = tool_calls[0]
    assert tool_call["id"] == function_call["call_id"]
    assert tool_call["function"]["name"] == function_call["name"]
    assert tool_call["function"]["arguments"] == function_call["arguments"]


@pytest.mark.parametrize("role", ["user", "system", "developer"])
def test_input_message_with_all_roles(converter, role: str):
    """
    The `_Converter.maybe_input_message` should recognize a dict with
    "type": "message" and a supported role as an input message. Ensure
    that such dicts are passed through by `items_to_messages`.
    """
    # Construct a dict with the proper required keys for a ResponseInputParam.Message
    casted_role = cast(Literal["user", "system", "developer"], role)
    message_dict: TResponseInputItem = {
        "type": "message",
        "role": casted_role,
        "content": "hi",
    }
    assert converter.maybe_input_message(message_dict) is not None
    # items_to_messages should process this correctly
    msgs = converter.items_to_messages([message_dict])
    assert len(msgs) == 1
    assert msgs[0]["role"] == casted_role
    assert msgs[0]["content"] == "hi"


def test_item_reference_errors(converter):
    """
    Test that item references are converted correctly.
    """
    with pytest.raises(UserError):
        converter.items_to_messages(
            [
                {
                    "type": "item_reference",
                    "id": "item1",
                }
            ]
        )


class TestObject:
    pass


def test_unknown_object_errors(converter):
    """
    Test that unknown objects are converted correctly.
    """
    with pytest.raises(UserError, match="❌ Invalid message format - Check documentation for supported types"):
        # Purposely ignore the type error
        converter.items_to_messages([TestObject()])  # type: ignore


def test_assistant_messages_in_history(converter):
    """
    Test that assistant messages are added to the history.
    """
    messages = converter.items_to_messages(
        [
            {
                "role": "user",
                "content": "Hello",
            },
            {
                "role": "assistant",
                "content": "Hello?",
            },
            {
                "role": "user",
                "content": "What was my Name?",
            },
        ]
    )

    assert messages == [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hello?"},
        {"role": "user", "content": "What was my Name?"},
    ]
    assert len(messages) == 3
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "Hello?"
    assert messages[2]["role"] == "user"
    assert messages[2]["content"] == "What was my Name?"
