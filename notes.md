## Future Ideas
* Results Page
  * Options for 'Field-by-Field' and 'Whole Page' (Show each ROI vs show the whole page)

## Links
* https://datascience.stackexchange.com/questions/66638/pretrained-handwritten-ocr-model

## Programming TODO
* Handle results exports in a dynamic format
  * Each result may want to export itself as N columns
  * Building up DF should ensure column uniqueness
* Remove the 'From Above' button from the tab order

## Things To Do
- [X] Handle 'Copy from previous' on certain fields (Only bottom of sheet)
- [ ] Date validation (Fix/parse dates in different formats)
- [ ] Break dates into 3 columns in the export
- [ ] Whole-form mode (See whole image on the left)
- [X] Custom validation and format for certain fields

## Icons Attribution
* <a href="https://www.flaticon.com/authors/alfredo-hernandez">Icons created by Alfredo Hernandez - Flaticon</a>


## Costs
* Query counts are per month
  * First 1000 queries: Free
  * Queries 1001-5,000,000: $1.50/thousand


* Average Form: 55 queries (~27 per half)
  * Checkboxes are free
  * Fields that look blank are not OCR'd


* Example Costs
  * 18 forms for free per month
  * ~$0.08 per form after that