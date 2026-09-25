# BACKROW 11.0 — International Presentation Script (English)

## Slide 1 — The information changed

“This slide says 2.5 percent. But from an audience position, the captured information becomes 25 percent. The audience never sees the source file. They see the result after distance, projection, focus, lighting, and perspective. BACKROW tests that physical path.”

## Slide 2 — The exact problem

“Presenters normally judge a slide on their own laptop or walk to the back of the room and inspect it manually. Source-side tools can check font size, contrast, or text complexity, but those checks cannot tell us what this particular room actually delivered.”

## Slide 3 — What BACKROW does

“I load the deck once and leave a camera where the audience sits. As I advance the presentation, BACKROW identifies the current slide, rectifies the camera view, maps evidence back to the source, and reports which exact information was recovered, uncertain, or lost.”

## Slide 4 — Live proof

“Please choose a slide. I will not give BACKROW the page number. It has to identify the slide itself. On this example, the source contains 2.5 percent. The audience evidence decodes 25 percent, so the exact region is marked at risk.”

## Slide 5 — What is actually AI

“Our custom model is AudienceNet 2.0, a small neural network using paired source, camera, and optional room features. Tesseract LSTM is third-party pretrained OCR. ORB, RANSAC, homography, numeric extraction, and evidence fusion are classical engineering. We separate those parts instead of calling the whole pipeline AI.”

## Slide 6 — Safety hierarchy

“A learned model is not allowed to overrule hard evidence. If the source says 2.5 percent and strong camera OCR says 25 percent, that contradiction wins. If the evidence is too weak or the slide cannot be matched reliably, BACKROW abstains.”

## Slide 7 — Prior art and what is new

“Lecture-hall legibility software existed years ago. Camera-based projected-content quality assessment also exists, and current PowerPoint tools can score the source file. So I do not claim that readability itself is new. BACKROW’s contribution is the integrated audience-position workflow: automatic source matching, physical-view evidence, exact localized loss, targeted repair, rescan, and a blinded physical validation path.”

## Slide 8 — Engineering evidence

“On the procedural curriculum, AudienceNet 2.0 reached macro-F1 0.942, compared with 0.406 and 0.479 for our two simple baselines. The bundled three-page deck matched all three pages without page indices. The judge regression detects the 2.5-to-25-percent failure and the repaired version removes both risk regions. These are engineering results, not human accuracy.”

## Slide 9 — The human test

“A camera is not a human eye. So the final study uses naïve readers, a frozen randomized order, six-second timed exposures by default, hidden source truth, immutable responses, separate calibration and locked studies, and a frozen evaluator with confidence intervals and kill gates.”

## Slide 10 — Fix, rescan, prove

“The product is not a score. It is a loop: find the exact lost information, fix that source region, and rescan from the same audience position. BACKROW is useful only if that loop improves what the audience can actually recover. Please choose a slide.”
