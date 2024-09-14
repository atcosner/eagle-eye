function updateViewport(forward, force_id) {
    // Determine the new iterator
    var temp_index = CURRENT_INDEX;
    if (force_id === null) {
        if (forward) {
            temp_index += 1;
        } else {
            temp_index -= 1;
        }

        // Handle overflow/underflow
        if (temp_index >= IMAGE_COUNT) {
            temp_index = 0;
        } else if (temp_index < 0) {
            temp_index = IMAGE_COUNT - 1;
        }
    } else {
        temp_index = force_id;
    }

    // Hide the current index and show the new index
    var current_div = document.getElementById("results-viewport-" + CURRENT_INDEX);
    current_div.style.display = "none";

    var new_div = document.getElementById("results-viewport-" + temp_index);
    new_div.style.display = "block";

    // Update the image label
    var image_label = document.getElementById("image_id");
    var display_index = temp_index + 1;
    image_label.innerHTML = display_index + " (" + display_index + "/" + IMAGE_COUNT + ")";
    CURRENT_INDEX = temp_index;
}

function copyFromTopRegion(sourceElementName, targetElementName) {
    const source_elements = document.getElementsByName(sourceElementName);
    if (source_elements.length !== 1) {
        throw Error('Source name matched multiple elements! ' + sourceElementName);
    }

    const target_elements = document.getElementsByName(targetElementName);
    if (target_elements.length !== 1) {
        throw Error('Target name matched multiple elements! ' + targetElementName);
    }

    // Get the text from the element
    var source_text = source_elements[0].value;
    target_elements[0].value = source_text;
}

window.onload = () => {
    let params = new URLSearchParams(document.location.search);
    let focus_id = params.get("focus_id");
    console.log("Focusing to " + focus_id);

    if (focus_id === null) {
        focus_id = 0;
    } else {
        focus_id = parseInt(focus_id);
    }
    updateViewport(true, focus_id);
};