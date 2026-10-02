# Rover pitch — September 2026

Open Rover-Pitch-Deck.pptx for the ten-slide editable deck. Photos contains four
white-background product edits and the editing provenance. Rover-Cover.png is a preview.

This deck preserves the capability statements made in September. Read the root
README for later cellular, audio, public-control and motion changes.

The build source requires the Codex presentation runtime. Set
PRESENTATION_SKILL_DIR to its presentations skill directory and expose
@oai/artifact-tool to Node. The runtime's Python/Node helper variables may also be
needed by its finalizePresentation helper. Then run `node build.mjs`.
Build outputs stay under this directory. The generated deck is supplied so a
runtime rebuild is not required to open or edit it.
