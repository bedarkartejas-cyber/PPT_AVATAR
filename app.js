// DOM Elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const fileNameDisplay = document.getElementById('file-name');
const uploadBtn = document.getElementById('upload-btn');
const progressBar = document.getElementById('progress-bar');
const progressContainer = document.getElementById('progress-container');
const connectCard = document.getElementById('connect-card');
const connectBtn = document.getElementById('connect-btn');
const slideCountSpan = document.getElementById('slide-count');

// Screen Elements
const setupScreen = document.getElementById('setup-screen');
const presentationScreen = document.getElementById('presentation-screen');
const videoContainer = document.getElementById('video-container');

// Slide Elements
let slideImageElement = null;
let selectedFile = null;
let heartbeatInterval = null;

// --- 1. FILE UPLOAD LOGIC ---
dropZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', (e) => handleFile(e.target.files[0]));
dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.style.borderColor = 'var(--primary)'; });
dropZone.addEventListener('dragleave', (e) => { e.preventDefault(); dropZone.style.borderColor = 'var(--card-border)'; });
dropZone.addEventListener('drop', (e) => { e.preventDefault(); dropZone.style.borderColor = 'var(--card-border)'; handleFile(e.dataTransfer.files[0]); });

function handleFile(file) {
    if (file && file.name.endsWith('.pptx')) {
        selectedFile = file;
        fileNameDisplay.textContent = file.name;
        uploadBtn.disabled = false;
        dropZone.style.borderColor = 'var(--success)';
        dropZone.style.background = 'rgba(16, 185, 129, 0.05)';
    } else {
        alert("Please select a valid .pptx file");
    }
}

uploadBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    uploadBtn.disabled = true;
    uploadBtn.innerHTML = `<span>Uploading...</span>`;
    progressContainer.style.display = 'block';
    
    // Simulate visual progress
    let progress = 0;
    const interval = setInterval(() => {
        progress += 5;
        if (progress > 90) clearInterval(interval);
        progressBar.style.width = `${progress}%`;
    }, 100);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch('/api/upload-ppt', { method: 'POST', body: formData });
        clearInterval(interval);
        
        if (response.ok) {
            const data = await response.json();
            progressBar.style.width = '100%';
            
            setTimeout(() => {
                document.getElementById('upload-card').classList.add('disabled');
                connectCard.classList.remove('disabled');
                connectBtn.disabled = false;
                document.getElementById('slide-info').style.display = 'block';
                slideCountSpan.textContent = data.slide_count || '?';
                uploadBtn.innerHTML = `<span>Upload Complete</span>`;
            }, 500);
        } else { throw new Error('Upload failed'); }
    } catch (error) {
        progressBar.style.width = '0%';
        alert("Error: " + error.message);
        uploadBtn.disabled = false;
        uploadBtn.textContent = "Try Again";
    }
});

// --- 2. CONNECTION LOGIC ---
connectBtn.addEventListener('click', async () => {
    connectBtn.disabled = true;
    connectBtn.innerHTML = `<span>Connecting...</span>`;

    try {
        const response = await fetch('/api/connection-details');
        const { serverUrl, participantToken } = await response.json();

        const room = new LivekitClient.Room();
        
        // A. HANDLE AVATAR VIDEO/AUDIO
        room.on(LivekitClient.RoomEvent.TrackSubscribed, (track, publication, participant) => {
            if (track.kind === 'video') {
                const element = track.attach();
                videoContainer.innerHTML = ''; 
                videoContainer.appendChild(element);
                
                // Switch Screens
                setupScreen.style.display = 'none';
                presentationScreen.style.display = 'flex';
                
                initSlideView();
            }
            if (track.kind === 'audio') {
                track.attach();
            }
        });

        // B. HANDLE SLIDE CHANGES
        room.on(LivekitClient.RoomEvent.DataReceived, (payload, participant) => {
            const decoder = new TextDecoder();
            const strData = decoder.decode(payload);
            try {
                const data = JSON.parse(strData);
                if (data.type === "slide_change" && slideImageElement) {
                    // Force refresh image to avoid caching
                    slideImageElement.src = data.image_url + "?t=" + new Date().getTime();
                    console.log("📸 Slide Updated to:", data.slide_number);
                }
            } catch (e) {
                // Ignore empty pings
            }
        });

        await room.connect(serverUrl, participantToken);
        
        console.log("🎙️ Enabling Microphone...");
        await room.localParticipant.setMicrophoneEnabled(true);
        await room.startAudio();

        // --- C. CRITICAL HEARTBEAT FIX ---
        // This prevents the browser from "sleeping" and killing the connection
        startHeartbeat(room);

    } catch (error) {
        console.error(error);
        alert("Connection Error: " + error.message);
        connectBtn.disabled = false;
        connectBtn.textContent = "Start Presentation";
    }
});

// --- 3. HELPER: HEARTBEAT ---
function startHeartbeat(room) {
    if (heartbeatInterval) clearInterval(heartbeatInterval);
    
    // Send a "Ping" every 2 seconds. 
    // This keeps the WebSocket active even if the Avatar is silent.
    heartbeatInterval = setInterval(() => {
        if (room.state === 'connected') {
            const ping = new TextEncoder().encode(JSON.stringify({ type: "ping" }));
            room.localParticipant.publishData(ping, { reliable: true });
        }
    }, 2000); 
}

// --- 4. HELPER: SLIDE VIEWER ---
function initSlideView() {
    if (document.getElementById('slide-viewer')) return;

    const viewer = document.createElement('div');
    viewer.id = 'slide-viewer';
    viewer.style.cssText = `
        display: flex;
        gap: 20px;
        padding: 20px;
        height: calc(100vh - 60px);
        width: 100%;
    `;

    // Slide Box
    const slideBox = document.createElement('div');
    slideBox.style.cssText = `
        flex: 3;
        background: #000;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        border: 1px solid #333;
    `;
    
    slideImageElement = document.createElement('img');
    slideImageElement.style.cssText = `max-width: 100%; max-height: 100%; object-fit: contain;`;
    slideImageElement.src = "/slides/Slide1.jpg"; 
    slideBox.appendChild(slideImageElement);

    // Avatar Box
    const avatarBox = document.getElementById('video-container');
    avatarBox.style.flex = '1';
    avatarBox.style.height = '100%';
    avatarBox.style.background = '#000';
    avatarBox.style.borderRadius = '16px';
    avatarBox.style.overflow = 'hidden';
    avatarBox.style.border = '1px solid #333';
    
    viewer.appendChild(slideBox);
    viewer.appendChild(avatarBox);
    presentationScreen.appendChild(viewer);
}