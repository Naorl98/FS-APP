function handleGenerate(event) {
  event.preventDefault();
  const form = document.getElementById('formulaForm');
  const formData = new FormData(form);

  fetch("/generate", {
    method: "POST",
    body: formData
  })
    .then(response => response.text())
    .then(taskUrl => {
      window.open('/watch_ad', 'adPopup', 'width=600,height=400');
      setTimeout(() => {
        window.location.href = taskUrl;
      }, 5000);
    })
    .catch(err => {
      alert("Error: " + err);
    });

  return false;
}
