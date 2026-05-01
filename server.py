import os
import time
from datetime import datetime
from dotenv import load_dotenv
from fastmcp import FastMCP
from slite_client import SliteClient
from typing import Dict, Any, List, Union

# Load environment variables
load_dotenv()

SLITE_API_KEY = os.getenv("SLITE_API_KEY")
if not SLITE_API_KEY:
    print("Warning: SLITE_API_KEY environment variable is not set. Tools will fail to authenticate.")

# Initialize FastMCP
mcp = FastMCP("Slite Knowledge Health Agent")

# Initialize SliteClient
slite_client = SliteClient(api_key=SLITE_API_KEY or "")

@mcp.tool
async def slite_get_workspace_overview() -> Dict[str, Any]:
    """Get an overview of the entire Slite workspace. Returns total note count and basic metadata. Always call this first before auditing."""
    try:
        user_info = await slite_client.get_me()
        all_notes = await slite_client.get_all_notes(limit=50)
        return {
            "user_info": user_info,
            "total_notes": len(all_notes)
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool
async def slite_get_all_notes() -> List[Dict[str, Any]]:
    """Fetch all notes from the workspace with their metadata including title, last edited date, last viewed date, owner, and verification status. Returns full list for health analysis."""
    try:
        return await slite_client.get_all_notes()
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool
async def slite_get_stale_docs() -> Union[Dict[str, Any], List[Any]]:
    """Get all inactive/stale documents that haven't been viewed or edited recently. These are candidates for review, update, or archiving."""
    try:
        return await slite_client.get_inactive_notes()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool
async def slite_get_empty_docs() -> Union[Dict[str, Any], List[Any]]:
    """Get all empty documents with no content. These are knowledge gaps that need to be filled or deleted."""
    try:
        return await slite_client.get_empty_notes()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool
async def slite_get_public_docs() -> Union[Dict[str, Any], List[Any]]:
    """Get all publicly exposed documents. These need extra scrutiny - public docs should be verified and up to date."""
    try:
        return await slite_client.get_public_notes()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool
async def slite_get_note_detail(note_id: str) -> Dict[str, Any]:
    """Get the full content and metadata of a specific note by its ID."""
    try:
        return await slite_client.get_note(note_id)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool
async def slite_flag_note_outdated(note_id: str, reason: str) -> Dict[str, Any]:
    """Flag a specific note as outdated. Use this when you identify a doc that needs updating. Requires note_id."""
    try:
        result = await slite_client.flag_note_outdated(note_id)
        if isinstance(result, dict) and "error" not in result:
            result["reason_logged"] = reason
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool
async def slite_verify_note(note_id: str) -> Dict[str, Any]:
    """Mark a specific note as verified and up to date. Use after confirming a doc is healthy."""
    try:
        return await slite_client.verify_note(note_id)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool
async def slite_create_health_report(report_markdown: str, overall_score: int) -> Dict[str, Any]:
    """Write a formatted health report document directly into the Slite workspace. 
Call this after completing your analysis to save findings. 
The report_markdown param should be a complete markdown document with:
- Overall health score
- Summary stats (total, healthy, stale, empty, public docs)  
- Critical issues table (note title, issue, recommended action)
- Patterns observed
- Recommended next steps"""
    try:
        title = f"Knowledge Health Report - {datetime.now().strftime('%Y-%m-%d')}"
        return await slite_client.create_note(title, report_markdown)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool
async def slite_ask_workspace(question: str) -> Dict[str, Any]:
    """Ask the Slite workspace a natural language question using AI search. 
Useful for understanding what topics are covered, finding specific docs, or verifying content."""
    try:
        return await slite_client.ask_workspace(question)
    except Exception as e:
        return {"error": str(e)}

def compute_health_score(note: dict) -> tuple[int, list[str]]:
    score = 100
    issues = []
    now = time.time()
    
    last_edited = note.get("updatedAt") or note.get("lastEditedAt")
    if last_edited:
        # Slite API timestamp comes in milliseconds, divide by 1000
        if last_edited > 1e11:
            last_edited_sec = last_edited / 1000
        else:
            last_edited_sec = last_edited
            
        days_since_edit = (now - last_edited_sec) / 86400
        if days_since_edit > 180:
            score -= 40
            issues.append(f"Not edited in {int(days_since_edit)} days (critical)")
        elif days_since_edit > 90:
            score -= 20
            issues.append(f"Not edited in {int(days_since_edit)} days")
    
    if not note.get("title") or note.get("title", "").strip() == "":
        score -= 20
        issues.append("Missing title")
    
    if not note.get("ownerId"):
        score -= 15
        issues.append("No owner assigned")
    
    return max(0, score), issues

@mcp.tool
async def slite_score_note(note_dict: dict) -> Dict[str, Any]:
    """Compute a health score (0-100) for a single note based on age, title, owner, and content. Returns score and list of issues found."""
    try:
        score, issues = compute_health_score(note_dict)
        return {"score": score, "issues": issues}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    mcp.run()
