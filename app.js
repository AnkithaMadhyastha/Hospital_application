// ============================================
// Global State
// ============================================
let patients = [];
let editingPatientId = null;

// ============================================
// API Functions
// ============================================
const API_BASE = '/api';

async function fetchPatients() {
    try {
        const response = await fetch(`${API_BASE}/patients`);
        patients = await response.json();
        renderPatientsTable();
        updateStats();
    } catch (error) {
        showToast('Failed to load patients', 'error');
    }
}

async function createPatient(data) {
    const response = await fetch(`${API_BASE}/patients`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.errors?.join(', ') || 'Failed to create patient');
    }

    return response.json();
}

async function updatePatient(id, data) {
    const response = await fetch(`${API_BASE}/patients/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.errors?.join(', ') || 'Failed to update patient');
    }

    return response.json();
}

async function deletePatient(id) {
    const response = await fetch(`${API_BASE}/patients/${id}`, {
        method: 'DELETE'
    });

    if (!response.ok) {
        throw new Error('Failed to delete patient');
    }
}

// ============================================
// UI Rendering
// ============================================
function renderPatientsTable() {
    const tbody = document.getElementById('patients-table-body');

    if (patients.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="empty-state">
                    No patients found. Click "Add New Patient" to get started.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = patients.map(patient => {
        const status = getHealthStatus(patient);
        return `
            <tr>
                <td><strong>${escapeHtml(patient.full_name)}</strong></td>
                <td>${formatDate(patient.date_of_birth)}</td>
                <td>${escapeHtml(patient.email)}</td>
                <td>${patient.glucose}</td>
                <td>${patient.haemoglobin}</td>
                <td>${patient.cholesterol}</td>
                <td><span class="status-badge ${status.class}">${status.icon} ${status.text}</span></td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-icon view" onclick="viewPatient(${patient.id})" title="View Details">👁️</button>
                        <button class="btn-icon edit" onclick="editPatient(${patient.id})" title="Edit">✏️</button>
                        <button class="btn-icon delete" onclick="confirmDelete(${patient.id})" title="Delete">🗑️</button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

function getHealthStatus(patient) {
    const remarks = patient.remarks || '';
    if (remarks.includes('🔴') || remarks.includes('multiple') || remarks.includes('High')) {
        return { class: 'danger', text: 'At Risk', icon: '⚠️' };
    } else if (remarks.includes('⚠️') || remarks.includes('Elevated') || remarks.includes('Borderline')) {
        return { class: 'warning', text: 'Monitor', icon: '⚡' };
    }
    return { class: 'healthy', text: 'Healthy', icon: '✓' };
}

function updateStats() {
    const total = patients.length;
    let healthy = 0;
    let atRisk = 0;

    patients.forEach(patient => {
        const status = getHealthStatus(patient);
        if (status.class === 'healthy') healthy++;
        else atRisk++;
    });

    document.getElementById('total-patients').textContent = total;
    document.getElementById('healthy-count').textContent = healthy;
    document.getElementById('risk-count').textContent = atRisk;
}

// ============================================
// Navigation
// ============================================
function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));

    document.getElementById(sectionId).classList.add('active');
    document.querySelector(`[data-section="${sectionId}"]`)?.classList.add('active');

    if (sectionId === 'add-patient' && !editingPatientId) {
        resetForm();
    }
}

document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const section = link.dataset.section;
        showSection(section);
    });
});

// ============================================
// Form Handling
// ============================================
document.getElementById('patient-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const submitBtn = document.getElementById('submit-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoading = submitBtn.querySelector('.btn-loading');

    // Clear previous errors
    document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
    document.querySelectorAll('input.error').forEach(el => el.classList.remove('error'));

    // Collect form data
    const formData = {
        full_name: document.getElementById('full_name').value.trim(),
        date_of_birth: document.getElementById('date_of_birth').value,
        email: document.getElementById('email').value.trim(),
        glucose: parseFloat(document.getElementById('glucose').value),
        haemoglobin: parseFloat(document.getElementById('haemoglobin').value),
        cholesterol: parseFloat(document.getElementById('cholesterol').value)
    };

    // Client-side validation
    const errors = validateForm(formData);
    if (errors.length > 0) {
        errors.forEach(err => {
            const errorEl = document.getElementById(`${err.field}-error`);
            const inputEl = document.getElementById(err.field);
            if (errorEl) errorEl.textContent = err.message;
            if (inputEl) inputEl.classList.add('error');
        });
        return;
    }

    // Show loading state
    submitBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoading.style.display = 'inline';

    try {
        if (editingPatientId) {
            await updatePatient(editingPatientId, formData);
            showToast('Patient updated successfully!', 'success');
        } else {
            await createPatient(formData);
            showToast('Patient added and analyzed!', 'success');
        }

        resetForm();
        await fetchPatients();
        showSection('dashboard');

    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        submitBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
    }
});

function validateForm(data) {
    const errors = [];

    if (!data.full_name || data.full_name.length < 2) {
        errors.push({ field: 'full_name', message: 'Name must be at least 2 characters' });
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(data.email)) {
        errors.push({ field: 'email', message: 'Please enter a valid email address' });
    }

    const dob = new Date(data.date_of_birth);
    if (isNaN(dob) || dob > new Date()) {
        errors.push({ field: 'date_of_birth', message: 'Date of birth cannot be in the future' });
    }

    if (isNaN(data.glucose) || data.glucose <= 0 || data.glucose > 1000) {
        errors.push({ field: 'glucose', message: 'Glucose must be between 0 and 1000' });
    }

    if (isNaN(data.haemoglobin) || data.haemoglobin <= 0 || data.haemoglobin > 30) {
        errors.push({ field: 'haemoglobin', message: 'Haemoglobin must be between 0 and 30' });
    }

    if (isNaN(data.cholesterol) || data.cholesterol <= 0 || data.cholesterol > 1000) {
        errors.push({ field: 'cholesterol', message: 'Cholesterol must be between 0 and 1000' });
    }

    return errors;
}

function resetForm() {
    document.getElementById('patient-form').reset();
    document.getElementById('patient-id').value = '';
    document.getElementById('form-title').textContent = 'Add New Patient';
    document.getElementById('submit-btn').querySelector('.btn-text').textContent = 'Save & Analyze';
    document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
    document.querySelectorAll('input.error').forEach(el => el.classList.remove('error'));
    editingPatientId = null;
}

// ============================================
// CRUD Operations
// ============================================
function viewPatient(id) {
    const patient = patients.find(p => p.id === id);
    if (!patient) return;

    document.getElementById('modal-patient-name').textContent = patient.full_name;

    const status = getHealthStatus(patient);
    document.getElementById('modal-body').innerHTML = `
        <div class="detail-grid">
            <div class="detail-item">
                <div class="detail-label">Full Name</div>
                <div class="detail-value">${escapeHtml(patient.full_name)}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Date of Birth</div>
                <div class="detail-value">${formatDate(patient.date_of_birth)}</div>
            </div>
            <div class="detail-item full-width">
                <div class="detail-label">Email Address</div>
                <div class="detail-value">${escapeHtml(patient.email)}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Glucose (mg/dL)</div>
                <div class="detail-value">${patient.glucose}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Haemoglobin (g/dL)</div>
                <div class="detail-value">${patient.haemoglobin}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Cholesterol (mg/dL)</div>
                <div class="detail-value">${patient.cholesterol}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Health Status</div>
                <div class="detail-value">
                    <span class="status-badge ${status.class}">${status.icon} ${status.text}</span>
                </div>
            </div>
            <div class="detail-item full-width">
                <div class="detail-label">AI Health Analysis</div>
                <div class="remarks-box">${escapeHtml(patient.remarks) || 'No analysis available'}</div>
            </div>
        </div>
    `;

    document.getElementById('patient-modal').classList.add('active');
}

function editPatient(id) {
    const patient = patients.find(p => p.id === id);
    if (!patient) return;

    editingPatientId = id;
    document.getElementById('form-title').textContent = 'Edit Patient';
    document.getElementById('submit-btn').querySelector('.btn-text').textContent = 'Update Patient';

    document.getElementById('full_name').value = patient.full_name;
    document.getElementById('date_of_birth').value = patient.date_of_birth;
    document.getElementById('email').value = patient.email;
    document.getElementById('glucose').value = patient.glucose;
    document.getElementById('haemoglobin').value = patient.haemoglobin;
    document.getElementById('cholesterol').value = patient.cholesterol;

    showSection('add-patient');
}

function confirmDelete(id) {
    const patient = patients.find(p => p.id === id);
    if (!patient) return;

    if (confirm(`Are you sure you want to delete ${patient.full_name}'s record? This action cannot be undone.`)) {
        deletePatientRecord(id);
    }
}

async function deletePatientRecord(id) {
    try {
        await deletePatient(id);
        showToast('Patient deleted successfully', 'success');
        await fetchPatients();
    } catch (error) {
        showToast('Failed to delete patient', 'error');
    }
}

function closeModal() {
    document.getElementById('patient-modal').classList.remove('active');
}

// Close modal on outside click
document.getElementById('patient-modal').addEventListener('click', (e) => {
    if (e.target.id === 'patient-modal') {
        closeModal();
    }
});

// ============================================
// Utility Functions
// ============================================
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 4000);
}

// ============================================
// Initialize
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    fetchPatients();

    // Set max date for DOB to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('date_of_birth').setAttribute('max', today);
});
