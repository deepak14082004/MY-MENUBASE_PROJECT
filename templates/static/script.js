const startButton = document.getElementById('start');
const output = document.getElementById('output');

if ('webkitSpeechRecognition' in window) {
    const recognition = new webkitSpeechRecognition();
    
    recognition.continuous = true; // Keep listening until stopped
    recognition.interimResults = true; // Show interim results

    recognition.onstart = () => {
        console.log('Voice recognition started. Speak into the microphone.');
    };

    recognition.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }
        output.textContent = transcript; // Display the result
        
        // Optionally send the transcript to the server
        fetch('/process_speech', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: transcript })
        });
    };

    recognition.onerror = (event) => {
        console.error('Error occurred in recognition: ' + event.error);
    };

    recognition.onend = () => {
        console.log('Voice recognition ended.');
    };

    startButton.onclick = () => {
        recognition.start(); // Start the speech recognition
    };
} else {
    console.error('Speech recognition not supported in this browser.');
}
