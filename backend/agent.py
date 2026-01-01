import os
import re
import requests
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from groq import Groq
from bs4 import BeautifulSoup
import ast
from memory.db import memory_db

router = APIRouter(prefix="/api")


def get_client(request: Request) -> Groq:
    try:
        return Groq(api_key=request.app.state.settings.GROQ_API_KEY)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Groq client: {str(e)}")


def safe_calc(expression: str) -> str:
    """Safe math evaluator - only allows basic math operations"""
    try:
        # Remove 'calc:' prefix and clean
        expr = re.sub(r'^calc:\s*', '', expression).strip()
        
        # Only allow safe characters
        if not re.match(r'^[\d\s\+\-\*\/\*\*\(\)\.]+$', expr):
            return "Error: Only basic math operations (+, -, *, /, **, parentheses) and numbers allowed"
        
        # Use ast.literal_eval for safe evaluation
        result = eval(expr, {"__builtins__": {}}, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Calculation error: {str(e)}"


def web_search(query: str, request: Request) -> str:
    """Web search using DuckDuckGo"""
    try:
        url = f"https://duckduckgo.com/html/?q={requests.utils.quote(query)}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        for result in soup.select('.result__title, .result__snippet')[:6]:  # Top 3 results
            if result.text.strip():
                results.append(result.text.strip())
        
        if not results:
            return "No search results found"
        
        # Summarize with Groq
        client = get_client(request)
        summary_prompt = f"Summarize these search results briefly with key points:\n\n" + "\n".join(results[:6])
        resp = client.chat.completions.create(
            model=request.app.state.settings.GROQ_MODEL,
            messages=[{"role": "user", "content": summary_prompt}],
            temperature=0.2,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Search error: {str(e)}"


def web_fetch(url: str, request: Request) -> str:
    """Fetch and summarize a web page"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text content
        text = soup.get_text()
        # Clean and limit
        text = re.sub(r'\s+', ' ', text).strip()[:1500]
        
        if not text:
            return "Could not extract content from the page"
        
        # Summarize with Groq
        client = get_client(request)
        summary_prompt = f"Summarize briefly with key points:\n\n{text}"
        resp = client.chat.completions.create(
            model=request.app.state.settings.GROQ_MODEL,
            messages=[{"role": "user", "content": summary_prompt}],
            temperature=0.2,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Fetch error: {str(e)}"


@router.post("/agent")
async def agent_chat(payload: dict, request: Request):
    try:
        # Support both new { "text": "...", "agent": "agent" } and legacy { "message": "..." }
        raw_message = payload.get("text") or payload.get("message") or ""
        user_message = str(raw_message).strip()
        if not user_message:
            return {"reply": "Ask me anything about ChetnaGPT build & business.", "tool": "llm"}

        # Search memory for context
        memory_context = ""
        try:
            memory_matches = memory_db.search(user_message, k=3)
            if memory_matches:
                memory_context = "Relevant memory:\n" + "\n".join([f"- {match['text']}" for match in memory_matches])
        except Exception as e:
            print(f"Memory search failed: {e}")

        # Tool router
        if "calc:" in user_message.lower() or "calculate" in user_message.lower():
            result = safe_calc(user_message)
            return {"reply": result, "tool": "calc"}
        
        elif "web:" in user_message.lower():
            # Extract URL after "web:"
            url_match = re.search(r'web:\s*(https?://\S+)', user_message, re.IGNORECASE)
            if url_match:
                url = url_match.group(1)
                result = web_fetch(url, request)
                return {"reply": result, "tool": "web"}
            else:
                return {"reply": "Error: Please provide a valid URL after 'web:'", "tool": "web"}
        
        elif "search" in user_message.lower():
            # Extract search query
            query_match = re.search(r'search\s+(.+)', user_message, re.IGNORECASE)
            if query_match:
                query = query_match.group(1)
                result = web_search(query, request)
                return {"reply": result, "tool": "web"}
            else:
                return {"reply": "Error: Please provide a search query after 'search'", "tool": "web"}
        
        else:
            # Default to LLM
            client = get_client(request)
            
            # Build system message with memory context
            system_message = "You are ChetnaGPT Agent. Be concise, helpful, and safe."
            if memory_context:
                system_message += f"\n\n{memory_context}"
            
            resp = client.chat.completions.create(
                model=request.app.state.settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.2,
            )
            reply = resp.choices[0].message.content
            return {"reply": reply, "tool": "llm"}
            
    except HTTPException as e:
        # Re-raise FastAPI HTTP errors
        raise e
    except Exception as e:
        return JSONResponse({"error": f"Agent error: {str(e)}"}, status_code=500)


