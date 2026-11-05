# Final presentation assembly

- `slides/G17_final.pptx`: 15 presentation pages, followed by 3 optional Q&A backups.
- Page 1 is the refreshed cover; page 15 is Thank you. Existing content page numbers 2–14 are unchanged.
- All pages contain speaker notes. A's existing scripts are embedded on pages 3–4; page 5 now has a full English script. The backup pages have short Q&A prompts.
- `slides/G17_final_speaker_notes.md` is extracted from the actual embedded notes, in visible presentation order.
- `slides/B_speaker_notes.md` contains page 5's script and sources.

Build from the repository root after setting `G17_ARTIFACT_RUNTIME` and
`G17_PRESENTATION_SKILL` to the installed bundled runtime and presentation skill:

```powershell
node scripts/build_final_deck.mjs
```

The builder reads `slides/G17_working_draft_with_D.pptx`, authors two matching
text-only bookends with Artifact Tool, and retains the reviewed quantitative
slides and dependencies byte for byte. It validates the package, slide size,
font policy, native backup tables and import before copying the final deck.
The input deck remains unchanged. Private candidates and receipts live in
`.build/final_deck/`.

All speaker notes still need presenter review and a real timed rehearsal.
The filename does not imply that a rehearsal or course submission has occurred.
