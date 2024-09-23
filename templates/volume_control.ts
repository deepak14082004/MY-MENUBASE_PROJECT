<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Volume Control</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f0f0f0;
        }

        .container {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            text-align: center;
        }

        input[type="range"] {
            width: 100%;
            margin: 20px 0;
        }

        button {
            padding: 10px 20px;
            margin: 10px;
            font-size: 16px;
            cursor: pointer;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
        }

        button:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Volume Control</h1>

        <!-- Display current volume -->
        <div>
            <p>Current Volume: <span id="currentVolume">Fetching...</span></p>
        </div>

        <!-- Slider to set volume -->
        <input type="range" min="-65.25" max="0" step="0.1" id="volumeRange">
        <button id="setVolumeButton">Set Volume</button>

        <!-- Buttons for mute/unmute -->
        <button id="muteButton">Mute</button>
        <button id="unmuteButton">Unmute</button>
    </div>

    <script>
        // Fetch and display the current volume
        function fetchCurrentVolume() {
            fetch('/volume')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('currentVolume').textContent = data.current_volume;
                    document.getElementById('volumeRange').value = data.current_volume;
                })
                .catch(error => {
                    console.error('Error fetching volume:', error);
                });
        }

        // Set volume using the slider value
        document.getElementById('setVolumeButton').addEventListener('click', function() {
            const targetVolume = document.getElementById('volumeRange').value;

            fetch('/volume', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ target_volume: targetVolume })
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                fetchCurrentVolume(); // Refresh current volume after setting
            })
            .catch(error => {
                console.error('Error setting volume:', error);
            });
        });

        // Mute volume
        document.getElementById('muteButton').addEventListener('click', function() {
            fetch('/mute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ mute: 1 })
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                fetchCurrentVolume(); // Refresh current volume after mute
            })
            .catch(error => {
                console.error('Error muting volume:', error);
            });
        });

        // Unmute volume
        document.getElementById('unmuteButton').addEventListener('click', function() {
            fetch('/mute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ mute: 0 })
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                fetchCurrentVolume(); // Refresh current volume after unmute
            })
            .catch(error => {
                console.error('Error unmuting volume:', error);
            });
        });

        // Fetch current volume on page load
        fetchCurrentVolume();
    </script>
</body>
</html>
