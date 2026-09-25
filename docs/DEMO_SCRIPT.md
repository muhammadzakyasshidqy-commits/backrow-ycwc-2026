# BACKROW 11.0 — Exhibition Demo Script

1. **Show source vs audience crop.** “The file says 2.5%. The audience capture says 25%.”
2. **Click Check a real slide / load deck.** “I load the deck once.”
3. **Judge chooses a slide.** Do not manually tell BACKROW the matched page.
4. **Capture from the audience position.** “The camera stays where the audience sits.”
5. **Run analysis.** Wait for page match + evidence.
6. **Point to localized region.** “This exact value failed; the rest is not automatically condemned.”
7. **Open technical evidence only if needed.** “AudienceNet is custom; OCR is pretrained; matching/homography are classical.”
8. **Fix the affected source region.** Increase size/contrast/redundancy according to evidence.
9. **Rescan from the same position.** Show the region moving out of risk.
10. **If live capture fails:** switch to the bundled deterministic judge case. State explicitly that it is the backup case, not live judge input.
11. **Close:** “A camera is evidence, not a human eye. Our final claim is measured with the blinded timed field study.”

Do not start with AI history, market size, or a feature list.

## Judge-controlled two-device path

1. Load the competition deck on the presenter workstation.
2. Click **Create observer link**.
3. Give the judge/audience phone the observer page and six-digit code.
4. Leave the phone at the back-row position and start live scan (HTTPS) or take one photo (fallback).
5. Advance the presentation from the front. BACKROW identifies the slide without receiving a page number.
6. The presenter screen receives the localized evidence automatically.
7. Fix the failing region and rescan from the same phone position.
