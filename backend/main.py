# this is a fast api backend


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from typing import List

class AnalyzeRequest(BaseModel):
    logs : List[str]

class LogRequest(BaseModel):
    failure_id : int

app = FastAPI()

# allow streamlit frontend to talk to the FastAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],  #for development only
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

@app.get("/message")
def get_message():
    return {"message":"Hello World"}


# Dummy failiures
failures = [
    {"id":1, "type":"VM Crash", "details":"vm-prod 21 went offline"},
    {"id":2, "type":"Pipeline Failure", "details":"CI/CD Pipeline failed out"},
    {"id":3, "type":"Disk Full", "details":"Disk usage exceeded 90%"}

]


@app.get("/failures")
def get_failures():
    return failures


@app.post("/logs")
def get_logs(req : LogRequest):
    dummy_logs = {
        1: ["[10:01] VM boot failed", "[10:02] Kernel panic", "[10:03] System halted"],
        2: ["[14:12] Build step 4 failed", "[14:13] Timeout after 5 mins"],
        3: ["[09:55] Disk usage: 92%", "[09:56] Alert triggered: DiskFull"],
    }

    return {"logs":dummy_logs.get(req.failure_id, ["No logs found for this failure"])}



@app.post("/analyze")
def analyze_logs(req: AnalyzeRequest):
    logs = req.logs
    analysis = "Analysis Result: \n"

    if any("kernel panic" in log for log in logs):
        analysis += "- Detected a system crash : kernel panic. \n"
    if any("Timeout" in log for log in logs):
        analysis += "- Likely issue with pipeline timeout.\n"
    if any("Disk usage" in log for log in logs):
        analysis += "- Disk may be full or nearing capacity.\n"



    if analysis.strip() == "Analysis Result:":
        analysis += "- No specific pattern detected. Manual check needed."

    return {"analysis": analysis}



class SuggestFixRequest(BaseModel):
    failure_type: str
    analysis: str

@app.post("/suggest_fix")
def suggest_fix(req: SuggestFixRequest):
    failure_type = req.failure_type.lower()
    analysis = req.analysis.lower()

    if "vm crash" in failure_type or "kernel panic" in analysis:
        return {"suggestion": "Try restarting the VM using the cloud provider console."}
    elif "pipeline" in failure_type or "timeout" in analysis:
        return {"suggestion": "Re-run the pipeline or increase timeout settings."}
    elif "disk" in failure_type or "disk full" in analysis:
        return {"suggestion": "Clear unnecessary files or increase disk size."}
    else:
        return {"suggestion": "No automatic fix available. Escalate to SRE team."}



