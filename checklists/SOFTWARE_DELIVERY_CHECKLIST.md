# Software delivery checklist

Apply this checklist when creating or changing a distributed tool, renaming a
software project, preparing a release, or moving experimental code behind a
CLI, GUI, API, notebook or service. Apply only the sections affected by the
change. Record evidence in the project's existing release notes or validation
record; use `templates/SOFTWARE_DELIVERY.md` when no format exists.

## Identify the source that users will execute

- Identify the accepted implementation by repository commit and source hashes.
  For research software, trace these to the experiment's frozen plan and saved
  outputs. A convenient local working copy is not evidence of experiment identity.
- Trace the user entry point through parsing, input loading, preprocessing,
  parameter resolution and defaults to the actual computational functions.
- Prefer one shared engine imported by both the experimental runner and the
  user interface. When packaging a frozen engine, record source pins and the
  exact transformations. Keep interface adapters thin.
- Treat independent implementations and copied engines as separate until
  source comparison and behavioral checks establish their relationship.
- Compare algorithm defaults, dependency versions, strand/orientation and
  coordinate rules, tie rules, stopping conditions and output processing.
  Document intentional differences; correct accidental drift before delivery.

## Verify computation through the installed interface

- Build and install the actual distributable away from the working source.
  Check imports resolve to the installed artifact, not an old checkout.
- Run representative fixtures through the public CLI/UI/API and compare with
  the accepted engine using identical ordered inputs and resolved parameters.
  Check hashes or exact values before applying rounded or aggregate metrics.
- For iterative methods, compare intermediate results and iteration history
  when available. Include edge cases that activate material branches, such as
  indels, ties, missing data, mixed orientation or optional modules.
- For research replays, choose the bounded sample independently of observed
  outcomes. Use saved inputs and results; do not silently replace scientific
  outputs or launch a new full experiment to validate packaging.
- Record the selection, versions, source/artifact hashes, settings, checks and
  failures. Unit-test counts or matching summary scores alone do not establish
  implementation identity or validity of the scientific claim.
- State the scope actually verified. A subset replay does not establish
  universal equivalence or full-grid equivalence to another snapshot.

## Use interoperable output formats

- Identify the downstream tools and established formats for each output type.
  Prefer those formats over an undocumented private layout. Check the relevant
  specification or the actual downstream reader when details are uncertain.
- Preserve format semantics: headers, identifiers, coordinates, units, encoding,
  missing values, ordering and compression. Give columns and metadata explicit
  definitions and a schema/version when the format needs one.
- Keep machine-readable results separate from progress messages. For a CLI,
  reserve stdout for the documented result and send diagnostics to stderr.
- Exercise the actual output with a relevant independent reader or downstream
  tool. A matching filename extension or successful write is not sufficient.
- For sequence tools, use FASTA for learned sequences when appropriate. SAM/BAM
  represents alignments and VCF represents variants; offer those formats only
  when the tool has the information and coordinate semantics needed to produce
  valid records. Do not invent fields merely to claim compatibility.
- Add a structured report or TSV/CSV for run metadata when users need it, while
  keeping domain results in their established format. Document which outputs
  are interoperable and which are tool-specific diagnostic records.

## Verify help and interface behavior

- A command-line tool must provide `--help` (normally also `-h`) and `--version`.
  Help must explain purpose, required inputs, accepted formats, output formats,
  defaults, units, major switches and at least one runnable example.
- `--help` and `--version` must return successfully without input files, network
  access, model/data downloads, starting the algorithm or creating result files.
- Test help from the installed command. Verify documented examples/options and
  defaults against the parser and exercised behavior; generated usage alone
  does not prove that the documentation is correct.
- Test invalid arguments and missing required inputs produce useful errors and
  a nonzero exit code. Test configuration precedence and relevant input adapters.
- For a GUI/service, provide equivalent discoverable help and version/settings
  information and test the user path that invokes the engine.

## Complete names, versions and publication surfaces

- For a rename, inventory repository names and links, distribution/module names,
  imports, callable API, command names, parser help, output annotations, cache
  paths, examples, package metadata, citation metadata, badges, CI and tests.
- Inspect what users actually see on the remote repository: README, About,
  website link, topics and visible release titles/descriptions. Renaming the
  repository alone does not update these surfaces.
- Keep versions coherent across package metadata, runtime, help and docs.
  Choose compatibility aliases deliberately and test them if provided.
- Preserve immutable experimental snapshots, old tags, archived assets and DOI
  deposits. Display metadata may explain historical naming without rewriting
  the code or results that an earlier claim depends on.
- After an authorized push/publication, verify the remote commit and visible
  metadata match the checked result. Record the current canonical source and
  mark stale local copies so the next session does not resume the wrong engine.
- Report remaining differences plainly. L1 delivery checks do not replace
  external user feedback or scientific validation.
