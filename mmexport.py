#!/usr/bin/env python
# coding: utf-8
#
#
# MoneyMe export: a tool to export data from the MoneyMe app in an useful way (for me)
#
#

import argparse
import sqlite3
from datetime import datetime, date
import sys

# Program arguments
parser = argparse.ArgumentParser(description='Export MoneyMe transaction in a suitable format for later analysis')
parser.add_argument('sqlite3_file',
                    help='The exported backup file from MoneyMe'
                    )

parser.add_argument('-s', '--start',
                    help='Start date in format "YYYY-MM-DD". If not provided, the 1st day of current month is used',
                    )    

parser.add_argument('-e', '--end',
                    help='End date in format "YYYY-MM-DD". If not provided, current date is used')
                    
                    
class MoneyMeQuery:
    """Extract useful data from a MoneyMe database"""
    
    def __init__(self, dbFilePath):
        # Init class attributes
        self.dbName = dbFilePath
        self.dbCon = sqlite3.connect(self.dbName)
        self.queryStatement = None
        self.queryResult = []
        self.startDate = None
        self.endDate = None
 
    def getStartDate(self):
        if self.startDate == None:
            self.startDate = date(datetime.now().year, datetime.now().month, 01)
        
        return self.startDate

    def setStartDate(self, startDate):
        self.startDate = startDate
        return self
        
    def getEndDate(self):
        if self.endDate == None:
            self.endDate = date.today()
        
        return self.endDate

    def setEndDate(self, endDate):
        self.endDate = endDate
        return self

    def getQueryStatement(self):
        if self.queryStatement == None:
            localStartDate = str(self.getStartDate())
            localEndDate = str(self.getEndDate())
                
            # TODO: sanitize input
            self.queryStatement =  "SELECT m.mov_fecha, c.nombre_cat, m.mov_nombre, m. mov_cantidad, f.fp_nombre ";
            self.queryStatement += "FROM moviments m, categories c, forma_de_pago f ";
            self.queryStatement += "WHERE m.mov_fecha ";
            self.queryStatement += "BETWEEN \""+localStartDate+"\" AND \""+localEndDate+"\" ";
            self.queryStatement += "AND m.mov_categoria=c._id AND m.mov_id_forma_pago=f._id ";
            self.queryStatement += "ORDER BY mov_fecha ASC";
        
        return self.queryStatement
    
    def processDate(self, strDate):
        (year, month, day) = strDate.split("-")
        dt = date(int(year), int(month), int(day))
        return dt.strftime("%d/%m/%Y")
    
    def processAmount(self, amount):
        # Transform "x.y" into "x,y". Grab only 2 elems after split(), just in case (I don't trust MoneyMe data)
        (amt_integer, amt_cents) = str(amount).split(".")[:2]
        
        # Put a nice ending "0" in the cents part if needed
        if len(str(amt_cents)) < 2:
            amt_cents = str(amt_cents) + "0"
        return ",".join([amt_integer, amt_cents])

        
    def processPaymentMethod(self, pm):
        retVal = ""
        if pm == "Tickers":
            retVal = "Ti"
        elif pm == u"Domiciliación bancaria":
            retVal = "D"
        elif pm == "Efectivo":
            retVal = "E"
        elif pm == u"Tarj débito":
            retVal = "TD"
        elif pm == "Tarjeta":
            retVal = "TC"
        elif pm == "Paypal":
            retVal = "P"
        else:
            retVal = "INVALID"
        
        return retVal
    
    def getResult(self):
        result = []
        cursor = self.dbCon.cursor()
        
        for transaction in cursor.execute(self.getQueryStatement()):
            #print transaction
            row = []
            (tr_date, tr_category, tr_name, tr_amount, tr_pay_method) = transaction
            #print tr_date, tr_category, tr_name, tr_amount, tr_pay_method

            # tr_date:
            row.append(self.processDate(tr_date))
           
            # tr_category:
            row.append(tr_category)
            
            # tr_name
            # TODO: add a processCategory
            if unicode(tr_category) == unicode(tr_name):
                row.append("") 
            else:
                row.append(tr_name) 
            
            # tr_amount:
            row.append(self.processAmount(tr_amount))
            
            # tr_pay_method:
            row.append(self.processPaymentMethod(tr_pay_method))
            
            result.append(row)
            
        
        return result
    
    def toString(self):
        retVal = u"fecha;categoría;comentario;importe;forma pago\n";
        for transaction in self.getResult():
            for i in range(4):
                retVal += unicode(transaction[i]) + u";"
        
            retVal += unicode(transaction[4]) + u"\n"
        
        return retVal
    
    def toCSV(self):
        return self.toString()
        
if __name__ == "__main__":
    args = parser.parse_args()    

    mmquery = MoneyMeQuery(args.sqlite3_file)
    # TODO: sanitize input
    mmquery.setStartDate(args.start)
    mmquery.setEndDate(args.end)
    
    result = mmquery.toCSV()
    print result.encode('utf-8')
