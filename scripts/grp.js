const ctx = document.getElementById('myChart').getContext('2d');
    
new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['01/01/2023', '01/02/2023', '01/03/2023', '01/04/2023', '01/05/2023','01/05/2023'],
        datasets: [{
            label: 'Sales',
            data: [20931,21651,24375,28044,27621,25851],
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgb(75, 85, 192)',
            borderWidth: 2
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                ticks: {
                    color: 'white', // X-axis label color
                    font: { size: 14, weight: 'bold' }
                }
            },
            y: {
                ticks: {
                    color: 'white', // Y-axis label color
                    font: { size: 14, weight: 'bold' }
                }
            }
        },
        
    },
    
});
let btn=document.querySelector(".predict-btn");
btn.addEventListener("click",function(){
    let pr=document.querySelector(".inp");
    pr.classList.add("entry");
});
let out=document.querySelector(".out");

let predict = document.querySelector("#submit-btn");
predict.addEventListener("click", function () {
    let val = document.getElementById("val").value;
    out.classList.add("in");
    fetch("https://a920-34-16-184-130.ngrok-free.app/predict", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ "interval": val })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.error || "Server error"); });
        }
        return response.json();
    })
    .then(data => {
        document.getElementById("output").innerText =data.prediction;
    })
    .catch(error => {
        console.error("Error:", error);
        document.getElementById("output").innerText = "Error: " + error.message;
    });
});