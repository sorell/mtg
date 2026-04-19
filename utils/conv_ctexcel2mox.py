#!/usr/bin/python3

import xlrd
import os
import re
import sys
from datetime import datetime

SETCODE_ROW = 3
ITEMNAME_ROW = 4
QUANT_ROW = 6
LANG_ROW = 8
FOIL_ROW = 9
ALTERED_ROW = 11
COLLECTORN_ROW = 13

class ParsingError(Exception):
    pass

def convertLanguage(languageKey):
    languages = {"en": "English", "it": "Italian"}
    try:
        return languages[languageKey]
    except:
        raise ParsingError(f"No language key '{languageKey}' found")

def convertFoiling(foilingKey):
    foilings = {0: "", 1: "foil"}
    try:
        return foilings[foilingKey]
    except:
        raise ParsingError(f"No foiling key '{foilingKey}' found")

def convertToTrueFalse(key):
    values = {0: "False", 1: "True"}
    try:
        return values[key]
    except:
        raise ParsingError(f"No true/false key '{key}' found")

def processCards(rows):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.000000")
    print('"Count","Tradelist Count","Name","Edition","Condition","Language","Foil","Tags","Last Modified","Collector Number","Alter","Proxy","Purchase Price"')
    for row in rows:
        try:
            setCode = row[SETCODE_ROW]
            itemName = re.sub(r" \(.*", "", row[ITEMNAME_ROW]).strip().replace("//", "/") # Remove stuff in parenthesis and convert // -> /
            quantity = row[QUANT_ROW]
            language = convertLanguage(row[LANG_ROW])
            foiling = convertFoiling(row[FOIL_ROW])
            altered = convertToTrueFalse(row[ALTERED_ROW])
            collectorNum = row[COLLECTORN_ROW]
            
            try:
                if len(collectorNum) < 1:
                    print(f"Warning: (no collector number): {itemName}", file=sys.stderr)
                else:
                    collectorNum = int(collectorNum)
            except Exception as e:
                print(f"Skipping: (bad collector number): {itemName}", file=sys.stderr)
                continue

            print(f'"{int(quantity)}","0","{itemName}","{setCode}","","{language}","{foiling}","","{now}","{collectorNum}","{altered}","False",""')
        except Exception as e:
            raise ParsingError(f"Error: {e},\nwhile parsing: {row}")

def openExcel(filePath):
    try:
        workbook = xlrd.open_workbook(filePath)
        sheet = workbook.sheet_by_index(0)

        expectedHeaders = [
            "Game", "Set Released At", "Set Name", "Set Code", "Item Name", "Price in EUR Cents", 
            "Quantity", "Condition", "Language", "Foil/Reverse", "Signed", "Altered", 
            "First Edition", "Collector Number"
        ]
        
        firstRow = sheet.row_values(0)
        if firstRow[:len(expectedHeaders)] != expectedHeaders:
            print("Error: The sheet's first row does not match the expected column headers.", file=sys.stderr)
            print(f"Got:      {firstRow}\nExpected: {expectedHeaders}", file=sys.stderr)
            sys.exit(1)
        
        remainingRows = [sheet.row_values(rowIdx) for rowIdx in range(1, sheet.nrows)]
        processCards(remainingRows)

    except FileNotFoundError:
        print("Error: The file was not found.", file=sys.stderr)
    except xlrd.XLRDError as e:
        print(f"Error reading Excel file: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    try:
        filePath = sys.argv[1]
        openExcel(filePath)
    except IndexError:
        print("Error: No file path provided. Usage: python conv_ctexcel2mox.py <file_path>", file=sys.stderr)
