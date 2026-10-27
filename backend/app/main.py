import base64, json, os
from typing import Any, Optional
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI

APP_NAME = os.getenv("APP_NAME", "BuildWise AI")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
app = FastAPI(title=APP_NAME, version="1.0.0")
origins = [x.strip() for x in os.getenv("FRONTEND_ORIGIN", "http://localhost:5173").split(",")]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

class ProjectInfo(BaseModel):
    area_sqft: float = Field(default=1000, gt=0)
    floors: int = Field(default=1, ge=1, le=100)
    location: str = "India"
    quality: str = "standard"
    budget_inr: Optional[float] = None
    description: str = ""

class AnalysisRequest(BaseModel):
    description: str = ""
    project: ProjectInfo = Field(default_factory=ProjectInfo)

def get_client():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise HTTPException(status_code=503, detail="AI service is not configured. Set OPENAI_API_KEY in backend environment.")
    return OpenAI(api_key=key)

def analyze(prompt: str, image_data_url: Optional[str] = None) -> dict[str, Any]:
    client = get_client()
    content = [{"type": "text", "text": prompt}]
    if image_data_url:
        content.append({"type": "image_url", "image_url": {"url": image_data_url, "detail": "high"}})
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": (
                    "You are BuildWise AI, an assistant for preliminary construction planning. "
                    "Return ONLY valid JSON matching the requested object. Be cautious and explicit about uncertainty. "
                    "Never claim an image alone proves structural safety. For potential structural danger, advise "
                    "restricting access and consulting a licensed structural engineer. Estimates are illustrative, "
                    "not professional certification or a binding quote."
                )},
                {"role": "user", "content": content}
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        return json.loads(response.choices[0].message.content or "{}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI request failed: {str(e)[:300]}")

@app.get("/health")
def health():
    return {"status": "ok", "app": APP_NAME, "ai_configured": bool(os.getenv("OPENAI_API_KEY"))}

@app.post("/api/analyze/safety")
async def safety_analysis(description: str = Form(""), image: Optional[UploadFile] = File(None)):
    data_url = None
    if image:
        if image.content_type not in ("image/jpeg", "image/png", "image/webp", "image/gif"):
            raise HTTPException(415, "Upload a JPG, PNG, WEBP, or GIF image.")
        raw = await image.read()
        if len(raw) > 10 * 1024 * 1024:
            raise HTTPException(413, "Image must be 10 MB or smaller.")
        data_url = f"data:{image.content_type};base64,{base64.b64encode(raw).decode()}"
    prompt = f"""Analyze this construction site for preliminary safety observations.
Return JSON with keys: summary (string), hazards (array of objects with hazard, severity [low|medium|high|critical|uncertain], evidence, recommended_action), ppe_issues (array of strings), immediate_actions (array of strings), limitations (array of strings). If evidence is insufficient, say so. Description: {description}"""
    return analyze(prompt, data_url)

@app.post("/api/analyze/cracks")
async def crack_analysis(description: str = Form(""), image: Optional[UploadFile] = File(None)):
    data_url = None
    if image:
        if image.content_type not in ("image/jpeg", "image/png", "image/webp", "image/gif"):
            raise HTTPException(415, "Upload a JPG, PNG, WEBP, or GIF image.")
        raw = await image.read()
        if len(raw) > 10 * 1024 * 1024:
            raise HTTPException(413, "Image must be 10 MB or smaller.")
        data_url = f"data:{image.content_type};base64,{base64.b64encode(raw).decode()}"
    prompt = f"""Give a preliminary visual crack assessment. Return JSON with keys: summary, observations (array of objects with crack_type, severity [low|medium|high|critical|uncertain], visible_evidence, possible_causes, recommended_next_steps), urgency, limitations. Do not diagnose structural integrity from a photo; recommend an on-site licensed structural engineer for wide, growing, diagonal, or structural-looking cracks. Description: {description}"""
    return analyze(prompt, data_url)

@app.post("/api/plan")
def planning(req: AnalysisRequest):
    prompt = f"""Create an illustrative construction plan. Return JSON with keys: assumptions (array), materials (array of objects with item, estimated_quantity, unit, notes), cost_estimate (object with currency, low_estimate, high_estimate, line_items array of objects with item, low_cost, high_cost), schedule (array of objects with task, duration_days, dependencies), visualization_brief (string), limitations (array). Avoid unsupported precision and mark local rates as needing validation. Project: {req.project.model_dump_json()}. Description: {req.description}"""
    return analyze(prompt)

@app.post("/api/valuation")
def valuation(req: AnalysisRequest):
    prompt = f"""Provide a rough real-estate valuation framework, not an official appraisal. Return JSON with keys: property_summary, assumptions (array), valuation_method, estimated_range_inr (object with low, high), key_value_factors (array), data_needed (array), limitations (array). Do not invent verified local comparable sales; clearly state if location-specific market data is missing. Project: {req.project.model_dump_json()}. Description: {req.description}"""
    return analyze(prompt)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
