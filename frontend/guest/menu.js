// ============================================================
// COFFEE SHOP - Guest Ordering Page (QR Scan)
// ============================================================

const API_BASE = window.APP_CONFIG?.API_BASE_URL || "/api";
const CART_KEY = "coffee_cart";

// --- State ---
let banId = null;
let menuItems = [];
let cart = JSON.parse(localStorage.getItem(CART_KEY)) || [];

// --- Init ---
document.addEventListener("DOMContentLoaded", async () => {
  const params = new URLSearchParams(window.location.search);
  const qrCode = params.get("ban");

  if (!qrCode) {
    document.getElementById("ban-label").textContent = "Lỗi: Thiếu mã bàn";
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/tables/qr/${qrCode}`);
    if (!res.ok) throw new Error("Bàn không tồn tại");
    const ban = await res.json();
    banId = ban.ID_Ban;
    document.getElementById("ban-label").textContent = ban.TenBan;
    document.getElementById("table-info").classList.remove("hidden");
  } catch (err) {
    document.getElementById("ban-label").textContent = "Lỗi: " + err.message;
    return;
  }

  await loadMenu();
  renderCartBadge();
});

// --- Load Menu ---
async function loadMenu() {
  try {
    const res = await fetch(`${API_BASE}/menu/`);
    menuItems = await res.json();
  } catch {
    Swal.fire("Lỗi", "Không thể tải thực đơn", "error");
    return;
  }

  renderCategories();
  renderMenu("all");
}

// --- Render Categories ---
function renderCategories() {
  const container = document.getElementById("category-tabs");
  const categories = [...new Set(menuItems.map((m) => m.DanhMuc))];

  categories.forEach((cat) => {
    const btn = document.createElement("button");
    btn.className =
      "category-btn px-4 py-2 rounded-full text-sm font-medium bg-gray-100 text-gray-700 hover:bg-amber-100";
    btn.dataset.category = cat;
    btn.textContent = cat;
    btn.onclick = () => filterMenu(cat, btn);
    container.appendChild(btn);
  });
}

function filterMenu(category, btn) {
  document.querySelectorAll(".category-btn").forEach((b) => {
    b.className =
      "category-btn px-4 py-2 rounded-full text-sm font-medium bg-gray-100 text-gray-700";
  });
  btn.className =
    "category-btn px-4 py-2 rounded-full text-sm font-medium bg-amber-600 text-white";
  renderMenu(category);
}

// --- Render Menu Items ---
function renderMenu(category) {
  const container = document.getElementById("menu-list");
  container.innerHTML = "";

  const filtered =
    category === "all"
      ? menuItems
      : menuItems.filter((m) => m.DanhMuc === category);

  filtered.forEach((item) => {
    const giaSauGiam = item.Gia * (1 - item.GiamGia / 100);
    const cartItem = cart.find((c) => c.ID_Mon === item.ID_Mon);
    const qty = cartItem ? cartItem.SoLuong : 0;

    const div = document.createElement("div");
    div.className = "bg-white rounded-xl shadow-sm p-4 flex gap-4 items-center";
    div.innerHTML = `
            <div class="w-20 h-20 bg-amber-100 rounded-lg flex items-center justify-center text-amber-600 text-3xl flex-shrink-0">
                <i class="fas fa-mug-hot"></i>
            </div>
            <div class="flex-1 min-w-0">
                <h3 class="font-semibold text-gray-800">${item.TenMon}</h3>
                <div class="flex items-center gap-2 mt-1">
                    <span class="text-red-600 font-bold">${formatMoney(giaSauGiam)}</span>
                    ${
                      item.GiamGia > 0
                        ? `<span class="text-gray-400 line-through text-sm">${formatMoney(item.Gia)}</span>
                        <span class="bg-red-100 text-red-600 text-xs px-1.5 py-0.5 rounded">-${item.GiamGia}%</span>`
                        : ""
                    }
                </div>
                <div class="flex items-center gap-2 mt-2">
                    <button onclick="updateCart(${item.ID_Mon}, -1)" class="w-7 h-7 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-600">
                        <i class="fas fa-minus text-xs"></i>
                    </button>
                    <span id="qty-${item.ID_Mon}" class="font-semibold w-6 text-center">${qty}</span>
                    <button onclick="updateCart(${item.ID_Mon}, 1)" class="w-7 h-7 rounded-full bg-amber-600 hover:bg-amber-700 text-white flex items-center justify-center">
                        <i class="fas fa-plus text-xs"></i>
                    </button>
                </div>
            </div>
        `;
    container.appendChild(div);
  });
}

// --- Cart Logic ---
function updateCart(idMon, delta) {
  const idx = cart.findIndex((c) => c.ID_Mon === idMon);
  if (idx === -1) {
    if (delta > 0) {
      const item = menuItems.find((m) => m.ID_Mon === idMon);
      cart.push({
        ID_Mon: idMon,
        SoLuong: 1,
        GiaTaiThoiDiem: item.Gia * (1 - item.GiamGia / 100),
      });
    }
  } else {
    cart[idx].SoLuong += delta;
    if (cart[idx].SoLuong <= 0) cart.splice(idx, 1);
  }

  localStorage.setItem(CART_KEY, JSON.stringify(cart));
  renderCartBadge();

  const qtySpan = document.getElementById(`qty-${idMon}`);
  if (qtySpan) {
    const ci = cart.find((c) => c.ID_Mon === idMon);
    qtySpan.textContent = ci ? ci.SoLuong : 0;
  }
}

function renderCartBadge() {
  const total = cart.reduce((s, c) => s + c.SoLuong, 0);
  const money = cart.reduce((s, c) => s + c.SoLuong * c.GiaTaiThoiDiem, 0);

  document.getElementById("cart-count").textContent = total;
  document.getElementById("cart-total").textContent = formatMoney(money);
  document.getElementById("cart-bar").classList.toggle("hidden", total === 0);
}

// --- Submit Order ---
document.getElementById("btn-order").addEventListener("click", async () => {
  if (!banId || cart.length === 0) return;

  try {
    const res = await fetch(`${API_BASE}/orders/dat-mon`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ID_Ban: banId,
        danh_sach_mon: cart,
      }),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail);
    }

    const result = await res.json();

    await Swal.fire({
      icon: "success",
      title: "Đặt món thành công!",
      text: result.message,
      timer: 2000,
      showConfirmButton: false,
    });

    cart = [];
    localStorage.removeItem(CART_KEY);
    renderCartBadge();
    renderMenu("all");
  } catch (err) {
    Swal.fire("Lỗi", err.message, "error");
  }
});

// --- Helpers ---
function formatMoney(n) {
  return new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
  }).format(n);
}
