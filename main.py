from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Service is live."}

@app.post("/enrich")
async def enrich(request: Request):
    try:
        data = await request.json()
        text = data.get("text", "")

        # Simulate LLM or metadata enrichment
        enriched = {
            "app_name": "SampleApp",
            "purpose": "Demonstrate FastAPI enrichment endpoint",
            "author": "@exampleuser",
            "github_link": "https://github.com/example/SampleApp",
            "paper_link": "https://arxiv.org/abs/1234.5678"
        }

        return JSONResponse(content={
            "input": text,
            "enriched_metadata": enriched
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# For local testing only (not used in Render deployments)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000, reload=True)
