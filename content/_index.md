---
title: "About me"
socialShare: false
---

{{< rawhtml >}}
<style>
/* Custom styles for home page with full-height image and overlay content */
body {
  position: relative;
}

.header-section.has-img {
  position: relative;
  margin-bottom: 0;
}

.intro-header.big-img {
  background-size: contain !important;
  background-position: center top !important;
  margin-bottom: 0 !important;
  position: relative;
  /* Set height based on image aspect ratio - adjust as needed */
  height: auto;
  min-height: 56.25vw; /* Approximate aspect ratio of sunset image */
}

.intro-header.big-img .page-heading {
  padding: 40px 0 20px 0 !important;
}

.intro-header.big-img .page-heading h1 {
  font-size: 30px !important;
  margin-bottom: 10px;
}

.intro-header.big-img .page-subheading {
  display: none !important;
}

/* Position content overlay - fixed position relative to image using vw units */
div[role="main"].container {
  position: absolute;
  top: 22vw; /* Position based on viewport width to match image scaling */
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 1200px;
  z-index: 100;
  padding-left: 15px;
  padding-right: 15px;
}

/* Position footer right below the header image */
footer {
  position: relative;
  margin-top: 0 !important;
}

.well {
  background-color: rgba(60, 60, 60, 0.4) !important;
  border: none !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
}

div[role="main"] .container .row .col-lg-8 .well {
  position: relative;
  padding: 30px 40px;
  border-radius: 8px;
  color: #fff;
  margin: 0 auto;
  backdrop-filter: blur(5px);
  max-width: 800px;
}

.container .row .col-lg-8 .well p {
  color: #fff;
  margin-bottom: 15px;
  line-height: 1.7;
}

.container .row .col-lg-8 .well strong {
  color: #fff;
}

.container .row .col-lg-8 .well a {
  color: #a8d5ff;
  text-decoration: none;
}

.container .row .col-lg-8 .well a:hover {
  color: #c4e3ff;
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

/* Responsive adjustments */
@media only screen and (max-width: 768px) {
  .intro-header.big-img .page-heading h1 {
    font-size: 25px !important;
  }
  
  .container .row .col-lg-8 .well {
    padding: 20px 25px;
    width: calc(100% - 20px);
  }
  
  div[role="main"].container {
    top: 22vw;
    transform: translateX(-50%);
  }
}

@media only screen and (min-width: 768px) {
  .intro-header.big-img .page-heading h1 {
    font-size: 35px !important;
  }
  
  div[role="main"].container {
    top: 22vw;
    transform: translateX(-50%);
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

