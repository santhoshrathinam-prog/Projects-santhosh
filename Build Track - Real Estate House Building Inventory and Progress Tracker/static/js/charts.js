/**
 * BuildTrack - Admin Dashboard Chart Visualizations (Chart.js)
 */

function initDashboardCharts(houseStats, invStats, stageData) {
  // 1. House Status Doughnut Chart
  const houseCtx = document.getElementById("houseStatusChart");
  if (houseCtx && houseStats) {
    new Chart(houseCtx, {
      type: "doughnut",
      data: {
        labels: ["Planned", "Under Construction", "On Hold", "Completed"],
        datasets: [{
          data: [
            houseStats.planned || 0,
            houseStats.under_construction || 0,
            houseStats.on_hold || 0,
            houseStats.completed || 0
          ],
          backgroundColor: ["#94a3b8", "#3b82f6", "#f59e0b", "#10b981"],
          borderWidth: 2,
          borderColor: "#ffffff"
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "bottom", labels: { boxWidth: 12, font: { size: 11 } } }
        },
        cutout: "68%"
      }
    });
  }

  // 2. Material Stock Status Doughnut Chart
  const invCtx = document.getElementById("invStatusChart");
  if (invCtx && invStats) {
    new Chart(invCtx, {
      type: "doughnut",
      data: {
        labels: ["Available", "Low Stock", "Out of Stock"],
        datasets: [{
          data: [
            invStats.available || 0,
            invStats.low_stock || 0,
            invStats.out_of_stock || 0
          ],
          backgroundColor: ["#10b981", "#f59e0b", "#ef4444"],
          borderWidth: 2,
          borderColor: "#ffffff"
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "bottom", labels: { boxWidth: 12, font: { size: 11 } } }
        },
        cutout: "68%"
      }
    });
  }

  // 3. Construction Stage Distribution Bar Chart
  const stageCtx = document.getElementById("stageDistChart");
  if (stageCtx && stageData) {
    const labels = stageData.map(item => item.construction_stage);
    const counts = stageData.map(item => item.cnt);

    new Chart(stageCtx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [{
          label: "Number of Houses",
          data: counts,
          backgroundColor: "#3b82f6",
          borderRadius: 6,
          maxBarThickness: 32
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            ticks: { stepSize: 1, precision: 0 }
          },
          x: {
            grid: { display: false },
            ticks: { font: { size: 11 } }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }
}
