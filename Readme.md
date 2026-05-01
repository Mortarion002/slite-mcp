# Slite Knowledge Health MCP Server

A FastMCP server that audits a Slite workspace for knowledge health issues and writes a report back into Slite. It connects to Claude Code via stdio transport.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file in the root directory and add your Slite API key:
   ```
   SLITE_API_KEY=your_key_here
   ```

## Connect to Claude Code

Add the following to your `claude_desktop_config.json` (make sure to replace the path with the absolute path to your `server.py`):

```json
{
  "mcpServers": {
    "slite-health": {
      "command": "python",
      "args": ["/absolute/path/to/slite-mcp/server.py"]
    }
  }
}
```

## Example Prompts

Once connected to Claude Code, you can try prompts like:
- "Audit my entire Slite workspace and write a health report"
- "Find all stale docs in my workspace and flag them as outdated"
- "Which docs have no owner assigned?"
- "What's the overall health score of my knowledge base?"

## How it Works

This MCP server provides a set of tools to interact with the Slite API. It can fetch all notes, identify inactive, empty, or publicly exposed documents, and calculate a health score for individual notes. Finally, it can compile these findings into a comprehensive markdown report and save it directly back to your Slite workspace.