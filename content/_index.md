---
title: "About me"
socialShare: false
---

{{< rawhtml >}}
<style>
/* Custom styles for home page - full sunset image with overlay text box */

/* Hide the page heading/title elements */
.intro-header.big-img .page-heading,
.intro-header.big-img .page-heading h1,
.intro-header.big-img .page-heading hr,
.intro-header.big-img .page-subheading {
  display: none !important;
}

/* Make the header show the full image without cropping */
.intro-header.big-img {
  background-size: cover !important;
  background-position: center center !important;
  min-height: 100vh !important;
  height: 100vh !important;
  margin-bottom: 0 !important;
  position: relative !important;
}

/* Position the main content container over the image */
div[role="main"].container {
  position: absolute !important;
  top: 50% !important;
  left: 50% !important;
  transform: translate(-50%, -50%) !important;
  width: 100% !important;
  max-width: 900px !important;
  z-index: 100 !important;
  margin: 0 !important;
  padding: 0 15px !important;
}

/* Style the content well */
.well {
  background-color: rgba(60, 60, 60, 0.4) !important;
  backdrop-filter: blur(5px) !important;
  border: none !important;
  border-radius: 8px !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
  padding: 30px 40px !important;
  color: #fff !important;
}

.well p {
  color: #fff !important;
  margin-bottom: 15px;
  line-height: 1.7;
}

.well p:last-child {
  margin-bottom: 0 !important;
}

.well strong {
  color: #fff !important;
}

.well a {
  color: #a8d5ff !important;
  text-decoration: none !important;
  border-bottom: 1px solid rgba(168, 213, 255, 0.5);
  transition: all 0.3s ease;
}

.well a:hover {
  color: #d0e9ff !important;
  border-bottom: 2px solid #d0e9ff;
}

/* Remove underlines from all links site-wide */
a {
  text-decoration: none !important;
}

/* Email spoiler styles */
.email-spoiler {
  position: relative;
  display: inline-block;
  cursor: pointer;
  user-select: none;
}
.email-spoiler .email-blurred {
  filter: blur(8px);
  transition: filter 0.3s ease;
  pointer-events: none;
  color: #fff;
}
.email-spoiler.revealed .email-blurred {
  filter: blur(0);
}
.email-spoiler .email-reveal-hint {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 12px;
  color: #ccc;
  opacity: 0.7;
  pointer-events: none;
  transition: opacity 0.3s ease;
}
.email-spoiler.revealed .email-reveal-hint {
  opacity: 0;
  pointer-events: none;
}
.email-spoiler:hover .email-reveal-hint {
  opacity: 1;
}

/* Position the footer below the sunset */
footer {
  position: relative !important;
  z-index: 50 !important;
}

/* Responsive adjustments */
@media only screen and (max-width: 768px) {
  .well {
    padding: 20px 25px !important;
  }
}
</style>
{{< /rawhtml >}}

Hello! I am a **plant biotechnologist**, **humanist**, and **optimist** - the second two lead me to the first. I am married to [Haoxing Du](https://www.haoxingdu.com/), we currently live in California.

I am deeply inspired by [effective altruism](https://www.effectivealtruism.org/), which aims to use engineering-style thinking to do as much good as possible. This moral inclination led me to choose the field of plant biotechnology as a lever for improving global human welfare, because plants constitute the vast majority of the human food supply and nutritional deficiencies have always been among humanity's top problems (but might not be in another few decades!)

Outside of my career, I enjoy **rock climbing**, **paragliding**, **wingfoiling**, **backpacking**, and **making things**.

{{< rawhtml >}}
<p>You can contact me at <span class="email-spoiler" onclick="this.classList.toggle('revealed')">
  <span class="email-blurred">Kaseymarkel@gmail.com</span>
  <span class="email-reveal-hint">Click to reveal</span>
</span></p>
{{< /rawhtml >}}

