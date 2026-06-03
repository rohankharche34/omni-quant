document.addEventListener('DOMContentLoaded', () => {
    const predictBtn = document.getElementById('predict-btn');
    const panel = document.getElementById('prediction-panel');
    const submitBtn = document.getElementById('submit-btn');
    const valInput = document.getElementById('val');
    const resultBox = document.getElementById('result-container');
    const priceValue = document.getElementById('price-value');
    const coinSelect = document.getElementById('coin-select');
    const graphBtn = document.getElementById('graph-btn');

    graphBtn.addEventListener('click', () => {
        const coin = coinSelect.value;
        window.location.href = `/graph.html?coin=${coin}`;
    });

    predictBtn.addEventListener('click', () => {
        panel.classList.toggle('hidden');
    });

    async function pollTask(taskId) {
        return new Promise((resolve, reject) => {
            const interval = setInterval(async () => {
                try {
                    const response = await fetch(`/task/${taskId}`);
                    const data = await response.json();
                    
                    if (data.state === 'SUCCESS') {
                        clearInterval(interval);
                        resolve(data.result);
                    } else if (data.state === 'FAILURE') {
                        clearInterval(interval);
                        reject(new Error(data.error || 'Task failed'));
                    }
                } catch (e) {
                    clearInterval(interval);
                    reject(e);
                }
            }, 2000); 
        });
    }

    submitBtn.addEventListener('click', async () => {
        const val = valInput.value;
        const coin = coinSelect.value;

        if (!val || val < 1) {
            alert('Please enter a valid number of days.');
            return;
        }

        submitBtn.innerText = "Analyzing Models...";
        submitBtn.disabled = true;

        try {
            const response = await fetch("/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ interval: val, coin_id: coin })
            });

            if (!response.ok) throw new Error("Server error");
            const data = await response.json();
            
            const result = await pollTask(data.task_id);
            
            const finalPrice = result.auto_arima.prediction;
            priceValue.innerText = finalPrice.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            resultBox.classList.remove('hidden');

        } catch (error) {
            console.error("Error:", error);
            priceValue.innerText = "Error";
            alert("Error: " + error.message);
        } finally {
            submitBtn.innerText = "Forecast";
            submitBtn.disabled = false;
        }
    });
});