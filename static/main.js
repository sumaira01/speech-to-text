let recordingInterval;
let elapsedSeconds = 0;

async function startRecording() {
    const recordButton = document.getElementById('recordBtn');
    const timeDisplay = document.getElementById('recordTime');

    // Reset timer and disable button
    recordButton.innerText = "Recording... 🎙️";
    recordButton.disabled = true;
    elapsedSeconds = 0;
    timeDisplay.innerText = "Recording Time: 0 seconds";

    // Start timer display
    recordingInterval = setInterval(() => {
        elapsedSeconds += 1;
        timeDisplay.innerText = `Recording Time: ${elapsedSeconds} seconds`;
    }, 1000);

    try {
        // Send request to start recording
        const response = await fetch('/record', { method: 'POST' });
        const result = await response.json();

        // Clear timer when recording finishes
        clearInterval(recordingInterval);

        if (result.transcription) {
            document.getElementById('transcriptionResult').innerText = `Transcription: ${result.transcription}`;
            timeDisplay.innerText += ` (Total Recording Time: ${result.record_time} seconds)`;
            document.getElementById('processTime').innerText = `Processing Time: ${result.process_time} seconds`;
        } else {
            document.getElementById('transcriptionResult').innerText = "Error in transcription.";
        }
    } catch (error) {
        document.getElementById('transcriptionResult').innerText = "Error in transcription.";
    } finally {
        // Reset button and timer
        recordButton.innerText = "🎙️ Click to Record";
        recordButton.disabled = false;
        clearInterval(recordingInterval);
        elapsedSeconds = 0;
    }
}
