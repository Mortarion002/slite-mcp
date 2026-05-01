import httpx
from typing import Dict, Any, List, Union

class SliteClient:
    def __init__(self, api_key: str):
        self.base_url = "https://api.slite.com/v1"
        self.headers = {
            "x-slite-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Union[Dict[str, Any], List[Any]]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method, 
                    f"{self.base_url}{endpoint}", 
                    headers=self.headers,
                    **kwargs
                )
                response.raise_for_status()
                # Return empty dict if no content (like 204 No Content)
                if not response.content:
                    return {}
                return response.json()
            except httpx.HTTPStatusError as e:
                return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
            except Exception as e:
                return {"error": str(e)}

    async def get_all_notes(self, limit: int = 50) -> List[Dict[str, Any]]:
        all_notes = []
        cursor = None
        
        while True:
            params = {"first": limit}
            if cursor:
                params["cursor"] = cursor
                
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(
                        f"{self.base_url}/knowledge-management/notes", 
                        headers=self.headers,
                        params=params
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    if "edges" in data:
                        notes = [edge.get("node", {}) for edge in data["edges"]]
                        all_notes.extend(notes)
                    else:
                        # Fallback if API response shape is different
                        if isinstance(data, list):
                            all_notes.extend(data)
                            break
                        elif "notes" in data:
                            all_notes.extend(data["notes"])
                    
                    page_info = data.get("pageInfo", {})
                    if page_info.get("hasNextPage") and page_info.get("endCursor"):
                        cursor = page_info["endCursor"]
                    else:
                        break
                except Exception as e:
                    # In case of error in pagination, return what we have so far
                    # and an error object to let the caller know it failed halfway
                    if not all_notes:
                        all_notes = [{"error": str(e)}]
                    break
                    
        return all_notes

    async def get_inactive_notes(self) -> Union[Dict[str, Any], List[Any]]:
        return await self._request("GET", "/knowledge-management/notes/inactive")

    async def get_empty_notes(self) -> Union[Dict[str, Any], List[Any]]:
        return await self._request("GET", "/knowledge-management/notes/empty")

    async def get_public_notes(self) -> Union[Dict[str, Any], List[Any]]:
        return await self._request("GET", "/knowledge-management/notes/public")

    async def get_note(self, note_id: str) -> Dict[str, Any]:
        return await self._request("GET", f"/notes/{note_id}")

    async def get_note_children(self, note_id: str) -> Union[Dict[str, Any], List[Any]]:
        return await self._request("GET", f"/notes/{note_id}/children")

    async def verify_note(self, note_id: str) -> Dict[str, Any]:
        return await self._request("PUT", f"/notes/{note_id}/verify", json={})

    async def flag_note_outdated(self, note_id: str) -> Dict[str, Any]:
        return await self._request("PUT", f"/notes/{note_id}/flag-as-outdated", json={})

    async def create_note(self, title: str, markdown: str, parent_note_id: str = None) -> Dict[str, Any]:
        body = {
            "title": title,
            "markdown": markdown
        }
        if parent_note_id:
            body["parentNoteId"] = parent_note_id
        return await self._request("POST", "/notes", json=body)

    async def ask_workspace(self, question: str) -> Dict[str, Any]:
        return await self._request("GET", "/ask", params={"question": question})

    async def get_me(self) -> Dict[str, Any]:
        return await self._request("GET", "/me")

    async def search_notes(self, query: str) -> Dict[str, Any]:
        return await self._request("GET", "/search-notes", params={"query": query})
