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


## Timeline For Completion
Eagle Eye is currently in an Alpha stage with large portions of functionality missing or buggy. As a solo developer
working on this in my spare time, I plan to work on this sporadically. I have laid out a rough timeline below but if
there is a feature you are particularly interested in please reach out to me at atcosner@gmail.com.

* SPNHC 2025 (May 30th, 2025)
  * Working processing pipeline demo
  * Basic reference form creation
* End of Summer 2025
  * Full reference form creation
  * Beta release
* End of 2025
  * Production Release
    * Binaries available for Windows, and Mac
    * Export/Import from a DB file

## Acknowledgements
This project would not have been possible without the support of the staff of the [KU Biodiversity Institute](https://biodiversity.ku.edu/)
with special thanks to the following people:
* [Abby Perkins - KU Ornithology Graduate Student](https://github.com/abbycperkins)
* [Lucas DeCicco - KU Ornithology Collections Manager](https://www.lhdecicco.com/)
