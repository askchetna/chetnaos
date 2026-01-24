async function evaluateLand() {
    const ph = document.getElementById("ph").value;
    const water = document.getElementById("water").value;
    const soil = document.getElementById("soil").value;
    const temp = document.getElementById("temp").value;
    const road = document.getElementById("road").value;
    const resultBox = document.getElementById("result");
    const output = document.getElementById("output");

    // Basic validation
    if (!ph || !water || !soil || !temp || !road) {
        resultBox.classList.remove("hidden");
        output.textContent = "Error: Please fill all fields.";
        return;
    }

    const payload = {
        ph: parseFloat(ph),
        water_depth: parseFloat(water),
        soil: soil,
        temp: parseFloat(temp),
        road: road
    };

    try {
        const response = await fetch("/evaluate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (!response.ok) {
            resultBox.classList.remove("hidden");
            output.textContent = `Error: ${result.error || "Something went wrong"}`;
            return;
        }

        resultBox.classList.remove("hidden");
        output.textContent = JSON.stringify(result, null, 4);
    } catch (error) {
        resultBox.classList.remove("hidden");
        output.textContent = `Error: Failed to connect to server. Please make sure the backend is running.`;
    }
}