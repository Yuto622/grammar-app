let chunks = [];
let mediaRecorder;
let stream

const startRecordButton = document.getElementById('start');
const stopRecordButton = document.getElementById('stop');
const recordedAudio = document.getElementById('recordedAudio');
const previewText = document.getElementById('preview-text');
const waitSpeck = document.getElementById('wait-speck');
const waitCheckGrammar = document.getElementById('wait-check-grammar');
const titleValueCheck = document.getElementById('title-value-check');
const matchesContainer = document.getElementById('check-false');

startRecordButton.addEventListener('click', async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.addEventListener('dataavailable', (event) => {
      if (event.data.size > 0) {
        chunks.push(event.data);
      }
    });

    mediaRecorder.start();
    startRecordButton.style.display = 'none';
    stopRecordButton.style.display = 'block';
    waitSpeck.style.display = 'flex'
  } catch (error) {
    console.error('Error accessing microphone:', error);
  }
});

stopRecordButton.addEventListener('click', () => {
  const form = document.getElementById('form-grammar');
  const formData = new FormData(form);
  const csrfToken = formData.get('csrfmiddlewaretoken');
  waitSpeck.style.display = 'none'
  waitCheckGrammar.style.display = 'flex'
  mediaRecorder.stop();


  mediaRecorder.addEventListener('stop', () => {
    const recordedBlob = new Blob(chunks, { type: 'audio/wav' });
    const formData = new FormData();
    formData.append('audio_file', recordedBlob, 'recorded_audio.wav');
    stream.getTracks().forEach(track => track.stop());
    fetch('/recognize-speech', {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': csrfToken
      },
    })
      .then(response => response.json())
      .then(data => {
        waitCheckGrammar.style.display = 'none'
        previewText.value = data.text
        recordedAudio.src = URL.createObjectURL(recordedBlob);
        recordedAudio.style.display = 'block';
        const dataMatches = data.match
        const error = data.error_count
        matchesContainer.innerHTML = ''
        console.log(dataMatches)
        console.log(error)
        if (error > 0) {
          titleValueCheck.innerHTML = 'Grammar mistakes found:'
          const matchDiv = document.createElement('div');
          matchDiv.classList.add('border', 'border-gray-200', 'rounded-lg', 'shadow-lg', 'px-2', 'py-5', 'mb-10',);
          matchDiv.innerHTML = `<pre class="whitespace-break-spaces">${dataMatches}</pre>`
          matchesContainer.appendChild(matchDiv)
        } else {
          titleValueCheck.innerHTML = 'No grammar mistakes found.'
        }
      })
      .catch(error => console.error('Error uploading file:', error));

    chunks = [];
    startRecordButton.style.display = 'block';
    stopRecordButton.style.display = 'none';
  });
});