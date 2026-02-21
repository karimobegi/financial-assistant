API_BASE = window.location.origin;
let chart1 = null;
let chart2 = null;
let chart3 = null;
let chart4 = null;
function monthlyChart(summary){
    const monthly = summary.monthly || [];

  if (monthly.length === 0) {
    // show empty state text somewhere
    return;
  }
   if (chart1) chart1.destroy();
    chart1 = new Chart(document.getElementById("chart1"), {
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

function categoryChart(summary){
    const category = summary.category_spend || [];
    if (category.length === 0){
        return;
    }
    if (chart2) chart2.destroy();
    chart2 = new Chart(document.getElementById("chart2"), {
    type: 'doughnut',
    data: {
      labels: category.map(row => row.category),
      datasets: [{
        label: 'Spending by Category',
        data: category.map(row => row.amount),
        borderWidth: 1
      },
    ]
    },
    options: {responsive: true, maintainAspectRatio: false }
  });
};

function merchantChart(summary){
    const merchant = summary.top_merchants;
    if (merchant.length === 0){
        return;
    }
    if (chart3) chart3.destroy();
    chart3 = new Chart(document.getElementById("chart3"), {
    type: 'bar',
    data: {
      labels: merchant.map(row => row.merchant),
      datasets: [{
        label: 'Merchants',
        data: merchant.map(row => row.amount),
        borderWidth: 1
      }
    ]
    },
    options: { indexAxis : "y", responsive: true, maintainAspectRatio: false }
  })

}

function transactionChart(summary){
    const transactions = summary.large_transactions;
    if (transactions.length === 0){
        return;
    }
    if (chart4) chart4.destroy();
    chart4 = new Chart(document.getElementById("chart4"), {
    type: 'bar',
    data: {
      labels: transactions.map(row => (row.date, row.merchant)),
      datasets: [{
        label: 'Transactions',
        data: transactions.map(row => row.amount),
        borderWidth: 1
      }
    ]
    },
    options: { indexAxis : "y", responsive: true, maintainAspectRatio: false }
  })
}

function renderDashboard(summary){
    monthlyChart(summary);
    categoryChart(summary);
    merchantChart(summary);
    transactionChart(summary);

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
document.addEventListener("DOMContentLoaded", loadDashboard);