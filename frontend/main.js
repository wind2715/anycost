// Các element
const uploadInput = document.getElementById('upload-input');
const uploadBtn = document.getElementById('upload-btn');
const editBtn = document.getElementById('edit-btn');
const directionSelect = document.getElementById('direction-select');
const strengthSlider = document.getElementById('strength-slider');
const strengthValue = document.getElementById('strength-value');
const channelSlider = document.getElementById('channel-slider');
const channelValue = document.getElementById('channel-value');
const resolutionSlider = document.getElementById('resolution-slider');
const resolutionValue = document.getElementById('resolution-value');
const originalImg = document.getElementById('original-img');
const editedImg = document.getElementById('edited-img');
const statusMessage = document.getElementById('status-message');
const loadingSpinner = document.getElementById('loading-spinner');

// API URL
const API_URL = 'http://localhost:5000';

// State
let currentLatentId = null;

// Khởi tạo
async function init() {
    // Tải danh sách directions
    try {
        const response = await fetch(`${API_URL}/directions`);
        const data = await response.json();
        
        if (data.directions && data.directions.length > 0) {
            // Thêm directions vào select
            directionSelect.innerHTML = '';
            data.directions.forEach(direction => {
                const option = document.createElement('option');
                option.value = direction;
                option.textContent = direction;
                directionSelect.appendChild(option);
            });
        }
    } catch (error) {
        showStatus('Error loading directions: ' + error.message, true);
    }
    
    // Event listeners
    uploadInput.addEventListener('change', () => {
        uploadBtn.disabled = !uploadInput.files.length;
    });
    
    uploadBtn.addEventListener('click', handleUpload);
    editBtn.addEventListener('click', handleEdit);
    
    strengthSlider.addEventListener('input', () => {
        strengthValue.textContent = strengthSlider.value;
    });
    
    channelSlider.addEventListener('input', () => {
        channelValue.textContent = channelSlider.value;
    });
    
    resolutionSlider.addEventListener('input', () => {
        resolutionValue.textContent = resolutionSlider.value;
    });
}

// Xử lý upload
async function handleUpload() {
    if (!uploadInput.files.length) return;
    
    showStatus('Uploading and encoding image...', false, true);
    
    const formData = new FormData();
    formData.append('image', uploadInput.files[0]);
    
    try {
        const response = await fetch(`${API_URL}/encode`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentLatentId = data.latent_id;
            originalImg.src = `data:image/jpeg;base64,${data.image}`;
            editedImg.src = originalImg.src;
            
            // Enable controls
            directionSelect.disabled = false;
            strengthSlider.disabled = false;
            channelSlider.disabled = false;
            resolutionSlider.disabled = false;
            editBtn.disabled = false;
            
            showStatus('Image encoded successfully!');
        } else {
            showStatus('Error: ' + (data.error || 'Unknown error'), true);
        }
    } catch (error) {
        showStatus('Error: ' + error.message, true);
    }
}

// Xử lý edit
async function handleEdit() {
    if (!currentLatentId) return;
    
    showStatus('Applying edit...', false, true);
    
    const params = {
        latent_id: currentLatentId,
        direction: directionSelect.value,
        strength: parseFloat(strengthSlider.value),
        channel_ratio: parseFloat(channelSlider.value),
        resolution: parseInt(resolutionSlider.value)
    };
    
    try {
        const response = await fetch(`${API_URL}/edit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentLatentId = data.latent_id;
            editedImg.src = `data:image/jpeg;base64,${data.image}`;
            showStatus('Edit applied successfully!');
        } else {
            showStatus('Error: ' + (data.error || 'Unknown error'), true);
        }
    } catch (error) {
        showStatus('Error: ' + error.message, true);
    }
}

// Hiển thị status
function showStatus(message, isError = false, showSpinner = false) {
    statusMessage.textContent = message;
    statusMessage.style.color = isError ? 'red' : 'green';
    loadingSpinner.style.display = showSpinner ? 'inline-block' : 'none';
}

// Khởi tạo khi page load
window.addEventListener('DOMContentLoaded', init);