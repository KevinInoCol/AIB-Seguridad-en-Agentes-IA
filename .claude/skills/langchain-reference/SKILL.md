---
name: langchain-reference
description: Access LangChain API reference documentation. Use when working with LangChain, LangGraph, LangSmith, or related Python/JavaScript SDKs.
license: MIT
compatibility: Works with any AI coding agent. MCP server available for IDE integration.
metadata:
  author: langchain-ai
  version: "1.0"
---

# LangChain API Reference

Access comprehensive API documentation for LangChain - a framework for building applications with large language models (LLMs). Covers Python and JavaScript SDKs for LangChain, LangGraph, LangSmith, and integrations.

## When to Use

Use this skill when:
- Working with LangChain Python or JavaScript code
- Looking up class signatures, method parameters, or return types
- Finding the right LangChain component for a task
- Understanding LangGraph agent workflows
- Integrating LangSmith for tracing and observability

## Accessing Documentation

### MCP Server (Recommended for IDEs)

Use the MCP server for structured API access:

```
https://reference.langchain.com/mcp
```

Available tools:
- `search_api`: Search for classes, functions, symbols by name or keyword
- `get_symbol`: Get full documentation for a specific symbol

### Markdown Endpoints

All documentation pages are available as markdown:

| Method | Example |
|--------|---------|
| Add `.md` suffix | `https://reference.langchain.com/python/langchain-core/RunnableSequence.md` |
| Accept header | `Accept: text/markdown` |
| Automatically detected | Requests from curl, wget, known AI user agents |

### Index Files

| Resource | URL | Purpose |
|----------|-----|---------|
| llms.txt | https://reference.langchain.com/llms.txt | Package index with descriptions |
| llms-full.txt | https://reference.langchain.com/llms-full.txt | Complete symbol listing |

## URL Patterns

```
https://reference.langchain.com/{language}/{package}.md                    # Package overview
https://reference.langchain.com/{language}/{package}/{Symbol}.md           # Symbol documentation
https://reference.langchain.com/{language}/{package}/{Symbol}/{member}.md  # Nested member
```

Languages: `python`, `javascript`, `java`, `go`

## Decision Guide

| Need | Use |
|------|-----|
| Find a class/function by name | `search_api` MCP tool or grep llms-full.txt |
| Get full symbol documentation | `get_symbol` MCP tool or fetch URL with `.md` |
| Browse package contents | Fetch package URL with `.md` suffix |
| Understand available packages | Read llms.txt |

## Python vs JavaScript

| Python Package | JavaScript Package | Purpose |
|---------------|-------------------|---------|
| `langchain-core` | `@langchain/core` | Core abstractions (Runnables, messages) |
| `langchain` | `langchain` | Chains, agents, retrieval |
| `langgraph` | `@langchain/langgraph` | Stateful multi-actor graphs |
| `langsmith` | `langsmith` | Tracing and observability |

Note: APIs are similar but not identical. Always check language-specific documentation.

## Gotchas

1. **Package name format differs by language**
   - Python: `langchain-core` (hyphenated)
   - JavaScript: `@langchain/core` (scoped package)

2. **Deprecated patterns** - Avoid these legacy approaches:
   - `LLMChain` → Use `create_agent` or `create_deep_agent` instead
   - `ConversationChain` → Use `create_agent` with message history
   - Direct `AgentExecutor` → Use `create_agent` or `create_deep_agent`
   - LCEL chains → Prefer `create_agent` for new projects

3. **Symbol paths use dots, not slashes**
   - Correct: `RunnableSequence.invoke`
   - URL becomes: `/python/langchain-core/RunnableSequence/invoke.md`

4. **Version differences** - The documentation reflects the latest stable versions.
   Check the version badge on package pages for exact versions.

## Common Tasks

### Using a Chat Model

```python
from langchain.chat_models import init_chat_model
model = init_chat_model("openai:gpt-5.4")
response = model.invoke("Hello!")
```

Search: `init_chat_model`, `ChatOpenAI`, `ChatAnthropic`

### Building an Agent

```python
from langchain.agents import create_agent

agent = create_agent(model="openai:gpt-5.4", tools=[...])
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Your task here"}]}
)
```

Search: `create_agent`, `create_deep_agent`, `Agent`

### RAG (Retrieval-Augmented Generation)

Search: `VectorStore`, `Retriever`, `create_retrieval_chain`

### Tools and Skills

Search: `Tool`, `BaseTool`, `StructuredTool`

## Best Practices

1. **Use `create_agent` or `create_deep_agent`** for building agent workflows
2. **Enable tracing** with LangSmith for debugging
3. **Prefer specific integrations** (e.g., `langchain-openai`) over generic interfaces
4. **Check inheritance** - Many classes extend `Runnable` with shared methods

## Guides and Tutorials

For conceptual guides, tutorials, and how-tos beyond API reference, see the main documentation site. Each product has its own skill file for detailed guidance:

- [LangChain docs](https://docs.langchain.com/oss/langchain/overview) — Agents, models, tools, and structured output
- [LangGraph docs](https://docs.langchain.com/oss/langgraph/overview) — Stateful workflows, durable execution, and human-in-the-loop
- [Deep Agents docs](https://docs.langchain.com/oss/deepagents/overview) — Batteries-included agents with planning and subagents
- [LangSmith docs](https://docs.langchain.com/langsmith/home) — Tracing, evaluation, and deployment

Skills for each product are available at `https://docs.langchain.com/.well-known/agent-skills/index.json`

## More Resources

- [LangChain Documentation](https://docs.langchain.com/) — Tutorials and guides
- [LangSmith](https://smith.langchain.com/) — Tracing and observability
