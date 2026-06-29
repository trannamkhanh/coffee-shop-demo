const API = window.APP_CONFIG?.API_BASE_URL || "/api";
const token = localStorage.getItem("token");
const chucVu = localStorage.getItem("chuc_vu");
const hoTen = localStorage.getItem("ho_ten");

if (!token || chucVu !== "Admin") {
  window.location.href = "../shared/login.html";
}

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

function logout() {
  localStorage.clear();
  window.location.href = "../shared/login.html";
}

// --- Tab switching ---
function switchTab(tab) {
  document.querySelectorAll(".tab-btn").forEach((b) => {
    b.className =
      "tab-btn px-5 py-2 rounded-lg font-medium bg-gray-200 text-gray-700";
  });
  document
    .getElementById("panel-menu")
    .classList.toggle("hidden", tab !== "menu");
  document
    .getElementById("panel-employees")
    .classList.toggle("hidden", tab !== "employees");

  const btn = document.getElementById(
    tab === "menu" ? "tab-menu" : "tab-employees",
  );
  btn.className =
    "tab-btn px-5 py-2 rounded-lg font-medium bg-amber-700 text-white";

  if (tab === "menu") loadMenu();
  else loadEmployees();
}

// --- INIT ---
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("user-info").textContent = `${hoTen} (Admin)`;
  loadMenu();
});

// ====================================================================
// MENU CRUD
// ====================================================================
async function loadMenu() {
  const container = document.getElementById("menu-table");
  container.innerHTML =
    '<div class="p-4 text-center text-gray-400"><i class="fas fa-spinner fa-spin mr-2"></i>Đang tải...</div>';

  try {
    const res = await fetch(`${API}/menu/`);
    const items = await res.json();

    container.innerHTML = `
            <table class="w-full text-sm">
                <thead class="bg-gray-50 text-gray-600 uppercase text-xs">
                    <tr>
                        <th class="text-left px-4 py-3">Tên món</th>
                        <th class="text-left px-4 py-3">Danh mục</th>
                        <th class="text-right px-4 py-3">Giá</th>
                        <th class="text-center px-4 py-3">Giảm</th>
                        <th class="text-center px-4 py-3">Trạng thái</th>
                        <th class="text-center px-4 py-3">Thao tác</th>
                    </tr>
                </thead>
                <tbody class="divide-y">
                    ${items
                      .map(
                        (m) => `
                        <tr class="hover:bg-gray-50">
                            <td class="px-4 py-3 font-medium">${m.TenMon}</td>
                            <td class="px-4 py-3 text-gray-500">${m.DanhMuc}</td>
                            <td class="px-4 py-3 text-right font-medium">${formatMoney(m.Gia)}</td>
                            <td class="px-4 py-3 text-center">${m.GiamGia > 0 ? `<span class="bg-red-100 text-red-600 px-2 py-0.5 rounded text-xs">-${m.GiamGia}%</span>` : "—"}</td>
                            <td class="px-4 py-3 text-center">
                                <span class="inline-block px-2 py-0.5 rounded text-xs font-medium ${m.TrangThai === "ConHang" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}">
                                    ${m.TrangThai === "ConHang" ? "Còn hàng" : "Hết hàng"}
                                </span>
                            </td>
                            <td class="px-4 py-3 text-center">
                                <button onclick="editMon(${m.ID_Mon})" class="text-blue-600 hover:text-blue-800 mx-1" title="Sửa"><i class="fas fa-edit"></i></button>
                                <button onclick="deleteMon(${m.ID_Mon})" class="text-red-600 hover:text-red-800 mx-1" title="Xóa"><i class="fas fa-trash"></i></button>
                            </td>
                        </tr>
                    `,
                      )
                      .join("")}
                </tbody>
            </table>
        `;
  } catch {
    container.innerHTML =
      '<div class="p-4 text-center text-red-400">Lỗi tải thực đơn</div>';
  }
}

function openAddMonModal() {
  document.getElementById("mon-modal-title").textContent = "Thêm món ăn";
  [
    "mon-id",
    "mon-ten",
    "mon-gia",
    "mon-giamgia",
    "mon-danhmuc",
    "mon-hinhanh",
  ].forEach((id) => {
    document.getElementById(id).value = "";
  });
  document.getElementById("mon-trangthai").value = "ConHang";
  document.getElementById("mon-modal").classList.remove("hidden");
  document.getElementById("mon-modal").classList.add("flex");
}

function closeMonModal() {
  document.getElementById("mon-modal").classList.add("hidden");
  document.getElementById("mon-modal").classList.remove("flex");
}

async function editMon(id) {
  try {
    const res = await fetch(`${API}/menu/${id}`);
    const m = await res.json();
    document.getElementById("mon-modal-title").textContent = "Sửa món ăn";
    document.getElementById("mon-id").value = m.ID_Mon;
    document.getElementById("mon-ten").value = m.TenMon;
    document.getElementById("mon-gia").value = m.Gia;
    document.getElementById("mon-giamgia").value = m.GiamGia;
    document.getElementById("mon-danhmuc").value = m.DanhMuc;
    document.getElementById("mon-hinhanh").value = m.HinhAnh || "";
    document.getElementById("mon-trangthai").value = m.TrangThai;
    document.getElementById("mon-modal").classList.remove("hidden");
    document.getElementById("mon-modal").classList.add("flex");
  } catch {
    Swal.fire("Lỗi", "Không thể tải thông tin món", "error");
  }
}

async function saveMon() {
  const id = document.getElementById("mon-id").value;
  const data = {
    TenMon: document.getElementById("mon-ten").value.trim(),
    Gia: parseFloat(document.getElementById("mon-gia").value) || 0,
    GiamGia: parseFloat(document.getElementById("mon-giamgia").value) || 0,
    DanhMuc: document.getElementById("mon-danhmuc").value.trim(),
    HinhAnh: document.getElementById("mon-hinhanh").value.trim() || null,
    TrangThai: document.getElementById("mon-trangthai").value,
  };

  if (!data.TenMon || !data.Gia || !data.DanhMuc) {
    Swal.fire("Lỗi", "Vui lòng nhập đầy đủ thông tin", "warning");
    return;
  }

  try {
    const isEdit = !!id;
    const url = isEdit ? `${API}/menu/${id}` : `${API}/menu/`;
    const method = isEdit ? "PUT" : "POST";
    const res = await fetch(url, {
      method,
      headers: apiHeaders(),
      body: JSON.stringify(data),
    });

    if (!res.ok) throw new Error("Lỗi lưu dữ liệu");

    Swal.fire({
      icon: "success",
      title: isEdit ? "Cập nhật thành công" : "Thêm thành công",
      timer: 1500,
      showConfirmButton: false,
    });
    closeMonModal();
    loadMenu();
  } catch (err) {
    Swal.fire("Lỗi", err.message, "error");
  }
}

async function deleteMon(id) {
  const result = await Swal.fire({
    title: "Xóa món này?",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#dc2626",
    confirmButtonText: "Xóa",
    cancelButtonText: "Hủy",
  });

  if (!result.isConfirmed) return;

  try {
    const res = await fetch(`${API}/menu/${id}`, {
      method: "DELETE",
      headers: apiHeaders(),
    });
    if (!res.ok) throw new Error("Không thể xóa");
    Swal.fire("Đã xóa", "", "success");
    loadMenu();
  } catch {
    Swal.fire("Lỗi", "Không thể xóa món này", "error");
  }
}

// ====================================================================
// EMPLOYEE CRUD
// ====================================================================
async function loadEmployees() {
  const container = document.getElementById("employee-table");
  container.innerHTML =
    '<div class="p-4 text-center text-gray-400"><i class="fas fa-spinner fa-spin mr-2"></i>Đang tải...</div>';

  try {
    const res = await fetch(`${API}/employees/`, { headers: apiHeaders() });
    const emps = await res.json();

    container.innerHTML = `
            <table class="w-full text-sm">
                <thead class="bg-gray-50 text-gray-600 uppercase text-xs">
                    <tr>
                        <th class="text-left px-4 py-3">Họ tên</th>
                        <th class="text-left px-4 py-3">Tên đăng nhập</th>
                        <th class="text-center px-4 py-3">Chức vụ</th>
                    </tr>
                </thead>
                <tbody class="divide-y">
                    ${emps
                      .map(
                        (e) => `
                        <tr class="hover:bg-gray-50">
                            <td class="px-4 py-3 font-medium">${e.HoTen}</td>
                            <td class="px-4 py-3 text-gray-500">${e.TenDangNhap}</td>
                            <td class="px-4 py-3 text-center">
                                <span class="inline-block px-2 py-0.5 rounded text-xs font-medium
                                    ${
                                      e.ChucVu === "Admin"
                                        ? "bg-purple-100 text-purple-700"
                                        : e.ChucVu === "ThuNgan"
                                          ? "bg-blue-100 text-blue-700"
                                          : "bg-gray-100 text-gray-700"
                                    }">
                                    ${
                                      e.ChucVu === "Admin"
                                        ? "Admin"
                                        : e.ChucVu === "ThuNgan"
                                          ? "Thu ngân"
                                          : "Phục vụ"
                                    }
                                </span>
                            </td>
                        </tr>
                    `,
                      )
                      .join("")}
                </tbody>
            </table>
        `;
  } catch {
    container.innerHTML =
      '<div class="p-4 text-center text-red-400">Lỗi tải nhân viên</div>';
  }
}

function openAddEmpModal() {
  ["emp-hoten", "emp-username", "emp-password"].forEach((id) => {
    document.getElementById(id).value = "";
  });
  document.getElementById("emp-chucvu").value = "ThuNgan";
  document.getElementById("emp-modal").classList.remove("hidden");
  document.getElementById("emp-modal").classList.add("flex");
}

function closeEmpModal() {
  document.getElementById("emp-modal").classList.add("hidden");
  document.getElementById("emp-modal").classList.remove("flex");
}

async function saveEmployee() {
  const data = {
    HoTen: document.getElementById("emp-hoten").value.trim(),
    TenDangNhap: document.getElementById("emp-username").value.trim(),
    MatKhau: document.getElementById("emp-password").value.trim(),
    ChucVu: document.getElementById("emp-chucvu").value,
  };

  if (!data.HoTen || !data.TenDangNhap || !data.MatKhau) {
    Swal.fire("Lỗi", "Vui lòng nhập đầy đủ thông tin", "warning");
    return;
  }

  try {
    const res = await fetch(`${API}/employees/`, {
      method: "POST",
      headers: apiHeaders(),
      body: JSON.stringify(data),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail);
    }

    Swal.fire({
      icon: "success",
      title: "Thêm nhân viên thành công",
      timer: 1500,
      showConfirmButton: false,
    });
    closeEmpModal();
    loadEmployees();
  } catch (err) {
    Swal.fire("Lỗi", err.message, "error");
  }
}
