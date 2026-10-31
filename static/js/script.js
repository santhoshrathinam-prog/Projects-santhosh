/**
 * FarmDirect – JavaScript Utility & Laptop Webcam Interactions
 * Clean, modern, vanilla JavaScript for interactive UI enhancements,
 * client-side validation, and real laptop webcam media capture.
 */

// Global Webcam Controller Object
const FarmDirectWebcam = {
    currentStream: null,
    targetInputId: null,
    targetPreviewId: null,
    targetContainerId: null,
    targetWarningId: null,
    capturedBlob: null,
    modalInstance: null,

    init: function () {
        const modalEl = document.getElementById('webcamModal');
        if (!modalEl) return;
        
        // Initialize bootstrap modal instance
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            this.modalInstance = new bootstrap.Modal(modalEl);
        }

        // Stop stream whenever modal is hidden (Esc, backdrop, cancel, 'X' button)
        modalEl.addEventListener('hidden.bs.modal', () => {
            this.stopStream();
            this.resetModalUI();
        });

        // Event delegation for "Take Photo" webcam trigger buttons
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('.btn-open-webcam');
            if (btn) {
                e.preventDefault();
                this.targetInputId = btn.getAttribute('data-input-target');
                this.targetPreviewId = btn.getAttribute('data-preview-target');
                this.targetContainerId = btn.getAttribute('data-container-target');
                this.targetWarningId = btn.getAttribute('data-warning-target');
                this.open();
            }

            // Event delegation for "Choose from Gallery" buttons
            const galleryBtn = e.target.closest('.btn-trigger-gallery');
            if (galleryBtn) {
                e.preventDefault();
                const inputId = galleryBtn.getAttribute('data-input-target');
                const fileInput = document.getElementById(inputId);
                if (fileInput) {
                    fileInput.click();
                }
            }
        });

        // Capture Photo button in modal
        const btnCapture = document.getElementById('btnWebcamCapture');
        if (btnCapture) {
            btnCapture.addEventListener('click', () => this.capture());
        }

        // Retake Photo button in modal
        const btnRetake = document.getElementById('btnWebcamRetake');
        if (btnRetake) {
            btnRetake.addEventListener('click', () => this.startStream());
        }

        // Save/Use Photo button in modal
        const btnSave = document.getElementById('btnWebcamSave');
        if (btnSave) {
            btnSave.addEventListener('click', () => this.saveCapturedPhoto());
        }

        // Cancel button in modal
        const btnCancel = document.getElementById('btnWebcamCancel');
        if (btnCancel) {
            btnCancel.addEventListener('click', () => {
                this.stopStream();
                if (this.modalInstance) this.modalInstance.hide();
            });
        }
    },

    open: function () {
        this.resetModalUI();
        if (this.modalInstance) {
            this.modalInstance.show();
        }
        this.startStream();
    },

    startStream: async function () {
        const video = document.getElementById('webcamVideo');
        const capturedImg = document.getElementById('webcamCapturedImage');
        const alertBox = document.getElementById('webcamAlert');
        const liveBadge = document.getElementById('webcamLiveBadge');
        const viewfinder = document.getElementById('webcamViewfinder');
        const liveControls = document.getElementById('webcamLiveControls');
        const capturedControls = document.getElementById('webcamCapturedControls');

        if (alertBox) alertBox.classList.add('d-none');
        if (capturedImg) capturedImg.classList.add('d-none');
        if (video) video.classList.remove('d-none');
        if (liveBadge) liveBadge.classList.remove('d-none');
        if (viewfinder) viewfinder.classList.remove('d-none');
        if (liveControls) liveControls.classList.remove('d-none');
        if (capturedControls) capturedControls.classList.add('d-none');

        // Check browser MediaDevices API compatibility
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            this.showError('Webcam capture is not supported by this browser. Please use Choose from Gallery.');
            if (video) video.classList.add('d-none');
            if (liveBadge) liveBadge.classList.add('d-none');
            if (viewfinder) viewfinder.classList.add('d-none');
            if (liveControls) liveControls.classList.add('d-none');
            return;
        }

        try {
            this.stopStream(); // Ensure previous stream tracks are stopped
            const constraints = {
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: 'user'
                },
                audio: false
            };

            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            this.currentStream = stream;
            if (video) {
                video.srcObject = stream;
                await video.play();
            }
        } catch (err) {
            console.error('Camera access error:', err);
            if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
                this.showError('Camera access was denied. Please allow camera permission in your browser settings or use Choose from Gallery.');
            } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
                this.showError('No webcam was detected on your laptop. Please connect a camera or use Choose from Gallery.');
            } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
                this.showError('Your webcam is already in use by another application. Please close it and try again.');
            } else {
                this.showError('Unable to start camera (' + (err.message || err.name) + '). Please use Choose from Gallery.');
            }
            if (video) video.classList.add('d-none');
            if (liveBadge) liveBadge.classList.add('d-none');
            if (viewfinder) viewfinder.classList.add('d-none');
            if (liveControls) liveControls.classList.add('d-none');
        }
    },

    capture: function () {
        const video = document.getElementById('webcamVideo');
        const canvas = document.getElementById('webcamCanvas');
        const capturedImg = document.getElementById('webcamCapturedImage');
        const liveBadge = document.getElementById('webcamLiveBadge');
        const viewfinder = document.getElementById('webcamViewfinder');
        const liveControls = document.getElementById('webcamLiveControls');
        const capturedControls = document.getElementById('webcamCapturedControls');

        if (!video || !canvas) return;

        const width = video.videoWidth || 640;
        const height = video.videoHeight || 480;

        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');

        // Mirror image horizontally to match what the user sees in the mirrored webcam preview
        ctx.translate(width, 0);
        ctx.scale(-1, 1);
        ctx.drawImage(video, 0, 0, width, height);

        canvas.toBlob((blob) => {
            if (!blob) return;
            this.capturedBlob = blob;

            // Stop webcam stream tracks immediately after capture
            this.stopStream();

            // Display captured image in modal preview
            const previewUrl = URL.createObjectURL(blob);
            if (capturedImg) {
                capturedImg.src = previewUrl;
                capturedImg.classList.remove('d-none');
            }
            if (video) video.classList.add('d-none');
            if (liveBadge) liveBadge.classList.add('d-none');
            if (viewfinder) viewfinder.classList.add('d-none');
            if (liveControls) liveControls.classList.add('d-none');
            if (capturedControls) capturedControls.classList.remove('d-none');
        }, 'image/jpeg', 0.92);
    },

    saveCapturedPhoto: function () {
        if (!this.capturedBlob) return;

        const fileName = 'webcam_capture_' + Date.now() + '.jpg';
        const file = new File([this.capturedBlob], fileName, { type: 'image/jpeg' });

        // Update target file input via standard DataTransfer
        if (this.targetInputId) {
            const input = document.getElementById(this.targetInputId);
            if (input) {
                try {
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(file);
                    input.files = dataTransfer.files;
                } catch (e) {
                    console.warn('DataTransfer not supported by this browser:', e);
                }

                // Update live image preview on host page
                if (this.targetPreviewId) {
                    const previewImg = document.getElementById(this.targetPreviewId);
                    if (previewImg) {
                        previewImg.src = URL.createObjectURL(this.capturedBlob);
                    }
                }

                // Show preview container
                if (this.targetContainerId) {
                    const container = document.getElementById(this.targetContainerId);
                    if (container) {
                        container.classList.remove('d-none');
                    }
                }

                // Clear any warning messages
                if (this.targetWarningId) {
                    const warning = document.getElementById(this.targetWarningId);
                    if (warning) warning.classList.add('d-none');
                }
            }
        }

        // Close modal and stop any remaining camera tracks
        this.stopStream();
        if (this.modalInstance) {
            this.modalInstance.hide();
        }
    },

    stopStream: function () {
        if (this.currentStream) {
            this.currentStream.getTracks().forEach(track => {
                track.stop();
            });
            this.currentStream = null;
        }
        const video = document.getElementById('webcamVideo');
        if (video) {
            video.srcObject = null;
        }
    },

    showError: function (msg) {
        const alertBox = document.getElementById('webcamAlert');
        if (alertBox) {
            alertBox.textContent = msg;
            alertBox.classList.remove('d-none');
        }
    },

    resetModalUI: function () {
        const alertBox = document.getElementById('webcamAlert');
        const capturedImg = document.getElementById('webcamCapturedImage');
        const liveControls = document.getElementById('webcamLiveControls');
        const capturedControls = document.getElementById('webcamCapturedControls');

        if (alertBox) alertBox.classList.add('d-none');
        if (capturedImg) {
            capturedImg.classList.add('d-none');
            capturedImg.src = '';
        }
        if (liveControls) liveControls.classList.remove('d-none');
        if (capturedControls) capturedControls.classList.add('d-none');
        this.capturedBlob = null;
    }
};

// DOM Content Loaded Handler
document.addEventListener('DOMContentLoaded', function () {
    // 1. Initialize Laptop Webcam Controller
    FarmDirectWebcam.init();

    // 2. Auto-dismiss Bootstrap alert banners after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // 3. Generic confirmation prompt for critical actions
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            const message = this.getAttribute('data-confirm') || 'Are you sure you want to proceed?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // 4. Dynamic role selector toggle in registration form
    const roleSelect = document.getElementById('roleSelect');
    const farmerFields = document.getElementById('farmerFields');
    const customerFields = document.getElementById('customerFields');

    function toggleRegistrationFields() {
        if (!roleSelect) return;
        const selectedRole = roleSelect.value;
        if (selectedRole === 'farmer') {
            if (farmerFields) farmerFields.style.display = 'block';
            if (customerFields) customerFields.style.display = 'none';
            toggleRequired(farmerFields, true);
            toggleRequired(customerFields, false);
        } else if (selectedRole === 'customer') {
            if (farmerFields) farmerFields.style.display = 'none';
            if (customerFields) customerFields.style.display = 'block';
            toggleRequired(farmerFields, false);
            toggleRequired(customerFields, true);
        } else {
            if (farmerFields) farmerFields.style.display = 'none';
            if (customerFields) customerFields.style.display = 'none';
            toggleRequired(farmerFields, false);
            toggleRequired(customerFields, false);
        }
    }

    function toggleRequired(container, isRequired) {
        if (!container) return;
        const inputs = container.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (input.dataset.mandatory === 'true') {
                if (isRequired) {
                    input.setAttribute('required', 'required');
                } else {
                    input.removeAttribute('required');
                }
            }
        });
    }

    if (roleSelect) {
        roleSelect.addEventListener('change', toggleRegistrationFields);
        toggleRegistrationFields();
    }

    // 5. Quantity increment/decrement buttons
    const qtyInputs = document.querySelectorAll('.qty-control-input');
    qtyInputs.forEach(input => {
        const container = input.closest('.qty-control-group');
        if (!container) return;

        const btnMinus = container.querySelector('.qty-btn-minus');
        const btnPlus = container.querySelector('.qty-btn-plus');
        const maxVal = parseFloat(input.getAttribute('max')) || 9999;
        const minVal = parseFloat(input.getAttribute('min')) || 1;
        const stepVal = parseFloat(input.getAttribute('step')) || 1;

        if (btnMinus) {
            btnMinus.addEventListener('click', function () {
                let current = parseFloat(input.value) || minVal;
                if (current - stepVal >= minVal) {
                    input.value = Math.round((current - stepVal) * 100) / 100;
                    input.dispatchEvent(new Event('change'));
                }
            });
        }

        if (btnPlus) {
            btnPlus.addEventListener('click', function () {
                let current = parseFloat(input.value) || minVal;
                if (current + stepVal <= maxVal) {
                    input.value = Math.round((current + stepVal) * 100) / 100;
                    input.dispatchEvent(new Event('change'));
                }
            });
        }
    });

    // 6. Gallery File Input Change Handler & Validation
    const imageInputs = document.querySelectorAll('.image-preview-input');
    imageInputs.forEach(function (input) {
        input.addEventListener('change', function () {
            const targetPreviewId = this.getAttribute('data-preview-target');
            const targetContainerId = this.getAttribute('data-preview-container');
            const previewImg = document.getElementById(targetPreviewId);
            const previewContainer = document.getElementById(targetContainerId);
            const warningBox = document.getElementById(this.getAttribute('data-warning-target'));

            if (this.files && this.files[0]) {
                const file = this.files[0];
                const maxBytes = 5 * 1024 * 1024; // 5 MB

                // Allowed extension check
                const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg'];
                if (file.type && !allowedTypes.includes(file.type.toLowerCase())) {
                    if (warningBox) {
                        warningBox.textContent = 'Invalid file format. Please choose a JPG, PNG, or WEBP image.';
                        warningBox.classList.remove('d-none');
                    } else {
                        alert('Invalid file format. Please choose a JPG, PNG, or WEBP image.');
                    }
                    this.value = '';
                    if (previewContainer) previewContainer.classList.add('d-none');
                    return;
                }

                // File size check
                if (file.size > maxBytes) {
                    if (warningBox) {
                        warningBox.textContent = 'Image size exceeds 5MB limit. Please choose a smaller photo.';
                        warningBox.classList.remove('d-none');
                    } else {
                        alert('Image size exceeds 5MB limit. Please choose a smaller photo.');
                    }
                    this.value = '';
                    if (previewContainer) previewContainer.classList.add('d-none');
                    return;
                }

                if (warningBox) {
                    warningBox.classList.add('d-none');
                }

                const reader = new FileReader();
                reader.onload = function (e) {
                    if (previewImg) {
                        previewImg.src = e.target.result;
                    }
                    if (previewContainer) {
                        previewContainer.classList.remove('d-none');
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    });

    // 7. Reset Image Preview Buttons
    const clearImageButtons = document.querySelectorAll('.btn-clear-preview');
    clearImageButtons.forEach(function (btn) {
        btn.addEventListener('click', function () {
            const inputId = this.getAttribute('data-input-target');
            const containerId = this.getAttribute('data-container-target');
            const fileInput = document.getElementById(inputId);
            const container = document.getElementById(containerId);

            if (fileInput) fileInput.value = '';
            if (container) container.classList.add('d-none');
        });
    });

    // 8. Demo Payment System Handler (Checkout Page)
    const paymentRadios = document.querySelectorAll('input[name="payment_method"]');
    const upiSection = document.getElementById('upiDemoSection');
    const cardSection = document.getElementById('cardDemoSection');
    const btnSubmitOrder = document.getElementById('btnSubmitOrder');
    const btnAutoFillCard = document.getElementById('btnAutoFillCard');
    const cardholderInput = document.getElementById('cardholder_name');
    const cardNumInput = document.getElementById('card_number');
    const cardExpiryInput = document.getElementById('card_expiry');
    const cardCvvInput = document.getElementById('card_cvv');
    const cardWarning = document.getElementById('cardValidationWarning');
    const checkoutForm = document.getElementById('checkoutPaymentForm');

    function updatePaymentMethodUI() {
        const selected = document.querySelector('input[name="payment_method"]:checked');
        if (!selected) return;

        const val = selected.value;
        if (upiSection) upiSection.classList.add('d-none');
        if (cardSection) cardSection.classList.add('d-none');
        if (cardWarning) cardWarning.classList.add('d-none');

        if (val === 'cod') {
            if (btnSubmitOrder) {
                btnSubmitOrder.innerHTML = '<i class="bi bi-bag-check me-2"></i>Place Order (Cash on Delivery)';
                btnSubmitOrder.className = 'btn btn-farm w-100 py-3 fw-bold fs-5 shadow-sm';
            }
        } else if (val === 'upi') {
            if (upiSection) upiSection.classList.remove('d-none');
            if (btnSubmitOrder) {
                btnSubmitOrder.innerHTML = '<i class="bi bi-qr-code-scan me-2"></i>Simulate UPI Payment & Place Order';
                btnSubmitOrder.className = 'btn btn-primary w-100 py-3 fw-bold fs-5 shadow-sm';
            }
        } else if (val === 'card') {
            if (cardSection) cardSection.classList.remove('d-none');
            if (btnSubmitOrder) {
                btnSubmitOrder.innerHTML = '<i class="bi bi-credit-card me-2"></i>Pay Now – Demo';
                btnSubmitOrder.className = 'btn btn-warning text-dark w-100 py-3 fw-bold fs-5 shadow-sm';
            }
        }
    }

    if (paymentRadios.length > 0) {
        paymentRadios.forEach(radio => {
            radio.addEventListener('change', updatePaymentMethodUI);
        });
        updatePaymentMethodUI();
    }

    // Auto-fill Demo Card
    if (btnAutoFillCard) {
        btnAutoFillCard.addEventListener('click', function () {
            if (cardholderInput) cardholderInput.value = 'Demo User';
            if (cardNumInput) cardNumInput.value = '4111 1111 1111 1111';
            if (cardExpiryInput) cardExpiryInput.value = '12/30';
            if (cardCvvInput) cardCvvInput.value = '123';
            if (cardWarning) cardWarning.classList.add('d-none');
        });
    }

    // Format Card Number input with spaces (#### #### #### ####)
    if (cardNumInput) {
        cardNumInput.addEventListener('input', function () {
            let val = this.value.replace(/\D/g, '').substring(0, 16);
            let formatted = val.match(/.{1,4}/g)?.join(' ') || val;
            this.value = formatted;
        });
    }

    // Format Expiry Date input (MM/YY)
    if (cardExpiryInput) {
        cardExpiryInput.addEventListener('input', function () {
            let val = this.value.replace(/\D/g, '').substring(0, 4);
            if (val.length >= 3) {
                this.value = val.substring(0, 2) + '/' + val.substring(2);
            } else {
                this.value = val;
            }
        });
    }

    // Restrict CVV input to digits (3-4)
    if (cardCvvInput) {
        cardCvvInput.addEventListener('input', function () {
            this.value = this.value.replace(/\D/g, '').substring(0, 4);
        });
    }

    // Form Validation on Checkout Submit
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', function (e) {
            const selected = document.querySelector('input[name="payment_method"]:checked');
            if (selected && selected.value === 'card') {
                const holder = cardholderInput ? cardholderInput.value.trim() : '';
                const num = cardNumInput ? cardNumInput.value.replace(/\s+/g, '') : '';
                const exp = cardExpiryInput ? cardExpiryInput.value.trim() : '';
                const cvv = cardCvvInput ? cardCvvInput.value.trim() : '';

                if (!holder) {
                    e.preventDefault();
                    showCardError('Please enter Cardholder Name (or click Auto-Fill Demo Card).');
                    return;
                }
                if (num.length !== 16 || !/^\d{16}$/.test(num)) {
                    e.preventDefault();
                    showCardError('Please enter a valid 16-digit demo card number.');
                    return;
                }
                if (!/^\d{2}\/\d{2}$/.test(exp)) {
                    e.preventDefault();
                    showCardError('Please enter a valid expiry date in MM/YY format (e.g. 12/30).');
                    return;
                }
                if (cvv.length < 3 || cvv.length > 4 || !/^\d+$/.test(cvv)) {
                    e.preventDefault();
                    showCardError('Please enter a 3 or 4-digit CVV (e.g. 123).');
                    return;
                }
            }
        });
    }

    function showCardError(msg) {
        if (cardWarning) {
            cardWarning.textContent = msg;
            cardWarning.classList.remove('d-none');
        } else {
            alert(msg);
        }
    }
});
