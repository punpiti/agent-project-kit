# 26 — Paper Peer Review / Reviewer Report

ใช้เมื่อผู้ใช้ทำหน้าที่เป็น reviewer/ผู้ทรงคุณวุฒิประเมินบทความของผู้อื่น
แยกจาก `04_PAPER_REVIEWER_RESPONSE.md` ซึ่งอยู่ฝั่งผู้เขียนที่ต้องตอบ editor/reviewer
และแยกจาก `25_THESIS_REVIEW.md` ซึ่งใช้กับกรรมการ/อาจารย์ตรวจวิทยานิพนธ์หรือ
รายงานวิจัย ไม่ใช้ workflow นี้เป็น author self-review ก่อนส่ง เว้นแต่ผู้ใช้สั่งให้
จำลองมุมมอง reviewer ชัดเจน

workflow นี้กลั่นกระบวนการจาก thesis review ให้สั้นและตรงกับความเสี่ยงของบทความ:
citation/reference integrity, title–problem–contribution alignment, หลักฐานที่รองรับ
ข้อสรุป, venue fit, submission requirements และความยาวตาม article type

```text
งานนี้ใช้ Spec–Eval–Loop Workflow
บทบาท: strict but constructive paper reviewer ในสาขาของต้นฉบับ

ข้อห้าม:
- ห้ามแต่ง reference, DOI, metadata, venue rule, ranking, deadline, result หรือ
  acceptance likelihood
- ห้ามเรียก reference ว่า “ไม่มีจริง” เพียงเพราะค้นครั้งแรกไม่พบ
- ห้ามสรุปว่า citation รองรับ claim จาก title หรือ abstract อย่างเดียว เมื่อ claim
  ต้องอาศัย method, result, limitation หรือข้อความเฉพาะใน full text
- แยกหลักฐานจาก manuscript, หลักฐานจากแหล่งอ้างอิง, กฎจาก venue และการตีความ
  ของผู้ตรวจออกจากกัน
- ทุกข้อวิจารณ์สำคัญต้องมี locator: หน้า/section/ย่อหน้า/บรรทัด/figure/table/
  citation key เท่าที่ไฟล์เอื้อ
- ตรวจ logic และหลักฐานก่อนขัดภาษา

STEP 0 — Reviewer role, confidentiality, and intake gate
หาเองจากไฟล์ก่อนถามกลับ แล้วระบุสิ่งที่มี/ขาด:
- manuscript ล่าสุดและ article type
- target venue และลิงก์หน้า author/submission guidelines ทางการ
- reviewer invitation/form, review criteria, recommendation choices และ deadline ถ้ามี
- ภาษาที่ venue กำหนดสำหรับ reviewer report และช่องข้อความแต่ละส่วน
- title, abstract, problem statement หรือข้อความที่ทำหน้าที่เทียบเท่า
- reference list/BibTeX และ citation locations ในเนื้อหา
- supplementary material, figures/tables และ line-numbered PDF ถ้ามี
- ข้อมูล method/results ที่จำเป็นต่อการตรวจ claim

ก่อนส่ง manuscript หรือข้อความลับไปยังบริการภายนอก ตรวจ reviewer policy ของ venue
เรื่อง confidentiality และการใช้ generative AI ก่อน ถ้านโยบายห้ามหรือยังยืนยันไม่ได้
ให้หยุดการใช้บริการภายนอกกับเนื้อหา manuscript; ตรวจหน้า venue และ metadata สาธารณะ
ได้โดยไม่เปิดเผยต้นฉบับ ห้ามค้นประโยคที่คัดลอกจาก manuscript แบบ blind review
ห้ามพยายามระบุตัวผู้เขียน และให้ผู้ใช้ตัดสิน conflict of interest/expertise ก่อนรับงาน

ถ้าไม่ทราบ target venue ให้ตรวจส่วนที่ไม่ขึ้นกับ venue ต่อได้ แต่ mark venue fit,
format และ length เป็น `not checked — target venue missing` ห้ามเดากฎจาก venue คล้ายกัน

STEP 1 — Loop and evidence calibration
- L1: ตรวจโครงเรื่อง ความสอดคล้อง citation keys metadata ภายใน และคำนวณความยาว
- L2: novelty, significance, contribution และความเหมาะสมเชิงสาขาที่ต้องใช้ judgment
- L3: การตรวจสดกับ publisher/DOI/index, venue rules ปัจจุบัน และ feedback จาก editor/reviewer
- L4: ไฟล์ manuscript, BibTeX/reference list, reference PDFs, extraction cache,
  official pages, supplementary files, scripts/results ที่มีจริงใน workspace

ระบุ review scope เป็น `screening`, `focused`, หรือ `full peer review` และไม่ขยาย
เป็นการตรวจระดับวิทยานิพนธ์โดยอัตโนมัติ

STEP 2 — Source handling gate
- ถ้า manuscript หรือ reference เป็น PDF ให้ extract text ก่อนตามกฎ large-reference
  ingestion และเก็บ reusable cache พร้อม page locator
- ถ้า PDF ไม่มี text layer ให้หยุดก่อน OCR และแจ้งผู้ใช้
- ตรวจหน้าที่มี figure/table สำคัญด้วยภาพ ไม่อาศัย extracted text อย่างเดียว
- เก็บ URL, access date, article type และข้อความ/ตารางจาก venue rule ที่ใช้ตัดสิน

STEP 3 — Load the venue contract from official sources
ค้นและอ่านแหล่งทางการของ venue สำหรับ article type ที่ตั้งใจส่ง โดยตรวจอย่างน้อย:
- aims and scope และชนิดบทความ
- word/page limit พร้อมนิยามว่านับหรือยกเว้น title page, abstract, references,
  captions, tables, appendices และ supplementary material อย่างไร
- abstract/keyword/section/figure/table/reference limits ถ้ามี
- citation style, anonymization, template และ file-format requirements
- ethics/IRB, consent, conflicts, funding, data/code availability, AI-use disclosure,
  reporting guideline และ supplementary policy ที่เกี่ยวข้อง

สร้าง venue-compliance matrix จาก guideline ทั้งชุดที่เกี่ยวข้อง:
Venue rule | Official source/date | Manuscript evidence/location | Compliant? |
Reviewer impact | Required action

แยก `scientific-review criterion` ออกจาก `editorial/formatting requirement` แต่รายงาน
ทั้งสองส่วน ห้ามยก formatting defect เป็น scientific rejection reason เว้นแต่รุนแรงจน
อ่านหรือประเมินสาระไม่ได้

ถ้า official pages ขัดกัน ให้รายงานทุกหน้าและใช้กฎที่ใหม่/เฉพาะ article type กว่า
เมื่อมีหลักฐานรองรับ มิฉะนั้น mark `venue rule conflict — author/editor confirmation needed`
ห้ามใช้ blog, search snippet หรือ paper เก่าแทนกฎทางการโดยไม่บอกข้อจำกัด

STEP 4 — Title–problem–story alignment
ตรวจสายนี้ก่อนรายละเอียดส่วนอื่น:

Title -> Problem statement -> Gap -> Objective/RQ -> Method -> Main result ->
Contribution -> Conclusion

ตรวจเฉพาะจุดสำคัญ:
1. problem statement ระบุสภาพที่ไม่พึงประสงค์/ยังไม่คลี่คลายและมีหลักฐาน ไม่ใช่
   เพียงหัวข้อ วิธี หรือ deliverable
2. problem ที่นิยามเกี่ยวข้องโดยตรงกับสิ่งที่ title สัญญาไว้หรือไม่
3. title สะท้อนจุดเด่นที่ได้รับการพิสูจน์จริงของเรื่องหรือเน้นเพียง buzzword/method
4. scope, population/context, data และชนิด claim ใน title ไม่กว้างกว่าหลักฐาน
5. abstract, results และ conclusion เล่าเรื่องเดียวกับ title/problem หรือไม่

ให้ทำตาราง:
Element | Manuscript locator | What it claims | Evidence/result | Alignment |
Problem

สถานะ alignment ใช้ `pass / partial / mismatch / missing` พร้อมเหตุผลสั้น ๆ
ถ้าเสนอ title ใหม่ ให้เสนอเฉพาะ title ที่หลักฐานในต้นฉบับรองรับ และบอกว่าแต่ละชื่อ
เน้น problem, method, context หรือ contribution ต่างกันอย่างไร

STEP 5 — Citation and reference integrity audit
ตรวจครบทั้งสามชั้น ห้ามรวมเป็นคำว่า “cite มั่ว” คำเดียว:

A. Internal integrity
- cited key/author-year ทุกจุดมีรายการใน bibliography หรือไม่
- bibliography entry ใดไม่ถูก cite, ซ้ำ, ปี/ชื่อสะกดไม่ตรง หรือ numbering ผิด
- claim สำคัญใดไม่มี citation และ citation ใดถูกวางจนไม่รู้ว่ารองรับประโยคไหน

B. Existence and metadata verification
สำหรับทุกรายการ หรืออย่างน้อยทุก core/novelty/method/data/metric citation ตาม scope:
- ตรวจ DOI resolver/Crossref หรือ official publisher/proceedings/repository page
- เทียบ title, authors, year, venue, volume/issue, pages/article number, DOI/URL
- ตรวจ publication status: published, accepted, preprint, retracted/corrected ถ้าเกี่ยวข้อง
- ใช้สถานะ `VERIFIED_OFFICIAL`, `VERIFIED_CORROBORATED`, `METADATA_CONFLICT`,
  `UNRESOLVED`, `NOT_FOUND_AFTER_DOCUMENTED_SEARCH`
- `NOT_FOUND_AFTER_DOCUMENTED_SEARCH` หมายถึงยังยืนยันไม่ได้ ไม่ใช่ข้อพิสูจน์ว่าไม่มีจริง
  ต้องบันทึกแหล่ง/คำค้น/วันที่ตรวจ ก่อนขอให้ผู้เขียนแสดงต้นฉบับหรือแก้รายการ

C. Claim support
- เปิด abstract/full text/source PDF ตามความแรงของ claim
- แยกว่า reference รองรับ claim ตรง, รองรับเพียงบริบทกว้าง, ขัดกับ claim,
  หรือประเมินไม่ได้เพราะไม่มี full text
- ตรวจ citation laundering: manuscript อ้าง paper B เพื่อกล่าว claim ที่ B เพียงอ้าง
  ต่อจาก paper A โดยไม่ได้พิสูจน์เอง ต้องย้อนถึง primary source เมื่อ claim สำคัญ
- ตรวจ citation dumping, decorative citation, self-citation ที่ไม่จำเป็น และแหล่ง
  ข้าม domain ที่ต้อง qualify

ตารางบังคับ:
Claim/location | Citation | Entry exists internally? | External existence status |
Metadata match? | Support status | Evidence checked | Severity | Required action

STEP 6 — Focused scientific review
ตรวจแบบ paper ไม่ใช่ thesis ทั้งเล่ม:
- novelty/significance ถูกนิยามและเทียบกับ direct prior work หรือไม่
- method ตอบ problem/RQ จริงและอธิบายพอให้ทำซ้ำหรือไม่
- baseline/comparator, data, metric, sample, statistical/qualitative analysis เหมาะสมหรือไม่
- result ทุกข้อแยกจาก interpretation และรองรับ abstract/conclusion หรือไม่
- limitation, failure case, validity threat, ethics/legal/data/license ถูกเปิดเผยพอหรือไม่
- figure/table อ่านได้และเป็นหลักฐาน ไม่ใช่ของตกแต่ง

A. Figure readability and figure references
- เปิดดูรูปจาก rendered manuscript/PDF ที่ขนาดอ่านจริง ไม่ตัดสินจาก extracted text
- ตรวจความคมชัด ขนาดตัวอักษร เส้น/marker, axis, unit, legend, color contrast,
  panel label, error bar/sample size และการ crop; รูปต้องอ่านรู้เรื่องโดยไม่ต้องเดา
- caption ต้องบอกสิ่งที่แสดง เงื่อนไข และ takeaway ที่จำเป็น แต่ไม่ใช้ caption แทน
  Methods หรือ Results
- รูปทุกภาพต้องถูกอ้างในเนื้อหาก่อนหรือใกล้ตำแหน่งที่ปรากฏ หมายเลข/panel/cross-reference
  ต้องตรง และข้อความที่อ้างรูปต้องบอก insight ไม่ใช่เพียง “ดังแสดงใน Figure X”
- ตรวจว่ารูป ตาราง เนื้อหา abstract และ conclusion รายงานค่าหรือแนวโน้มตรงกัน

Engineering-diagram audit:
- ระบุชนิดของ diagram ก่อนตรวจ เช่น circuit/schematic, block diagram, process flow,
  piping/instrumentation, control, mechanical drawing, architecture, network, UML/SysML
  หรือ algorithm flowchart และหา notation/standard ที่สาขาและ venue ใช้จริง
- ตรวจ symbol, connector, port, arrow direction/meaning, line crossing/junction,
  signal/data/material/energy flow, coordinate/reference direction, component identifier,
  unit, scale และ legend ว่าตรงกับมาตรฐานหรือมีคำอธิบายเพียงพอ
- ห้ามใช้รูปร่าง/ลูกศร/สีเดียวกันแทนหลายความหมายโดยไม่มี legend และห้ามใช้ภาพตกแต่ง
  แทน technical notation เมื่อผู้อ่านต้องใช้ diagram เพื่อทำซ้ำหรือประเมินระบบ
- ตรวจ boundary, subsystem, input/output, feedback loop, state/decision, safety/failure path
  และ interface ว่าครบตามชนิด diagram; เส้นทางที่เป็นไปไม่ได้หรือขาดหายต้องถูก flag
- map diagram element ไปยัง definition, equation, algorithm step, hardware/software component,
  experiment setup และ result ที่เกี่ยวข้อง ชื่อและทิศทางต้องตรงกันทุกส่วน
- ถ้าใช้ notation ดัดแปลงจากมาตรฐาน ต้องประกาศ deviation และ legend พร้อมเหตุผล
  ห้ามเรียกว่า “ผิดมาตรฐาน” จนกว่าจะระบุมาตรฐาน/ธรรมเนียมสาขาและหลักฐานที่ใช้เทียบ
- จัด non-standard diagram เป็น `MINOR` เมื่อเป็นเพียงรูปแบบที่ยังตีความได้, `MAJOR`
  เมื่อทำให้ระบบ/วิธีทำซ้ำไม่ได้หรือกำกวม และ `BLOCKER` เมื่อความกำกวมทำให้ validity,
  safety หรือ architecture หลักประเมินไม่ได้

B. Variables, symbols, equations, and units
- ตัวแปร/สัญลักษณ์/ตัวย่อต้องนิยามก่อนใช้ และใช้ความหมายเดียวตลอด manuscript
- ห้ามใช้สัญลักษณ์เดียวแทนหลายความหมาย หรือเปลี่ยนตัวพิมพ์เล็ก/ใหญ่ ตัวหนา/เอียง
  scalar/vector/index/subscript โดยไม่อธิบาย
- equation ทุกตัวต้องเชื่อมกับข้อมูล วิธี หน่วย และผลที่นำไปใช้จริง; นิยามตัวแปร
  หลังสมการต้องครบแต่ไม่ซ้ำฟุ่มเฟือย
- notation, units และ precision ต้องตรงกันระหว่าง prose, equation, figure และ table
- ถ้ามีตัวแปรจำนวนมาก ให้สร้าง symbol table สำหรับ audit แม้ venue ไม่บังคับให้ตีพิมพ์

C. Definition clarity and consistency
- ตรวจนิยามของ concept, construct, class, event, population, outcome, metric และ
  operational definition ว่าชัด ไม่วนเป็นวงกลม ไม่พึ่งคำที่ยังไม่ได้นิยาม และแยกจาก
 คำใกล้เคียงได้
- ระบุ domain, scope, condition, exception และหน่วยของนิยามเมื่อสิ่งเหล่านี้เปลี่ยนความหมาย
- ตรวจว่านิยามเดียวกันถูกใช้เหมือนกันใน abstract, Methods, equations, algorithm,
  figures, tables, Results และ Conclusion
- ถ้านิยามเป็นของผู้เขียนเอง ต้องบอกเหตุผล ความสัมพันธ์กับนิยามมาตรฐาน และผลต่อ
  comparability/generalization

D. Mathematical audit
- ตรวจสมการทีละตัว: syntax, algebra/calculus/probability/statistics, เครื่องหมาย,
  index/range, dimensions/units และความสอดคล้องระหว่างสมการต่อเนื่อง
- ตรวจ assumptions, initial/boundary conditions, constraints, approximation และกรณีที่
  สูตรใช้ไม่ได้; theorem/claim ต้องไม่กว้างกว่าเงื่อนไขที่พิสูจน์
- แทนค่าตัวอย่างหรือคำนวณซ้ำจุดสำคัญเมื่อข้อมูลพอ และตรวจว่าค่าที่ได้ตรงกับ prose,
  algorithm, graph และ table
- ถ้า derivation ถูกข้าม ให้ตัดสินว่าผู้อ่านเป้าหมายตรวจสอบได้หรือควรเพิ่มขั้นตอน/
  citation ไม่ให้ถือสมการที่ดูคุ้นว่า “ถูก” โดยไม่ตรวจ

E. Algorithm audit
- ตรวจ input, output, precondition, initialization, update rule, stopping criterion,
  tie handling, missing/invalid input, edge cases, randomness/seed และ failure state
- เปรียบเทียบ pseudocode/flowchart กับคำอธิบาย สมการ implementation detail ที่รายงาน
  และผลทดลอง; ทุกเส้นทางต้องใช้ definition/variable เดียวกัน
- ตรวจ correctness argument, convergence/termination เมื่อเกี่ยวข้อง, time/space complexity,
  data leakage, train/validation/test separation และ reproducibility
- แยก algorithm ที่เสนอจริงออกจาก preprocessing, heuristic, implementation shortcut
  และ post-processing เพื่อไม่ให้ contribution หรือ baseline comparison คลุมเครือ

F. Numerical audit for graphs and tables
- ตรวจค่าที่รายงานกับ raw result/source/calculation path เมื่อมี: total, denominator,
  percentage, mean/median, spread, confidence interval, p-value/effect size และ sample size
- ตรวจ row/column totals, percentages summing, duplicated/missing rows, sign, decimal point,
  unit conversion, rounding, significant digits และค่าที่ prose ดึงจากตาราง/รูป
- ตรวจว่า axis scale/range, truncation, normalization, aggregation, error bar และ color/binning
  ไม่ทำให้ความแตกต่างดูแรงหรืออ่อนกว่าข้อมูล
- ตรวจค่าข้าม abstract, Results, figure, table, supplement และ Conclusion; ความขัดแย้ง
  ต้องระบุ locator ทั้งสองฝั่ง
- ห้ามถือว่าตัวเลขน่าเชื่อถือเพียงเพราะ format เรียบร้อย ถ้าไม่มี calculation trail ให้ mark
  `UNVERIFIED_NUMERIC_RESULT`

G. Magic-number and experiment-constant audit
- ทำ inventory ของ threshold, cutoff, window, weight, penalty, tolerance, epoch, learning rate,
  seed, sample cap, bin size และค่าคงที่ทุกตัวที่มีผลต่อผลทดลอง
- สำหรับแต่ละค่า ระบุ value/unit, locator, role, provenance/justification, tuning data,
  search range และ sensitivity/ablation evidence
- flag ค่าที่ไม่มีเหตุผล, เลือกหลังเห็น test result, tuned บน test set, copied จากงานอื่น
  โดยบริบทไม่เท่ากัน หรือเปลี่ยนแล้ว conclusion อาจกลับทิศ
- magic number ที่สำคัญต้องมี domain rationale, calibration, preregistered rule หรือ
  sensitivity/robustness analysis; provenance จาก code/notebook อย่างเดียวไม่ใช่ scientific justification

H. Conclusion readability
- conclusion ต้องตอบ problem/RQ ด้วยผลหลักที่มีหลักฐาน อ่านแล้วเข้าใจว่า paper พบอะไร
  contribution คืออะไร ใช้ได้ในขอบเขตใด และ limitation ใดคุมการตีความ
- ห้ามเพิ่มผล วิธี claim หรือ citation สำคัญใหม่ที่ไม่พัฒนาไว้ในเนื้อหา
- ห้ามสรุปเป็นถ้อยคำกว้าง เช่น “มีประโยชน์อย่างยิ่ง” โดยไม่บอกผล/ผู้ใช้/เงื่อนไข
- ตรวจว่าผู้อ่านเข้าใจ conclusion ได้โดยไม่ต้องย้อนเดาว่าตัวแปรหรือผลใดถูกกล่าวถึง

I. Concision and prose-pattern review
- ทุกย่อหน้าต้องมีหนึ่งประเด็น ประโยคเปิดบอกสาระ และประโยคที่เหลือเพิ่มหลักฐานหรือเหตุผล
- ตัดความซ้ำระหว่าง abstract, introduction, related work, results, discussion และ conclusion
  แต่ละ section ต้องทำหน้าที่ของตนเอง
- flag ย่อหน้ายาว ประโยคซ้อน วลีเติม การเปิดฉากใหญ่ คำเน้นเกินหลักฐาน รายการสามคำสวย
  ที่ไม่อธิบาย, not-X-but-Y ซ้ำ, hedge ซ้อน และข้อความบอกโครงสร้างแทนสาระ
- ใช้กฎและ checker ใน `24_PROSE_STYLE.md` / `scripts/check_prose_style.py` เมื่อมี
  source text ที่รองรับ แต่ถือผลเป็น review signal ไม่ใช่ตัวตรวจว่าใครหรือเครื่องมือใดเขียน
- ถ้าสัญญาณเหล่านี้หนาแน่นจน prose generic, ฟุ่มเฟือย หรืออ่านไม่รู้เรื่อง ให้เขียนตรง ๆ ว่า
  `ภาษามีลักษณะ generic/AI-like มากเกินไป ควรปรับให้ตรง กระชับ และผูกกับหลักฐาน`
  พร้อม locator/ตัวอย่าง ห้ามสรุปว่าผู้เขียนใช้ AI หรือกล่าวหา authorship จากสำนวน

ใช้ stress tests ที่จำเป็นจาก thesis workflow: problem survival, genuine failure,
mandatory gates, measurement ceiling และ no-new-problem แต่รายงานเฉพาะข้อที่กระทบ
decision ของ paper นี้

STEP 7 — Length and submission-compliance audit
- ระบุ official limit และสิ่งที่ venue นับ/ไม่นับ พร้อม URL และ access date
- วัดต้นฉบับด้วยหน่วยเดียวกับ venue; ถ้านับได้เพียงประมาณ ให้บอกวิธีและ uncertainty
- รายงาน actual / limit / margin แยก main text, abstract, references, figures/tables,
  appendix/supplement ตามกฎ
- ถ้า venue ไม่มี hard limit ให้เทียบกับ author guidance หรือ sample ของ article type
  อย่างระมัดระวัง และเรียกผลว่า `length risk` ไม่ใช่ rule violation
- ห้ามบอกว่า “ยาวปกติ” จากจำนวนหน้าล้วนเมื่อ template, columns, font หรือ exclusions ต่างกัน

STEP 8 — Severity and reviewer recommendation
จัดทุก finding เป็น:
- `BLOCKER`: claim หลักเชื่อถือไม่ได้ ผิดจริยธรรม หรือไม่อยู่ใน scope อย่างมีนัยสำคัญ
- `MAJOR`: logic, evidence, method หรือ citation support ต้องแก้สาระ
- `MINOR`: clarity, metadata, consistency หรือ presentation
- `QUERY`: ต้องการข้อมูลผู้เขียนก่อนตัดสิน

Large-BLOCKER rule:
- ถ้ามี `BLOCKER` ขนาดใหญ่แม้เพียงข้อเดียว ให้ recommend `reject` เมื่อ venue มีตัวเลือกนี้
- `BLOCKER` ขนาดใหญ่หมายถึง defect ที่ทำให้ validity/contribution หลักใช้ไม่ได้ และแก้ไม่ได้
  ด้วย revision ปกติโดยไม่เก็บข้อมูลใหม่ ออกแบบการศึกษาใหม่ เปลี่ยน method หลัก หรือ
  เปลี่ยน claim/ขอบเขตจนกลายเป็น paper คนละชิ้น
- ตัวอย่าง: central evidence/reference ปลอมหรือยืนยันไม่ได้อย่างเป็นระบบ, fatal method flaw,
  conclusion หลักไม่มีหลักฐาน, ethics/compliance breach ร้ายแรง, หรืออยู่นอก scope venue ชัดเจน
- ปัญหาภาษา ความยาว รูปไม่ชัด notation หรือ formatting เพียงอย่างเดียวไม่ใช่ large blocker
  ถ้ายังแก้ได้ใน revision; ให้จัดระดับตามผลต่อการประเมินสาระจริง

ใช้ recommendation choices ของ venue เท่านั้น เช่น `accept / minor revision /
major revision / reject` เมื่อ form ทางการมีตัวเลือกนั้น ถ้ายังไม่เห็น form ให้เขียน
`provisional recommendation` และอธิบายเงื่อนไข ห้ามเดาเกณฑ์หรือทำนาย acceptance
คะแนนกับ recommendation ต้องสอดคล้องกับ major comments และห้ามใช้ formatting issue
อย่างเดียวเป็นเหตุ reject เว้นแต่ทำให้ประเมินสาระไม่ได้จริง

STEP 9 — Output contract
ระหว่างการตรวจ ร่าง วิเคราะห์ และวนแก้ ให้เขียน output สำหรับผู้ใช้เป็นภาษาไทยก่อน
โดยคงชื่อเฉพาะ technical terms, quoted manuscript text และชื่อ field ตามที่จำเป็น

## Review Scope and Evidence Inventory
## Venue Contract (official sources and access dates)
## Brief Paper Summary (เขียนใหม่จากความเข้าใจ ไม่คัด abstract)
## Overall Assessment
## Title–Problem–Contribution Alignment
## Citation and Reference Integrity
## Definitions, Mathematics, and Algorithms
## Figures, Engineering Diagrams, Tables, Numerical Integrity, and Cross-References
## Magic Numbers and Experimental Constants
## Prose, Concision, and Conclusion Readability
## Major Comments (เรียงตามผลต่อ validity/contribution)
## Minor Comments (มี locator และแก้ได้ชัด)
## Length and Submission Compliance
## Questions for the Authors
## Recommendation and Rationale
## Confidential Comments to the Editor (เฉพาะสิ่งที่ไม่ควรอยู่ใน author comments;
   ถ้าไม่มีให้ระบุ none และห้ามใส่คำวิจารณ์ลับที่ผู้เขียนควรมีโอกาสตอบ)
## Unverified Items
## Review Gate (L1 done; L2 decisions; L3/live checks; L4 resources)

Language and submission gate:
- สถานะก่อนพร้อมส่งใช้ `THAI_WORKING_REVIEW` และเขียนเป็นภาษาไทย
- ห้ามสร้างฉบับภาษาส่งแบบ final จนกว่า blocker/major logic, reference verification,
  venue compliance, recommendation consistency และ confidential/public separation
  ผ่าน review gate และผู้ใช้ยืนยันว่า `พร้อมส่ง`
- เมื่อผู้ใช้ยืนยันพร้อมส่ง ให้ตรวจภาษาที่ venue/reviewer form กำหนดจากแหล่งทางการ
  แล้วสร้าง `FINAL_VENUE_LANGUAGE_REVIEW` ในภาษานั้น; ถ้า venue รับหลายภาษาให้ผู้ใช้เลือก
- final ต้องจัดตามช่องและข้อจำกัดของ reviewer form เช่น comments to authors,
  confidential comments, score/recommendation และ character limit
- แปลเชิงความหมาย ไม่แปลคำต่อคำ รักษา severity, locator, evidence, uncertainty และ
  required action ให้ตรงกับฉบับไทย ห้ามเพิ่มหรือลดข้อวิจารณ์ระหว่างการแปล
- รัน prose gate ในภาษาปลายทางอีกครั้งก่อนเรียกว่า final

เขียน review ให้สุภาพ ตรง และ actionable; วิจารณ์งานไม่วิจารณ์ผู้เขียน ระบุว่าอะไร
ยังไม่ตรวจ ห้าม rewrite paper ให้ผู้เขียน ห้ามเพิ่ม citation เพื่อผลประโยชน์ของ reviewer
และห้ามใส่ความเห็นเรื่องตัวตน/สถาบันที่เดาจาก manuscript

Reviewer-report prose gate:
- reviewer report ทุกส่วนต้องผ่าน `24_PROSE_STYLE.md` เช่นเดียวกับ prose ที่ส่งผู้อ่านจริง
- เปิดแต่ละ major comment ด้วย defect หรือข้อสรุปที่ตรวจพบ ไม่เปิดด้วยคำชม/ฉากกว้าง/
  ข้อความบอกโครงสร้าง
- หนึ่ง comment ต่อหนึ่งปัญหา แล้วเรียง `finding -> locator/evidence -> why it matters ->
  required revision or author question`
- ตัดคำซ้ำ คำเน้น วลีสุภาพที่ไม่เพิ่มสาระ และคำตัดสินกว้างที่ไม่มีหลักฐาน
- ใช้ภาษาตรง กระชับ เป็นกลาง และคง terminology เดียวกับ manuscript/venue
- ห้ามใช้สำนวน generic/AI-like ในตัว review เอง และห้ามสร้างรายการสามข้อเพียงเพื่อให้ดูครบ
- ก่อนส่ง review ให้รัน prose checker เมื่อ output อยู่ในไฟล์ที่รองรับ แล้วอ่านทวนเชิงความหมาย
  เพราะผล checker เป็นเพียง signal ไม่ใช่คำตัดสิน
```

## Minimum acceptance criteria

- venue rules มาจาก official source และผูกกับ article type/date
- citation audit แยก internal existence, external existence, metadata และ claim support
- ไม่มีการเรียก reference ว่า fabricated โดยไม่มี documented verification trail
- problem statement เชื่อมกับ title และ title สะท้อน contribution ที่มีหลักฐาน
- actual length เทียบกับ limit ด้วย counting basis เดียวกัน
- รูปถูกตรวจจาก rendered output, อ่านได้ และการอ้างรูป/หมายเลข/panel ตรงกัน
- engineering diagram ใช้ notation มาตรฐานของสาขา หรือประกาศ deviation/legend ชัดเจน
  และสอดคล้องกับ definitions, equations, algorithms และ system interfaces
- ตัวแปร สัญลักษณ์ สมการ และหน่วยนิยามครบและใช้สม่ำเสมอ
- definition ชัด ใช้คงที่ และระบุ scope/condition/exception ที่เปลี่ยนความหมาย
- math และ algorithm ผ่านการตรวจ correctness, assumptions, edge cases และความสอดคล้อง
  กับ implementation/results เท่าที่หลักฐานเอื้อ
- ตัวเลขสำคัญในกราฟ/ตารางย้อนกลับถึง source/calculation ได้ หรือถูก mark ว่ายัง verify ไม่ได้
- magic numbers มีที่มา เหตุผล tuning boundary และ sensitivity evidence ที่เหมาะกับผลกระทบ
- conclusion ตอบ problem/RQ ด้วยผลที่มีหลักฐานและอ่านรู้เรื่อง
- prose gate รายงานความกระชับและสัญญาณ generic/AI-like โดยไม่กล่าวหา AI authorship
- reviewer report เองผ่าน prose gate และทุก major comment มี finding, locator/evidence,
  consequence และ required action/question
- working review เป็นภาษาไทยจนผู้ใช้ยืนยันพร้อมส่ง; final จึงใช้ภาษาที่ venue กำหนด
  และผ่าน prose gate ในภาษาปลายทาง
- recommendation ย้อนกลับไปยัง major comments/locator/evidence ได้ ใช้ตัวเลือกของ venue
  และไม่ทำนายผลรับตีพิมพ์
- large BLOCKER ที่ทำลาย validity/contribution และต้องเปลี่ยนงานระดับแกนกลางนำไปสู่ reject
- ผ่าน confidentiality, conflict-of-interest และ venue AI-policy gate ก่อนใช้เครื่องมือ
