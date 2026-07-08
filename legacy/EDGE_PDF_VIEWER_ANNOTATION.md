# Microsoft Edge PDF Annotation Issue

Date noted: 2026-06-27
Machine/user context: Windows + Microsoft Edge, OneDrive workspace.

## Problem

Microsoft Edge PDF viewer handwriting/drawing annotations may disappear, lag, or behave incorrectly after lifting the pen/mouse.

## Workaround investigated

Suggested workaround was to disable this Edge flag:

```text
edge://flags/#edge-new-pdf-viewer
New PDF Viewer
#edge-new-pdf-viewer
```

A safe helper script was created here:

```text
C:\Users\punpi\OneDrive\chonthanawat\fix-edge-pdf-viewer.ps1
C:\Users\punpi\OneDrive\chonthanawat\restore-edge-pdf-viewer.ps1
```

The script behavior is intentionally conservative:

- does not delete Edge profile data
- does not edit registry
- asks before closing Edge
- backs up Edge `Local State` before any edit
- edits only if the Chromium flags format is confidently found
- otherwise opens `edge://flags/#edge-new-pdf-viewer` and prints manual instructions

## Result on current Edge

Observed Edge version from flags page:

```text
150.0.4078.28
```

The script did not find an existing `edge-new-pdf-viewer` entry in Edge `Local State` and therefore did not edit anything.

The page opened by `edge://flags/#edge-new-pdf-viewer` did not show a `New PDF Viewer` / `#edge-new-pdf-viewer` flag in the copied flags list. This likely means the flag is absent, expired, renamed, or no longer user-configurable in this Edge version.

Do not randomly change unrelated flags.

## Closest visible PDF-related flags in this Edge version

Seen in the copied flags list:

```text
Enable improved PDF Read Aloud experience in the new PDF viewer
#edge-pdf-read-aloud-enhanced

Enable Digital Signature for PDF on Legacy (PDFium based) PDF Viewer
#edge-digsig-enabled-pdf

Enable support for XFA in PDF
#edge-pdf-viewer-xfa

Undo/Redo for PDF Annotations
#edge-pdf-undo-redo

OOPIF for PDF Viewer Extension
#edge-pdf-extension-oopif

PDF MIP view label
#edge-pdf-mip-view-label
```

The closest annotation-specific flag is:

```text
Undo/Redo for PDF Annotations
#edge-pdf-undo-redo
```

If the issue persists and a reversible experiment is needed, try setting only `#edge-pdf-undo-redo` from `Default` to `Disabled`, relaunch Edge, test PDF annotation, and restore it to `Default` if it does not help.

## Closing Edge when scripts need it

If Edge background processes remain open, this was used successfully from PowerShell:

```powershell
taskkill /F /IM msedge.exe /T
```

Then rerun:

```powershell
cd C:\Users\punpi\OneDrive\chonthanawat
powershell -ExecutionPolicy Bypass -File .\fix-edge-pdf-viewer.ps1
```

## Current status

Unconfirmed whether the annotation issue is fixed. Keep this note as context before changing more Edge flags.
