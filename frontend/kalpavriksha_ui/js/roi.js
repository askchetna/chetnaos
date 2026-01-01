async function calculateROI() {
    const acres = document.getElementById("acres").value;
    const model = document.getElementById("model").value;
    const box = document.getElementById("result");

    // Basic validation
    if (!acres || acres <= 0) {
        box.classList.remove("hidden");
        box.innerHTML = `<p style="color: red;"><strong>Error:</strong> Please enter a valid number of acres.</p>`;
        return;
    }

    if (!model) {
        box.classList.remove("hidden");
        box.innerHTML = `<p style="color: red;"><strong>Error:</strong> Please select a plantation model.</p>`;
        return;
    }

    const payload = {
        acres: Number(acres),
        model: model
    };

    try {
        const response = await fetch("http://127.0.0.1:8000/roi", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (!response.ok) {
            // Handle API error response
            box.classList.remove("hidden");
            box.innerHTML = `<p style="color: red;"><strong>Error:</strong> ${result.error || "Something went wrong"}</p>`;
            return;
        }

        box.classList.remove("hidden");
        box.innerHTML = `
            <h3>ROI Result</h3>
            <p><strong>Acres:</strong> ${result.acres}</p>
            <p><strong>Model:</strong> ${result.model}</p>
            <p><strong>Total Cost:</strong> ₹${result.total_cost.toLocaleString()}</p>
            <p><strong>Total Yield:</strong> ₹${result.total_yield.toLocaleString()}</p>
            <p><strong>Net Profit:</strong> ₹${result.net_profit.toLocaleString()}</p>
            <p><strong>ROI (%):</strong> ${result.roi_percent}%</p>
            <p><strong>Project Duration:</strong> ${result.duration_years} years</p>
        `;
    } catch (error) {
        box.classList.remove("hidden");
        box.innerHTML = `<p style="color: red;"><strong>Error:</strong> Failed to connect to server. Please make sure the backend is running.</p>`;
    }
}