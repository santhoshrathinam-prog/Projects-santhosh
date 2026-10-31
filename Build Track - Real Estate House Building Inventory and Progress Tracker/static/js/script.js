/**
 * BuildTrack - Real Estate House Building Inventory Management System
 * Core Client-Side Utilities and Dynamic Calculators
 */

document.addEventListener("DOMContentLoaded", function () {
  // 1. Mobile Sidebar Toggle
  const sidebarToggle = document.getElementById("sidebarToggle");
  const sidebar = document.querySelector(".sidebar");
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener("click", function () {
      sidebar.classList.toggle("show");
    });

    // Close when clicking outside on mobile
    document.addEventListener("click", function (e) {
      if (window.innerWidth < 992) {
        if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
          sidebar.classList.remove("show");
        }
      }
    });
  }

  // 2. Material Select Auto-Unit and Available Stock Populator
  const materialSelects = document.querySelectorAll(".material-ajax-select");
  materialSelects.forEach(function (select) {
    select.addEventListener("change", function () {
      const materialId = this.value;
      if (!materialId) return;

      fetch(`/api/materials/${materialId}`)
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            const mat = data.material;
            // Update all unit placeholders
            document.querySelectorAll(".material-unit-label").forEach((el) => {
              el.textContent = mat.unit;
            });
            // Update available stock badge if present
            const availBadge = document.getElementById("availableStockBadge");
            if (availBadge) {
              availBadge.textContent = `${mat.available_quantity} ${mat.unit}`;
              availBadge.className = "badge " + (mat.available_quantity <= 0 ? "bg-danger" : (mat.available_quantity <= mat.minimum_stock_level ? "bg-warning text-dark" : "bg-success"));
            }
            // Update unit price field if present
            const priceInput = document.getElementById("unit_price");
            if (priceInput && !priceInput.value) {
              priceInput.value = mat.unit_price;
              calculateInwardTotal();
            }
            // Update max constraint for outward quantity
            const outwardQtyInput = document.getElementById("outward_quantity");
            if (outwardQtyInput) {
              outwardQtyInput.setAttribute("max", mat.available_quantity);
            }
          }
        })
        .catch((err) => console.error("Error fetching material info:", err));
    });
  });

  // 3. Inward Total Cost Calculator
  const inwardQty = document.getElementById("inward_quantity");
  const inwardPrice = document.getElementById("unit_price");
  const inwardTotal = document.getElementById("total_cost_display");

  function calculateInwardTotal() {
    if (inwardQty && inwardPrice && inwardTotal) {
      const qty = parseFloat(inwardQty.value) || 0;
      const price = parseFloat(inwardPrice.value) || 0;
      const total = qty * price;
      inwardTotal.value = `₹ ${total.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }
  }

  if (inwardQty) inwardQty.addEventListener("input", calculateInwardTotal);
  if (inwardPrice) inwardPrice.addEventListener("input", calculateInwardTotal);

  // 4. Builder Live Stock Calculator: Remaining = Opening + Received - Used
  const openStockInput = document.getElementById("opening_stock");
  const recvStockInput = document.getElementById("material_received");
  const usedStockInput = document.getElementById("material_used");
  const remStockDisplay = document.getElementById("remaining_stock_display");
  const remStockWarning = document.getElementById("remaining_stock_warning");
  const submitStockBtn = document.getElementById("submitStockBtn");

  function calculateBuilderRemaining() {
    if (openStockInput && recvStockInput && usedStockInput && remStockDisplay) {
      const open = parseFloat(openStockInput.value) || 0;
      const recv = parseFloat(recvStockInput.value) || 0;
      const used = parseFloat(usedStockInput.value) || 0;
      const remaining = open + recv - used;

      remStockDisplay.value = remaining.toFixed(2);

      if (remaining < 0) {
        remStockDisplay.classList.add("is-invalid");
        if (remStockWarning) remStockWarning.classList.remove("d-none");
        if (submitStockBtn) submitStockBtn.disabled = true;
      } else {
        remStockDisplay.classList.remove("is-invalid");
        if (remStockWarning) remStockWarning.classList.add("d-none");
        if (submitStockBtn) submitStockBtn.disabled = false;
      }
    }
  }

  if (openStockInput) openStockInput.addEventListener("input", calculateBuilderRemaining);
  if (recvStockInput) recvStockInput.addEventListener("input", calculateBuilderRemaining);
  if (usedStockInput) usedStockInput.addEventListener("input", calculateBuilderRemaining);

  // 5. Auto-dismiss alerts after 6 seconds
  setTimeout(function () {
    const alerts = document.querySelectorAll(".alert-dismissible");
    alerts.forEach(function (alert) {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    });
  }, 6000);
});
