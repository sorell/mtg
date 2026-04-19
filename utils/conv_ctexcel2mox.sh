#!/usr/bin/python3

import openpyxl
import os
import sys

def openExcel(filePath):
    try:
        # Load the workbook
        workbook = openpyxl.load_workbook(filePath)
        
        # Get the sheet names
        sheet_names = workbook.sheetnames
        print(f"Sheets available: {sheet_names}")
        
        # Select the first sheet
        sheet = workbook.active
        print(f"Opening sheet: {sheet.title}")
        
        # Print the first few rows of data
        for row in sheet.iter_rows(min_row=1, max_row=5, values_only=True):
            print(row)
        
    except FileNotFoundError:
        print("Error: The file was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    try:
        filePath = sys.argv[1]
        openExcel(filePath)
    except IndexError:
        print("Error: No file path provided. Usage: python conv_ctexcel2mox.py <file_path>")
