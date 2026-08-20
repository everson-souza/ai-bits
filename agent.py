"""
AI assistant with an agent loop + MCP client + Agent Skills.

Layers (each has a role):
    - MCP (vector_server.py): WHAT the agent can do (search/index docs)
    - Skills (skills_loader.py + skills/ folder): HOW and WHEN to do things
    - This file: orchestrates the model -> tools -> model loop

Requirements:
    pip install mcp anthropic
    export ANTHROPIC_API_KEY="your-key"

Expected structure:
    agent.py
    skills_loader.py
    vector_server.py
    skills/
        atendimento/
            SKILL.md
            references/escalonamento.md

Run:
    python agent.py
"""

import asyncio
from contextlib import AsyncExitStack

from dotenv import load_dotenv

load_dotenv()

from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from skills_loader import (
    READ_SKILL_TOOL,
    discover_skills,
    read_skill_file,
    build_system_prompt,
)

MODELO = "claude-sonnet-4-6"
MAX_TOKENS = 8192

class Assistant:
    def __init__(self, identity: str) -> None:
        self.anthropic = Anthropic()  # reads ANTHROPIC_API_KEY from env
        self.stack = AsyncExitStack()
        self.routes: dict[str, ClientSession] = {}  # MCP tool -> session
        self.tools: list[dict] = [READ_SKILL_TOOL]  # local + MCP tools
        self.history: list[dict] = []
        self.skills = discover_skills()
        self.system_prompt = build_system_prompt(identity, self.skills)
 
    async def connect_stdio_server(self, command: str, args: list[str]) -> None:
        """Start a local MCP server process and register its tools."""
        params = StdioServerParameters(command=command, args=args)
        read, write = await self.stack.enter_async_context(stdio_client(params))
        sess = await self.stack.enter_async_context(ClientSession(read, write))
 
        await sess.initialize()  # handshake: version + capabilities

        response = await sess.list_tools()
        for t in response.tools:
            self.routes[t.name] = sess
            self.tools.append(
                {
                    "name": t.name,
                    "description": t.description or "",
                    "input_schema": t.inputSchema,
                }
            )
        names = ", ".join(t.name for t in response.tools)
        print(f"[mcp] connected — tools: {names}")
 
    async def _execute_tool(self, name: str, arguments: dict) -> str:
        # Local tool (skills) or remote (MCP)?
        if name == "read_skill_file":
            return read_skill_file(arguments["path"])
        sess = self.routes[name]
        result = await sess.call_tool(name, arguments)
        return "\n".join(
            block.text for block in result.content if block.type == "text"
        )
 
    async def respond(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})
 
        while True:
            response = self.anthropic.messages.create(
                model=MODELO,
                max_tokens=MAX_TOKENS,
                system=self.system_prompt,
                tools=self.tools,
                messages=self.history,
            )
            self.history.append(
                {"role": "assistant", "content": response.content}
            )

            if response.stop_reason != "tool_use":
                return "".join(
                    b.text for b in response.content if b.type == "text"
                )

            results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                print(f"[agent] calling {block.name}({block.input})")
                out = await self._execute_tool(block.name, block.input)
                results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": out,
                    }
                )
            self.history.append({"role": "user", "content": results})
 
    async def close(self) -> None:
        await self.stack.aclose()