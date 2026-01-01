---
title: "Recreation"
socialShare: false
---

{{< rawhtml >}}
<style>
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
}
.recreation-image img {
  width: 100%;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
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

Outside of my academic work, I'm passionate about outdoor adventure sports and creative pursuits. Here are some of the activities I enjoy:

{{< rawhtml >}}
<div class="recreation-section">
  <div class="recreation-text">
    <h2>Rock Climbing</h2>
    <p>Rock climbing combines physical challenge with problem-solving in beautiful natural settings. Whether it's bouldering, sport climbing, or traditional climbing, I love the mental and physical aspects of this sport.</p>
  </div>
  <div class="recreation-image">
    <img src="/img/Climbing%20pic%20for%20website.jpg" alt="Rock Climbing">
  </div>
</div>

<div class="recreation-section reverse">
  <div class="recreation-text">
    <h2>Paragliding</h2>
    <p>Flying through the air with nothing but a wing and harness is an incredible experience. Paragliding offers a unique perspective on the world below and the freedom of flight.</p>
  </div>
  <div class="recreation-image">
    <img src="/img/shasta%20pic%20for%20website.jpg" alt="Paragliding">
  </div>
</div>

<div class="recreation-section">
  <div class="recreation-text">
    <h2>Wingfoiling</h2>
    <p>Wingfoiling combines elements of windsurfing, kitesurfing, and foiling into one exciting water sport. It's a relatively new discipline that's rapidly growing in popularity.</p>
  </div>
  <div class="recreation-image">
    <img src="/img/wingfoiling%20pic.JPG" alt="Wingfoiling">
  </div>
</div>

<div class="recreation-section reverse">
  <div class="recreation-text">
    <h2>Backpacking</h2>
    <p>Exploring remote wilderness areas with everything I need on my back is one of my favorite ways to disconnect and reconnect with nature. There's something special about waking up to a sunrise in the backcountry.</p>
  </div>
  <div class="recreation-image">
    <img src="/img/website%20backpacking%20photo.jpg" alt="Backpacking">
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
  <a href="/page/thing-1/" class="thing-button">Wing Watcher's Perch</a>
  <a href="/page/thing-2/" class="thing-button">Living Wall</a>
  <a href="/page/thing-3/" class="thing-button">Thing 3</a>
  <a href="/page/thing-4/" class="thing-button">Thing 4</a>
</div>
{{< /rawhtml >}}

