document.addEventListener("DOMContentLoaded", function () {
    setupChangeMailContextMenu();
    setupChangeMailEvents();
});

function setupChangeMailEvents() {
    const table = document.getElementById("change-mail-table");
    if (!table) return;

    // Click phải trên bảng để mở menu
    table.addEventListener("contextmenu", function (e) {
        e.preventDefault();
        showChangeMailContextMenu(e.pageX, e.pageY);
    });
}

// ===== CONTEXT MENU =====
function setupChangeMailContextMenu() {
    const menu = document.createElement("div");
    menu.className = "context-menu";
    menu.id = "change-mail-context-menu";

    menu.innerHTML = `
        <div class="context-menu-item" id="cmail-add-account">📋 Nhập UID|PASS|COOKIE (Clipboard)</div>
        <div class="context-menu-item" id="cmail-add-newmail">📧 Nhập Mail mới (Clipboard)</div>
        <div class="context-menu-item" id="cmail-add-proxy">🌐 Nhập Proxy (Clipboard)</div>
        <div class="context-menu-separator"></div>
        <div class="context-menu-item" id="cmail-paste-mail-input">📥 Paste vào ô Nhập Mail mới</div>
        <div class="context-menu-item" id="cmail-clear-mail-input">🗑️ Xóa ô Nhập Mail mới</div>
        <div class="context-menu-separator"></div>
        <div class="context-menu-item" id="cmail-select-all">✅ Chọn tất cả</div>
        <div class="context-menu-item" id="cmail-deselect-all">🚫 Bỏ chọn tất cả</div>
        <div class="context-menu-separator"></div>
        <div class="context-menu-item" id="cmail-delete-selected">❌ Xóa dòng đã chọn</div>
    `;

    document.body.appendChild(menu);

    // Click phải trong toàn khu vực change-mail
    const section = document.getElementById("change-mail");
    if (section) {
        section.addEventListener("contextmenu", function (e) {
            e.preventDefault();
            showChangeMailContextMenu(e.pageX, e.pageY);
        });
    }

    // Ẩn menu khi click chỗ khác
    document.addEventListener("click", function () {
        menu.style.display = "none";
    });

    menu.addEventListener("click", handleChangeMailMenuClick);
}

function showChangeMailContextMenu(x, y) {
    const menu = document.getElementById("change-mail-context-menu");
    if (!menu) return;
    menu.style.left = `${x}px`;
    menu.style.top = `${y}px`;
    menu.style.display = "block";
}

function openLDPlayerSettings() {
    document.getElementById("ldplayer-settings-modal").style.display = "block";
}
function closeLDPlayerSettings() {
    document.getElementById("ldplayer-settings-modal").style.display = "none";
}
function saveLDPlayerSettings() {
    document.getElementById("ldplayer-settings-modal").style.display = "none";
}
async function browseDriverPath() {
    try {
        const folderPath = await eel.browse_driver_path()(); // Gọi hàm Python
        if (folderPath) {
            document.getElementById("change-mail-driver-path").value = folderPath;
        }
    } catch (err) {
        alert("Không thể chọn đường dẫn!");
        console.error(err);
    }
}


// ===== MENU ACTIONS =====
async function handleChangeMailMenuClick(e) {
    const id = e.target.id;
    if (!id) return;
    const menu = document.getElementById("change-mail-context-menu");
    if (menu) menu.style.display = "none";

    switch (id) {
        case "cmail-add-account":
            await changeMailImportAccount();
            break;
        case "cmail-add-newmail":
            await changeMailImportNewMail();
            break;
        case "cmail-add-proxy":
            await changeMailImportProxy();
            break;
        case "cmail-paste-mail-input":
            await pasteToMailInput();
            break;
        case "cmail-clear-mail-input":
            clearChangeMailInput();
            break;
        case "cmail-select-all":
            changeMailSelectAll();
            break;
        case "cmail-deselect-all":
            changeMailDeselectAll();
            break;
        case "cmail-delete-selected":
            changeMailDeleteSelected();
            break;
    }
}

// ====== IMPORT FUNCTIONS ======
async function changeMailImportAccount() {
    try {
        const text = await navigator.clipboard.readText();
        const rows = text.split("\n").map(line => line.trim()).filter(line => line);

        const tbody = document.getElementById("change-mail-tbody");
        let index = tbody.querySelectorAll("tr").length;

        rows.forEach(line => {
            const parts = line.split("|");
            if (parts.length >= 3) {
                const uid = parts[0] || "";
                const pass = parts[1] || "";
                const cookie = parts.slice(2).join("|") || "";

                index++;
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td><input type="checkbox" class="change-mail-row-checkbox" onchange="updateChangeMailSelectedCount()"></td>
                    <td>${index}</td>
                    <td>${uid}</td>
                    <td>${pass}</td>
                    <td>${cookie}</td>
                    <td></td>
                    <td><span style="color: #4ec9b0;">✓ Ready</span></td>
                `;
                tbody.appendChild(tr);
            }
        });
        updateChangeMailSelectedCount();
    } catch {
        alert("Không đọc được clipboard!");
    }
}

async function changeMailImportNewMail() {
    try {
        const text = await navigator.clipboard.readText();
        const mails = text.split("\n").map(line => line.trim()).filter(line => line);

        const tbody = document.getElementById("change-mail-tbody");
        const checkboxes = tbody.querySelectorAll(".change-mail-row-checkbox");

        let i = 0;
        checkboxes.forEach(cb => {
            if (i < mails.length) {
                const row = cb.closest("tr");
                row.cells[5].innerText = mails[i]; // cột MAIL
                i++;
            }
        });
    } catch {
        alert("Không đọc được clipboard!");
    }
}

async function changeMailImportProxy() {
    try {
        const text = await navigator.clipboard.readText();
        const proxies = text.split("\n").map(line => line.trim()).filter(line => line);

        const tbody = document.getElementById("change-mail-tbody");
        const checkboxes = tbody.querySelectorAll(".change-mail-row-checkbox");

        let i = 0;
        checkboxes.forEach(cb => {
            if (i < proxies.length) {
                const row = cb.closest("tr");
                // Thêm proxy vào cuối COOKIE cho dễ debug
                row.cells[4].innerText += ` | PROXY: ${proxies[i]}`;
                i++;
            }
        });
    } catch {
        alert("Không đọc được clipboard!");
    }
}

async function pasteToMailInput() {
    try {
        const text = await navigator.clipboard.readText();
        document.getElementById("change-mail-input").value = text;
    } catch {
        alert("Không đọc được clipboard!");
    }
}

function clearChangeMailInput() {
    document.getElementById("change-mail-input").value = "";
}

// ====== SELECTION FUNCTIONS ======
function changeMailSelectAll() {
    document.querySelectorAll("#change-mail-table .change-mail-row-checkbox")
        .forEach(cb => cb.checked = true);
    updateChangeMailSelectedCount();
}

function changeMailDeselectAll() {
    document.querySelectorAll("#change-mail-table .change-mail-row-checkbox")
        .forEach(cb => cb.checked = false);
    updateChangeMailSelectedCount();
}

function changeMailDeleteSelected() {
    const rows = document.querySelectorAll("#change-mail-table .change-mail-row-checkbox:checked");
    rows.forEach(cb => cb.closest("tr").remove());
    updateChangeMailSelectedCount();
}

function updateChangeMailSelectedCount() {
    const count = document.querySelectorAll("#change-mail-table .change-mail-row-checkbox:checked").length;
    const el = document.getElementById("change-mail-selected-count");
    if (el) el.innerText = `Đã chọn: ${count}`;
}
function refreshEmailCodeTable() {
    // Giả lập dữ liệu, sau này bạn gọi API hoặc xử lý thực tế ở đây
    const sampleData = [
        { mail: "example1@gmail.com", pass: "pass123", code: "654321" },
        { mail: "example2@yahoo.com", pass: "pass456", code: "987654" }
    ];

    const tbody = document.getElementById("email-code-tbody");
    tbody.innerHTML = "";

    sampleData.forEach((item, index) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${index + 1}</td>
            <td>${item.mail}</td>
            <td>${item.pass}</td>
            <td>${item.code}</td>
        `;
        tbody.appendChild(tr);
    });
}

function clearEmailCodeTable() {
    document.getElementById("email-code-tbody").innerHTML = "";
}

function loadDevices() {

}