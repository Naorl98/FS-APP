// static/js/download.js

/**
 * Downloads a PDF file from the backend by task ID.
 * Assumes the backend returns: { filename: "example.pdf", content: "base64string" }
 * @param {string} taskId - The unique task ID of the generated formula sheet
 */
function downloadBase64PDF(taskId) {
  fetch(`${API_BASE}/download/${taskId}`)
    .then(response => {
      if (!response.ok) {
        throw new Error("Failed to fetch the file");
      }
      return response.json();
    })
    .then(data => {
      const base64 = data.content;
      const filename = data.filename || "formula_sheet.pdf";

      // Convert base64 to binary data
      const byteCharacters = atob(base64);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'application/pdf' });

      // Create a temporary link and trigger the download
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    })
    .catch(err => {
      console.error(err);
      alert("An error occurred while downloading your file.");
    });
}
