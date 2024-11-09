Tally Daybook API

This project provides an API for parsing Tally Daybook XML files to extract transaction data. The API processes **"Receipt"** voucher types and returns a structured Excel file that includes **Parent**, **Child**, and **Other** transaction types. 

## Features
- Upload XML: Accepts a Tally Daybook XML file via POST request.
- Data Extraction: Extracts and organizes transaction details including `Date`, `Voucher Number`, `Reference Number`, `Debtor`, `Amount`, and more.
- Excel Export: Generates an Excel file with a consistent format, summarizing the transactions.

## Technologies
- Python and Flask: For the API backend.
- pandas: For data handling and Excel file generation.
- openpyxl: For Excel file support.

## Setup Instructions

### Prerequisites
- **Python 3.x**
- Install required packages:
  
      pip install flask pandas openpyxl
  

### Installation
1. **Clone the repository**:
   
       git clone https://github.com/yourusername/API-creation-.git
       cd API-creation-
   
2. **Run the API**:
  
         python Python_API_Project.py
   
   By default, the API runs at `http://127.0.0.1:5000`.

## API Usage

### Endpoint
- **`POST /upload`**: Accepts an XML file and returns an Excel file.

### Request Example
To test the API, you can use **curl** .

#### Using curl:

curl -X POST -F "file=@path/to/your/Input.xml" http://127.0.0.1:5000/upload -o Tally_Daybook_Receipts.xlsx


### Response
The API returns an Excel file (`Tally_Daybook_Receipts.xlsx`) with the following columns:

| Date       | Transaction Type | Vch No. | Ref No | Ref Type | Ref Date | Debtor           | Ref Amount | Amount | Particulars       | Vch Type | Amount Verified |
|------------|------------------|---------|--------|----------|----------|------------------|------------|--------|--------------------|----------|-----------------|
| `dd-mm-yyyy` | Parent/Child/Other | `12345` | NA/...  | NA/...    | NA/...    | `Party/Ledger Name` | NA/...      | `1000` | `Party/Ledger Name` | `Receipt` | Yes/No |

## Project Structure
- Python_API_Project.py: Main API script for handling XML processing and file generation.
- README.md: Project documentation.


## Consistency and Flexibility
The API is designed to handle various Tally Daybook XML files consistently. The output format remains consistent across different inputs, with `NA` values for missing data and verified `Amount` fields based on child transactions.

