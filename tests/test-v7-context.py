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
cases += [
 ("เขียนหนังสือตำรากลศาสตร์ของไหลจากหลักฐานที่ตรวจแล้ว","book-writing","book",set()),
 ("เขียนหนังสือวิศวกรรมจาก PDF DOCX และ PPTX ขนาดใหญ่","book-writing","book",set()),
 ("build หนังสือเป็น EPUB และ PDF","book-writing","book",set()),
 ("วาง storyline สำหรับ presentation ผู้บริหาร","general","presentation",set()),
 ("จัดทำหนังสือราชการถึงคณะ","operations","document",set())]
for request,domain,deliverable,methods in cases:
    out=subprocess.check_output([sys.executable,str(ROOT/"scripts/route_task.py"),request],text=True)
    data=json.loads(out); assert data["domain"]==domain,(request,data); assert data["deliverable"]==deliverable,(request,data); assert methods.issubset(set(data["methods"])),(request,data)
    assert data["schema_version"]==2 and data["primary_pipeline"],(request,data)
    if deliverable == "book" and not request.startswith("build "): assert "publication-production" not in data["secondary_workflows"],(request,data)
    if request.startswith("build หนังสือ"): assert "publication-production" in data["secondary_workflows"],(request,data)
    if request == "จัดทำหนังสือราชการถึงคณะ": assert "publication-production" not in data["secondary_workflows"],(request,data)
    if request == "วาง storyline สำหรับ presentation ผู้บริหาร": assert "presentation-production" not in data["secondary_workflows"],(request,data)

production_cases=[
 ("สร้างสไลด์สำหรับสอน machine learning","presentation-production"),
 ("create slides for the council briefing","presentation-production"),
 ("export the book manuscript to EPUB","publication-production"),
 ("เกลาภาษาบทความวิจัยให้กระชับ","prose-style"),
 ("revise the manuscript prose before submission","prose-style")]
for request,workflow in production_cases:
    out=subprocess.check_output([sys.executable,str(ROOT/"scripts/route_task.py"),request],text=True)
    data=json.loads(out); assert workflow in data["secondary_workflows"],(request,data)

adversarial_cases = [
 ("fix the presentation mode bug in the slide viewer app","software","code","software-development-automation"),
 ("write the paper based on my seminar talk","research","paper","research-activities"),
 ("ช่วยหาข้อมูลร้านอาหารใกล้บ้าน","general","analysis","general"),
 ("วิเคราะห์สภาพแวดล้อมของตลาด","general","analysis","general"),
 ("สมัครใจเข้าร่วมกิจกรรม","general","analysis","general"),
 ("เขียนหนังสือราชการถึงคณะ","operations","document","administrative-professional-operations"),
 # Engineering requests from this kit's own roadmap (self-hosted v2 trial).
 ("สร้าง JSON Schema สำหรับ workflow registry และ apk.json binding","software","code","software-development-automation"),
 ("ย้าย router rules ออกจาก route_task.py ไปเป็น data ที่ test ได้","software","code","software-development-automation"),
 ("ย้าย transaction logic ของ installer ไป Python แล้วให้ bash กับ powershell เป็น wrapper","software","code","software-development-automation"),
 ("add a GitHub Actions CI matrix for Linux and Windows running release_check.py","software","code","software-development-automation"),
 ("release 7.8.0 canary: bump version, tag, push, publish GitHub Release and Pages","software","code","software-development-automation"),
 ("prepare a course on python for first-year students","education","course-material","course-material-development"),
]
for request,domain,deliverable,primary in adversarial_cases:
    data=json.loads(subprocess.check_output([sys.executable,str(ROOT/"scripts/route_task.py"),request],text=True))
    assert (data["domain"],data["deliverable"],data["primary_pipeline"])==(domain,deliverable,primary),(request,data)

data=json.loads(subprocess.check_output([sys.executable,str(ROOT/"scripts/route_task.py"),"export the revised paper to pdf, convert the policy draft to docx"],text=True))
assert "publication-production" in data["workflow"]["stages"],data
data=json.loads(subprocess.check_output([sys.executable,str(ROOT/"scripts/route_task.py"),"draft a formal letter to the dean"],text=True))
assert "publication-production" not in data["workflow"]["stages"],data
data=json.loads(subprocess.check_output([sys.executable,str(ROOT/"scripts/route_task.py"),"preview the thesis draft"],text=True))
assert "reviewer-response" not in data["workflow"]["stages"],data
data=json.loads(subprocess.check_output([sys.executable,str(ROOT/"scripts/route_task.py"),"fix the bug using user feedback then bump version"],text=True))
assert "package-release" in data["workflow"]["stages"],data
assert not any(item["id"]=="package-release" for item in data["omitted"]),data
data=json.loads(subprocess.check_output([sys.executable,str(ROOT/"scripts/route_task.py"),"ย้าย router rules ออกจาก route_task.py ไปเป็น data ที่ test ได้"],text=True))
assert "data-analytics" not in data["methods"],data
data=json.loads(subprocess.check_output([sys.executable,str(ROOT/"scripts/route_task.py"),"migrate legacy state.json to the new project.json schema"],text=True))
assert data["lifecycle"]!="bootstrap" and "new-project-bootstrap" not in data["workflow"]["state_actions"],data
data=json.loads(subprocess.check_output([sys.executable,str(ROOT/"scripts/route_task.py"),"start a new project"],text=True))
assert data["lifecycle"]=="bootstrap",data
data=json.loads(subprocess.check_output([sys.executable,str(ROOT/"scripts/route_task.py"),"ตรวจ secret และ private path ก่อน release"],text=True))
assert "release-boundary" in data["workflow"]["gates"],data
data=json.loads(subprocess.check_output([sys.executable,str(ROOT/"scripts/route_task.py"),"วิเคราะห์ผลสำรวจความคิดเห็นอาจารย์เพื่อประกอบข้อเสนอนโยบาย"],text=True))
assert data["primary_pipeline"]=="educational-policy-development" and "data-analytics" in data["workflow"]["methods"],data

# Onboarding follows the authoritative Markdown state, not a placeholder project.json.
with tempfile.TemporaryDirectory() as tmp:
    project=Path(tmp); (project/".ai").mkdir(); (project/"notes.md").write_text("x",encoding="utf-8")
    (project/".ai/project.json").write_text(json.dumps({"schema_version":1,"status":"placeholder"}),encoding="utf-8")
    template=(ROOT/"templates/PROJECT_STATE.md").read_text(encoding="utf-8")
    route=lambda: json.loads(subprocess.check_output([sys.executable,str(ROOT/"scripts/route_task.py"),"--project",str(project),"fix the bug"],text=True))
    (project/".ai/PROJECT_STATE.md").write_text(template,encoding="utf-8")
    assert "existing-project-onboarding" in route()["workflow"]["state_actions"]
    (project/".ai/PROJECT_STATE.md").write_text("# PROJECT_STATE\n\n- Project name: Real project\n",encoding="utf-8")
    assert "existing-project-onboarding" not in route()["workflow"]["state_actions"]

data=json.loads(subprocess.check_output([sys.executable,str(ROOT/"scripts/route_task.py"),"write a research paper or a policy brief"],text=True))
assert data["needs_clarification"],data

with tempfile.TemporaryDirectory() as tmp:
    project=Path(tmp); (project/".ai").mkdir();
    (project/".ai/project.json").write_text(json.dumps({"schema_version":1,"status":"configured","name":"Fixture","objective":"Test compact context"}),encoding="utf-8")
    (project/".ai/state.json").write_text(json.dumps({"schema_version":1,"status":"configured","active_task":"route test","next_actions":[]}),encoding="utf-8")
    out=subprocess.check_output([sys.executable,str(ROOT/"scripts/context.py"),"fix the website login bug","--project",str(project)],text=True)
    bundle=json.loads(out); assert bundle["routing"]["domain"]=="software"; assert bundle["schema_version"]==2; assert bundle["metrics"]["bytes"]<=12000; assert len(bundle["sources"])==2
    out=subprocess.check_output([sys.executable,str(ROOT/"scripts/context.py"),"สร้างสไลด์สำหรับสอน machine learning","--project",str(project)],text=True)
    bundle=json.loads(out); assert bundle["primary"]["prompt"]=="prompts/05_SLIDES_TEACHING.md"; assert any(item["id"]=="presentation-production" and item["prompt"]=="prompts/23_PRESENTATION_PRODUCTION.md" for item in bundle["secondary"])
    out=subprocess.check_output([sys.executable,str(ROOT/"scripts/context.py"),"build หนังสือเป็น EPUB และ PDF","--project",str(project)],text=True)
    bundle=json.loads(out); assert bundle["primary"]["prompt"]=="prompts/22_BOOK_WRITING.md"; assert any(item["id"]=="publication-production" and item["prompt"]=="prompts/10_DOCUMENT_PRODUCTION.md" for item in bundle["secondary"])
    out=subprocess.check_output([sys.executable,str(ROOT/"scripts/context.py"),"วิเคราะห์ข้อมูลผลสอบและทำกราฟ","--project",str(project)],text=True)
    bundle=json.loads(out); assert bundle["primary"]["id"]=="data-analytics",bundle
    out=subprocess.check_output([sys.executable,str(ROOT/"scripts/context.py"),"conduct thematic content analysis of interviews","--project",str(project)],text=True)
    bundle=json.loads(out); assert bundle["primary"]["id"]=="content-analysis",bundle

with tempfile.TemporaryDirectory() as tmp:
    project=Path(tmp); (project/".ai").mkdir()
    (project/".ai/project.json").write_text(json.dumps({"schema_version":1,"status":"configured","objective":"OLD objective"}),encoding="utf-8")
    (project/".ai/state.json").write_text(json.dumps({"schema_version":1,"status":"configured","active_task":"OLD task"}),encoding="utf-8")
    (project/".ai/PROJECT_STATE.md").write_text("# State\n\nNEW authoritative objective\n"+("ภาษาไทย"*3000),encoding="utf-8")
    result=subprocess.run([sys.executable,str(ROOT/"scripts/context.py"),"fix the website login bug","--project",str(project),"--max-bytes","12000"],capture_output=True)
    assert result.returncode==0,result.stderr.decode()
    assert len(result.stdout)<=12000,len(result.stdout)
    bundle=json.loads(result.stdout)
    assert bundle["metrics"]["bytes"]==len(result.stdout),bundle["metrics"]
    assert "NEW authoritative objective" in bundle["project_context"]
    assert "OLD task" not in bundle["project_context"]
    assert str(project/".ai/PROJECT_STATE.md") in bundle["sources"]

with tempfile.TemporaryDirectory() as tmp:
    project=Path(tmp); (project/"existing.txt").write_text("existing\n",encoding="utf-8")
    data=json.loads(subprocess.check_output([sys.executable,str(ROOT/"scripts/route_task.py"),"install a missing document library","--project",str(project)],text=True))
    assert "existing-project-onboarding" in data["workflow"]["state_actions"],data
    assert "machine-discovery" in data["workflow"]["state_actions"],data
print("v7 structured context tests: PASS")
