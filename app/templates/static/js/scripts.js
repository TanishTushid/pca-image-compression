const form = document.getElementById('compressForm');
const fileInput = document.getElementById('fileInput');
const targetMb = document.getElementById('targetMb');
const targetValue = document.getElementById('targetValue');
const resultBox = document.getElementById('resultBox');
const compressedImage = document.getElementById('compressedImage');
const origSize = document.getElementById('origSize');
const newSize = document.getElementById('newSize');
const psnr = document.getElementById('psnr');
const downloadButton = document.getElementById('downloadButton');

if (targetMb && targetValue) {
  const updateTargetLabel = () => {
    targetValue.textContent = `${Number(targetMb.value).toFixed(1)} MB`;
  };

  targetMb.addEventListener('input', updateTargetLabel);
  updateTargetLabel();
}

if (fileInput) {
  fileInput.addEventListener('change', (event) => {
    const file = event.target.files && event.target.files[0];
    if (!file) return;

    const label = fileInput.closest('.dropzone');
    if (label) {
      label.querySelector('strong').textContent = file.name;
      label.querySelector('small').textContent = `${(file.size / (1024 * 1024)).toFixed(2)} MB`;
    }
  });
}

if (form) {
  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const file = fileInput.files && fileInput.files[0];
    if (!file) {
      alert('Please choose an image first.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('target_mb', targetMb.value);

    try {
      const response = await fetch('/api/compress', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Compression failed.');
      }

      if (compressedImage) {
        compressedImage.src = data.image_data_url;
      }

      if (downloadButton) {
        downloadButton.href = data.image_data_url;
        downloadButton.download = data.filename || 'compressed-image.jpg';
        downloadButton.hidden = false;
      }

      if (resultBox) {
        resultBox.hidden = false;
      }

      if (origSize) origSize.textContent = `${(data.original_size_bytes / (1024 * 1024)).toFixed(2)} MB`;
      if (newSize) newSize.textContent = `${(data.output_size_bytes / (1024 * 1024)).toFixed(2)} MB`;
      if (psnr) psnr.textContent = `${Number(data.psnr).toFixed(1)} dB`;
    } catch (error) {
      alert(error.message || 'Something went wrong while compressing the image.');
    }
  });
}
