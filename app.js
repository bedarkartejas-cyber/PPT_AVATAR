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

let selectedFile = null;

// --- FILE UPLOAD LOGIC ---
dropZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', (e) => handleFile(e.target.files[0]));
dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.style.borderColor = 'var(--primary)'; });
dropZone.addEventListener('dragleave', (e) => { e.preventDefault(); dropZone.style.borderColor = 'var(--border)'; });
dropZone.addEventListener('drop', (e) => { e.preventDefault(); dropZone.style.borderColor = 'var(--border)'; handleFile(e.dataTransfer.files[0]); });

function handleFile(file) {
    if (file && file.name.endsWith('.pptx')) {
        selectedFile = file;
        fileNameDisplay.textContent = file.name;
        uploadBtn.disabled = false;
    } else {
        alert("Please select a valid .pptx file");
    }
}

uploadBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    uploadBtn.disabled = true;
    uploadBtn.textContent = "Uploading...";
    progressContainer.style.display = 'block';
    progressBar.style.width = '40%';

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch('/api/upload-ppt', { method: 'POST', body: formData });
        if (response.ok) {
            const data = await response.json();
            progressBar.style.width = '100%';
            
            setTimeout(() => {
                document.getElementById('upload-card').style.opacity = '0.5';
                document.getElementById('upload-card').style.pointerEvents = 'none';
                connectCard.classList.remove('disabled');
                connectBtn.disabled = false;
                document.getElementById('slide-info').style.display = 'block';
                slideCountSpan.textContent = data.slide_count || '?';
                uploadBtn.textContent = "Upload Complete";
            }, 500);
        } else { throw new Error('Upload failed'); }
    } catch (error) {
        alert("Error: " + error.message);
        uploadBtn.disabled = false;
        uploadBtn.textContent = "Try Again";
    }
});

// --- CONNECTION LOGIC (UPDATED FOR MICROPHONE) ---
connectBtn.addEventListener('click', async () => {
    connectBtn.disabled = true;
    connectBtn.textContent = "Connecting...";

    try {
        const response = await fetch('/api/connection-details');
        const { serverUrl, participantToken } = await response.json();

        // 1. Create Room
        const room = new LivekitClient.Room();
        
        // 2. Handle Agent Video/Audio
        room.on(LivekitClient.RoomEvent.TrackSubscribed, (track, publication, participant) => {
            if (track.kind === 'video') {
                const element = track.attach();
                videoContainer.innerHTML = ''; 
                videoContainer.appendChild(element);
                
                // Switch Screens only when video appears
                setupScreen.style.display = 'none';
                presentationScreen.style.display = 'flex';
            }
            if (track.kind === 'audio') {
                track.attach(); // Hear the agent
            }
        });

        // 3. Connect
        await room.connect(serverUrl, participantToken);
        
        // 4. ENABLE MICROPHONE (Crucial Step Added Here)
        console.log("🎙️ Enabling Microphone...");
        await room.localParticipant.setMicrophoneEnabled(true);

        // 5. Enable Audio Output (Just in case)
        await room.startAudio();

    } catch (error) {
        console.error(error);
        alert("Connection Error: " + error.message);
        connectBtn.disabled = false;
        connectBtn.textContent = "Start Presentation";
    }
});