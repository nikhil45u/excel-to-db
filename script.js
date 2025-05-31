function uploadFile() {
  const fileInput = document.getElementById('excelFile');
  const file = fileInput.files[0];
  const message = document.getElementById('message');
  const loader = document.getElementById('loader');

  // Reset message
  message.textContent = '';
  message.className = '';

  // File validation
  if (!file) {
    message.textContent = '❌ Please select an Excel file!';
    message.className = 'message error';
    return;
  }

  // Validate Excel file format
  const allowedTypes = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
  if (!allowedTypes.includes(file.type)) {
    message.textContent = '❌ Only .xlsx Excel files are allowed!';
    message.className = 'message error';
    return;
  }

  const formData = new FormData();
  formData.append('file', file);

  loader.style.display = 'block';

  fetch('http://127.0.0.1:5000/upload', {
    method: 'POST',
    body: formData,
  })
    .then(async (response) => {
      loader.style.display = 'none';
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Server Error');
      }
      return response.json();
    })
    .then((data) => {
      message.textContent = `✅ ${data.message}`;
      message.className = 'message success';
      fileInput.value = '';
    })
    .catch((error) => {
      message.textContent = `❌ Error: ${error.message}`;
      message.className = 'message error';
    });
}
