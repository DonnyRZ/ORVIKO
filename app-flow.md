# ODIN - TikTok Slide: App Flow (User Journey)

This document describes the step-by-step app flow from input to output.
It follows how a user would actually use the app from start to finish.

## 1) Entry and initial state

1. User opens the app.
2. The workspace shows three columns:
   - Left: slide input(s)
   - Middle: preview (9:16)
   - Right: generated results
3. Slide 1 is active (expanded) on the left.
4. Preview shows Slide 1 placeholder or last selected result.
5. Results panel shows Slide 1 outputs (if any), otherwise empty state.

## 2) Create Slide 1 (input phase)

1. User edits "Slide text" (required).
2. User optionally adds "Slide design (optional)".
3. User optionally uploads embed images (logos/icons).
4. User chooses "Image quantity" (1–5).
5. User clicks "Generate images".

### 2.1 Validation
- If Slide text is empty, show inline warning and skip generation.
- Otherwise proceed.

## 3) Generate outputs (processing phase)

1. App packages Slide 1 payload:
   - Text, design notes, embed images, quantity.
2. App sends request to the generator.
3. App receives N image options.
4. Results are stored under Slide 1.
5. The first option becomes the selected result if none is selected.

## 4) Review outputs (output phase)

1. Right panel now lists the generated options for Slide 1.
2. User clicks "Use for preview" on an option:
   - That option becomes Slide 1 selected result.
   - Middle preview updates to show that selected option.
3. User can download a single option via "Download".

## 5) Add more slides

1. User clicks "+ Add new slide".
2. App creates Slide 2 and expands it.
3. Slide 2 starts with empty/default values.
4. User repeats the input → generate → review flow for Slide 2.
5. User can add Slide 3, Slide 4, etc. the same way.

## 6) Switch active slide (left panel)

1. Left panel shows slides stacked vertically.
2. Clicking "Open" on a slide expands it and collapses others.
3. This action only changes the left panel inputs.
4. It does NOT change the preview slide.

## 7) Switch preview slide (middle panel)

1. Preview slide changes only by using the arrow controls:
   - Left arrow = previous slide
   - Right arrow = next slide
2. When preview changes:
   - The preview canvas updates.
   - The right panel updates to show results for that preview slide.
3. The active slide on the left remains unchanged.

## 8) Download flow

### 8.1 Download single image
1. User clicks "Download" on a specific option in the right panel.
2. That option is saved as a single image file.

### 8.2 Download selected
1. User clicks "Download selected" in the header or right panel.
2. App collects only selected options across slides.
3. App exports them in a ZIP file.

### 8.3 Download all slides
1. User clicks "Download all slides" in the header.
2. For each slide, app chooses:
   - Selected option if available
   - Otherwise the first generated option
   - Otherwise skip
3. App exports in a ZIP file.

## 9) Error and empty states

- If generation fails:
  - Show inline error message in that slide.
  - Keep previous results.
- If no results exist:
  - Preview shows a neutral placeholder.
  - Right panel shows empty state text.

## 10) Key rules summary

- Left panel controls inputs only.
- Preview changes only via arrow navigation.
- Right panel always follows the current preview slide.
- Slide text must be fully used in the final image.
