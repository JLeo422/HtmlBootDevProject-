from enum import Enum
from textnode import TextNode, TextType
from parentnode import ParentNode
from textnode_to_html import text_node_to_html_node
from inline_markdown import text_to_textnodes


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    result = []

    for block in blocks:
        stripped = block.strip()
        if stripped:
            result.append(stripped)

    return result


def block_to_block_type(block):
    lines = block.split("\n")

    if block.startswith("#"):
        heading_level = 0
        while heading_level < len(block) and block[heading_level] == "#":
            heading_level += 1
        if 1 <= heading_level <= 6:
            if heading_level < len(block) and block[heading_level] == " ":
                return BlockType.HEADING

    if block.startswith("```\n") and block.endswith("\n```"):
        return BlockType.CODE

    is_quote = True
    for line in lines:
        if not line.startswith(">"):
            is_quote = False
            break
    if is_quote:
        return BlockType.QUOTE

    is_unordered_list = True
    for line in lines:
        if not line.startswith("- "):
            is_unordered_list = False
            break
    if is_unordered_list:
        return BlockType.UNORDERED_LIST

    is_ordered_list = True
    for i in range(len(lines)):
        expected = f"{i + 1}. "
        if not lines[i].startswith(expected):
            is_ordered_list = False
            break
    if is_ordered_list:
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH


def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    html_nodes = []

    for text_node in text_nodes:
        html_nodes.append(text_node_to_html_node(text_node))

    return html_nodes


def paragraph_to_html_node(block):
    text = " ".join(block.split("\n"))
    children = text_to_children(text)
    return ParentNode("p", children)


def heading_to_html_node(block):
    level = 0
    while level < len(block) and block[level] == "#":
        level += 1

    text = block[level + 1:]
    children = text_to_children(text)
    return ParentNode(f"h{level}", children)


def quote_to_html_node(block):
    lines = block.split("\n")
    cleaned_lines = []

    for line in lines:
        content = line[1:]
        if content.startswith(" "):
            content = content[1:]
        cleaned_lines.append(content)

    text = " ".join(cleaned_lines)
    children = text_to_children(text)
    return ParentNode("blockquote", children)


def unordered_list_to_html_node(block):
    lines = block.split("\n")
    list_items = []

    for line in lines:
        text = line[2:]
        children = text_to_children(text)
        list_items.append(ParentNode("li", children))

    return ParentNode("ul", list_items)


def ordered_list_to_html_node(block):
    lines = block.split("\n")
    list_items = []

    for i, line in enumerate(lines, start=1):
        text = line[len(f"{i}. "):]
        children = text_to_children(text)
        list_items.append(ParentNode("li", children))

    return ParentNode("ol", list_items)


def code_to_html_node(block):
    text = block[4:-3]
    text_node = TextNode(text, TextType.CODE)
    code_node = text_node_to_html_node(text_node)
    return ParentNode("pre", [code_node])


def block_to_html_node(block):
    block_type = block_to_block_type(block)

    if block_type == BlockType.PARAGRAPH:
        return paragraph_to_html_node(block)
    if block_type == BlockType.HEADING:
        return heading_to_html_node(block)
    if block_type == BlockType.CODE:
        return code_to_html_node(block)
    if block_type == BlockType.QUOTE:
        return quote_to_html_node(block)
    if block_type == BlockType.UNORDERED_LIST:
        return unordered_list_to_html_node(block)
    if block_type == BlockType.ORDERED_LIST:
        return ordered_list_to_html_node(block)

    raise ValueError("invalid block type")


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []

    for block in blocks:
        children.append(block_to_html_node(block))

    return ParentNode("div", children)
    
def extract_title(markdown):
    lines = markdown.split("\n")

    for line in lines:
        if line.startswith("# "):
            return line[2:].strip()

    raise ValueError("No h1 header found")