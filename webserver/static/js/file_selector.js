const fileSelector = document.getElementById("file-selector-input");
const fileList = document.getElementById("file-selection-list");
const fileCountLabel = document.getElementById("file-selection-count-label");

fileList.style.cursor = 'pointer';
fileList.onclick = function() {
    fileSelector.click();
};

fileSelector.addEventListener("change", handleFilesSelected, false);

function handleFilesSelected() {
    if (!('files' in this) || !this.files.length) {
        fileList.innerHTML = "<h5>Drag and drop files or click to upload</h5>";
        fileCountLabel.innerHTML = "0";
    } else {
        fileList.innerHTML = "";
        const list = document.createElement("ul");
        fileList.appendChild(list);
        for (let i = 0; i < this.files.length; i++) {
            const li = document.createElement("li");
            list.appendChild(li);

            const img = document.createElement("img");
            img.src = URL.createObjectURL(this.files[i]);
            img.height = 60;
            img.onload = () => {
                URL.revokeObjectURL(img.src);
            };
            li.appendChild(img);
            const info = document.createElement("span");
            info.innerHTML = `${this.files[i].name}: ${this.files[i].size} bytes`;
            li.appendChild(info);
        }

        fileCountLabel.innerHTML = this.files.length;
    }
}

function upload(file) {
    fetch(
        '/file-upload',
        {
            method: 'POST',
            body: file
        }
    );
};

function uploadFiles() {
    // Don't do anything if we have no files
    if (!fileSelector.files.length) {
        console.log("No files selected, not uploading")
        return;
    }

    for (let i = 0; i < fileSelector.files.length; i++) {
        const file = fileSelector.files[i];
        console.log("Uploading file: ", file.name);
        upload(file);
    }
}
