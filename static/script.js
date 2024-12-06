document.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const uploadButton = document.getElementById('uploadButton');
    const preview = document.getElementById('preview');

    uploadButton.addEventListener('click', (event) => {
        event.preventDefault();
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        handleFile(file);
    });

    function handleFile(file) {
        if (file && file.name.endsWith('.dxf') && file.size < 5 * 1024 * 1024) {
            const formData = new FormData();
            formData.append('file', file);

            preview.innerHTML = '';

            const loadingMessage = document.createElement('p');
            loadingMessage.textContent = 'Uploading...';
            preview.appendChild(loadingMessage);

            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                // Check content type first
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    if (!response.ok) {
                        return response.json().then(err => {
                            throw new Error(err.error || 'Unknown error occurred');
                        });
                    }
                    return response.json();
            }
            throw new Error('Server returned invalid response format');
        })
            .then(data => {
                loadingMessage.remove();
                if (data.svg) {
                    preview.innerHTML = data.svg;

                    const downloadLink = document.createElement('a');
                    downloadLink.href = data.download_url;
                    downloadLink.textContent = 'Download Converted File';
                    downloadLink.classList.add('download-button');
                    preview.appendChild(downloadLink);
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                // Remove loading message
                loadingMessage.remove();

                console.error('Error uploading file:', error); // Log detailed error
                if (error instanceof TypeError && error.message === 'Failed to fetch') {
                    alert('Network error: Could not reach the server.');
                } else {
                    alert(`Error: ${error.message}`);
                }
            });
        } else {
            alert('Please upload a valid DXF file (max 5MB).');
        }
    }

    //start of new code: for interactive svgs

    preview.addEventListener('mouseover', (event) => {
        const target = event.target;

        if (target.tagName === 'line') {
            const length = target.getAttribute('data-length');
            const thickness = target.getAttribute('data-thickness');
            showTooltip(event, `Length: ${length}, Thickness: ${thickness}`);
        } else if (target.tagName === 'circle') {
            const radius = target.getAttribute('data-radius');
            const thickness = target.getAttribute('data-thickness');
            showTooltip(event, `Radius: ${radius}, Thickness: ${thickness}`);
        } else if (target.tagName === 'path') {
            const arcInfo = target.getAttribute('data-arc-info');
            const thickness = target.getAttribute('data-thickness');
            showTooltip(event, `Arc Info: ${arcInfo}, Thickness: ${thickness}`);
        }
    });

    preview.addEventListener('mouseout', () => {
        hideTooltip();
    });

    function showTooltip(event, content) {
        let tooltip = document.getElementById('tooltip');
        if (!tooltip) {
            tooltip = document.createElement('div');
            tooltip.id = 'tooltip';
            document.body.appendChild(tooltip);
        }
        tooltip.textContent = content;
        tooltip.style.position = 'absolute';
        tooltip.style.left = `${event.pageX + 10}px`;
        tooltip.style.top = `${event.pageY + 10}px`;
        tooltip.style.backgroundColor = '#fff';
        tooltip.style.border = '1px solid #ccc';
        tooltip.style.padding = '5px';
        tooltip.style.zIndex = '1000';
        tooltip.style.pointerEvents = 'none';
    }

    function hideTooltip() {
        const tooltip = document.getElementById('tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }
});
