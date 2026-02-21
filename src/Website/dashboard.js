API_BASE = window.location.origin;

function renderDashboard(summary){
    const monthly = summary.monthly || [];

  if (monthly.length === 0) {
    // show empty state text somewhere
    return;
  }
   if (chart1) chart1.destroy();
new Chart(document.getElementById("chart1"), {
    type: 'bar',
    data: {
      labels: monthly.map(row => row.month),
      datasets: [{
        label: 'Income',
        data: monthly.map(row => row.income),
        borderWidth: 1
      },
      {
        label: 'Expenses',
        data: monthly.map(row => row.expenses),
        borderWidth: 1
      },
      {
        type: 'line',
        label: 'Net',
        data: monthly.map(row => row.net),
        tension: 0.2
      }
    ]
    },
    options: {responsive: true, maintainAspectRatio: false }
  });


}



async function loadDashboard() {
    try {
        const res = await fetch(`${API_BASE}/analysis/summary`);

        if (!res.ok) {
            throw new Error("Failed to load dashboard");
        }

        const summary = await res.json();

        renderDashboard(summary);

    } catch (error) {
        console.error(error);
    }
}