<div align="center">
<img width="200" src="https://github.com/atcosner/eagle-eye-qt/blob/e9cc5264ca59fc15aea242288048640b689fa816/src/gui/resources/white_icon.png">
</div>

# Eagle Eye

## Description
This project was created for the [University of Kansas Biodiversity Institute](https://biodiversity.ku.edu/) to allow for the automatic OCR and digitization of paper collection forms.
While testing and development was done for specific KU collection forms this project was designed to allow for the addition of other form templates.

Optical Character Recognition (OCR) is supported by the [Google Vision API](https://cloud.google.com/vision?hl=en) but swapping for other handwriting recognition models is possible.


## Features
* Batch processing on scanned forms in image or PDF formats
* Automatic image alignment with support for rotated images during the scanning process
* OCR of text in the form via the Google Vision API
* A simple interface for correcting the OCR detections
* Validators to ensure form data complies with pre-specified formats (i.e. times look like HH:MM)
* Export of data into Excel or CSV formats for further processing


## Acknowledgements
This project would not have been possible without the support of the staff of the [KU Biodiversity Institute](https://biodiversity.ku.edu/)
with special thanks to the following people:
* [Abby Perkins - KU Ornithology Graduate Student](https://github.com/abbycperkins)
* [Lucas DeCicco - KU Ornithology Collections Manager](https://www.lhdecicco.com/)
