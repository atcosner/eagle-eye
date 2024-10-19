async function checkForJobCompletion() {
    const url = "/job-thread-status/" + JOB_ID;
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        var response_text = await response.text();
        console.log(response_text);
        if (response_text === "true") {
            window.location.replace("/job-status/" + JOB_ID + "/results");
        }
    } catch (error) {
        console.error(error.message);
    }
}

window.onload = () => {
    setInterval(checkForJobCompletion, 1000);
}
