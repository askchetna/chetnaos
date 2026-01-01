// frontend/kalpavriksha_ui/js/crop.js
async function planCrop() {
    const soil_ph = parseFloat(document.getElementById('soil_ph').value || 7.0);
    const temp = parseFloat(document.getElementById('temp').value || 28);
    const water_depth = parseFloat(document.getElementById('water_depth').value || 10);
    const soil_type = document.getElementById('soil_type').value;
    const road_access = document.getElementById('road_access').value;
    const acres = parseFloat(document.getElementById('acres').value || 1);
  
    const payload = { soil_ph, temp, water_depth, soil_type, road_access, acres };
  
    const resultBox = document.getElementById('result');
    resultBox.innerHTML = 'Planning...';
    resultBox.classList.remove('hidden');
  
    try {
      const resp = await fetch('http://127.0.0.1:8000/crop', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
  
      if (!resp.ok) {
        const err = await resp.json().catch(()=>({error: 'server error'}));
        resultBox.innerHTML = '<pre style="color:red;">API error: ' + JSON.stringify(err) + '</pre>';
        return;
      }
  
      const data = await resp.json();
      // render top 3 recommendations
      let html = '<h3>Recommendations</h3>';
      html += '<ol>';
      data.ranked_recommendations.slice(0,6).forEach(r => {
        html += `<li><strong>${r.crop}</strong> — Score: ${r.score}<br/>Note: ${r.note}<br/>Economics: <pre>${JSON.stringify(r.economics, null, 2)}</pre></li>`;
      });
      html += '</ol>';
      resultBox.innerHTML = html;
    } catch (e) {
      resultBox.innerHTML = '<pre style="color:red;">' + e.toString() + '</pre>';
    }
  }
  
  document.getElementById('planBtn').addEventListener('click', planCrop);