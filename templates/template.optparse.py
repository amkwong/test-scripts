# This is a python script template to use optparse to set arguments
# More formal than getopt, with a lot more standardization
# User can use -h to get help, and -v to get version number

import sys, optparse, datetime

# Returns a string that indicates the current date and time
def timenow():
    t = datetime.datetime.today()
    return(str(t.year) + "-" + str(t.month).zfill(2) + "-" + str(t.day).zfill(2) + " " + str(t.hour).zfill(2) + ":" + str(t.minute).zfill(2) + ":" + str(t.second).zfill(2))

# Returns a string that indicates the difference between t1 and t2, with a multiplication factor (1=default)
def timediff(t1,t2,factor):
    try: # Supported in Python 3.x
        t = (t2-t1)*factor
        days = t.days
        secs = t.seconds
    except: # Non-integer multiplication of a time object leads to an error in Python 2.X, which redirects here
        tdiff = (t2-t1)
        days = tdiff.days * factor
        secs = tdiff.seconds * factor # 86400 seconds / day
        newms = tdiff.microseconds * factor # 1e6 ms / second
        if newms > 1e6: # If the number of microseconds after multiplication is more than a second, add the extra second(s) to the proper variable
            (addSec,newms) = divmod(newms,1e6)
            secs += addSec
        if secs > 86400: # If the number of seconds after multiplication is more than a day, add the extra day(s) to the proper variable
            (addDay,newsecs) = divmod(newsecs,86400)
            days += addDay
        days = int(days) # Days and seconds should be integers for proper display
        secs = int(secs)
    txt = ""
    if days > 0: # at least one day
        txt += str(days) + " day"
        if days > 1:
            txt += "s"
        txt += ", "
    if secs/3600.0 >= 1: # at least one hour
        minsecs = secs % 3600
        hours = int((secs - minsecs)/3600)
        txt += str(hours) + " hour"
        if hours > 1:
            txt += "s"
        txt += ", "
        secs = minsecs
    if secs/60.0 >= 1: # at least one minute
        minsecs = secs % 60
        mins = int((secs - minsecs)/60)
        txt += str(mins) + " minute"
        if mins > 1:
            txt += "s"
        txt += ", "
        secs = minsecs
    txt += str(secs) + " second"
    if secs > 1:
        txt += "s"
    return(txt)

def printProgressBar(percentage): # Returns a visual representation of the current progress; percentage is between 0 and 100, inclusive
    '''Each progress bar character will be 2%'''
    if percentage >= 0 and percentage <= 100:
        numChar = int(percentage/2)
        pctTxt = str(round(percentage,1))
        pctTxt += "0"*(4-len(pctTxt))
        return('[' + ('|'*numChar) + (' '*(50-numChar)) + '] ' + pctTxt + "% Complete           ")
    else:
        return('[' + ('?'*50) + '] ??% Complete          ')


def main():
    # Usage line printed at the top of the help message
    usageText = "Usage: %prog [options] arg"

    # Initialize parser
    parser = optparse.OptionParser(usage=usageText,version="%prog v0.1")

    # Set option defaults
    parser.set_defaults(infile="")
    parser.set_defaults(outfile="")
    parser.set_defaults(quiet=False)
    parser.set_defaults(notes=False)

    # Add options
    parser.add_option("-i","--in", dest="infile", action="store", type="string", help="input file", metavar="INFILE")
    parser.add_option("-o","--out",dest="outfile", action="store", type="string", help="output file", metavar="OUTFILE")
    parser.add_option("-q","--quiet",dest="quiet", action="store_true")
    parser.add_option("-n","--notes",dest="notes", action="store_true")

    # Parse options here
    (options, args) = parser.parse_args()

    if (options.notes==True):
        notes()
        sys.exit()
    

    # options is a dictionary that contains key:value pairs
    # args contain all positional arguments that come after all the options

    if "" in [options.infile, options.outfile]:
        print("Missing required parameters, exiting script.\n")
        parser.print_help()
        sys.exit(2)

    def printOptions():
        print("")
        parser.print_version()
        print("\nOptions in use:")
        print(" Input file:   [ " + options.infile + " ]")
        print(" Output file:  [ " + options.outfile + " ]")
        print(" Verbose mode: [ " + {False:"ON",True:"OFF"}[options.quiet] + " ]\n")

    printOptions()

    timeTxt = timenow()
    print("Started run at " + timeTxt + "\n")
    starttime = datetime.datetime.now()
    
    #################################
    # Insert code to do things here #
    #################################


    #################################
    #      end of coding block      #
    #################################

    endtime = datetime.datetime.now()
    timeTxt = timenow()
    print("\nFinished run at " + timeTxt)
    print("Total Runtime: " + timediff(starttime,endtime,1.0))

def notes():
    print('''template.optparse.py - Template for a Python script using optparse

Features:
 - Uses modern optparse format to parse command line options
 - Tracks elapsed time 
 - Allows printing of a progress bar to the screen
 
Useful code:
 sys.stdout.write("\\033[F") # Moves cursor up one line
 sys.stdout.write("\\033[K") # Clears to the end of line

Written by Alan Kwong, amkwong@umich.edu
Last edited 2018-02-20
''')

    
if __name__ == "__main__":
    main()

