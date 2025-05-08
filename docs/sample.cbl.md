
# Program Documentation

## Purpose
This program processes customer transactions against the customer master file.

## Inputs
- CUSTMAST: Customer master file
- TRANFILE: Transaction input file

## Outputs
- Updated customer master file
- PRNTFILE: Report of processed transactions

## Processing Logic
1. Read transaction records
2. For each transaction:
   - Look up customer in master file
   - Apply transaction based on type
   - Update master record
3. Generate summary report

## Error Handling
The program includes error handling for:
- Invalid customer numbers
- Transaction amount limits
- File I/O errors
            