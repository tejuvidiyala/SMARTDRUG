async function analyze(){
  const medicine = document.getElementById("medicineInput").value;
  const food = document.getElementById("foodInput").value;
  const allergies = document.getElementById("allergyInput").value
      .split(",").map(a=>a.trim()).filter(a=>a);

  const res = await fetch("http://127.0.0.1:5000/analyze",{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({medicine, food, allergies})
  });

  const data = await res.json();

  const riskBar = document.getElementById("riskBar");
  const result = document.getElementById("analysisResult");

  if(!data.found){
    result.innerHTML = data.message;
    return;
  }

  const risk = Math.round(data.risk_probability * 100);
  riskBar.style.width = risk + "%";

  let color = "green";
  if(risk > 75) color = "red";
  else if(risk > 45) color = "orange";

  riskBar.style.background = color;

  result.innerHTML = `
    <h2>Severity: ${data.severity}</h2>
    <p><strong>Risk:</strong> ${risk}%</p>
    <p><strong>Confidence:</strong> ${Math.round(data.confidence*100)}%</p>

    <p><strong>Reason:</strong> ${data.interaction_reason}</p>
    <p><strong>Time Gap:</strong> ${data.time_gap}</p>

    <p><strong>About Drug:</strong></p>
    <p>${data.drug_info}</p>

    <p><strong>Side Effects:</strong></p>
    <ul>${data.side_effects.map(s=>`<li>${s}</li>`).join("")}</ul>

    <p><strong>Alternatives:</strong></p>
    <ul>${data.alternatives.map(a=>`<li>${a}</li>`).join("")}</ul>

    <p><strong>Recipes:</strong></p>
    <ul>${data.recipes.map(r=>`<li>${r}</li>`).join("")}</ul>
  `;
}