#!/usr/bin/env python3
"""Deterministically classify a request into structured Agent Project Kit axes."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = json.loads((ROOT / "config" / "workflow-registry.json").read_text(encoding="utf-8"))

RULES = {
 "domain": {
  "software":["code","bug","debug","api","website","web app","script","software","automation","configuration","router","prompt","ci","github actions","json schema","installer","powershell","wrapper","โปรแกรม","โค้ด","เว็บ","ระบบอัตโนมัติ"],
  "research":["research","paper","manuscript","thesis","literature","experiment","วิจัย","บทความ","วิทยานิพนธ์","หลักฐาน"],
  "book-writing":["book","textbook","book writing","write a book","write the book","ตำรา","เขียนหนังสือ","เขียนตำรา","ต้นฉบับหนังสือ","ต้นฉบับตำรา"],
  "education":["course","lesson","syllabus","student","teaching","rubric","curriculum","workshop","seminar","หลักสูตร","บทเรียน","รายวิชา","เอกสารคำสอน","สอน","สัมมนา","แบบฝึก","กิจกรรมการเรียน"],
  "governance":["policy","governance","council","regulation","standard","master plan","institutional transformation","ipst","ioi","นโยบาย","สภามหาวิทยาลัย","ข้อบังคับ","สสวท","มาตรฐาน","แผนแม่บท"],
  "operations":["deadline","submit","submission","compliance","dossier","correspondence","coordination","follow up","nomination","application","academic promotion","academic-rank","KU forms","meeting follow-up","กำหนดส่ง","ยื่น","เอกสารราชการ","ติดตาม","ประสานงาน","เสนอชื่อ","ใบสมัคร","สมัครงาน","สมัครเรียน","แฟ้ม","ตำแหน่งวิชาการ","ศาสตราจารย์"]},
 "deliverable": {
  "code":["code","implement","fix","debug","refactor","build app","โค้ด","แก้บั๊ก","รีแฟกเตอร์","พัฒนาโปรแกรม"],
  "analysis":["analysis","analyze","finding","วิเคราะห์","ผลวิเคราะห์"],
  "paper":["paper","manuscript","thesis","reviewer","บทความ","วิทยานิพนธ์","ผู้ทรงคุณวุฒิ"],
  "book":["book","textbook","book writing","write a book","write the book","ตำรา","เขียนหนังสือ","เขียนตำรา","ต้นฉบับหนังสือ","ต้นฉบับตำรา"],
  "policy":["policy","regulation","proposal to council","master plan","นโยบาย","ข้อบังคับ","เสนอสภา","แผนแม่บท"],
  "presentation":["slide","slides","presentation","deck","talk","seminar","briefing","สไลด์","นำเสนอ","บรรยาย","สัมมนา"],
  "course-material":["course","lesson","syllabus","exercise","rubric","course material","teaching document","workshop","บทเรียน","ประมวลรายวิชา","รายวิชา","แบบฝึก","เอกสารสอน","เอกสารคำสอน","กิจกรรมการเรียน"],
  "document":["document","documents","form","forms","letter","report","dossier","correspondence","nomination","เอกสาร","แบบฟอร์ม","หนังสือ","รายงาน","จดหมาย","แฟ้ม","เสนอชื่อ"],
  "decision":["recommend","strategy","choose","decision","แนะนำ","กลยุทธ์","ตัดสินใจ","เลือก"]},
 "method": {
  "content-analysis":["content analysis","codebook","corpus","thematic","วิเคราะห์เนื้อหา","กรอบรหัส"],
  "data-analytics":["data","metric","dashboard","statistics","chart","ข้อมูล","ตัวชี้วัด","สถิติ","กราฟ"],
  "web-development":["website","web app","frontend","backend","responsive","accessibility","เว็บไซต์","เว็บแอป"],
  "research-synthesis":["literature","evidence synthesis","sources","review papers","ทบทวนวรรณกรรม","สังเคราะห์หลักฐาน"],
  "strategy-advisory":["strategy","options","recommend","recommendation","recommendations","advise","advisory","กลยุทธ์","ทางเลือก","คำแนะนำ"]},
 "lifecycle": {
  "bootstrap":["bootstrap","new project","เริ่มโปรเจกต์","ตั้งโปรเจกต์"],
  "resume":["resume","status","ค้างตรงไหน","ทำต่อ","สถานะ"],
  "review":["review","critique","audit","ตรวจ","วิจารณ์","ประเมิน"],
  "publish":["publish","release","submit","deploy","เผยแพร่","ส่งงาน","ขึ้นระบบ"],
  "monitor":["monitor","track","watch","ติดตาม","เฝ้าดู"],
  "implement":["implement","code","fix","refactor","build","แก้บั๊ก","รีแฟกเตอร์","พัฒนาซอฟต์แวร์"]}}

def matches(text: str, terms: list[str]) -> int:
    folded=text.casefold()
    score=0
    for term in terms:
        needle=term.casefold()
        if needle.isascii():
            # A dot followed by a word character continues a token, so the file
            # name "project.json" does not match the phrase "new project".
            score += bool(re.search(rf"(?<![a-z0-9_.]){re.escape(needle)}(?![a-z0-9_]|\.[a-z0-9])", folded))
        else:
            score += needle in folded
    return score

def best(text: str, group: str, default: str) -> tuple[str,float]:
    scores={key:matches(text,terms) for key,terms in RULES[group].items()}; top=max(scores,key=scores.get)
    if scores[top]==0: return default,0.25
    ordered=sorted(scores.values(),reverse=True); confidence=0.9 if len(ordered)<2 or ordered[0]>ordered[1] else 0.6
    return top,confidence

SOURCE_FILE=re.compile(r"(?<![\w.])[\w-]+\.(?:py|sh|ps1|js|ts)(?![\w.])", re.IGNORECASE)

def contains_any(text: str, phrases: list[str]) -> bool:
    return any(matches(text,[phrase]) for phrase in phrases)


def select_primary(domain: str, deliverable: str, methods: list[str]) -> tuple[str, list[dict]]:
    scored = []
    for pipeline_id, item in REGISTRY["primary_pipelines"].items():
        selectors = item["selectors"]
        score = 0
        reasons = []
        matching_methods = sorted(set(methods) & set(selectors["methods"]))
        specialist_ready = not selectors.get("requires_method") or bool(matching_methods)
        if specialist_ready and deliverable in selectors["deliverables"]:
            score += 100
            reasons.append(f"deliverable:{deliverable}")
        if matching_methods:
            score += 80
            reasons.extend(f"method:{method}" for method in matching_methods)
        if domain in selectors["domains"]:
            score += 40
            reasons.append(f"domain:{domain}")
        if pipeline_id == "general":
            score += 1
            reasons.append("fallback")
        scored.append({"id": pipeline_id, "score": score, "reasons": reasons})
    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[0]["id"], scored


def bounded(items: list[str], limit: int, category: str) -> tuple[list[str], list[dict]]:
    unique = list(dict.fromkeys(items))
    selected = unique[:limit]
    omitted = [
        {"id": item, "category": category, "reason": f"{category} limit {limit} reached"}
        for item in unique[limit:]
    ]
    return selected, omitted

def classify(request: str, project: Path | None = None) -> dict:
    domain,dc=best(request,"domain","general"); deliverable,oc=best(request,"deliverable","analysis")
    strong_domains=[
      ("software",["fix the","implement","refactor","software project","software package","task router","แก้บั๊ก","พัฒนาซอฟต์แวร์"]),
      ("operations",["compliance tracking","organize and preserve correspondence","nomination dossier","academic promotion","academic-rank","KU forms","check the deadline","official letter","ติดตามกำหนด","แฟ้มเสนอชื่อ","หนังสือราชการ","หนังสือภายนอก","หนังสือภายใน","ตำแหน่งวิชาการ","ศาสตราจารย์"]),
      ("research",["write the paper","write a paper","revise the paper","research manuscript","เขียนบทความ","แก้บทความ"]),
      ("education",["prepare the lesson","prepare the course","teaching document","course workspace","seminar","เตรียมการสอน","เอกสารคำสอน","พัฒนาการสอน","สัมมนา"]),
      ("book-writing",["write a book","write the book","book writing","textbook","build the book","export the book","เขียนหนังสือ","เขียนตำรา","ต้นฉบับหนังสือ","ต้นฉบับตำรา","build หนังสือ","export หนังสือ","จัดรูปเล่มหนังสือ","ผลิตหนังสือ"]),
      ("governance",["policy proposal","master plan","university council","institutional transformation","IOI / POSN","แผนแม่บท","เสนอสภา"])]
    for candidate,hints in strong_domains:
        if contains_any(request,hints): domain,dc=candidate,0.95; break
    package_release=contains_any(request,[
      "package release","release the package","release the kit","bump version",
      "create a release","tag and release","publish the package","ออก release",
      "ออกเวอร์ชัน","เพิ่มเวอร์ชัน","สร้าง tag","ปล่อยเวอร์ชัน"])
    if domain=="general" and (package_release or SOURCE_FILE.search(request)):
        domain,dc="software",0.8
    # Strong output phrases outrank subject-matter mentions. Merely mentioning a
    # thesis, policy, test, or document does not select that output by itself.
    strong_outputs=[
      ("code",["implement","fix the","debug","refactor","code change","task router","แก้บั๊ก","รีแฟกเตอร์","พัฒนาซอฟต์แวร์"]),
      ("document",["prepare the document","submission document","selection documents","nomination dossier","correspondence","formal letter","official letter","จัดทำเอกสาร","แฟ้มเสนอชื่อ","หนังสือราชการ","หนังสือภายนอก","หนังสือภายใน","จดหมาย"]),
      ("presentation",["prepare a presentation","create slides","slide deck","slide decks","create a deck","สไลด์","เตรียมนำเสนอ","การบรรยาย"]),
      ("paper",["write the paper","write a paper","review the paper","revise the paper","review the manuscript","revise the manuscript","reviewer concerns","เขียนบทความ","แก้บทความ","ตรวจวิทยานิพนธ์"]),
      ("book",["write a book","write the book","book writing","textbook","build the book","export the book","เขียนหนังสือ","เขียนตำรา","ต้นฉบับหนังสือ","ต้นฉบับตำรา","build หนังสือ","export หนังสือ","จัดรูปเล่มหนังสือ","ผลิตหนังสือ"]),
      ("policy",["policy proposal","master plan","draft policy","แผนแม่บท","ร่างนโยบาย","เสนอสภา"]),
      ("course-material",["prepare the lesson","prepare the course","teaching document","course material","workshop activity","เตรียมการสอน","เอกสารคำสอน","แบบฝึก"]),
      ("decision",["assess how to","advise","supervise","recommend a direction","evidence set","academic-rank route","ประเมินแนวทาง","วางแนวทาง","ให้คำแนะนำ"])]
    strong_output=False
    for candidate,hints in strong_outputs:
        if contains_any(request,hints): deliverable,oc,strong_output=candidate,0.95,True; break
    if not strong_output:
        preferred={"software":"code","research":"paper","book-writing":"book","education":"course-material","governance":"policy","operations":"document"}.get(domain)
        if preferred and matches(request,RULES["deliverable"][preferred]): deliverable,oc=preferred,0.8
        # Engineering work in a software domain produces code unless the
        # request names some other output.
        elif domain=="software" and oc<0.5: deliverable,oc="code",0.8
    methods=[key for key,terms in RULES["method"].items() if matches(request,terms)]
    # In software work "data" usually means configuration or fixtures.
    bare_data=[] if domain=="software" else ["data"]
    if "data-analytics" in methods and not contains_any(request,bare_data+[
        "data analysis","analyze data","analyse data","dataset","metric","dashboard",
        "statistics","statistical","chart","วิเคราะห์ข้อมูล","ข้อมูลสถิติ","ชุดข้อมูล",
        "ฐานข้อมูล","ตัวชี้วัด","สถิติ","กราฟ"]):
        methods.remove("data-analytics")
    lifecycle,lc=best(request,"lifecycle","create")
    primary_pipeline, primary_scores = select_primary(domain, deliverable, methods)
    method_candidates=[]
    method_map={
      "web-development":"web",
      "strategy-advisory":"strategy",
      "data-analytics":"data-analytics",
      "content-analysis":"content-analysis",
      "research-synthesis":"research-synthesis"}
    for method in methods:
        module_id=method_map.get(method)
        if module_id and module_id != primary_pipeline:
            method_candidates.append(module_id)
    method_modules,omitted=bounded(
      method_candidates,REGISTRY["composition"]["method_max"],"method")
    stages=[]
    if deliverable=="code": stages.append("implementation")
    if deliverable=="paper" and contains_any(request,["reviewer","review the","peer review","ผู้ทรง"]): stages.append("reviewer-response")
    publication_production=contains_any(request,[
      "typeset","typesetting","build pdf","generate pdf","create pdf","export pdf",
      "final pdf","build docx","generate docx","export docx","build epub",
      "generate epub","export epub","html publication","page layout","final layout",
      "convert to pdf","convert to docx","convert to epub","จัดรูปเล่ม","สร้าง pdf",
      "สร้าง docx","สร้าง epub","ส่งออก pdf","ส่งออก docx","ส่งออก epub","เป็น epub","เป็น pdf","ตรวจไฟล์ final"])
    publication_production = publication_production or (
      contains_any(request,["build","generate","export","convert","typeset","render","สร้าง","ส่งออก","แปลง","จัดรูปเล่ม"])
      and contains_any(request,["pdf","docx","word file","epub","html publication","print-ready","ไฟล์พิมพ์"])
    )
    presentation_production=contains_any(request,[
      "create slides","build slides","make slides","create a deck","build a deck",
      "make a deck","edit pptx","create pptx","build pptx","export pptx",
      "render slides","render deck","export slides","export deck","final deck",
      "google slides file","keynote file","html deck","สร้างสไลด์","ทำสไลด์",
      "สร้าง pptx","แก้ pptx","ส่งออกสไลด์","เรนเดอร์สไลด์","ตรวจไฟล์สไลด์"])
    if publication_production and deliverable != "presentation":
        stages.append("publication-production")
    if deliverable == "presentation" and presentation_production:
        stages.append("presentation-production")
    if contains_any(request,[
      "user feedback","student feedback","stakeholder feedback","reviewer feedback",
      "survey feedback","external feedback","ผลตอบรับ","ข้อเสนอแนะจากผู้ใช้",
      "เสียงสะท้อน","ความคิดเห็นของนักเรียน","ความคิดเห็นของผู้มีส่วนได้ส่วนเสีย"]):
        stages.append("external-feedback")
    markdown_cleanup=contains_any(request,[
      "markdown cleanup","clean up markdown","migrate markdown","markdown inventory",
      "recover markdown","จัดระเบียบ markdown","ย้ายไฟล์ markdown","กู้ markdown"])
    markdown_cleanup = markdown_cleanup or (
      contains_any(request,["markdown"])
      and contains_any(request,["clean up","cleanup","migrate","inventory","recover","จัดระเบียบ","ย้าย","กู้"]))
    if markdown_cleanup:
        stages.append("markdown-cleanup")
    if package_release:
        # Integrity and privacy gates must survive the stage limit.
        stages.insert(0,"package-release")
    lifecycle_stages,stage_omitted=bounded(
      stages,REGISTRY["composition"]["stage_max"],"stage")
    omitted.extend(stage_omitted)
    prose_writing=contains_any(request,[
      "write","draft","revise","rewrite","edit the prose","polish","proofread","wording",
      "prose","writing style","เขียน","ร่าง","แก้ภาษา","เกลา","ร้อยแก้ว","ปรับภาษา","สำนวน"])
    gates=[]
    if deliverable in {"paper","book","document","course-material","policy"} and prose_writing:
        gates.append("prose-style")
    if package_release or contains_any(request,[
      "secret","secrets","credential","credentials","api key","private path",
      "leak","ความลับ","รหัสผ่าน","ข้อมูลลับ"]):
        gates.append("release-boundary")
    state_actions=[]
    if lifecycle=="resume": state_actions.append("resume")
    if project is not None:
        ai_dir=project/".ai"; project_file=ai_dir/"project.json"
        try: project_data=json.loads(project_file.read_text(encoding="utf-8"))
        except (OSError,json.JSONDecodeError): project_data=None
        visible_entries=any(item.name != ".ai" for item in project.iterdir()) if project.exists() else False
        if not project_data or project_data.get("status")=="placeholder":
            state_actions.append("existing-project-onboarding" if visible_entries else "new-project-bootstrap")
        machine_needed=contains_any(request,[
          "dependency","library","package","environment","gpu","cuda","ocr","build pdf",
          "build docx","render","ติดตั้ง","ไลบรารี","แพ็กเกจ","สภาพแวดล้อม"])
        if machine_needed and not (ai_dir/"MACHINE_PROFILE.md").exists():
            state_actions.append("machine-discovery")
        if publication_production and deliverable in {"paper","book","document","course-material","policy"} and not (ai_dir/"DOCUMENT_STYLE.md").exists():
            state_actions.append("document-style-bootstrap")
    elif lifecycle=="bootstrap": state_actions.append("new-project-bootstrap")
    state_actions=list(dict.fromkeys(state_actions))
    compatibility=list(dict.fromkeys(lifecycle_stages+method_modules+gates+state_actions))
    return {
      "schema_version":2,
      "request":request,
      "domain":domain,
      "deliverable":deliverable,
      "methods":methods,
      "lifecycle":lifecycle,
      "primary_pipeline":primary_pipeline,
      "workflow":{
        "primary":primary_pipeline,
        "methods":method_modules,
        "stages":lifecycle_stages,
        "gates":gates,
        "state_actions":state_actions},
      "secondary_workflows":compatibility,
      "omitted":omitted,
      "selection_trace":{"primary_candidates":primary_scores},
      "confidence":round(min(dc if domain!="general" else 0.7,oc,0.6 if len(primary_scores)>1 and primary_scores[0]["score"]==primary_scores[1]["score"] else 0.9),2),
      "needs_clarification":oc<0.5 or (len(primary_scores)>1 and primary_scores[0]["score"]==primary_scores[1]["score"] and primary_scores[0]["score"]>1) or (contains_any(request,["or","either","หรือ"]) and sum(bool(matches(request,terms)) for terms in RULES["deliverable"].values())>1)}

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("request",nargs="+"); p.add_argument("--pretty",action="store_true"); p.add_argument("--project"); a=p.parse_args()
    project=Path(a.project).resolve() if a.project else None
    print(json.dumps(classify(" ".join(a.request),project),ensure_ascii=False,indent=2 if a.pretty else None)); return 0
if __name__=="__main__": raise SystemExit(main())
