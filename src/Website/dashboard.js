API_BASE = window.location.origin;

function renderDashboard(summary){};
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