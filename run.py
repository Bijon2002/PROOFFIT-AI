"""Convenience runner script for PROOFFIT AI server."""
import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("  PROOFFIT AI - Enterprise Data Readiness Assessment Engine")
    print("  Server starting at: http://localhost:8000")
    print("  API Docs available at: http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
