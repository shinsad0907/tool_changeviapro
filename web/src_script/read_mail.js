// read_mail.js

// Xóa nội dung ô nhập mail
function clearReadMailInput() {
    document.getElementById("read-mail-input").value = "";
}

// Dán từ clipboard vào ô nhập
async function pasteReadMailFromClipboard() {
    try {
        const text = await navigator.clipboard.readText();
        document.getElementById("read-mail-input").value = text;
    } catch (err) {
        showToast("error", "Không thể dán từ clipboard!");
    }
}

// Xóa bảng kết quả
function clearReadMailTable() {
    document.getElementById("read-mail-tbody").innerHTML = `<tr><td colspan="7" style="text-align:center;">No result!</td></tr>`;
}

// Xuất dữ liệu bảng ra file
function exportReadMailData() {
    // Lấy tất cả các dòng trong bảng
    const rows = Array.from(document.querySelectorAll('#read-mail-tbody tr'));
    
    // Kiểm tra xem có dữ liệu không
    if (rows.length === 0 || (rows.length === 1 && rows[0].textContent.includes('No result'))) {
        alert('Không có dữ liệu để xuất!');
        return;
    }

    // Lấy dữ liệu từ tất cả các dòng
    const lines = rows.map(row => {
        const tds = row.querySelectorAll('td');
        // Bỏ qua những dòng không đúng format
        if (tds.length < 7) return null;
        
        const values = [
            tds[1]?.textContent.trim() || "", // mailadd
            tds[2]?.textContent.trim() || "", // mailadd
            tds[6]?.textContent.trim() || "", // uid
            tds[7]?.textContent.trim() || "", // code
        ];
        // Chỉ lấy những dòng có ít nhất một giá trị
        return values.some(v => v !== "") ? values.join('|') : null;
    }).filter(line => line !== null); // Lọc bỏ các dòng null

    if (lines.length === 0) {
        alert('Không có dữ liệu hợp lệ để xuất!');
        return;
    }
    
    eel.save_exported_accounts(lines)(function(result) {
        if (result && result.success) {
            alert('Xuất file thành công!');
        } else if (result && result.cancelled) {
            // Người dùng bấm Cancel
        } else {
            alert('Có lỗi khi lưu file!');
        }
    });
}
// Biến đếm STT
let readMailRowCounter = 0;

// Hàm để cập nhật kết quả vào table (được gọi từ Python) - SỬA LẠI ĐỂ NHẬN 7 THAM SỐ
eel.expose(updateReadMailResult);
function updateReadMailResult(mailadd, from_name, date_str, subject, uid, code, status) {
    const tbody = document.getElementById("read-mail-tbody");
    
    // Xóa dòng "No result!" hoặc "Đang đọc..." nếu có
    if (tbody.children.length === 1) {
        const firstRowText = tbody.children[0].textContent.trim();
        if (firstRowText.includes("No result!") || firstRowText.includes("Đang đọc")) {
            tbody.innerHTML = "";
        }
    }

    // Tìm index của mail trong mailOrder
    const mailInfo = mailOrder.find(m => m.mailadd === mailadd);
    const orderIndex = mailInfo ? mailInfo.index : -1;
    
    // Xác định màu sắc cho status
    let statusColor = "#28a745"; // xanh lá (thành công)
    if (status.includes("❌")) {
        statusColor = "#dc3545"; // đỏ (lỗi)
    } else if (status.includes("⚠️")) {
        statusColor = "#ffc107"; // vàng (cảnh báo)
    }
    
    // Xác định màu cho code
    let codeColor = "#28a745";
    let codeText = code;
    if (code === "N/A" || !code) {
        codeColor = "#6c757d"; // xám
        codeText = "N/A";
    }
    
    const row = document.createElement("tr");
    row.setAttribute('data-order', orderIndex);
    row.innerHTML = `
        <td>${orderIndex + 1}</td>
        <td>${mailInfo ? mailInfo.mail : mailadd}</td>
        <td>${mailadd}</td>
        <td>${from_name}</td>
        <td>${date_str}</td>
        <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${subject}">${subject}</td>
        <td style="color: ${codeColor}; font-weight: bold;">${uid}</td>
        <td style="color: ${codeColor}; font-weight: bold;">${codeText}</td>
        <td style="color: ${statusColor}; font-weight: bold; font-size: 12px;">${status}</td>
    `;

    // Chèn row vào đúng vị trí
    const rows = Array.from(tbody.children);
    const insertIndex = rows.findIndex(r => 
        parseInt(r.getAttribute('data-order')) > orderIndex
    );

    if (insertIndex === -1) {
        tbody.appendChild(row);
    } else {
        tbody.insertBefore(row, rows[insertIndex]);
    }
    
    console.log(`[JS] Updated treeview for ${mailadd}: ${status}`);
}

// Reset counter khi bắt đầu đọc mail mới
function resetReadMailCounter() {
    readMailRowCounter = 0;
}

let mailOrder = [];

// Sửa lại hàm startReadMail để lưu thứ tự mail
async function startReadMail() {
    let input = document.getElementById("read-mail-input").value.trim();
    let threadInput = document.getElementById("read-mail-thread-count");
    let threadCount = threadInput ? parseInt(threadInput.value) : 3;

    if (!input) {
        showToast("error", "Vui lòng nhập danh sách mail!");
        return;
    }

    try {
        await setButtonStatus("running");
        
        // Reset counter và clear table
        resetReadMailCounter();
        clearReadMailTable();
        let tbody = document.getElementById("read-mail-tbody");
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;">⏳ Đang đọc...</td></tr>`;

        // Lưu thứ tự mail từ input
        mailOrder = [];
        const accounts = [];
        input.split("\n").forEach((line, index) => {
            let parts = line.trim().split("|");
            if (parts.length >= 3) {
                const mail = parts[0].trim();
                const mailadd = parts[2].trim();
                mailOrder.push({mail, mailadd, index});
                accounts.push({
                    mail: mail,
                    pass: parts[1],
                    mailadd: mailadd
                });
            }
        });

        console.log(`[JS] Sending ${accounts.length} accounts to Python:`);
        accounts.forEach((acc, i) => {
            console.log(`  ${i+1}. ${acc.mail} -> ${acc.mailadd}`);
        });

        // Tạo object gửi backend
        const data = {
            accounts: accounts,
            thread_count: threadCount
        };
        
        await eel.start_read_mail(data)();
        showToast("info", "Bắt đầu đọc mail...");
        
    } catch (error) {
        console.error("Error in startReadMail:", error);
        await setButtonStatus("error");
    }
}

// Hàm toast để thông báo
function showToast(type, message) {
    let toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.innerText = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// Expose setButtonStatus function for Python
eel.expose(setButtonStatus);
function setButtonStatus(status) {
    return new Promise((resolve) => {
        const btn = document.getElementById("read-mail-start-btn");
        
        // Guard clause for missing button
        if (!btn) {
            console.error("Button with ID 'read-mail-start-btn' not found!");
            resolve(false);
            return;
        }

        const spinner = '<span class="spinner-border spinner-border-sm me-2"></span>';
        
        switch(status) {
            case "running":
                btn.disabled = true;
                btn.innerHTML = `${spinner}Đang đọc mail...`;
                btn.classList.add("processing");
                break;
                
            case "done":
                btn.disabled = false;
                btn.innerHTML = "Bắt đầu đọc mail";
                btn.classList.remove("processing");
                showToast("success", "Hoàn tất đọc mail!");
                break;
                
            case "error":
                btn.disabled = false;
                btn.innerHTML = "Bắt đầu đọc mail";
                btn.classList.remove("processing");
                showToast("error", "Có lỗi xảy ra khi đọc mail!");
                break;
                
            default:
                btn.disabled = false;
                btn.innerHTML = "Bắt đầu đọc mail";
                btn.classList.remove("processing");
        }
        
        resolve(true);
    });
}