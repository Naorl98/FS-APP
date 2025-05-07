const circle = document.querySelector(".progress-ring__circle");
const text = document.getElementById("progress-value");
const radius = 90;
const circumference = 2 * Math.PI * radius;

circle.style.strokeDasharray = `${circumference}`;
circle.style.strokeDashoffset = `${circumference}`;

function setProgress(percent) {
  const offset = circumference - (percent / 100) * circumference;
  circle.style.strokeDashoffset = offset;
  text.textContent = percent + "%";
}

function updateProgress() {
  fetch(`/progress/${taskId}`)
    .then(res => {
      if (!res.ok) throw new Error("Failed to fetch progress.");
      return res.json();
    })
    .then(data => {
      setProgress(data.progress);
      if (data.progress < 100) {
        setTimeout(updateProgress, 1000);
      } else {
        window.location.href = `/download/${taskId}`;
      }
    })
    .catch(err => {
      const errorDiv = document.getElementById("error");
      errorDiv.textContent = "An error occurred while checking progress.";
      errorDiv.style.display = "block";
      console.error(err);
    });
}

updateProgress();
