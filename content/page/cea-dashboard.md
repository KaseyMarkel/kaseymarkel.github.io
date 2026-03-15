---
title: "Biofortified Maize CEA Dashboard"
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

.password-box h2 { color: #333; margin-bottom: 10px; font-size: 1.5rem; }
.password-box p { color: #666; margin-bottom: 25px; font-size: 0.95rem; }

.password-box input[type="password"] {
  width: 100%; padding: 12px 16px; border: 2px solid #e0e0e0;
  border-radius: 8px; font-size: 1rem; margin-bottom: 15px;
  transition: border-color 0.2s; box-sizing: border-box;
}

.password-box input[type="password"]:focus { outline: none; border-color: #667eea; }

.password-box button {
  width: 100%; padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white; border: none; border-radius: 8px;
  font-size: 1rem; font-weight: 600; cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.password-box button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.password-error { color: #ef4444; font-size: 0.9rem; margin-top: 10px; display: none; }
.password-error.show { display: block; }

#cea-container { display: none; }
#cea-container.unlocked { display: block; }

.back-link {
  display: inline-block;
  padding: 8px 16px;
  margin: 10px 20px;
  color: #667eea;
  text-decoration: none;
  font-size: 0.9rem;
}
.back-link:hover { text-decoration: underline; }
</style>

<div id="password-gate" class="password-gate">
  <div class="password-box">
    <h2>CEA Dashboard</h2>
    <p>Enter password to access</p>
    <input type="password" id="cea-password" placeholder="Enter password" onkeypress="if(event.key === 'Enter') checkCEAPassword()">
    <button onclick="checkCEAPassword()">Access Dashboard</button>
    <p id="cea-error" class="password-error">Incorrect password. Please try again.</p>
  </div>
</div>

<div id="cea-container">
  <a class="back-link" href="/page/private-projects/">&larr; Back to Private Projects</a>
  <iframe id="cea-frame" src="/cea-dashboard/" style="width: 100%; height: calc(100vh - 100px); border: none;"></iframe>
</div>

<script>
function checkCEAPassword() {
  var input = document.getElementById('cea-password');
  var error = document.getElementById('cea-error');
  var gate = document.getElementById('password-gate');
  var container = document.getElementById('cea-container');

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
    document.getElementById('cea-container').classList.add('unlocked');
  }
});
</script>
{{< /rawhtml >}}
