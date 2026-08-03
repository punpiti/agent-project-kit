#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
cases=[
 ("fix the responsive website login bug","software","code",{"web-development"}),
 ("refactor the software prompt routing and run acceptance tests","software","code",set()),
 ("วิเคราะห์ข้อมูลผลสอบและทำกราฟ","general","analysis",{"data-analytics"}),
 ("prepare an IPST education policy proposal for council","governance","policy",set()),
 ("review the IPST education policy and prepare recommendations","governance","policy",{"strategy-advisory"}),
 ("prepare a presentation for the university council policy proposal","governance","presentation",set()),
 ("review the genome manuscript against reviewer concerns","research","paper",set()),
 ("ติดตามกำหนดส่งเอกสาร sabbatical leave","operations","document",set()),
 ("write a literature review for the rainfall paper","research","paper",{"research-synthesis"}),
 ("สร้างสไลด์สำหรับสอน machine learning","education","presentation",set())]
cases += [
 ("prepare a Decidim participatory-budgeting workshop activity","education","course-material",set()),
 ("review the IPST AI for Future Education master plan","governance","policy",set()),
 ("prepare a university alumni award nomination dossier","operations","document",set()),
 ("coordinate TMD correspondence and meeting follow-up","operations","document",set()),
 ("develop an open-channel-flow teaching document for the course","education","course-material",set())]
cases += [
 ("assess how to supervise an undergraduate research student","research","decision",set()),
 ("maintain the IOI / POSN curriculum and selection documents","governance","document",set()),
 ("refactor the task router configuration","software","code",set())]
cases += [
 ("prepare a one-hour research review seminar for graduate students","education","presentation",set()),
 ("maintain the academic promotion evidence and KU forms","operations","document",set())]
cases += [("plan an academic-rank evidence set before filling forms","operations","decision",set())]
for request,domain,deliverable,methods in cases:
    out=subprocess.check_output([sys.executable,str(ROOT/"scripts/route_task.py"),request],text=True)
    data=json.loads(out); assert data["domain"]==domain,(request,data); assert data["deliverable"]==deliverable,(request,data); assert methods.issubset(set(data["methods"])),(request,data)

with tempfile.TemporaryDirectory() as tmp:
    project=Path(tmp); (project/".ai").mkdir();
    (project/".ai/project.json").write_text(json.dumps({"schema_version":1,"status":"configured","name":"Fixture","objective":"Test compact context"}),encoding="utf-8")
    (project/".ai/state.json").write_text(json.dumps({"schema_version":1,"status":"configured","active_task":"route test","next_actions":[]}),encoding="utf-8")
    out=subprocess.check_output([sys.executable,str(ROOT/"scripts/context.py"),"fix the website login bug","--project",str(project)],text=True)
    bundle=json.loads(out); assert bundle["routing"]["domain"]=="software"; assert bundle["metrics"]["secondary_modules"]<=2; assert bundle["metrics"]["bytes"]<=12000; assert len(bundle["sources"])==2
print("v7 structured context tests: PASS")
