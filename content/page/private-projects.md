---
title: "Private Projects"
socialShare: false
---

{{< rawhtml >}}
<style>
.intro-header { display: none !important; }
.header-section.has-img { display: none !important; }

div[role="main"].container {
  padding-top: 80px !important;
  margin-top: 0 !important;
  max-width: 100% !important;
  padding-left: 0 !important;
  padding-right: 0 !important;
}

footer { display: none !important; }

.password-gate {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.password-box {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
  text-align: center;
  max-width: 400px;
  width: 90%;
}

.password-box h2 {
  color: #333;
  margin-bottom: 10px;
  font-size: 1.5rem;
}

.password-box p {
  color: #666;
  margin-bottom: 25px;
  font-size: 0.95rem;
}

.password-box input[type="password"] {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  margin-bottom: 15px;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.password-box input[type="password"]:focus {
  outline: none;
  border-color: #667eea;
}

.password-box button {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.password-box button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.password-error {
  color: #ef4444;
  font-size: 0.9rem;
  margin-top: 10px;
  display: none;
}

.password-error.show { display: block; }

/* Project listing styles */
#projects-container {
  display: none;
  min-height: 80vh;
  background: #f8f9fa;
  padding: 60px 20px;
}

#projects-container.unlocked { display: block; }

.projects-header {
  text-align: center;
  margin-bottom: 50px;
}

.projects-header h1 {
  font-size: 2rem;
  color: #333;
  margin-bottom: 8px;
}

.projects-header p {
  color: #666;
  font-size: 1.1rem;
}

.projects-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 30px;
  justify-content: center;
  max-width: 900px;
  margin: 0 auto;
}

.project-card {
  background: white;
  border-radius: 16px;
  padding: 36px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  width: 380px;
  text-decoration: none;
  color: inherit;
  transition: transform 0.2s, box-shadow 0.2s;
  display: block;
}

.project-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0,0,0,0.12);
  text-decoration: none;
  color: inherit;
}

.project-card .card-icon {
  font-size: 2.5rem;
  margin-bottom: 16px;
}

.project-card h3 {
  font-size: 1.3rem;
  color: #333;
  margin-bottom: 10px;
}

.project-card p {
  color: #666;
  font-size: 0.95rem;
  line-height: 1.5;
}

.project-card .card-tag {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  margin-top: 16px;
}

.tag-live {
  background: #dcfce7;
  color: #166534;
}

.tag-new {
  background: #fef3c7;
  color: #92400e;
}
</style>

<div id="password-gate" class="password-gate">
  <div class="password-box">
    <h2>Private Projects</h2>
    <p>Enter password to access</p>
    <input type="password" id="pp-password" placeholder="Enter password" onkeypress="if(event.key === 'Enter') checkPPPassword()">
    <button onclick="checkPPPassword()">Access Projects</button>
    <p id="pp-error" class="password-error">Incorrect password. Please try again.</p>
  </div>
</div>

<div id="projects-container">
  <div class="projects-header">
    <h1>Private Projects</h1>
    <p>Select a project to view</p>
  </div>
  <div class="projects-grid">
    <a class="project-card" href="/page/dashboard/">
      <div class="card-icon">🌱</div>
      <h3>Breeding Dashboard</h3>
      <p>Real-time breeding program metrics — pipeline funnel, trait pyramiding, cycle speed, and operational issues.</p>
      <span class="card-tag tag-live">Live</span>
    </a>
    <a class="project-card" href="/page/cea-dashboard/">
      <div class="card-icon">📊</div>
      <h3>Biofortified Maize CEA</h3>
      <p>Interactive cost-effectiveness analysis for Semilla Nueva's biofortified maize program — DALYs, WELLBYs, and benefit-cost modeling.</p>
      <span class="card-tag tag-new">New</span>
    </a>
  </div>
</div>

<script>
function checkPPPassword() {
  var input = document.getElementById('pp-password');
  var error = document.getElementById('pp-error');
  var gate = document.getElementById('password-gate');
  var container = document.getElementById('projects-container');

  if (input.value === 'Semilla') {
    gate.style.display = 'none';
    container.classList.add('unlocked');
    sessionStorage.setItem('private-projects-auth', 'true');
  } else {
    error.classList.add('show');
    input.value = '';
    input.focus();
  }
}

document.addEventListener('DOMContentLoaded', function() {
  if (sessionStorage.getItem('private-projects-auth') === 'true') {
    document.getElementById('password-gate').style.display = 'none';
    document.getElementById('projects-container').classList.add('unlocked');
  }
});
</script>
{{< /rawhtml >}}
