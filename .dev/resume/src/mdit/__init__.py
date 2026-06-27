"""Minimal mdit compatibility shim for non-interactive CLI use."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace


class MDContainer(list[object]):
    """Tiny list-backed container compatible with pyserials exception helpers."""

    def __init__(self, *items: object) -> None:
        """Store container items in order."""
        super().__init__(items)

    def __str__(self) -> str:
        """Render the stored items as a concatenated string."""
        return "".join(str(item) for item in self)


@dataclass
class Document:
    """Minimal document object with the target config attribute pyserials sets."""

    heading: object | None = None
    body: object | None = None
    section: dict[str, object] | None = None
    target_configs: dict[str, object] = field(default_factory=dict)

    def __str__(self) -> str:
        """Render the lightweight document as plain text."""
        parts = [self.heading, self.body]
        return "\n".join(str(part) for part in parts if part is not None)


def inline_container(*items: object, separator: str = "") -> MDContainer:
    """Join inline items into a lightweight container."""
    container_items: list[object] = []
    for index, item in enumerate(items):
        if index and separator:
            container_items.append(separator)
        container_items.append(item)
    return MDContainer(*container_items)


def block_container(*items: object, **_kwargs: object) -> MDContainer:
    """Collect block items into a lightweight container."""
    return MDContainer(*items)


def document(
    heading: object | None = None,
    body: object | None = None,
    section: dict[str, object] | None = None,
    **_kwargs: object,
) -> Document:
    """Create a minimal document instance."""
    return Document(heading=heading, body=body, section=section)


def _admonition(**kwargs: object) -> dict[str, object]:
    return kwargs


def _code_block(**kwargs: object) -> dict[str, object]:
    return kwargs


def _code_span(value: object) -> str:
    return str(value)


def _field_list(items: list[object]) -> list[object]:
    return items


def _field_list_item(title: object, body: object) -> tuple[object, object]:
    return title, body


def _unordered_list(items: list[object]) -> list[object]:
    return items


def _render_sphinx(*_unused_args: object, **_unused_kwargs: object) -> None:
    return


element = SimpleNamespace(
    Admonition=dict,
    FieldList=list,
    admonition=_admonition,
    code_block=_code_block,
    code_span=_code_span,
    field_list=_field_list,
    field_list_item=_field_list_item,
    unordered_list=_unordered_list,
)

container = SimpleNamespace(MDContainer=MDContainer)
render = SimpleNamespace(
    get_sphinx_config=lambda config=None: config or {},
    sphinx=_render_sphinx,
)
target = SimpleNamespace(sphinx=lambda **kwargs: kwargs)

__all__ = [
    "Document",
    "MDContainer",
    "block_container",
    "container",
    "document",
    "element",
    "inline_container",
    "render",
    "target",
]
