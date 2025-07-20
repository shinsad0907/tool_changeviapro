// Global data object
const data = {
    isRunning: false,
    selectedCount: 0,
    total: 0,
    processed: 0,
    success: 0,
    failed: 0,
    config: {
        threadCount: 3,
        batchSize: 10
    }
};

// Setup context menu cho tab Add Mail
function setupAddMailContextMenu() {
    const contextMenuAddMail = document.createElement('div');
    contextMenuAddMail.className = 'context-menu context-menu-addmail';
    contextMenuAddMail.innerHTML = `
        <div class="context-menu-item" id="add-mail">Nhập MAIL|PASS</div>
        <div class="context-menu-separator"></div>
        <div class="context-menu-item" id="select-all-menu">Chọn tất cả</div>
        <div class="context-menu-item" id="deselect-all-menu">Bỏ chọn tất cả</div>
        <div class="context-menu-item" id="select-errors">Chọn tài khoản bôi đen</div>
        <div class="context-menu-separator"></div>
        <div class="context-menu-item" id="delete-selected">❌ Delete mail</div>
    `;
    document.body.appendChild(contextMenuAddMail);

    // Lắng nghe right-click trên toàn bộ tab Add Mail
    const addMailTab = document.getElementById('add-mail');
    if (addMailTab) {
        addMailTab.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            e.stopPropagation();
            showContextMenu(e.pageX, e.pageY);
        });
    }

    // Chặn context menu mặc định cho toàn bộ tab Add Mail
    document.addEventListener('contextmenu', function(e) {
        if (e.target.closest('#add-mail')) {
            e.preventDefault();
        }
    });

    // Ẩn menu khi click ra ngoài
    document.addEventListener('click', function(e) {
        if (!contextMenuAddMail.contains(e.target)) {
            contextMenuAddMail.style.display = 'none';
        }
    });

    // Xử lý các action trong menu
    contextMenuAddMail.addEventListener('click', handleAddMailContextMenuClick);

    function showContextMenu(x, y) {
        contextMenuAddMail.style.display = 'block';
        contextMenuAddMail.style.left = x + 'px';
        contextMenuAddMail.style.top = y + 'px';
    }
}

function handleAddMailContextMenuClick(e) {
    const id = e.target.id;
    if (!id) return;
    document.querySelector('.context-menu-addmail').style.display = 'none';

    switch (id) {
        case 'add-mail':
            try {
                navigator.clipboard.readText().then(text => {
                    if (text) {
                        addMailsFromText(text);
                    } else {
                        alert('Clipboard trống!');
                    }
                });
            } catch (err) {
                console.error('Clipboard error:', err);
                alert('Không thể đọc clipboard. Hãy cấp quyền truy cập clipboard cho trình duyệt.');
            }
            break;
        case 'select-all-menu':
            const selectAllCheckbox = document.getElementById('source-mail-select-all');
            if (selectAllCheckbox) {
                selectAllCheckbox.checked = true;
                toggleSourceMailSelectAll();
            }
            break;
        case 'deselect-all-menu':
            const deselectAllCheckbox = document.getElementById('source-mail-select-all');
            if (deselectAllCheckbox) {
                deselectAllCheckbox.checked = false;
                toggleSourceMailSelectAll();
            }
            break;
        case 'select-errors':
            selectErrorRows();
            break;
        case 'delete-selected':
            deleteSelectedMails();
            break;
    }
}

function copySelectedMails(type) {
    const selectedRows = Array.from(document.querySelectorAll('.source-mail-row-checkbox:checked'))
        .map(checkbox => checkbox.closest('tr'));

    if (selectedRows.length === 0) {
        alert('Vui lòng chọn ít nhất một mail!');
        return;
    }

    let content = '';
    selectedRows.forEach(row => {
        const mail = row.cells[2].textContent;
        const password = row.cells[3].textContent;
        
        switch(type) {
            case 'mail':
                content += mail + '\n';
                break;
            case 'password':
                content += password + '\n';
                break;
            case 'full':
                content += `${mail}|${password}\n`;
                break;
        }
    });

    navigator.clipboard.writeText(content.trim())
        .then(() => alert('Đã copy thành công!'))
        .catch(() => alert('Không thể copy. Vui lòng thử lại!'));
}

function deleteSelectedMails() {
    const selectedRows = document.querySelectorAll('.source-mail-row-checkbox:checked');
    if (selectedRows.length === 0) {
        alert('Vui lòng chọn ít nhất một mail để xóa!');
        return;
    }

    if (confirm(`Bạn có chắc muốn xóa ${selectedRows.length} mail đã chọn?`)) {
        selectedRows.forEach(checkbox => {
            checkbox.closest('tr').remove();
        });
        updateSourceMailSelectedCount();
        updateStats();
    }
}

function clearAllMails() {
    if (confirm('Bạn có chắc muốn xóa tất cả mail?')) {
        const tbody = document.getElementById('source-mail-tbody');
        tbody.innerHTML = '';
        updateSourceMailSelectedCount();
        updateStats();
    }
}

// Treeview functions
function addMailToTreeview(mail, password, status = 'Ready') {
    const tbody = document.getElementById('source-mail-tbody');
    const rowCount = tbody.children.length;

    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td><input type="checkbox" class="source-mail-row-checkbox" onchange="updateSourceMailSelectedCount()"></td>
        <td>${rowCount + 1}</td>
        <td>${mail}</td>
        <td>${password}</td>
        <td><span style="color: ${status === 'Ready' ? '#4ec9b0' : '#f44747'}">
            ${status === 'Ready' ? '✓' : '❌'} ${status}
        </span></td>
    `;

    tbody.appendChild(tr);
    data.total = tbody.children.length;
    updateStats();
}

function addMailsFromText(text) {
    const mails = text.split('\n')
        .map(line => line.trim())
        .filter(line => line)
        .map(line => {
            const [email, password] = line.split('|').map(s => s.trim());
            return { email, password };
        })
        .filter(mail => mail.email && mail.password);

    if (mails.length === 0) {
        alert('Không tìm thấy mail hợp lệ. Vui lòng kiểm tra định dạng MAIL|PASSWORD');
        return;
    }

    mails.forEach(mail => {
        addMailToTreeview(mail.email, mail.password);
    });

    alert(`Đã thêm ${mails.length} mail vào danh sách!`);
}

// UI update functions
function updateSourceMailSelectedCount() {
    const checkboxes = document.querySelectorAll('.source-mail-row-checkbox:checked');
    data.selectedCount = checkboxes.length;
    document.getElementById('source-mail-selected-count').textContent = `Đã chọn: ${data.selectedCount}`;
}

function toggleSourceMailSelectAll() {
    const mainCheckbox = document.getElementById('source-mail-select-all');
    const checkboxes = document.querySelectorAll('.source-mail-row-checkbox');
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = mainCheckbox.checked;
    });
    
    updateSourceMailSelectedCount();
}

function updateStats() {
    document.getElementById('total-source-mail').textContent = data.total;
    document.getElementById('processed-mail').textContent = data.processed;
    document.getElementById('success-mail').textContent = data.success;
    document.getElementById('failed-mail').textContent = data.failed;
}

function selectErrorRows() {
    const rows = document.querySelectorAll('#source-mail-tbody tr');
    rows.forEach(row => {
        const statusCell = row.querySelector('td:nth-child(5)');
        const checkbox = row.querySelector('.source-mail-row-checkbox');
        if (statusCell && checkbox) {
            // Kiểm tra nếu status có chứa ký tự ❌
            if (statusCell.textContent.includes('❌')) {
                checkbox.checked = true;
                row.classList.add('selected');
            } else {
                checkbox.checked = false;
                row.classList.remove('selected');
            }
        }
    });
    updateSourceMailSelectedCount();
}

// Clear and paste functions
function clearAddMailInput() {
    document.getElementById('add-mail-input').value = '';
}

async function pasteAddMailFromClipboard() {
    try {
        const text = await navigator.clipboard.readText();
        document.getElementById('add-mail-input').value = text;
        // Tự động thêm mail vào treeview sau khi paste
        addMailsFromText();
    } catch (err) {
        alert('Không thể truy cập clipboard. Vui lòng kiểm tra quyền truy cập.');
    }
}

// Main functionality
function updateConfig() {
    data.config = {
        threadCount: parseInt(document.getElementById('add-mail-thread-count').value) || 3,
        batchSize: parseInt(document.getElementById('add-mail-batch-size').value) || 10
    };
}

function getSelectedMails() {
    const selectedRows = document.querySelectorAll('.source-mail-row-checkbox:checked');
    return Array.from(selectedRows).map(checkbox => {
        const row = checkbox.closest('tr');
        return {
            email: row.cells[2].textContent,
            password: row.cells[3].textContent
        };
    });
}

function parseInputMails() {
    const input = document.getElementById('add-mail-input').value;
    return input.split('\n')
        .map(line => line.trim())
        .filter(line => line)
        .map(line => {
            const [email, password] = line.split('|');
            return { email: email?.trim(), password: password?.trim() };
        })
        .filter(mail => mail.email && mail.password);
}

async function startAddMail() {
    if (data.isRunning) {
        alert('Đang trong tiến trình Add Mail!');
        return;
    }

    updateConfig();
    const selectedMails = getSelectedMails();
    const inputMails = parseInputMails();

    if (selectedMails.length === 0) {
        alert('Vui lòng chọn ít nhất một mail nguồn!');
        return;
    }

    if (inputMails.length === 0) {
        alert('Vui lòng nhập danh sách mail cần add!');
        return;
    }

    // Reset counters
    data.total = selectedMails.length;
    data.processed = 0;
    data.success = 0;
    data.failed = 0;
    updateStats();

    // Update UI state
    data.isRunning = true;
    document.getElementById('add-mail-start-btn').disabled = true;
    document.getElementById('add-mail-stop-btn').disabled = false;

    try {
        // Call Python function through eel
        const result = await eel.run_add_mail({
            data: {
                sourceMails: selectedMails,
                inputMails: inputMails,
                config: data.config
            }
        })();

        if (result && result.success) {
            // Update các mail đã xử lý thành công
            const rows = document.querySelectorAll('#source-mail-tbody tr');
            rows.forEach(row => {
                const mailCell = row.cells[2];
                const statusCell = row.cells[4];
                const statusData = result.mailStatus[mailCell.textContent];
                
                if (mailCell && statusCell && statusData) {
                    const status = statusData.success ? 'Success' : 'Failed';
                    const icon = statusData.success ? '✓' : '❌';
                    const color = statusData.success ? '#4ec9b0' : '#f44747';
                    const message = statusData.message || status;
                    statusCell.innerHTML = `<span style="color: ${color}">${icon} ${message}</span>`;
                }
            });
        } else {
            throw new Error(result.message || 'Unknown error');
        }
    } catch (error) {
        console.error('Error during add mail process:', error);
        alert('Có lỗi xảy ra trong quá trình thêm mail!');
    } finally {
        stopAddMail();
    }
}

function stopAddMail() {
    data.isRunning = false;
    document.getElementById('add-mail-start-btn').disabled = false;
    document.getElementById('add-mail-stop-btn').disabled = true;
}

function exportAddMailData() {
    // Get the table data
    const table = document.getElementById('source-mail-table');
    if (!table) return;

    let csvContent = "STT,MAIL,PASS,STATUS\n";
    
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    rows.forEach((row, index) => {
        const cells = Array.from(row.cells);
        const rowData = [
            index + 1,
            cells[2].textContent, // MAIL
            cells[3].textContent, // PASS
            cells[4].textContent.replace('✓', '').replace('❌', '').trim() // STATUS
        ];
        csvContent += rowData.join(',') + '\n';
    });

    // Create and trigger download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute("href", url);
        link.setAttribute("download", `add_mail_export_${new Date().toISOString().slice(0,10)}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// Listen for updates from Python
eel.expose(updateAddMailProgress);
function updateAddMailProgress(progress) {
    if (progress && typeof progress === 'object') {
        data.processed = progress.processed || 0;
        data.success = progress.success || 0;
        data.failed = progress.failed || 0;
        
        // Cập nhật status cho từng mail nếu có
        if (progress.mailStatus) {
            const rows = document.querySelectorAll('#source-mail-tbody tr');
            rows.forEach(row => {
                const mailCell = row.cells[2];
                const statusCell = row.cells[4];
                const statusData = progress.mailStatus[mailCell.textContent];
                
                if (mailCell && statusCell && statusData) {
                    const icon = statusData.status === 'Success' ? '✓' : '❌';
                    const color = statusData.status === 'Success' ? '#4ec9b0' : '#f44747';
                    const message = statusData.message;
                    statusCell.innerHTML = `<span style="color: ${color}">${icon} ${message}</span>`;
                }
            });
        }

        // Cập nhật danh sách mail đã add với mail nguồn
        if (progress.results) {
            const addMailInput = document.getElementById('add-mail-input');
            if (addMailInput) {
                // Hiển thị mail|pass|mail nguồn cho các mail đã add thành công
                addMailInput.value = progress.results
                    .filter(mail => mail.full_info)  // Chỉ lấy những mail đã add thành công
                    .map(mail => mail.full_info)
                    .join('\n');
            }
        }
        
        updateStats();
    }
}

// Initialize event listeners when document is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize table events
    const sourceMailTable = document.getElementById('source-mail-table');
    if (sourceMailTable) {
        // Setup context menu
        setupAddMailContextMenu();
        
        // Checkbox change event
        sourceMailTable.addEventListener('change', function(e) {
            if (e.target.classList.contains('source-mail-row-checkbox')) {
                updateSourceMailSelectedCount();
            }
        });

        // Row selection on click
        sourceMailTable.addEventListener('click', function(e) {
            const row = e.target.closest('tr');
            if (!row || e.target.type === 'checkbox') return;

            const checkbox = row.querySelector('.source-mail-row-checkbox');
            if (checkbox) {
                checkbox.checked = !checkbox.checked;
                updateSourceMailSelectedCount();
            }
        });
    }

    // Add mail input events
    const addMailInput = document.getElementById('add-mail-input');
    if (addMailInput) {
        // Auto add mails when pressing Enter in the input
        addMailInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                addMailsFromText();
            }
        });

        // Paste event
        addMailInput.addEventListener('paste', function(e) {
            setTimeout(addMailsFromText, 0);
        });
    }

    // Initialize button states
    document.getElementById('add-mail-stop-btn').disabled = true;

    // Initialize keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (!document.querySelector('#add-mail.tab-pane.active')) return;
        
        // Ctrl + A: Select all
        if (e.ctrlKey && e.key === 'a') {
            e.preventDefault();
            const mainCheckbox = document.getElementById('source-mail-select-all');
            mainCheckbox.checked = !mainCheckbox.checked;
            toggleSourceMailSelectAll();
        }
        // Delete: Delete selected
        if (e.key === 'Delete') {
            deleteSelectedMails();
        }
        // Ctrl + V: Paste
        if (e.ctrlKey && e.key === 'v') {
            pasteAddMailFromClipboard();
        }
    });
});
