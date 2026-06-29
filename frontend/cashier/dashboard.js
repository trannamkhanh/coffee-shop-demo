const API = window.APP_CONFIG?.API_BASE_URL || "/api";
const token = localStorage.getItem("token");
const chucVu = localStorage.getItem("chuc_vu");
const hoTen = localStorage.getItem("ho_ten");

// --- Auth check ---
if (!token) {
  window.location.href = "../shared/login.html";
}

// --- Helpers ---
function apiHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

function formatMoney(n) {
  return new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
  }).format(n);
}

function formatDate(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleString("vi-VN");
}

function logout() {
  localStorage.clear();
  window.location.href = "../shared/login.html";
}

// --- Init ---
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("user-info").textContent = `${hoTen} (${chucVu})`;
  loadOccupiedTables();
  loadInvoices();
});

// --- Load occupied tables ---
async function loadOccupiedTables() {
  const grid = document.getElementById("table-grid");
  grid.innerHTML =
    '<div class="col-span-full text-center text-gray-400 py-4"><i class="fas fa-spinner fa-spin mr-2"></i>Đang tải...</div>';

  try {
    const res = await fetch(`${API}/cashier/ban-co-khach`, {
      headers: apiHeaders(),
    });
    if (res.status === 401) logout();
    const tables = await res.json();

    grid.innerHTML = "";
    if (tables.length === 0) {
      grid.innerHTML =
        '<div class="col-span-full text-center text-gray-400 py-4"><i class="fas fa-check-circle text-green-400 mr-2"></i>Hiện không có bàn nào đang có khách</div>';
      return;
    }

    tables.forEach((t) => {
      const div = document.createElement("div");
      div.className =
        "bg-white rounded-xl shadow p-4 text-center border-l-4 border-green-500 cursor-pointer hover:shadow-lg transition";
      div.innerHTML = `
                <i class="fas fa-chair text-3xl text-green-600 mb-2"></i>
                <p class="font-bold text-gray-800">${t.TenBan}</p>
                <p class="text-xs text-gray-400">${t.Ma_QR_Code}</p>
            `;
      div.onclick = () => showInvoiceDetail(t.ID_Ban);
      grid.appendChild(div);
    });
  } catch {
    grid.innerHTML =
      '<div class="col-span-full text-center text-red-400">Lỗi tải dữ liệu</div>';
  }
}

// --- Load invoices ---
async function loadInvoices() {
  const container = document.getElementById("invoice-list");
  container.innerHTML =
    '<div class="text-center text-gray-400 py-4"><i class="fas fa-spinner fa-spin mr-2"></i>Đang tải...</div>';

  try {
    const res = await fetch(`${API}/cashier/hoa-don-chua-thanh-toan`, {
      headers: apiHeaders(),
    });
    if (res.status === 401) logout();
    const invoices = await res.json();

    container.innerHTML = "";
    if (invoices.length === 0) {
      container.innerHTML =
        '<div class="text-center text-gray-400 py-8 bg-white rounded-xl shadow"><i class="fas fa-check-circle text-green-400 text-3xl mb-2"></i><p>Tất cả hóa đơn đã được thanh toán</p></div>';
      return;
    }

    invoices.forEach((inv) => {
      const div = document.createElement("div");
      div.className = "bg-white rounded-xl shadow p-4";
      div.innerHTML = `
                <div class="flex justify-between items-start mb-3">
                    <div>
                        <p class="font-bold text-gray-800">
                            <i class="fas fa-chair mr-1 text-amber-600"></i>Bàn ${inv.TenBan}
                        </p>
                        <p class="text-xs text-gray-400">${formatDate(inv.ThoiGianTao)}</p>
                    </div>
                    <span class="text-xl font-bold text-red-600">${formatMoney(inv.TongTien)}</span>
                </div>
                <div class="border-t pt-2 space-y-1 text-sm text-gray-600">
                    ${inv.chi_tiet
                      .slice(0, 3)
                      .map(
                        (c) =>
                          `<div class="flex justify-between">
                            <span>${c.TenMon} x${c.SoLuong}</span>
                            <span>${formatMoney(c.ThanhTien)}</span>
                        </div>`,
                      )
                      .join("")}
                    ${inv.chi_tiet.length > 3 ? `<p class="text-xs text-gray-400">...và ${inv.chi_tiet.length - 3} món khác</p>` : ""}
                </div>
                <div class="flex gap-2 mt-3">
                    <button onclick="showInvoiceDetail(${inv.ID_Ban})" class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 py-2 rounded-lg text-sm font-medium transition">
                        <i class="fas fa-eye mr-1"></i>Chi tiết
                    </button>
                    <button onclick="processPayment(${inv.ID_HoaDon})" class="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 rounded-lg text-sm font-medium transition">
                        <i class="fas fa-check mr-1"></i>Thanh toán
                    </button>
                </div>
            `;
      container.appendChild(div);
    });
  } catch {
    container.innerHTML =
      '<div class="text-center text-red-400">Lỗi tải dữ liệu</div>';
  }
}

// --- Show invoice detail modal ---
async function showInvoiceDetail(idBan) {
  const modal = document.getElementById("invoice-modal");
  const body = document.getElementById("modal-body");
  body.innerHTML =
    '<div class="text-center py-4"><i class="fas fa-spinner fa-spin"></i></div>';
  modal.classList.remove("hidden");
  modal.classList.add("flex");

  try {
    const res = await fetch(`${API}/cashier/ban/${idBan}/hoa-don-chi-tiet`, {
      headers: apiHeaders(),
    });
    if (!res.ok) throw new Error("Không có hóa đơn");
    const inv = await res.json();

    body.innerHTML = `
            <div class="space-y-3">
                <p class="text-sm text-gray-500">${formatDate(inv.ThoiGianTao)}</p>
                <div class="border-t border-b py-3 space-y-2 max-h-60 overflow-y-auto">
                    ${inv.chi_tiet
                      .map(
                        (c) =>
                          `<div class="flex justify-between text-sm">
                            <span>${c.TenMon} <span class="text-gray-400">x${c.SoLuong}</span></span>
                            <span class="font-medium">${formatMoney(c.ThanhTien)}</span>
                        </div>`,
                      )
                      .join("")}
                </div>
                <div class="flex justify-between text-lg font-bold">
                    <span>Tổng cộng</span>
                    <span class="text-red-600">${formatMoney(inv.TongTien)}</span>
                </div>
                <button onclick="processPayment(${inv.ID_HoaDon})" class="w-full bg-green-600 hover:bg-green-700 text-white py-3 rounded-lg font-semibold transition">
                    <i class="fas fa-check mr-2"></i>Xác nhận thanh toán
                </button>
                <button onclick="closeModal()" class="w-full bg-gray-100 hover:bg-gray-200 text-gray-600 py-2 rounded-lg text-sm transition">
                    Đóng
                </button>
            </div>
        `;
  } catch (err) {
    body.innerHTML = `<div class="text-center text-red-500 py-4">${err.message}</div>`;
  }
}

function closeModal() {
  document.getElementById("invoice-modal").classList.add("hidden");
  document.getElementById("invoice-modal").classList.remove("flex");
}

// --- Process payment ---
async function processPayment(idHoaDon) {
  const result = await Swal.fire({
    title: "Xác nhận thanh toán?",
    text: "Sau khi xác nhận, hóa đơn sẽ được đóng lại.",
    icon: "question",
    showCancelButton: true,
    confirmButtonColor: "#16a34a",
    confirmButtonText: "Xác nhận",
    cancelButtonText: "Hủy",
  });

  if (!result.isConfirmed) return;

  try {
    const res = await fetch(`${API}/cashier/thanh-toan/${idHoaDon}`, {
      method: "POST",
      headers: apiHeaders(),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail);
    }

    const data = await res.json();
    Swal.fire({
      icon: "success",
      title: "Thanh toán thành công!",
      text: `${formatMoney(data.TongTien)} - ${data.NhanVien}`,
      timer: 2000,
      showConfirmButton: false,
    });

    closeModal();
    loadOccupiedTables();
    loadInvoices();
  } catch (err) {
    Swal.fire("Lỗi", err.message, "error");
  }
}

// --- Auto refresh every 30s ---
setInterval(() => {
  loadOccupiedTables();
  loadInvoices();
}, 30000);
