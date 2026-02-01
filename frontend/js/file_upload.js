// ========================================
// FILE UPLOAD HANDLER
// Handles drag-and-drop, file selection, and upload
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    const fileDropArea = document.getElementById('file-drop-area');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');
    const fileInfo = document.getElementById('file-info');
    const fileNameEl = document.getElementById('file-name');
    const fileSizeEl = document.getElementById('file-size');
    const fileTypeEl = document.getElementById('file-type');
    const fileTypeIcon = document.getElementById('file-type-icon');
    const removeFileBtn = document.getElementById('remove-file-btn');
    const startTransferBtn = document.getElementById('start-transfer');
    const fileDetailsModal = document.getElementById('file-details-modal');
    const closeFileModalBtn = document.getElementById('close-file-modal');
    const closeFileDetailsBtn = document.getElementById('close-file-details');

    let currentFile = null;
    let currentFileInfo = null;

    // Initialize drag-and-drop
    initDragAndDrop();
    initEventListeners();

    function initDragAndDrop() {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            fileDropArea.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        // Highlight drop area when file is dragged over
        ['dragenter', 'dragover'].forEach(eventName => {
            fileDropArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            fileDropArea.addEventListener(eventName, unhighlight, false);
        });

        // Handle dropped files
        fileDropArea.addEventListener('drop', handleDrop, false);
    }

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight() {
        fileDropArea.classList.add('drag-over');
        fileDropArea.parentElement.classList.add('drag-over');
    }

    function unhighlight() {
        fileDropArea.classList.remove('drag-over');
        fileDropArea.parentElement.classList.remove('drag-over');
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length) {
            handleFiles(files);
        }
    }

    function initEventListeners() {
        // Browse button click
        browseBtn.addEventListener('click', () => {
            fileInput.click();
        });

        // File input change
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length) {
                handleFiles(e.target.files);
            }
        });

        // Remove file button
        removeFileBtn.addEventListener('click', removeFile);

        // Close modal buttons
        closeFileModalBtn.addEventListener('click', closeModal);
        closeFileDetailsBtn.addEventListener('click', closeModal);

        // Modal click outside
        fileDetailsModal.addEventListener('click', (e) => {
            if (e.target === fileDetailsModal) {
                closeModal();
            }
        });
    }

    function handleFiles(files) {
        const file = files[0];

        // Validate file size (max 100MB)
        if (file.size > 100 * 1024 * 1024) {
            addLogEntry(`File too large: ${file.name} (${formatBytes(file.size)}). Max 100MB.`, 'error');
            return;
        }

        currentFile = file;

        // Display file info
        displayFileInfo(file);

        // Upload file to server
        uploadFile(file);
    }

    function displayFileInfo(file) {
        // Show file info section
        fileInfo.style.display = 'flex';

        // Update UI elements
        fileNameEl.textContent = file.name;
        fileSizeEl.textContent = formatBytes(file.size);
        fileTypeEl.textContent = getFileType(file);

        // Set file icon based on type
        setFileIcon(file);

        // Enable start transfer button
        startTransferBtn.disabled = false;

        // Add log entry
        addLogEntry(`File selected: ${file.name} (${formatBytes(file.size)}, ${getFileType(file)})`, 'info');
    }

    function setFileIcon(file) {
        const type = getFileType(file);
        let iconClass = 'fa-file';

        if (type.includes('Image')) iconClass = 'fa-file-image';
        else if (type.includes('Video')) iconClass = 'fa-file-video';
        else if (type.includes('Audio')) iconClass = 'fa-file-audio';
        else if (type.includes('Document') || type.includes('PDF')) iconClass = 'fa-file-pdf';
        else if (type.includes('Archive')) iconClass = 'fa-file-archive';
        else if (type.includes('Text')) iconClass = 'fa-file-alt';

        fileTypeIcon.className = `fas ${iconClass}`;
    }

    function getFileType(file) {
        const fileName = file.name.toLowerCase();
        const type = file.type;

        if (fileName.endsWith('.jpg') || fileName.endsWith('.jpeg') || fileName.endsWith('.png') || fileName.endsWith('.gif')) {
            return 'Image File';
        } else if (fileName.endsWith('.mp4') || fileName.endsWith('.avi') || fileName.endsWith('.mkv')) {
            return 'Video File';
        } else if (fileName.endsWith('.mp3') || fileName.endsWith('.wav') || fileName.endsWith('.flac')) {
            return 'Audio File';
        } else if (fileName.endsWith('.pdf') || fileName.endsWith('.doc') || fileName.endsWith('.docx')) {
            return 'Document';
        } else if (fileName.endsWith('.zip') || fileName.endsWith('.rar') || fileName.endsWith('.tar') || fileName.endsWith('.gz')) {
            return 'Archive';
        } else if (fileName.endsWith('.txt') || fileName.endsWith('.log') || fileName.endsWith('.csv')) {
            return 'Text File';
        } else {
            return 'Binary File';
        }
    }

    function removeFile() {
        currentFile = null;
        fileInfo.style.display = 'none';
        fileInput.value = '';
        startTransferBtn.disabled = true;
        addLogEntry('File removed', 'info');
    }

    function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        fetch('/api/upload-file', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    addLogEntry(`File uploaded successfully: ${data.file_info.name} (${data.file_info.size_mb} MB)`, 'success');
                    addLogEntry(`File Type: ${data.file_info.type}, Complexity: ${data.file_info.complexity}`, 'info');
                    addLogEntry(`File Hash: ${data.file_info.hash.substring(0, 16)}...`, 'info');

                    currentFileInfo = data.file_info;
                    // Show file details modal
                    showFileDetailsModal(data.file_info);
                } else {
                    addLogEntry(`Upload failed: ${data.error}`, 'error');
                    removeFile();
                }
            })
            .catch(error => {
                addLogEntry(`Upload error: ${error.message}`, 'error');
                console.error('Upload error:', error);
                removeFile();
            });
    }

    function showFileDetailsModal(fileInfo) {
        document.getElementById('modal-file-name').textContent = fileInfo.name;
        document.getElementById('modal-file-size').textContent = `${fileInfo.size_mb} MB`;
        document.getElementById('modal-file-type').textContent = fileInfo.type;
        document.getElementById('modal-file-complexity').textContent = fileInfo.complexity.toFixed(2);
        document.getElementById('modal-file-hash').textContent = fileInfo.hash ? fileInfo.hash.substring(0, 24) + '...' : 'N/A';

        // Calculate estimated times
        const profile = SystemProfiles.getCurrentProfile();
        const cpuTime = fileInfo.size_mb / (profile.max_dma_bandwidth * 0.6); // CPU is slower
        const dmaTime = fileInfo.size_mb / profile.max_dma_bandwidth;

        document.getElementById('modal-estimated-cpu').textContent = `${cpuTime.toFixed(2)} seconds`;
        document.getElementById('modal-estimated-dma').textContent = `${dmaTime.toFixed(2)} seconds`;

        fileDetailsModal.style.display = 'flex';
    }

    function closeModal() {
        fileDetailsModal.style.display = 'none';
    }

    function formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Expose functions globally for other modules
    window.fileUpload = {
        getCurrentFile: () => currentFile,
        getFileInfo: () => currentFileInfo,
        removeFile: removeFile,
        addLogEntry: addLogEntry
    };
});

// Helper function to add log entries (will be available globally)
function addLogEntry(message, type = 'info') {
    const logContent = document.getElementById('log-content');
    const time = new Date().toLocaleTimeString();
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.innerHTML = `
        <span class="log-time">[${time}]</span>
        <span class="log-message">${message}</span>
    `;
    logContent.appendChild(entry);
    logContent.scrollTop = logContent.scrollHeight;

    // Keep only last 100 entries
    while (logContent.children.length > 100) {
        logContent.removeChild(logContent.firstChild);
    }
}