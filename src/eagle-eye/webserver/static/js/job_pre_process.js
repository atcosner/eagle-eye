function updateViewport(forward) {
    // Determine the new iterator
    var temp_index = CURRENT_INDEX;
    if (forward) {
        temp_index += 1;
    } else {
        temp_index -= 1;
    }

    // Handle overflow/underflow
    if (temp_index >= RESULTS_COUNT) {
        temp_index = 0;
    } else if (temp_index < 0) {
        temp_index = RESULTS_COUNT - 1;
    }

    // Hide the current index and show the new index
    var current_div = document.getElementById("results-viewport-" + CURRENT_INDEX);
    current_div.style.display = "none";

    var new_div = document.getElementById("results-viewport-" + temp_index);
    new_div.style.display = "block";

    // Update the image label
    var image_label = document.getElementById("image_id");
    var display_index = temp_index + 1;
    image_label.innerHTML = display_index + " (" + display_index + "/" + RESULTS_COUNT + ")";
    CURRENT_INDEX = temp_index;
}
