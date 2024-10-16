var CURRENT_IMAGE_DISPLAY_FORMAT = 'field-snippets';

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

function changeRoiCellsDisplay(visible) {
    const roi_cells = document.getElementsByClassName("roi-cell");
    for (let i = 0; i < roi_cells.length; i++) {
        var cell = roi_cells[i];

        if (visible === true) {
            cell.style.display = "block";
        } else {
            cell.style.display = "none";
        }
    }
}

function changeWholeImageDisplay(visible) {
    const wholeFormDivs = document.getElementsByClassName("whole-form-image-div");
    for (let i = 0; i < wholeFormDivs.length; i++) {
        var wholeFormDiv = wholeFormDivs[i];

        if (visible === true) {
            wholeFormDiv.style.display = "block";
        } else {
            wholeFormDiv.style.display = "none";
        }
    }
}

function updateImageDisplayFormat(formatString) {
    console.log("Switching image display to: " + formatString);
    CURRENT_IMAGE_DISPLAY_FORMAT = formatString;

    if (formatString === "field-snippets") {
        changeRoiCellsDisplay(true);
        changeWholeImageDisplay(false);
    } else if (formatString === "whole-form") {
        changeRoiCellsDisplay(false);
        changeWholeImageDisplay(true);
    } else {
        throw Error("Unknown format: " + formatString);
    }
}

function installMultiCheckboxListeners() {
    const optional_text_fields = document.getElementsByClassName("multi-checkbox-optional-text");
    for (let i = 0; i < optional_text_fields.length; i++) {
        var field = optional_text_fields[i];

        // Find the matching checkbox
        var checkbox_name = field.name.replace("-text", "");
        var matched_checkbox = document.getElementById(checkbox_name);
        if (matched_checkbox === null) {
            throw Error("Did not find matching checkbox with name: " + checkbox_name);
        }

        matched_checkbox.onchange = function() {
            document.getElementById(this.id + "-text").disabled = !this.checked;
        };
    }
}

function installLinkCheckboxListeners() {
    const link_checkboxes = document.getElementsByClassName("link-checkbox");
    for (let i = 0; i < link_checkboxes.length; i++) {
        var checkbox = link_checkboxes[i];

        checkbox.onchange = function() {
            // Get the matching input box (Drop the last "-XXXX" from the ID)
            var text_input_id = this.id.split("-").slice(0, -1).join("-");

            var text_input = document.getElementById(text_input_id);
            if (text_input === null) {
                throw Error("Did not find matching input with id: " + text_input_id);
            }

            // Return to manual entry if we are not checked
            if (!this.checked) {
                text_input.readOnly = false;
                text_input.tabIndex = 0;
                return;
            }

            // Disable manual editing and remove from the tab order
            text_input.readOnly = true;
            text_input.tabIndex = -1;

            // Find the linked element
            var linked_input_id = text_input.id.replace("bottom", "top");
            var linked_text_input = document.getElementById(linked_input_id);
            if (linked_text_input === null) {
                throw Error("Did not find matching linked input with id: " + linked_input_id);
            }

            // Set our text to the linked elements value
            text_input.value = linked_text_input.value;
        };
    }
}

function installLinkInputListeners() {
    const correction_boxes = document.getElementsByClassName("corrections-box");
    for (let i = 0; i < correction_boxes.length; i++) {
        var correction_box = correction_boxes[i];

        // Only install these on boxes in the "top" region
        if (!correction_box.id.includes("top")) {
            continue;
        }

        correction_box.oninput = function() {
            // Find the linked element
            var linked_input_id = this.id.replace("top", "bottom");
            var linked_text_input = document.getElementById(linked_input_id);
            if (linked_text_input === null) {
                throw Error("Did not find matching linked input with id: " + linked_input_id);
            }

            if (linked_text_input.readOnly) {
                linked_text_input.value = this.value;
            }
        }
    }
}

function installDisplayFormatListeners() {
    const format_radio_buttons = document.getElementsByName("image-display-format");
    for (let i = 0; i < format_radio_buttons.length; i++) {
        var radio_button = format_radio_buttons[i];

        radio_button.onchange = function() {
            if (this.value === CURRENT_IMAGE_DISPLAY_FORMAT) {
                return;
            }

            updateImageDisplayFormat(this.value);
        }
    }
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

    // Install all the event listeners we are using
    installDisplayFormatListeners();
    installMultiCheckboxListeners();
    installLinkCheckboxListeners();
    installLinkInputListeners();

    // Ensure we use the display that matched the selected value
    const format_radio_buttons = document.getElementsByName("image-display-format");
    for (let i = 0; i < format_radio_buttons.length; i++) {
        var radio_button = format_radio_buttons[i];
        if (radio_button.checked === true) {
            updateImageDisplayFormat(radio_button.value);
        }
    }
};