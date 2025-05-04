let btn=document.querySelector("#graph-btn");
function siteChange(){
    window.location.href="graph.html";
}
btn.addEventListener("click",siteChange);

let btn2=document.querySelector("#predict-btn");
btn2.addEventListener("click",function(){
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