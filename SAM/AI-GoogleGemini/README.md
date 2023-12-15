# AI Google Gemini

### About BIC code for containers

![Image](https://www.bic-code.org/wp-content/uploads/2022/06/idnumber.png)

The BIC code is a unique identification code for containers. It consists of 11 characters, of which the first 4 are letters and the last 7 are numbers. The first 3 characters are the owner code, the next 6 are the serial number of the container, and the last 2 are the check digit. The check digit is calculated using the Luhn algorithm. The BIC code is also called the ISO 6346 code.

### About the app

This app read images from S3 bucket and extract the BIC code from the image. The app is written in Python and uses the Google Cloud Vision API to extract the text from the image.

### How to run the app
Upload the image to the S3 bucket. The app will read the image from the S3 bucket and extract the BIC code from the image. The app will then write the BIC code to the DynamoDB table.



