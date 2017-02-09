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
from calendar import monthrange
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

parser.add_argument('-m', '--month',
                    help='Process full `month\' from current year. Accepted values are numeric,' +
                    ' or `Jan\'/`January\', or `Ene\'/`Enero\', etc; case insensitive. Takes precedence over '+
                    ' the other date options' )

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

    def __monthStrToNum(self, monthStr):
        return {
            'jan' : 1,
            'january' : 1,
            'ene': 1,
            'enero': 1,
            'feb': 2,
            'february': 2,
            'febrero': 2,
            'mar': 3,
            'march': 3,
            'marzo': 3,
            'apr': 4,
            'april': 4,
            'abr': 4,
            'abril': 4,
            'may': 5,
            'mayo': 5,
            'jun': 6,
            'june': 6,
            'junio': 6,
            'jul': 7,
            'july': 7,
            'julio': 7,
            'aug': 8,
            'august': 8,
            'ago': 8,
            'agosto': 8,
            'sep': 9,
            'september': 9,
            'septiembre': 9,
            'oct': 10,
            'october': 10,
            'octubre': 10,
            'nov': 11,
            'november': 11,
            'noviembre': 11,
            'dec': 12,
            'december': 12,
            'dic': 12,
            'diciembre': 12,
        }.get(monthStr.lower(), 0) # 0 is the default value if not found

    def __parseMonth(self, monthStr):
        month = 0

        # First, try to obtain a numeric month
        try:
            # cast to int
            month = int(monthStr)
            if month < 1 or month > 12:
                # Fallback to current month
                month = datetime.now().month
        except:
            pass

        # Second, try to obtain the month from a string
        if  month == 0:
            month = self.__monthStrToNum(str(monthStr))

        return month

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

    def setMonth(self, monthStr):
        """Set startDate and endDate to process the full `monthStr' of current year"""
        month = self.__parseMonth(monthStr)

        # If month != 0 it means we could understand it: create appropriate strings for start and end dates.
        # Otherwise, remove start and end date (just in case user also put them in command line): we will
        # automatically use current month for dates.
        if month != 0:
            endDay = monthrange(datetime.now().year, month)[1]
            self.setStartDate(date(datetime.now().year, month, 01))
            self.setEndDate(date(datetime.now().year, month, endDay))
        else:
            # month == 0
            self.setStartDate(None)
            self.setEndDate(None)


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
            #print "q", self.queryStatement
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
    if args.month != None:
        mmquery.setMonth(args.month)
    else:
        mmquery.setStartDate(args.start)
        mmquery.setEndDate(args.end)

    result = mmquery.toCSV()
    print result.encode('utf-8'),
