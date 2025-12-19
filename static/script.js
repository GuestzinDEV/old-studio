async function loadStats() {
  const res = await fetch("/stats");
  const data = await res.json();

  document.getElementById("visitors").textContent = data.total_visits;
  document.getElementById("online").textContent = data.online_users;
}

loadStats();
setInterval(loadStats, 5000);
