import requests
import json
import os
from datetime import datetime
from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from app.prompts.peo_prompt import build_peo_prompt, build_po_prompt, build_pso_prompt
from app.schemas.programme_models import (
    PEORequest, PEOResponse, PEOObject,
    PORequest, POResponse, POObject,
    PSORequest, PSOResponse, PSOObject,
    ProgrammeRequest, ProgrammeResponse
)

OUTPUTS_DIR = "outputs"

def call_ollama(prompt: str, timeout: int = 180) -> dict:
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "format": "json"},
        timeout=timeout
    )
    if response.status_code != 200:
        raise Exception(f"Ollama error: {response.text}")
    raw  = response.json()
    text = raw.get("response", "").strip()
    if "```" in text:
        for part in text.split("```"):
            if "{" in part:
                text = part.lstrip("json").strip()
                break
    return json.loads(text.strip())

def save_output(data: dict, prefix: str, name: str):
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"{OUTPUTS_DIR}/{prefix}_{name.replace(' ','_')}_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved: {filename}")

def generate_peos(request: PEORequest) -> PEOResponse:
    try:
        parsed = call_ollama(build_peo_prompt(request.programme_name, request.programme_description, request.n_peos))
        peos   = [PEOObject(peo_id=i.get("peo_id",f"PEO{n+1}"), text=i.get("text",""), focus_area=i.get("focus_area","General")) for n,i in enumerate(parsed.get("peos",[]))]
        save_output({"programme": request.programme_name, "peos": [p.dict() for p in peos]}, "peos", request.programme_name)
        return PEOResponse(programme_name=request.programme_name, peos=peos)
    except Exception as e:
        print(f"PEO error: {e}")
        return PEOResponse(programme_name=request.programme_name, peos=[])

def generate_pos(request: PORequest) -> POResponse:
    try:
        parsed = call_ollama(build_po_prompt(request.programme_name, request.programme_description))
        pos    = [POObject(po_id=i.get("po_id",f"PO{n+1}"), title=i.get("title",""), text=i.get("text","")) for n,i in enumerate(parsed.get("pos",[]))]
        save_output({"programme": request.programme_name, "pos": [p.dict() for p in pos]}, "pos", request.programme_name)
        return POResponse(programme_name=request.programme_name, pos=pos)
    except Exception as e:
        print(f"PO error: {e}")
        return POResponse(programme_name=request.programme_name, pos=[])

def generate_psos(request: PSORequest) -> PSOResponse:
    try:
        parsed = call_ollama(build_pso_prompt(request.programme_name, request.course_list, request.n_psos))
        psos   = [PSOObject(pso_id=i.get("pso_id",f"PSO{n+1}"), text=i.get("text",""), domain=i.get("domain","General")) for n,i in enumerate(parsed.get("psos",[]))]
        save_output({"programme": request.programme_name, "psos": [p.dict() for p in psos]}, "psos", request.programme_name)
        return PSOResponse(programme_name=request.programme_name, psos=psos)
    except Exception as e:
        print(f"PSO error: {e}")
        return PSOResponse(programme_name=request.programme_name, psos=[])

def generate_programme(request: ProgrammeRequest) -> ProgrammeResponse:
    peo_r = generate_peos(PEORequest(programme_name=request.programme_name, programme_description=request.programme_description, n_peos=request.n_peos))
    po_r  = generate_pos(PORequest(programme_name=request.programme_name, programme_description=request.programme_description))
    pso_r = generate_psos(PSORequest(programme_name=request.programme_name, course_list=request.course_list, n_psos=request.n_psos))
    save_output({"programme_name": request.programme_name, "generated_at": datetime.now().isoformat(), "peos": [p.dict() for p in peo_r.peos], "pos": [p.dict() for p in po_r.pos], "psos": [p.dict() for p in pso_r.psos]}, "programme_complete", request.programme_name)
    return ProgrammeResponse(programme_name=request.programme_name, peos=peo_r.peos, pos=po_r.pos, psos=pso_r.psos)