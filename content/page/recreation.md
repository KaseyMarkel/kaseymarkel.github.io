---
title: "Recreation"
socialShare: false
---

{{< rawhtml >}}
<style>
/* Hide entire header section and add top spacing */
.intro-header {
  display: none !important;
}
.header-section.has-img {
  display: none !important;
}

/* Add top padding to main content to account for navigation bar */
div[role="main"].container {
  padding-top: 120px !important;
  margin-top: 0 !important;
}

.recreation-section {
  margin-bottom: 60px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}
.recreation-section.reverse {
  flex-direction: row-reverse;
}
.recreation-text {
  flex: 1;
  min-width: 300px;
  padding: 20px 30px;
}
.recreation-image {
  flex: 1;
  min-width: 300px;
  padding: 20px;
  position: relative;
}
.recreation-image-wrapper {
  position: relative;
  display: inline-block;
  width: 100%;
}
.recreation-image img {
  width: 100%;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  max-width: 100%;
  display: block;
}
/* Image caption overlay - matches image size exactly */
.recreation-image-caption {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 20px;
  border-radius: 8px;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
  box-sizing: border-box;
}
.recreation-image-wrapper:hover .recreation-image-caption {
  opacity: 1;
}
.recreation-image-caption p {
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
}
@media (max-width: 768px) {
  .recreation-section {
    flex-direction: column !important;
  }
  .recreation-text {
    padding: 20px 0;
  }
}
</style>
{{< /rawhtml >}}

Outside of work, I'm passionate about outdoor adventure sports and creative pursuits. Here are some of the activities I enjoy:

{{< rawhtml >}}
<div class="recreation-section">
  <div class="recreation-text">
    <h2>Rock Climbing</h2>
    <p>Rock climbing combines physical challenge with problem-solving in beautiful natural settings. Whether it's bouldering, sport climbing, or traditional climbing, I love the mental and physical aspects of this sport. These days my climbing mostly consists of regular social sessions in the gym and low-frequency trips for big trad lines like Matthes Crest and Saber Ridge.</p>
  </div>
  <div class="recreation-image">
    <div class="recreation-image-wrapper">
      <img src="/img/Climbing%20pic%20for%20website.jpg" alt="Rock Climbing">
      <div class="recreation-image-caption">
        <p>Matthes crest in Yosemite. My brother Kory is visible ~50 meters away on the ridge, following on simul-climb.</p>
      </div>
    </div>
  </div>
</div>

<div class="recreation-section reverse">
  <div class="recreation-text">
    <h2>Paragliding</h2>
    <p>Flying through the air with nothing but a wing and harness is an incredible experience. Paragliding offers a unique perspective on the world below and the freedom of flight. It's an aircraft that fits in a backpack - what more could you want?</p>
  </div>
  <div class="recreation-image">
    <div class="recreation-image-wrapper">
      <img src="/img/shasta%20pic%20for%20website.jpg" alt="Paragliding">
      <div class="recreation-image-caption">
        <p>Flying near Mount Shasta. Photo credit to my wife Haoxing, who was slightly above me one thermal to the North.</p>
      </div>
    </div>
  </div>
</div>

<div class="recreation-section">
  <div class="recreation-text">
    <h2>Wingfoiling</h2>
    <p>Wingfoiling combines elements of windsurfing, kitesurfing, and foiling into one exciting water sport. It's a relatively new discipline that's rapidly growing in popularity. It's an awesome way to explore the bay: cheaper, faster, and more flexible than sailing, but with the right gear still secure enough to be comfortable going miles from shore.</p>
  </div>
  <div class="recreation-image">
    <div class="recreation-image-wrapper">
      <img src="/img/wingfoiling%20pic.JPG" alt="Wingfoiling">
      <div class="recreation-image-caption">
        <p>Wingfoiling on the bay. Hair down and no shades for the photo, normally I'm fairly covered and a lot harder to identify. Photo credit @drethelin</p>
      </div>
    </div>
  </div>
</div>

<div class="recreation-section reverse">
  <div class="recreation-text">
    <h2>Backpacking</h2>
    <p>Exploring remote wilderness areas with everything I need on my back is one of my favorite ways to disconnect and reconnect with nature. There's something special about waking up to a sunrise in the backcountry. I've thru-hiked the Colorado Trail, Tour du Mont Blanc, and Cradle Mountain Trek.</p>
  </div>
  <div class="recreation-image">
    <div class="recreation-image-wrapper">
      <img src="/img/website%20backpacking%20photo.jpg" alt="Backpacking">
      <div class="recreation-image-caption">
        <p>An October blizzard on a solo trip in the Wind River Range in Wyoming. Extremely cold, but beautiful. I love nice weather as much as the next guy, but inclement conditions offer a different experience, and almost guarantee a good amount of solitude.</p>
      </div>
    </div>
  </div>
</div>
{{< /rawhtml >}}

## Making Things

I enjoy working with my hands and creating things, whether it's woodworking, electronics projects, or other DIY endeavors. There's satisfaction in bringing an idea from concept to reality.

{{< rawhtml >}}
<style>
.things-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-top: 30px;
  margin-bottom: 40px;
}
.thing-button {
  display: block;
  padding: 20px;
  text-align: center;
  background-color: #f5f5f5;
  border: 2px solid #0085a1;
  border-radius: 8px;
  color: #0085a1;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
}
.thing-button:hover {
  background-color: #0085a1;
  color: white;
  text-decoration: none;
}
@media (max-width: 768px) {
  .things-grid {
    grid-template-columns: 1fr;
  }
}
</style>

<div class="things-grid">
  <a href="/page/wing-watchers-perch/" class="thing-button">Wing Watcher's Perch</a>
  <a href="/page/living-wall/" class="thing-button">Living Wall</a>
  <a href="/page/origin/" class="thing-button">Origin</a>
  <a href="/page/glass/" class="thing-button">Glass</a>
  <a href="/page/gallery/" class="thing-button">Pour Paintings</a>
</div>
{{< /rawhtml >}}

