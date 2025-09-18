from fastapi import FastAPI, HTTPException
from mcp_server.models.document import Document
from mcp_server.components.parser import parse_document

app = FastAPI(
    title="MCP Documentation Server",
    version="1.0.0",
)

@app.get("/")
def read_root():
    """Root endpoint providing a welcome message."""
    return {"message": "Welcome to the MCP Documentation Server!"}

@app.get("/parse/", response_model=Document)
def parse_file(filepath: str):
    """
    Parses a single AsciiDoc file and returns its structure.
    """
    try:
        document = parse_document(filepath)
        return document
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
