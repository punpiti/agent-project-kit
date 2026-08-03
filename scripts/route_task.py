#!/usr/bin/env python3
"""Deterministically classify a request into structured Agent Project Kit axes."""
from __future__ import annotations
import argparse, json, re

RULES = {
 "domain": {
  "software":["code","bug","debug","api","website","web app","script","software","automation","configuration","router","prompt","โปรแกรม","โค้ด","เว็บ","ระบบอัตโนมัติ"],
  "research":["research","paper","manuscript","thesis","literature","experiment","วิจัย","บทความ","วิทยานิพนธ์","หลักฐาน"],
  "education":["course","lesson","syllabus","student","teaching","rubric","curriculum","workshop","seminar","หลักสูตร","บทเรียน","รายวิชา","เอกสารคำสอน","สอน","สัมมนา","แบบฝึก","กิจกรรมการเรียน"],
  "governance":["policy","governance","council","regulation","standard","master plan","institutional transformation","ipst","ioi","นโยบาย","สภา","ข้อบังคับ","สสวท","มาตรฐาน","แผนแม่บท"],
  "operations":["deadline","submit","submission","compliance","dossier","correspondence","coordination","follow up","nomination","application","academic promotion","academic-rank","KU forms","meeting follow-up","กำหนดส่ง","ยื่น","เอกสารราชการ","ติดตาม","ประสานงาน","เสนอชื่อ","สมัคร","แฟ้ม","ตำแหน่งวิชาการ","ศาสตราจารย์"]},
 "deliverable": {
  "code":["code","implement","fix","debug","refactor","build app","โค้ด","แก้บั๊ก","รีแฟกเตอร์","พัฒนาโปรแกรม"],
  "analysis":["analysis","analyze","finding","วิเคราะห์","ผลวิเคราะห์"],
  "paper":["paper","manuscript","thesis","reviewer","บทความ","วิทยานิพนธ์","ผู้ทรงคุณวุฒิ"],
  "policy":["policy","regulation","proposal to council","master plan","นโยบาย","ข้อบังคับ","เสนอสภา","แผนแม่บท"],
  "presentation":["slide","slides","presentation","deck","talk","seminar","briefing","สไลด์","นำเสนอ","บรรยาย","สัมมนา"],
  "course-material":["course","lesson","syllabus","exercise","rubric","course material","teaching document","workshop","บทเรียน","ประมวลรายวิชา","รายวิชา","แบบฝึก","เอกสารสอน","เอกสารคำสอน","กิจกรรม"],
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
            score += bool(re.search(rf"(?<![a-z0-9_]){re.escape(needle)}(?![a-z0-9_])", folded))
        else:
            score += needle in folded
    return score

def best(text: str, group: str, default: str) -> tuple[str,float]:
    scores={key:matches(text,terms) for key,terms in RULES[group].items()}; top=max(scores,key=scores.get)
    if scores[top]==0: return default,0.25
    ordered=sorted(scores.values(),reverse=True); confidence=0.9 if len(ordered)<2 or ordered[0]>ordered[1] else 0.6
    return top,confidence

def contains_any(text: str, phrases: list[str]) -> bool:
    return any(matches(text,[phrase]) for phrase in phrases)

def classify(request: str) -> dict:
    domain,dc=best(request,"domain","general"); deliverable,oc=best(request,"deliverable","analysis")
    strong_domains=[
      ("software",["fix the","implement","refactor","software project","software package","task router","แก้บั๊ก","พัฒนาซอฟต์แวร์"]),
      ("education",["prepare the lesson","prepare the course","teaching document","course workspace","seminar","เตรียมการสอน","เอกสารคำสอน","พัฒนาการสอน","สัมมนา"]),
      ("operations",["compliance tracking","organize and preserve correspondence","nomination dossier","academic promotion","academic-rank","KU forms","check the deadline","ติดตามกำหนด","แฟ้มเสนอชื่อ","ตำแหน่งวิชาการ","ศาสตราจารย์"]),
      ("governance",["policy proposal","master plan","university council","institutional transformation","IOI / POSN","แผนแม่บท","เสนอสภา"])]
    for candidate,hints in strong_domains:
        if contains_any(request,hints): domain,dc=candidate,0.95; break
    # Strong output phrases outrank subject-matter mentions. Merely mentioning a
    # thesis, policy, test, or document does not select that output by itself.
    strong_outputs=[
      ("presentation",["prepare a presentation","create slides","slide deck","slide decks","presentation","seminar","สไลด์","เตรียมนำเสนอ","การบรรยาย","สัมมนา"]),
      ("course-material",["prepare the lesson","prepare the course","teaching document","course material","workshop activity","เตรียมการสอน","เอกสารคำสอน","แบบฝึก"]),
      ("code",["implement","fix the","debug","refactor","code change","task router","แก้บั๊ก","รีแฟกเตอร์","พัฒนาซอฟต์แวร์"]),
      ("document",["prepare the document","submission document","selection documents","nomination dossier","correspondence","formal letter","จัดทำเอกสาร","แฟ้มเสนอชื่อ","จดหมาย"]),
      ("paper",["write the paper","review the paper","revise the paper","review the manuscript","revise the manuscript","reviewer concerns","เขียนบทความ","แก้บทความ","ตรวจวิทยานิพนธ์"]),
      ("policy",["policy proposal","master plan","draft policy","แผนแม่บท","ร่างนโยบาย","เสนอสภา"]),
      ("decision",["assess how to","advise","supervise","recommend a direction","evidence set","academic-rank route","ประเมินแนวทาง","วางแนวทาง","ให้คำแนะนำ"])]
    strong_output=False
    for candidate,hints in strong_outputs:
        if contains_any(request,hints): deliverable,oc,strong_output=candidate,0.95,True; break
    if not strong_output:
        preferred={"software":"code","research":"paper","education":"course-material","governance":"policy","operations":"document"}.get(domain)
        if preferred and matches(request,RULES["deliverable"][preferred]): deliverable,oc=preferred,0.8
    methods=[key for key,terms in RULES["method"].items() if matches(request,terms)]
    lifecycle,lc=best(request,"lifecycle","create")
    workflows=[]
    if deliverable=="code": workflows.append("implementation")
    if deliverable=="paper" and any(x in request.lower() for x in ("reviewer","review","ผู้ทรง")): workflows.append("reviewer-response")
    if deliverable=="document": workflows.append("document-production")
    if "web-development" in methods: workflows.append("web")
    if "strategy-advisory" in methods: workflows.append("strategy")
    if lifecycle=="resume": workflows.append("resume")
    return {"request":request,"domain":domain,"deliverable":deliverable,"methods":methods,"lifecycle":lifecycle,"secondary_workflows":workflows[:2],"confidence":round(min(dc,oc,lc),2),"needs_clarification":oc<0.5}

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("request",nargs="+"); p.add_argument("--pretty",action="store_true"); a=p.parse_args()
    print(json.dumps(classify(" ".join(a.request)),ensure_ascii=False,indent=2 if a.pretty else None)); return 0
if __name__=="__main__": raise SystemExit(main())
