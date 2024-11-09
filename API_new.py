from flask import Flask, request, send_file
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime
import tempfile

app = Flask(__name__)

@app.route('/')
def index():
    return "Welcome to the Tally Daybook API! Use the /upload endpoint to upload an XML file."

def parse_tally_daybook(xml_content):
    tree = ET.ElementTree(ET.fromstring(xml_content))
    root = tree.getroot()
    transactions = []
    parent_amounts = {}

    for voucher in root.findall('.//VOUCHER'):
        voucher_type = voucher.find('VOUCHERTYPENAME').text if voucher.find('VOUCHERTYPENAME') is not None else ""
        voucher_number = voucher.find('VOUCHERNUMBER').text if voucher.find('VOUCHERNUMBER') is not None else ""
        
        if voucher_type == "Receipt":
            date = datetime.strptime(voucher.find('DATE').text, '%Y%m%d').strftime('%d-%m-%Y') if voucher.find('DATE') is not None else ""
            party_name = voucher.find('PARTYLEDGERNAME').text if voucher.find('PARTYLEDGERNAME') is not None else ""
            amount = float(voucher.find('.//AMOUNT').text) if voucher.find('.//AMOUNT') is not None else None
            parent_amounts[voucher_number] = {'total_amount': amount, 'ref_sum': 0}

            transactions.append({
                'Date': date,
                'Transaction Type': "Parent",
                'Vch No.': voucher_number,
                'Ref No': "NA",
                'Ref Type': "NA",
                'Ref Date': "NA",
                'Debtor': party_name,
                'Ref Amount': "NA",
                'Amount': amount,
                'Particulars': party_name,
                'Vch Type': voucher_type,
                'Amount Verified': ""  # To be calculated later
            })
            
            for ledger_entry in voucher.findall('.//ALLLEDGERENTRIES.LIST'):
                ledger_name = ledger_entry.find('LEDGERNAME').text if ledger_entry.find('LEDGERNAME') is not None else ""
                ref_amount = float(ledger_entry.find('AMOUNT').text) if ledger_entry.find('AMOUNT') is not None else None
                bill_allocations = ledger_entry.findall('BILLALLOCATIONS.LIST')
                
                if bill_allocations:
                    for bill_allocation in bill_allocations:
                        ref_no = bill_allocation.find('NAME').text if bill_allocation.find('NAME') is not None else "NA"
                        ref_type = bill_allocation.find('BILLTYPE').text if bill_allocation.find('BILLTYPE') is not None else "NA"
                        ref_date_raw = bill_allocation.find('DUEDATE').text if bill_allocation.find('DUEDATE') is not None else ""
                        ref_date = datetime.strptime(ref_date_raw, '%Y%m%d').strftime('%d-%m-%Y') if ref_date_raw else "NA"
                        
                        parent_amounts[voucher_number]['ref_sum'] += ref_amount

                        transactions.append({
                            'Date': date,
                            'Transaction Type': "Child",
                            'Vch No.': voucher_number,
                            'Ref No': ref_no,
                            'Ref Type': ref_type,
                            'Ref Date': ref_date,
                            'Debtor': ledger_name,
                            'Ref Amount': ref_amount,
                            'Amount': "NA",
                            'Particulars': ledger_name,
                            'Vch Type': voucher_type,
                            'Amount Verified': "NA"
                        })
                else:
                    transactions.append({
                        'Date': date,
                        'Transaction Type': "Other",
                        'Vch No.': voucher_number,
                        'Ref No': "NA",
                        'Ref Type': "NA",
                        'Ref Date': "NA",
                        'Debtor': ledger_name,
                        'Ref Amount': "NA",
                        'Amount': ref_amount,
                        'Particulars': ledger_name,
                        'Vch Type': voucher_type,
                        'Amount Verified': "NA"
                    })

    for transaction in transactions:
        if transaction['Transaction Type'] == "Parent":
            voucher_number = transaction['Vch No.']
            parent_data = parent_amounts.get(voucher_number, {})
            transaction['Amount Verified'] = (
                "Yes" if parent_data.get('total_amount') == parent_data.get('ref_sum') else "No"
            )

    return transactions

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    
    file = request.files['file']
    
    if file.filename == '':
        return "No selected file", 400
    
    content = file.read()
    transactions = parse_tally_daybook(content.decode())
    
    # Create a DataFrame and save to an Excel file in a temporary directory
    columns_order = [
        'Date', 'Transaction Type', 'Vch No.', 'Ref No', 'Ref Type', 'Ref Date',
        'Debtor', 'Ref Amount', 'Amount', 'Particulars', 'Vch Type', 'Amount Verified'
    ]
    df = pd.DataFrame(transactions, columns=columns_order)
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    df.to_excel(temp_file.name, index=False)
    temp_file.close()
    
    return send_file(temp_file.name, as_attachment=True, download_name="Tally_Daybook_Receipts.xlsx")

if __name__ == "__main__":
    app.run(debug=True)
