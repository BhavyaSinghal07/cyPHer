async function getCameras() {
    const devices = await navigator.mediaDevices.enumerateDevices();
    const cameras = devices.filter(device => device.kind === 'videoinput');
    const select = document.getElementById('camera-select');
    
    cameras.forEach(camera => {
        const option = document.createElement('option');
        option.value = camera.deviceId;
        option.text = camera.label || `Camera ${select.length + 1}`;
        select.appendChild(option);
    });
}

async function startCamera() {
    const cameraId = document.getElementById('camera-select').value;
    const video = document.getElementById('camera-feed');

    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: cameraId ? {deviceId: {exact: cameraId}} : true
        });
        video.srcObject = stream;
    } catch (err) {
        console.error('Error accessing camera:', err);
        alert('Error accessing camera. Please make sure you have granted camera permissions.');
    }
}

// Initialize camera list when page loads
getCameras().catch(console.error);

function stopCamera() {
    const video = document.getElementById('camera-feed');
    const stream = video.srcObject;
    
    if (stream) {
        const tracks = stream.getTracks();
        tracks.forEach(track => track.stop());
        video.srcObject = null;
    }
}