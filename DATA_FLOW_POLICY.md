# DATA_FLOW_POLICY — Storage, Cache, and Source Ingestion

This is the canonical rule set for where project data lives, how source files
(PDF, image, DOCX, XLSX, PPTX) become something an agent reads, and which
artifacts may travel over cloud sync, Git, or a metered link. Other documents
link here instead of repeating these rules.

Goal, in priority order:

1. Keep work quality and evidence traceability intact.
2. Spend AI tokens only on judgment, never on work a deterministic tool can do
   or on work already done in an earlier session.
3. Upload and download only what another machine or person actually needs;
   keep high-churn and regenerable files off cloud sync and metered links.

## Core Rules

1. **Extract once, read small.** Convert each source once with a deterministic,
   format-native tool into a content-addressed cache. Agents read the cache's
   index and distilled evidence, not the original file, unless layout or
   fidelity requires it.
2. **Place by rebuild cost.** Regenerable outputs stay on fast local storage
   and never sync. Outputs that contain human or AI judgment are small, durable,
   and synced or committed. See [Rebuild Classes](#rebuild-classes).
3. **Synced folders are for durable inputs and finals.** Git repositories,
   environments, caches, renders, and build intermediates live outside
   cloud-synced trees.
4. **Never pay twice for AI.** Before any AI reading, OCR, vision, or
   summarization, check the cache. Persist every AI-produced result that cost
   tokens, with its source hash, so no later session repeats it.
5. **Ask before bulk network traffic on a metered or unknown link.** Do not
   hydrate cloud-only placeholders in bulk. See [Network Rules](#network-rules).

## Storage Tiers

| Tier | Typical location | Holds | Sync / backup | Rebuild from |
|---|---|---|---|---|
| `git` | Git remote (GitHub) + local clone on fast disk | code, Markdown source, `.ai/` state, distilled evidence, small fixtures, cache manifests that record judgment | Git push | — (source of truth for text) |
| `durable` | cloud drive: OneDrive, Google Drive, Dropbox, iCloud Drive | raw inputs (source PDF, received DOCX/XLSX/PPTX, photos, raw data), final deliverables, binary R2 artifacts | cloud sync | — (source of truth for binaries) |
| `hot` | local SSD: WSL ext4 `~`, `~/.cache`, `C:\Users\<user>\AppData\Local` | working clones, Conda environments, extraction cache, build intermediates | none | `git` + `durable` by rerunning tools |
| `cold` | local or external HDD, NAS | large datasets, cold caches, archives, the second checksum-verified backup copy | manual or scheduled copy | `durable`, or kept as a backup |
| `scratch` | `$TMPDIR`, `/tmp`, `/var/tmp/<project>` | OCR page images, render scratch, unzip/convert temporaries | none | rerun; delete after the run |

- On Windows with WSL2, the `hot` tier is the WSL ext4 filesystem, not
  `/mnt/c` or `/mnt/<drive>`. Cross-filesystem access through `/mnt/*` is slow,
  and inside a synced folder it can return `Input/output error` for cloud-only
  files. Copy the hot subset into ext4 rather than running builds against
  `/mnt/*`.
- Run environments, builds, and caches on SSD. HDD and USB drives are for
  `cold` data. External drives may be absent: record them in
  `.ai/LOCAL_RESOURCES.md` with `Required?` and a fallback.
- Check free space on the drive that hosts the WSL virtual disk (`ext4.vhdx`)
  before moving work into WSL. If that drive is nearly full, move the distro
  first (`wsl --manage <distro> --move <path>`).
- Code reads `durable` and `cold` paths from machine-local variables (see
  [Variables](#variables)), never from hardcoded paths or from symlinks into
  synced folders.
- A new machine needs only: clone the repo, set `.env`, rebuild the cache on
  demand.

## Rebuild Classes

Classify every generated artifact by what it costs to make again, then place it
accordingly.

| Class | Meaning | Examples | Place in | Never |
|---|---|---|---|---|
| `R0` cheap, deterministic | seconds to minutes, no AI, no network | PDF text layer, page renders, figure crops, DOCX→Markdown, XLSX sheet dumps, PPTX slide text, thumbnails, LaTeX/Pandoc intermediates | `hot` | sync, commit, upload |
| `R1` costly, deterministic | long runtime or large download, no judgment | Tesseract OCR of a long scan, bulk format conversion, downloaded datasets, model weights | `hot`; optional copy on `cold` | commit; sync unless small and needed on another machine |
| `R2` judgment | contains a human or AI decision that cannot be regenerated for free | `--review`/`--manual-crop` records, AI OCR or vision transcription, AI summaries, evidence units, extraction QA notes | `git` if text, `durable` if binary; keep it compact | leave only in `hot` or `scratch` |
| `final` | deliverable | submitted PDF/DOCX/PPTX/XLSX, published figures | `durable` (and `git` if the project versions finals) | rebuild silently |

- When one cache mixes classes, persist the R2 part (manifest, review state,
  manual crops, AI text) and let R0/R1 files regenerate from it.
- A file whose class is unclear is treated as R2 until the user decides; do
  not delete it.
- Delete from `durable` only regenerable files, only after two copies exist
  elsewhere with every file checksum-verified, and only with user confirmation.

## Source Ingestion Pipeline

```text
durable source ──(1) locate & fingerprint──▶ (2) cache lookup ──hit──▶ (5) read
     (read-only)                                   │miss
                                                   ▼
                                (3) deterministic extract (R0/R1, hot tier)
                                                   ▼
                                (4) distill evidence units (R2, git tier)
                                                   ▼
                                (5) agent reads index → evidence → extract
                                                   ▼
                                (6) build output in hot tier
                                                   ▼
                                (7) publish final once to durable / git
```

1. **Locate and fingerprint.** List metadata first (name, size, mtime); this
   does not download cloud-only files. Read the file content once to compute
   SHA-256; that read is the single hydration this source needs.
2. **Cache lookup.** Look under `$APK_CACHE_ROOT/extract/<stem>-<sha12>/` (or
   the tool's own cache, such as the PDF figure cache) for `manifest.json` and
   `INDEX.md`. A hit with matching tool version and settings means no
   extraction and no AI reading of the original.
3. **Deterministic extract.** On a miss, run the format-native tool for only
   the pages, slides, sheets, or sections the task needs. Write the result and a
   `manifest.json` (source path, size, SHA-256, tool and version, settings,
   extracted scope, known losses, date). Partial caches are normal; later runs
   extend them.
4. **Distill.** Write the small, task-relevant evidence units with their
   locators (source, version/hash, page/slide/sheet/section) as R2 text in the
   project. This is what future sessions read.
5. **Read with the token ladder.** Stop at the first rung that answers the
   question:
   1. cache `INDEX.md` / manifest, and existing evidence units;
   2. `grep` or a local query over the extracted text or data;
   3. targeted extracted sections;
   4. low-resolution renders or crops, for layout, figures, or verification;
   5. full-resolution image or the original file, only when fidelity is the
      question.
6. **Build locally.** Pandoc, LaTeX, Python, and Office conversions write
   intermediates in `hot` or `scratch`, never inside the synced tree.
7. **Publish once.** Copy only the final deliverable into `durable`, once,
   after QA (including the Thai DOCX gate when it applies). Repeated rebuilds
   do not touch the synced folder.

## Format Playbook

All extraction runs in the shared Conda-family environment named in `AGENTS.md`
(`text` for documents, `image` for OCR and image work). Record losses rather
than hiding them.

| Format | Extract with | Cache (R0/R1) | AI reads | Escalate to vision/original when |
|---|---|---|---|---|
| PDF | `scripts/reference_extract/pdf_text_extract.py` for page ranges; `pdf_figures.py` per figure; `pdf_render_pages.py` as fallback | text per page with page markers; figure crops and `overview/` | `INDEX.md`, evidence units, page-range text | layout, equations, figures, page-number checks; scanned pages need the user's OCR decision |
| Image | hash, then Pillow/OpenCV for size, EXIF, and a downscaled preview; Tesseract for text | preview at the smallest resolution that answers, crops of the region of interest, OCR text | OCR text and metadata first, then preview or crop | the question is visual (diagram, photo content, handwriting) |
| DOCX | `pandoc` to Markdown (`--track-changes=all` when revisions matter), `--extract-media`; comments/notes as needed | Markdown plus media folder | heading outline, then sections | layout, styles, or Thai rendering matter; check the rendered PDF |
| XLSX | `openpyxl`/`pandas`: per-sheet name, dimensions, header, types, a few sample rows, formula count; formulas and cached values separately | per-sheet CSV or Parquet plus a schema summary | schema summary and local query results | charts, formatting, or merged-cell meaning matter |
| PPTX | `python-pptx`: per-slide text, tables, speaker notes, media map; render via LibreOffice → PDF → `pdf_render_pages.py` | per-slide Markdown with slide numbers; thumbnails on demand | slide text and notes | slide design or visual QA is the task |

- Spreadsheets: compute totals, filters, joins, and statistics locally and give
  the agent the result, never the full sheet.
- Images: downscale and crop before sending to a vision model; prefer
  Tesseract over AI OCR, and escalate only with a recorded reason. Persist any
  AI transcription as R2.
- OCR on scans requires the user's decision first (see `AGENTS.md` PDF rules).
- DOCX/PPTX/XLSX are ZIP containers: unzip in `scratch`, not next to the
  source in a synced folder.

## Network Rules

### Cloud drives

- Cloud-only placeholders (OneDrive Files On-Demand, Dropbox online-only,
  Google Drive streaming, iCloud optimized storage) download when their content
  is read. Do not run recursive content scans (`grep -r`, `rg`, hashing,
  `find -exec`, bulk copy) from a sync root. Stay inside the project and narrow
  by path. Metadata listing (size, count, mtime) is fine.
- Keep frequently read inputs "always available on this device" per folder,
  not for the whole drive.
- Do not create symlinks inside a synced folder or point one into it: the
  sync client can stall on them and leave the folder's sync status stuck. Use
  a machine-local path variable instead (see [Variables](#variables)). A
  virtualenv contains symlinks, so never create one in a synced folder. To
  clean up existing links, see `MACHINE_PROFILES.md` "OneDrive stops syncing".
- Never let a build or cache write repeatedly into a synced folder. Sync cost
  grows with file count and churn more than total size; many small files and
  regenerated caches dominate upload.
- Before cleanup, hashing, copying, or bulk reads over many synced files, ask
  the user to pause syncing, or move the work to `hot` storage with approval.

### Git and GitHub

- Keep clones in the `hot` tier, not in synced folders. If a repo must stay in
  a synced folder, run `git gc` occasionally.
- Commit source, distilled evidence, and R2 manifests; ignore R0/R1 caches and
  build output. Large binaries go in `durable`, not in Git history.
- To read another repository, prefer `git clone --depth 1` or
  `--filter=blob:none` with sparse checkout. Defer Git LFS pulls on a metered
  link.
- Kit updates use the manifest-only notice in `scripts/check-update-notice.py`;
  they never download on their own.

### Metered links

- Check cost before heavy downloads instead of asking. On Windows/WSL2:

  ```powershell
  [void][Windows.Networking.Connectivity.NetworkInformation,Windows.Networking.Connectivity,ContentType=WindowsRuntime]
  [Windows.Networking.Connectivity.NetworkInformation]::GetInternetConnectionProfile().GetConnectionCost().NetworkCostType
  ```

  `Unrestricted` means unmetered; `Fixed` or `Variable` means metered. A router
  or hotspot backed by mobile data reports `Unrestricted` unless the user marks
  that network as metered, so suggest doing that once.
- On a metered or unknown link: state the estimated size and wait for approval
  before environment installs, model or dataset downloads, LFS pulls, or
  hydrating many cloud files (threshold and approval rules:
  `ENVIRONMENT_POLICY.md`). Suggest turning off editor auto-updates (VS Code:
  `"extensions.autoUpdate": false`, `"update.mode": "manual"`).
- Prefer work that is already local: an existing cache, an installed
  environment, a downloaded copy on `cold`.

## Variables

| Variable | Meaning | Default |
|---|---|---|
| `APK_CACHE_ROOT` | root of the kit's extraction cache (`hot` tier) | `${XDG_CACHE_HOME:-$HOME/.cache}/agent-project-kit-cache` (not the kit clone directory `.../agent-project-kit`) |
| `APK_PDF_FIGURE_CACHE` | PDF figure cache used by `pdf_figures.py` | `references/pdf-figures` in the project |
| `PROJECT_DATA_ROOT` | raw inputs (`durable` or `cold`) | project-specific |
| `PROJECT_CACHE_ROOT` | project-specific cache and intermediates (`hot`) | `$APK_CACHE_ROOT/projects/<project>` |
| `PROJECT_OUTPUT_ROOT` | where finals are published (`durable`) | project-specific |

Set them in a machine-local `.env` or `.ai/ENVIRONMENT_VARIABLES.md`; record
non-portable locations in `.ai/LOCAL_RESOURCES.md`.

The PDF figure cache defaults to the project because its `manifest.json`
holds R2 review and manual-crop decisions. In a cloud-synced project with many
figures, point `APK_PDF_FIGURE_CACHE` to the `hot` tier and keep a copy of
each source's `manifest.json` and `INDEX.md` in the project, or accept the sync
cost knowingly. Record the choice in `.ai/DOCUMENT_PIPELINE.md`.

## Markdown Discovery

Distilled evidence only saves tokens if later sessions find it. The context
bundle from `scripts/context.py` carries `related_markdown`: up to five pointers
(path, title, matched headings, size, reason) to project Markdown that matches
the request, ranked by `scripts/md_index.py`. It never carries file content.

- Read the listed files' matched sections before browsing. An empty list means
  nothing indexed matched; do not open other Markdown just because it exists.
- A supplied source file (`--file`) whose hash matches a cache directory
  (`<stem>-<sha12>`) or a `source_sha256` front-matter value ranks first. The
  lookup also checks `$APK_CACHE_ROOT/extract/` and `$APK_PDF_FIGURE_CACHE`
  directly, so caches kept off the project are found; those hits obey the
  same private rules, judged by where a link points. A same-name cache with a
  different hash is flagged as possibly stale.
- The index is R0: it lives at `$APK_CACHE_ROOT/md-index/`. Listing is
  metadata only. Each call reads up to `$APK_MD_INDEX_READ_BUDGET` (default 40)
  new or changed files whose path matches the request or that are evidence,
  cache, or `.ai` notes, plus at most `$APK_MD_INDEX_DISCOVERY` (default 5)
  other files. This caps how many placeholders one call hydrates; each file it
  does read is downloaded in full. Unread files match by path until a later
  call reads them (`unread_files` in the result), and a cache folder's hash is
  known before its `INDEX.md` is read. `md_index.py --build-all` reads
  everything once; in a cloud-synced project ask the user before running it.
- It never indexes private areas from `config/release-boundary.json`
  (`private/`, `internal/`, `local-profiles/`, `*.private.md`, or a symlink
  that points into one or outside the project), the installed
  kit snapshot, dependency and build folders, or `PROJECT_STATE.md`, which the
  bundle already carries. `.ai/archive/` is indexed but penalized.
- Make new evidence and cache notes findable: give each file an H1 title that
  names the source and topic, use descriptive `##` headings, and optionally add
  front matter:

  ```yaml
  ---
  title: Reading cache — White 2011, ch. 3
  summary: Bernoulli equation and its assumptions, pp. 140–152
  keywords: bernoulli, energy equation, กลศาสตร์ของไหล
  source_sha256: <sha256 of the source file>
  ---
  ```

- Query the router directly with
  `python3 scripts/md_index.py "<request>" --project . [--file SOURCE]`.

## Recording

- `.ai/LOCAL_RESOURCES.md`: every non-portable location with its tier, rebuild
  class, size, and regenerate command.
- `.ai/DOCUMENT_PIPELINE.md`: per-source extraction records (hash, tool,
  scope, cache path, losses, OCR status).
- `.ai/MACHINE_PROFILE.md`: this machine's storage devices (SSD/HDD/external),
  sync clients, and network-cost status.
- Never imply that a partial cache covers a whole source.

## Retention

- `scratch`: delete at the end of the run.
- `hot` caches: deletable at any time; they rebuild on demand. When space is
  short, remove the oldest R0 entries first, or move R1 entries to `cold`.
- R2 and finals: never deleted implicitly.
