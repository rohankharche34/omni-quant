document.addEventListener('DOMContentLoaded', async () => {
    const predictBtn = document.querySelector('.predict-toggle');
    const panel = document.getElementById('prediction-panel');
    const submitBtn = document.getElementById('submit-btn');
    const valInput = document.getElementById('val');
    const resultBox = document.getElementById('result-container');
    const priceValue = document.getElementById('price-value');
    const coinSelect = document.getElementById('coin-select');
    const loader = document.getElementById('chart-loader');

    // Check if coin was passed in URL from index.html
    const urlParams = new URLSearchParams(window.location.search);
    const urlCoin = urlParams.get('coin');
    if (urlCoin) {
        coinSelect.value = urlCoin;
    }

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

    // Native HTML5 Canvas Chart Implementation
    let resizeHandler = null;

    function drawNativeChart(canvasId, data) {
        const canvas = document.getElementById(canvasId);
        if(!canvas) return;
        
        // Ensure canvas matches container dimensions for responsive drawing
        const container = canvas.parentElement;
        canvas.width = container.clientWidth;
        canvas.height = container.clientHeight || 400;
        
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const padding = 45;
        const width = canvas.width - padding * 2;
        const height = canvas.height - padding * 2;
        
        const prices = data.prices;
        const maxPrice = Math.max(...prices);
        const minPrice = Math.min(...prices);
        const priceRange = maxPrice - minPrice || 1;
        
        // Draw Grid
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
        ctx.lineWidth = 1;
        for (let i = 0; i <= 5; i++) {
            const y = padding + (height / 5) * i;
            ctx.beginPath();
            ctx.moveTo(padding, y);
            ctx.lineTo(padding + width, y);
            ctx.stroke();
            
            const priceLabel = (maxPrice - (priceRange / 5) * i).toFixed(2);
            ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
            ctx.font = '10px Outfit';
            ctx.fillText(priceLabel, 0, y + 4);
        }
        
        const xStep = width / (prices.length - 1);
        
        // Draw Area Fill
        const gradient = ctx.createLinearGradient(0, padding, 0, padding + height);
        gradient.addColorStop(0, 'rgba(99, 102, 241, 0.4)');
        gradient.addColorStop(1, 'rgba(99, 102, 241, 0.0)');
        
        ctx.beginPath();
        ctx.moveTo(padding, padding + height);
        for (let i = 0; i < prices.length; i++) {
            const x = padding + i * xStep;
            const y = padding + height - ((prices[i] - minPrice) / priceRange) * height;
            ctx.lineTo(x, y);
        }
        ctx.lineTo(padding + width, padding + height);
        ctx.closePath();
        ctx.fillStyle = gradient;
        ctx.fill();
        
        // Draw Line with Neon Glow
        ctx.beginPath();
        ctx.shadowBlur = 10;
        ctx.shadowColor = '#6366f1';
        ctx.strokeStyle = '#6366f1';
        ctx.lineWidth = 2;
        for (let i = 0; i < prices.length; i++) {
            const x = padding + i * xStep;
            const y = padding + height - ((prices[i] - minPrice) / priceRange) * height;
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.stroke();
        ctx.shadowBlur = 0; // Reset
    }

    async function loadChart(coin) {
        loader.classList.remove('hidden');
        
        try {
            const response = await fetch(`/api/market-data/${coin}`);
            const data = await response.json();
            
            if (data && data.prices && data.prices.length > 0) {
                drawNativeChart('myChart', data);
                
                // Add resize listener safely
                if (resizeHandler) window.removeEventListener('resize', resizeHandler);
                resizeHandler = () => drawNativeChart('myChart', data);
                window.addEventListener('resize', resizeHandler);
            }

        } catch (e) {
            console.error("Failed to load historical data", e);
        } finally {
            loader.classList.add('hidden');
        }
    }

    loadChart(coinSelect.value);

    coinSelect.addEventListener('change', (e) => {
        loadChart(e.target.value);
        resultBox.classList.add('hidden');
    });
});