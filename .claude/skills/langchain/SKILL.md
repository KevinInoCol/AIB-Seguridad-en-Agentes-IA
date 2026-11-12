---
name: langchain
description: Use when building AI agents, implementing tool calling workflows,
  creating multi-agent systems, deploying stateful applications, or integrating
  LLM capabilities into production systems. Covers LangChain (agent framework),
  LangGraph (orchestration runtime), Deep Agents (batteries-included harness),
  and LangSmith (observability/deployment).
metadata:
  mintlify-proj: langchain
  version: "1.0"
---

# LangChain Skill

## Product summary

LangChain is an open-source framework for building AI agents and LLM applications. The ecosystem includes:

- **LangChain**: Agent framework with `create_agent` harness, model integrations (OpenAI, Anthropic, Google, etc.), tool abstractions, and middleware for customization
- **LangGraph**: Low-level orchestration runtime for stateful workflows with persistence, streaming, human-in-the-loop, and durable execution
- **Deep Agents**: Batteries-included agent harness with planning, subagents, virtual filesystem, memory, and context management built on LangChain + LangGraph
- **LangSmith**: Observability platform for tracing, evaluation, prompt management, and deployment

Key files and commands:
- Install: `pip install langchain` or `npm install langchain`
- Core imports: `from langchain.agents import create_agent` (Python) or `import { createAgent } from "langchain/agents"` (JS)
- LangGraph: `pip install langgraph` with `StateGraph` for graph-based workflows
- Deep Agents: `pip install deepagents` with `create_deep_agent` for production harness
- Tracing: Set `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY` to enable observability

Primary docs: https://docs.langchain.com

## When to use

Reach for this skill when:

- **Building agents**: Creating AI systems that call tools, make decisions, and take actions in loops
- **Tool calling workflows**: Implementing structured function calling with models (OpenAI, Anthropic, Google, etc.)
- **Multi-agent systems**: Designing supervisor agents, subagents, handoffs, or routers for complex tasks
- **Stateful applications**: Building long-running workflows with persistence, human-in-the-loop, and resumable execution
- **Production deployment**: Deploying agents to cloud, self-hosted, or hybrid infrastructure with monitoring
- **Context management**: Implementing RAG, memory, skills, or prompt caching for knowledge-heavy agents
- **Observability**: Tracing agent execution, debugging tool calls, evaluating performance, and monitoring production

## Quick reference

### Agent creation patterns

| Pattern | Use case | Key parameters |
|---------|----------|-----------------|
| `create_agent` | Lightweight, customizable agent | `model`, `tools`, `system_prompt`, `middleware` |
| `create_deep_agent` | Production agent with planning, memory, subagents | `model`, `tools`, `memory`, `interrupt_on`, `backend` |
| `StateGraph` | Custom graph workflows (LangGraph) | `state_schema`, nodes, edges, `compile()` |
| Router | Classify input and dispatch to agents | Rule-based or LLM-based routing logic |
| Supervisor + Subagents | Main agent delegates to specialized agents | Main agent calls `task` tool to spawn subagents |

### Model string format

```
provider:model-name
```

Examples: `openai:gpt-4o`, `anthropic:claude-sonnet-4-6`, `google_genai:gemini-2.5-flash-lite`, `bedrock_converse:us.anthropic.claude-sonnet-4-6`

### Tool definition

```python
def my_tool(param1: str, param2: int) -> str:
    """Tool description for the model."""
    return result

agent = create_agent(model="...", tools=[my_tool])
```

### Middleware types

| Type | Purpose | Example |
|------|---------|---------|
| Node-style | Sequential logic (logging, validation) | Custom validation before tool execution |
| Wrap-style | Control flow (retry, fallback, caching) | Retry failed tool calls, cache results |
| Built-in | Common patterns | `TodoListMiddleware`, `HumanInTheLoopMiddleware` |

### LangGraph state and nodes

```python
from langgraph.graph import StateGraph, MessagesState, START, END

graph = StateGraph(MessagesState)
graph.add_node("agent_node", agent_function)
graph.add_edge(START, "agent_node")
graph.add_edge("agent_node", END)
compiled = graph.compile()
```

### Tracing and observability

```python
import os
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = "your-key"

# Traces appear automatically in LangSmith
result = agent.invoke({"messages": [...]})
```

## Decision guidance

### When to use each framework

| Need | LangChain `create_agent` | LangGraph | Deep Agents | LangSmith Deployment |
|------|--------------------------|-----------|-------------|----------------------|
| Simple agent with tools | ✓ | | | |
| Custom control flow | | ✓ | ✓ | |
| Planning + subagents | | | ✓ | ✓ |
| Virtual filesystem | | | ✓ | ✓ |
| Persistent memory | | ✓ | ✓ | ✓ |
| Human-in-the-loop | ✓ | ✓ | ✓ | ✓ |
| Production deployment | | | ✓ | ✓ |
| Self-hosted flexibility | | ✓ | ✓ | ✓ |

### Router vs. Supervisor vs. Handoff

| Pattern | When to use | Characteristics |
|---------|------------|-----------------|
| **Router** | Clear input categories, lightweight classification | Single routing step, stateless, no conversation memory |
| **Supervisor + Subagents** | Flexible multi-step orchestration, conversation-aware | Main agent maintains context, calls subagents as tools, parallel execution |
| **Handoff** | Multiple distinct agents with bespoke implementations | Separate graph nodes, explicit context engineering, use `Command.PARENT` |

### Structured output strategies

| Strategy | When to use | Trade-off |
|----------|------------|-----------|
| **Tool strategy** | Works with all models | Requires tool calling support |
| **Provider strategy** | Native model support (Anthropic, OpenAI) | Provider-specific, faster |
| **Pydantic/Dataclass** | Type-safe Python objects | Requires validation |

## Workflow

### Build and deploy an agent

1. **Define the agent's purpose and tools**
   - List what actions the agent should take (API calls, database queries, file operations)
   - Write tool functions with clear docstrings (docstrings become model prompts)
   - Test tools independently before adding to agent

2. **Choose the right framework**
   - Use `create_agent` for simple, customizable agents
   - Use `create_deep_agent` for production with planning, memory, subagents
   - Use `StateGraph` (LangGraph) for custom workflows mixing deterministic and agentic steps

3. **Create the agent**
   ```python
   from langchain.agents import create_agent
   
   agent = create_agent(
       model="openai:gpt-4o",
       tools=[tool1, tool2],
       system_prompt="You are a helpful assistant...",
   )
   ```

4. **Add middleware for advanced behavior**
   - Validation: Check inputs/outputs before execution
   - Retry logic: Handle transient failures
   - Human-in-the-loop: Pause for approval on sensitive operations
   - Custom routing: Add conditional logic

5. **Enable tracing and observability**
   - Set `LANGSMITH_TRACING=true` and API key
   - Run agent and inspect traces in LangSmith UI
   - Check tool calls, model reasoning, and latency

6. **Test and evaluate**
   - Create test datasets with expected inputs/outputs
   - Run evaluations in LangSmith (LLM-as-judge, code evaluators)
   - Compare agent versions and iterate

7. **Deploy to production**
   - Use LangSmith Cloud for managed deployment
   - Use LangSmith Deployment for custom infrastructure
   - Use Deep Agents SDK for self-hosted flexibility
   - Monitor traces, set up alerts, track costs

## Common gotchas

- **Tool docstrings matter**: The model only sees tool docstrings, not implementation. Write clear, concise descriptions of what each tool does and its parameters.

- **Context window limits**: Long conversations and large tool results consume tokens. Use summarization, context offloading, or subagents to manage context.

- **Tool calling failures**: Not all models support tool calling equally. Test with your chosen model. Use `response_format` for structured output fallback.

- **Subagent context isolation**: By default, subagents start with fresh context. Use `mode: "fork"` to inherit parent conversation history if needed.

- **Handoff context engineering**: When using handoffs between agents, explicitly decide what messages pass between them. Malformed context breaks downstream agents.

- **Interrupt durability**: Human-in-the-loop pauses are durable (survive page refresh), but only if using a persistent checkpointer. Default is in-memory.

- **Model string format**: Use exact provider:model format. Typos silently fail. Check LangSmith docs for current model names.

- **Middleware order matters**: Place critical middleware (auth, validation) first. Middleware runs in declaration order.

- **Memory file paths**: Deep Agents memory uses `AGENTS.md` files. Paths are relative to the configured backend. Use `/AGENTS.md` for agent-level, `/memories/user-123/AGENTS.md` for user-scoped.

- **Permissions don't apply to sandboxes**: Filesystem permission rules only apply to file tools, not sandbox `execute` commands. Use backend policy hooks for custom validation.

## Verification checklist

Before submitting agent code:

- [ ] All tools have clear, descriptive docstrings
- [ ] Model string is correct format (`provider:model-name`)
- [ ] Tools are tested independently and work as expected
- [ ] System prompt clearly defines agent behavior and constraints
- [ ] Tracing is enabled (`LANGSMITH_TRACING=true`) for debugging
- [ ] Agent handles errors gracefully (no unhandled exceptions)
- [ ] For production: checkpointer is configured (not in-memory)
- [ ] For production: human-in-the-loop is set for sensitive operations
- [ ] For multi-agent: context engineering is explicit (what passes between agents)
- [ ] Evaluation dataset exists and agent passes baseline tests
- [ ] Cost tracking is enabled to monitor token usage

## Resources

**Comprehensive navigation**: https://docs.langchain.com/llms.txt

**Critical documentation pages**:
1. [LangChain Overview](https://docs.langchain.com/oss/python/langchain/overview) — Framework architecture and `create_agent` basics
2. [LangGraph Overview](https://docs.langchain.com/oss/python/langgraph/overview) — Orchestration runtime, persistence, and streaming
3. [Deep Agents Overview](https://docs.langchain.com/oss/python/deepagents/overview) — Production harness with planning, memory, subagents
4. [LangSmith Observability](https://docs.langchain.com/langsmith/observability) — Tracing, debugging, and monitoring
5. [Multi-agent Patterns](https://docs.langchain.com/oss/python/langchain/multi-agent/index) — Subagents, handoffs, routers, skills

---

> For additional documentation and navigation, see: https://docs.langchain.com/llms.txt
