# โปรไฟล์การเขียนหนังสือ: แม่แบบสำหรับหนังสือเป้าหมาย

ไฟล์นี้เก็บค่า นโยบาย ตัวอย่าง และบทเรียนเฉพาะหนังสือที่เติมลงใน
`prompts/22_BOOK_WRITING.md` ไม่ใช่ metadata สำหรับหน้าชื่อเรื่อง และห้ามนำค่า
จากหนังสือต้นทางหรือหนังสือเล่มอื่นมาใช้โดยปริยาย

ก่อนใช้ ให้คัดลอกไฟล์นี้เข้าโครงการหนังสือเป็น `BOOK_WRITING_PROFILE.md` แล้ว
แทนค่า `{{BOOK:...}}` ทุกจุดตามลำดับต่อไปนี้:

1. ค้นจากบริบทของหนังสือเป้าหมายก่อน ได้แก่ project state, book metadata,
   master outline, chapter plan, glossary, variable registry, reference catalog,
   build scripts, style files และ production policy ที่มีอยู่จริง
2. อนุมานได้เฉพาะเมื่อมีหลักฐานในโครงการรองรับชัดเจน และต้องบันทึกแหล่งที่ใช้
   ตัดสินใจไว้ใน profile; ห้ามเติมจากความคุ้นเคยหรือจากหนังสือเล่มก่อน
3. หากยังตัดสินค่า นโยบาย หรือตัวอย่างไม่ได้ ให้ถามผู้ใช้เป็นคำถามสั้นที่มีผลต่อ
   งานจริงก่อนเขียน ห้ามปล่อย placeholder ให้ไหลเข้า manuscript
4. ค่าใดไม่ใช้ ให้แทนด้วย `N/A` พร้อมเหตุผลและวิธีทดแทน ห้ามลบ marker

ข้อความระหว่าง marker เป็นค่าที่เครื่องตรวจใช้ประกอบ prompt ห้ามเปลี่ยนชื่อ
marker หรือเติมคำอธิบายนอกค่าที่ตั้งใจใช้จริงภายใน block

## `output-production-contract`

<!-- BOOK_PROFILE_BEGIN:output-production-contract -->
{{BOOK:OUTPUT_PRODUCTION_CONTRACT}}

ระบุจากข้อกำหนดของโครงการเป้าหมายอย่างน้อย: source of truth และ working-file
roles, reader-facing output format ทุกชนิด, page/screen geometry, language/font,
style/citation/cross-reference convention, equation/table/figure representation,
draft กับ production behavior, author-only material, build commands/outputs และ
acceptance/QA ต่อ format หาก project ไม่ได้กำหนด ห้ามใช้ A4/16:9/B5/PDF/
DOCX/EPUB/HTML/Markdown/Pandoc/LaTeX หรือ frame จากเล่มก่อนเป็น default ให้ถาม
ผู้ใช้เฉพาะการตัดสินใจที่จำเป็นก่อนเปลี่ยนโครงหรือ build
<!-- BOOK_PROFILE_END:output-production-contract -->

## `large-reference-ingestion-procedure`

<!-- BOOK_PROFILE_BEGIN:large-reference-ingestion-procedure -->
{{BOOK:LARGE_REFERENCE_INGESTION_PROCEDURE}}

ทำ inventory ชนิดและขนาดของแหล่งอ้างอิงก่อน แล้วระบุ extractor/command และ cache
schema แยกตาม format ที่มีจริง เช่น PDF, DOCX, PPTX/ODP, EPUB, HTML archive หรือ
ชุด Markdown/text ต้องกำหนด source locator ที่ย้อนกลับได้ (page/slide/section/
paragraph/table), partial-extraction rule, media extraction/rendering, revision/
notes handling, cache path/naming, tool limitation และ visual/original-source
verification gate หากยังไม่รู้เครื่องมือหรือความหมายของ revision/layout ให้ถาม
ผู้ใช้ก่อน conversion/OCR หรือการอ่านแบบเสียโครงสร้าง
<!-- BOOK_PROFILE_END:large-reference-ingestion-procedure -->

## `reader-domain-contract`

<!-- BOOK_PROFILE_BEGIN:reader-domain-contract -->
{{BOOK:READER_DOMAIN_CONTRACT}}

ระบุผู้อ่านเป้าหมาย ความรู้ตั้งต้น ระดับความลึก ภาษา/น้ำเสียง เป้าหมายการเรียนรู้
หรือการใช้งาน และบริบทที่หนังสือต้องช่วยให้วิเคราะห์ ตีความ หรือตัดสินใจ จาก
book metadata/outline/คำสั่งผู้ใช้ ห้ามใช้ “นักศึกษาปริญญาตรี” หรือ “งานวิศวกรรม”
เป็นค่าเริ่มต้นของหนังสือทุกเล่ม หากยังไม่รู้และมีผลต่อตัวอย่าง/ความลึกให้ถามผู้ใช้
<!-- BOOK_PROFILE_END:reader-domain-contract -->

## `primary-teaching-source-label`

<!-- BOOK_PROFILE_BEGIN:primary-teaching-source-label -->
{{BOOK:PRIMARY_TEACHING_SOURCE_LABEL}}<!-- BOOK_PROFILE_END:primary-teaching-source-label -->

## `primary-teaching-source-citation-code`

<!-- BOOK_PROFILE_BEGIN:primary-teaching-source-citation-code -->
{{BOOK:PRIMARY_TEACHING_SOURCE_CITATION_CODE}}<!-- BOOK_PROFILE_END:primary-teaching-source-citation-code -->

## `draft-page-size`

<!-- BOOK_PROFILE_BEGIN:draft-page-size -->
{{BOOK:DRAFT_PAGE_SIZE}}<!-- BOOK_PROFILE_END:draft-page-size -->

## `text-extraction-python`

<!-- BOOK_PROFILE_BEGIN:text-extraction-python -->
{{BOOK:TEXT_EXTRACTION_PYTHON}}<!-- BOOK_PROFILE_END:text-extraction-python -->

## `manuscript-root`

<!-- BOOK_PROFILE_BEGIN:manuscript-root -->
{{BOOK:MANUSCRIPT_ROOT}}<!-- BOOK_PROFILE_END:manuscript-root -->

## `domain-thai-noun`

<!-- BOOK_PROFILE_BEGIN:domain-thai-noun -->
{{BOOK:DOMAIN_THAI_NOUN}}<!-- BOOK_PROFILE_END:domain-thai-noun -->

## `example-primary-reference-author`

<!-- BOOK_PROFILE_BEGIN:example-primary-reference-author -->
{{BOOK:EXAMPLE_PRIMARY_REFERENCE_AUTHOR}}<!-- BOOK_PROFILE_END:example-primary-reference-author -->

## `example-secondary-reference-author`

<!-- BOOK_PROFILE_BEGIN:example-secondary-reference-author -->
{{BOOK:EXAMPLE_SECONDARY_REFERENCE_AUTHOR}}<!-- BOOK_PROFILE_END:example-secondary-reference-author -->

## `example-primary-reference-code`

<!-- BOOK_PROFILE_BEGIN:example-primary-reference-code -->
{{BOOK:EXAMPLE_PRIMARY_REFERENCE_CODE}}<!-- BOOK_PROFILE_END:example-primary-reference-code -->

## `example-secondary-reference-code`

<!-- BOOK_PROFILE_BEGIN:example-secondary-reference-code -->
{{BOOK:EXAMPLE_SECONDARY_REFERENCE_CODE}}<!-- BOOK_PROFILE_END:example-secondary-reference-code -->

## `current-draft-build-status`

<!-- BOOK_PROFILE_BEGIN:current-draft-build-status -->
> **สถานะเครื่องมือ:** {{BOOK:CURRENT_DRAFT_BUILD_STATUS}} ตรวจจาก build script,
> filter, template และผล smoke build ของโครงการปัจจุบันก่อนกรอก ต้องแยกให้ชัดว่า
>สิ่งใดทำได้แล้วใน Draft build สิ่งใดมีเฉพาะ production build และสิ่งใดยังไม่มี
>จริง ห้ามเขียนนโยบายในอนาคตให้ดูเหมือนเป็นความสามารถที่ทดสอบแล้ว
<!-- BOOK_PROFILE_END:current-draft-build-status -->

## `large-reference-project-findings`

<!-- BOOK_PROFILE_BEGIN:large-reference-project-findings -->
  - ตรวจทุกครั้งว่าแหล่งสอนหลักกับตำราอ้างอิงเป็นคนละหลักฐานกันหรือไม่ การมีภาพ
    จากแหล่งหนึ่งอยู่แล้วไม่ใช่เหตุผลให้ข้ามรูป ตาราง หรือแผนภูมิจากอีกแหล่งที่
    evidence ledger อ้างถึง
  - เครื่องมือ `--images` มักเห็นเฉพาะ raster object และอาจไม่เห็นไดอะแกรมที่
    วาดด้วย vector primitives ห้ามสรุปว่า “หน้านี้ไม่มีรูป” จากผล image extraction
    เพียงอย่างเดียว ให้ render เต็มหน้าเมื่อข้อความหรือ evidence ชี้ว่ามีองค์ประกอบ
    ภาพอยู่จริง
  - ใช้ full-page rendering เป็นค่าเริ่มต้นสำหรับ vector diagram และเอกสารที่มี
    caption หรือหลาย panel การ auto-crop ใช้ได้เฉพาะ preview ที่ตรวจภาพทุกไฟล์
    แล้ว เพราะอาจตัด caption หรือ panel หายโดยไม่รายงานข้อผิดพลาด
  - บันทึกไฟล์ที่ render ใน figure index พร้อมแหล่ง ฉบับ เลขหน้าพิมพ์ เลขหน้า PDF,
    เลขรูป/caption และหัวข้อที่จะใช้ เพื่อให้การตรวจสิทธิ์และการสร้างรูปใหม่ติดตามได้
  - อย่าสมมติ offset ระหว่างเลขหน้าพิมพ์กับเลขหน้า PDF ว่าคงที่ตลอดเล่ม ก่อนอ้าง
    ช่วงใหม่ให้ยืนยันกับ heading, running header, section หรือ equation ที่เห็นจริง
  - {{BOOK:PDF_EXTRACTION_PROJECT_FINDINGS}} หากยังไม่มีบทเรียนเฉพาะโครงการให้
    กรอก `N/A — ยังไม่มีผลจากการใช้งานจริง` และเพิ่มภายหลังจาก L3/ผลตรวจจริง
<!-- BOOK_PROFILE_END:large-reference-project-findings -->

## `draft-build-procedure`

<!-- BOOK_PROFILE_BEGIN:draft-build-procedure -->
{{BOOK:DRAFT_BUILD_PROCEDURE}}

ต้องระบุ command, input, output และจังหวะ build ที่ตรวจแล้วจริงสำหรับหนังสือ
เป้าหมาย รวมทั้งวิธีตรวจ heading, reference, caption, marker, font และข้อความสกัด
หากยังไม่มี pipeline ให้ถามผู้ใช้ว่าจะสร้าง pipeline หรือใช้ smoke path ใด ห้ามยืม
ชื่อ script, chapter directory, template หรือ output path จากหนังสืออื่น
<!-- BOOK_PROFILE_END:draft-build-procedure -->

## `book-unit-policy`

<!-- BOOK_PROFILE_BEGIN:book-unit-policy -->
- **นโยบายหน่วยของหนังสือเล่มนี้:** {{BOOK:UNIT_POLICY}} ระบุระบบหน่วยหลัก
  ระบบที่อนุญาตให้กล่าวถึง เงื่อนไขการแปลง การปัดเลข และข้อยกเว้นทางสาขาให้ชัด
  จาก metadata/outline/มาตรฐานที่โครงการเลือก หากบริบทไม่พอให้ถามผู้ใช้ ห้าม
  สมมติว่าหนังสือทุกเล่มใช้ระบบหน่วยเดียวกัน
<!-- BOOK_PROFILE_END:book-unit-policy -->

## `chapter-1-required-comparison-tables`

<!-- BOOK_PROFILE_BEGIN:chapter-1-required-comparison-tables -->
{{BOOK:REQUIRED_COMPARISON_TABLES}}

รายการนี้ต้องมาจากชื่อบท แผน เนื้อหาที่หลักฐานรองรับ และภาระการอ่านของผู้อ่าน
เป้าหมาย ไม่บังคับจำนวนหรือหัวข้อตารางจากหนังสืออื่น หากไม่มีตารางบังคับให้กรอก
`N/A — ไม่มีตารางเปรียบเทียบบังคับสำหรับบทนี้` พร้อมเหตุผล
<!-- BOOK_PROFILE_END:chapter-1-required-comparison-tables -->

## `book-figure-example-and-conventions`

<!-- BOOK_PROFILE_BEGIN:book-figure-example-and-conventions -->
- รูปที่ยังไม่ได้สร้างให้จองตำแหน่งด้วย stable anchor ใน `needs-figure` เช่น

  ```markdown
  ดังแสดงในรูปที่ \ref{fig-chNN-topic} ... `[SOURCE p. n]`

  ::: {#fig-chNN-topic .needs-figure}
  {{BOOK:EXAMPLE_READER_FACING_FIGURE_CAPTION}}
  :::
  ```

  ข้อความใน `needs-figure` ต้องเป็น caption สำหรับผู้อ่าน ไม่ใช่คำสั่งวาดรูป
  รายละเอียดสำหรับผู้วาด แหล่ง compositional reference และข้อจำกัดด้านสิทธิ์
  อยู่ใน `ref-note` แยกต่างหาก
- ใช้ anchor scheme `{{BOOK:FIGURE_ANCHOR_SCHEME}}` ซึ่งต้องไม่ซ้ำและคงเดิม
  เมื่อแทน placeholder ด้วยรูปจริง
- เมื่อมีรูปต้นฉบับจริง ให้แทน `needs-figure` ด้วย `book-figure` โดยคง anchor
  และ caption เดิม และตรวจว่า pipeline วางเลข caption กับ label ถูกต้อง
- หากมีภาพอ้างอิงชั่วคราว ให้เรียง `ข้อความชี้รูป → needs-figure/book-figure →
  ภาพอ้างอิง → ref-note` เก็บหลักฐาน author-only ใน Markdown และกำหนดให้
  production build กรองออกโดยไม่ทำลาย source
<!-- BOOK_PROFILE_END:book-figure-example-and-conventions -->

## `book-variable-examples`

<!-- BOOK_PROFILE_BEGIN:book-variable-examples -->
   ทุกรายการต้องคัดสัญลักษณ์ ชื่อ หน่วย และมิติจากทะเบียนตัวแปรของหนังสือ
   เป้าหมายโดยตรง สัญลักษณ์ต้องคงที่ตลอดเล่ม หากสัญลักษณ์นิยมชนกัน ให้กำหนด
   รูปหลักและรูปที่ห้ามใช้ในทะเบียนก่อนเขียน พร้อมตัวอย่างเฉพาะสาขาที่ตรวจจาก
   `{{BOOK:VARIABLE_REGISTRY_PATH}}`; หากยังไม่มีทะเบียนให้ถามว่าจะสร้างที่ใด
   และห้ามยืมตัวแปรตัวอย่างจากหนังสืออื่น
<!-- BOOK_PROFILE_END:book-variable-examples -->

## `slide-reference-example`

<!-- BOOK_PROFILE_BEGIN:slide-reference-example -->
สื่ออ้างอิงชั่วคราวจาก `{{BOOK:PRIMARY_SOURCE_MEDIA_KIND}}` ไม่ใช่สื่อพร้อม
ตีพิมพ์ เว้นแต่โครงการยืนยันสิทธิ์และสถานะ production ไว้ชัด ใช้ path และคำอธิบาย
ที่ตรวจจาก asset tree ของหนังสือเป้าหมาย เช่น

```markdown
![{{BOOK:REFERENCE_MEDIA_ALT}}]({{BOOK:REFERENCE_MEDIA_PATH}} "{{BOOK:REFERENCE_MEDIA_TITLE}}")

::: ref-note
{{BOOK:REFERENCE_MEDIA_NOTE}}
:::
```

วาง `ref-note` ต่อท้ายภาพหรือกลุ่มภาพที่เกี่ยวข้อง ระบุว่าสื่อจริงควรสื่ออะไร
อ้างมาจากไหน มีข้อจำกัดด้านสิทธิ์ใด และต้องแทนที่หรือไม่ ให้ Draft build แสดง
เพื่อการตรวจ ส่วน production build ต้องทำตาม policy ที่ทดสอบแล้วของโครงการ
<!-- BOOK_PROFILE_END:slide-reference-example -->

## `citation-registry`

<!-- BOOK_PROFILE_BEGIN:citation-registry -->
ทะเบียนรหัส citation และบรรณานุกรมเต็มอยู่ที่ `{{BOOK:CITATION_REGISTRY_PATH}}`
ซึ่งต้องตรวจจากโครงการเป้าหมาย รหัสตัวอย่างที่อนุญาตคือ
`{{BOOK:CITATION_CODE_EXAMPLES}}`; ระบุด้วยว่ารหัสใดเป็น internal evidence ที่
ไม่สร้างรายการท้ายบท เมื่อเพิ่มแหล่งใหม่ต้องอัปเดตทั้ง source bibliography,
registry/filter และทดสอบ build ห้ามยืมรหัส ชื่อผู้แต่ง หรือรายการอ้างอิงจากเล่มอื่น
<!-- BOOK_PROFILE_END:citation-registry -->

## `chapter-1-table-qa`

<!-- BOOK_PROFILE_BEGIN:chapter-1-table-qa -->
- [ ] ตารางเปรียบเทียบบังคับตาม `{{BOOK:REQUIRED_TABLE_QA}}` ครบ หากไม่มีให้
  ระบุ `N/A` ให้ตรงกับค่า `chapter-1-required-comparison-tables`
<!-- BOOK_PROFILE_END:chapter-1-table-qa -->

## `book-spelling-qa`

<!-- BOOK_PROFILE_BEGIN:book-spelling-qa -->
- [ ] ผ่านรายการสะกดและรูปศัพท์เฉพาะหนังสือที่ `{{BOOK:SPELLING_POLICY_PATH}}`
  และรัน `{{BOOK:SPELLING_QA_COMMAND}}`; หากยังไม่มี policy/command ให้รวบรวม
  รูปศัพท์จาก glossary และถามผู้ใช้เฉพาะคำที่มีทางเลือกเชิงบรรณาธิการ
<!-- BOOK_PROFILE_END:book-spelling-qa -->

## `project-derived-pitfalls`

<!-- BOOK_PROFILE_BEGIN:project-derived-pitfalls -->
**2. ทำสาระจากแหล่งสอนหลักหล่นระหว่างตรวจเข้มกับแหล่งรอง** — แหล่งสอนหลักที่
โครงการรับรองอาจเป็นหลักฐานในตัวเองตาม citation policy ความเสี่ยงคือผู้เขียนลบ
สาระที่แหล่งหลักรองรับเพียงเพราะยังหาแหล่งรองไม่พบ แก้โดยไล่เทียบ source zone
กับ bullet ทีละหน่วย และแยก “ไม่มีแหล่งรอง” ออกจาก “ไม่มีหลักฐานใดเลย”

**3. ชื่อหัวข้อสัญญาเนื้อหาที่หลักฐานไม่มีจริง** — master outline อาจถูกเขียนก่อน
ตรวจแหล่งจริง หากค้นแหล่งที่กำหนดแล้วไม่พบสาระตามชื่อ ห้ามแต่งให้เข้าชื่อ ให้ลด
ขอบเขต เปลี่ยนชื่อ หรือเปิด evidence gap พร้อมบันทึกแหล่งและคำค้นที่ตรวจแล้ว

{{BOOK:PROJECT_DERIVED_PITFALLS}} เพิ่มเฉพาะบทเรียนที่เกิดจากการทำงาน/QA/
feedback ของหนังสือเป้าหมายจริง หากยังไม่มีให้กรอก `N/A — ยังไม่มีบทเรียนเฉพาะ`
<!-- BOOK_PROFILE_END:project-derived-pitfalls -->

## `structure-check-spelling-rule`

<!-- BOOK_PROFILE_BEGIN:structure-check-spelling-rule -->
7. **การสะกดเฉพาะเล่ม** ตรวจตาม `{{BOOK:STRUCTURE_SPELLING_RULE}}` โดยกำหนด
ข้อยกเว้นและขอบเขตไฟล์ให้ชัด หากไม่มี rule เฉพาะให้กรอก `N/A`
<!-- BOOK_PROFILE_END:structure-check-spelling-rule -->

## `book-terminology-rule`

<!-- BOOK_PROFILE_BEGIN:book-terminology-rule -->
- **นโยบายศัพท์เฉพาะเล่ม:** {{BOOK:TERMINOLOGY_RULE}} ต้องอ้าง glossary,
  style guide, มาตรฐานวิชาชีพ หรือคำตัดสินของผู้ใช้ ระบุคำที่เลือก คำที่ไม่ใช้
  ข้อยกเว้นสำหรับข้อความคัดลอก และขอบเขตการตรวจ หากหลักฐานขัดกันให้ถามผู้ใช้
  ห้ามนำคำเลือกเฉพาะสาขาหรือบทเรียนการสะกดจากหนังสืออื่นมาเป็นค่าเริ่มต้น
<!-- BOOK_PROFILE_END:book-terminology-rule -->
