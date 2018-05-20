# convert all GLs to PLs in a VCF file
import getopt, sys, subprocess, datetime, gzip

def timenow():
    t = datetime.datetime.today()
    return(str(t.year) + "-" + str(t.month).zfill(2) + "-" + str(t.day).zfill(2) + " " + str(t.hour).zfill(2) + ":" + str(t.minute).zfill(2) + ":" + str(t.second).zfill(2))

def timediff(t1,t2,factor):
    try:
        t = (t2-t1)*factor
        days = t.days
        secs = t.seconds
    except:
        #t = (t2-t1)*int(factor)
        tdiff = (t2-t1)
        days = tdiff.days * factor
        secs = tdiff.seconds * factor # 86400 seconds / day
        newms = tdiff.microseconds * factor # 1e6 ms / second
        if newms > 1e6:
            (addSec,newms) = divmod(newms,1e6)
            secs += addSec
        if secs > 86400:
            (addDay,newsecs) = divmod(newsecs,86400)
            days += addDay
        days = int(days)
        secs = int(secs)
    txt = ""
    if days > 0: # at least one day
        txt += str(days) + " days, "
    if secs/3600.0 >= 1: # at least one hour
        minsecs = secs % 3600
        hours = int((secs - minsecs)/3600)
        txt += str(hours) + " hour"
        if hours > 1:
            txt += "s"
        txt += ", "
        secs = minsecs
    if secs/60.0 >= 1:
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

def printProgressBar(percentage): # percentage is between 0 and 100, inclusive
    '''Each progress bar character will be 2%'''
    if percentage >= 0 and percentage <= 100:
        numChar = int(percentage/2)
        pctTxt = str(round(percentage,1))
        pctTxt += "0"*(4-len(pctTxt))
        return('[' + ('|'*numChar) + (' '*(50-numChar)) + '] ' + pctTxt + "% Complete           ")
    else:
        return('[' + ('?'*50) + '] ??% Complete          ')

def main():
    infile = ""
    outfile = ""
    quiet = 0
    varCount = 1000000
    try:
        opts,args = getopt.getopt(sys.argv[1:],"i:o:e:qh",["in=","out=","estimate=","quiet","help"])
    except(getopt.GetoptError, err):
        print(str(err))
        sys.exit(2)
    for o,a in opts:
        if o in ["-i","--in"]:
            infile = a
        elif o in ["-o","--out"]:
            if a[-3:] == '.gz':
                outfile = a[:-3]
            else:
                outfile = a
        elif o in ["-h","--help"]:
            usage()
            sys.exit()
        elif o in ["-q","--quiet"]:
            quiet = 1
        elif o in ["-e","--estimate"]:
            try:
                varCount = int(a)
            except:
                print("Invalid estimated variant count, using default = " + str(varCount))
        else:
            print("Ignoring unknown option: " + o + " " + a)

    print("gl2pl.py\nParameters in effect:")
    print("Input file :             [ " + infile + " ]")
    print("Output file:             [ " + outfile + ".gz ]")
    if varCount == 0:
        varTxt = "count in file"
    else:
        varTxt = str(varCount)
    print("Estimated variant count: [ " + varTxt + " ]\n\n\n")
            
    if "" in [infile,outfile]:
        print("Missing required parameter, exiting.")
        usage()
        sys.exit()
            
    # Start tracking time
    timeTxt = timenow()
    print("Started run at " + timeTxt + "\n")
    starttime = datetime.datetime.now()

    # Count variants to give an estimate of how long the script will take to run
    if quiet == 0 and varCount == 0:
        print("Counting variants...\n (This can take a while, to skip this step, enter a non-zero estimated variant count with -e)")
        zgrep    = subprocess.Popen(["zgrep", "-v", "^#", infile],stdout=subprocess.PIPE)
        #zcut     = subprocess.Popen(["cut","-s","-f","1-2"],stdin=zcat.stdout, stdout=subprocess.PIPE)
        varCount = int(subprocess.check_output(["wc","-l"], stdin=zgrep.stdout)) # - 1
        zgrep.wait()
        print(str(varCount) + " total variants found for " + infile + "\n\n\n\n")

    if quiet == 0:
        ct = 0
        firstTime = datetime.datetime.now()
        timeToFinish = "\nEstimating total runtime..."
 
    #################
    # Put code here #
    #################

    with gzip.open(infile,'rt') as f, open(outfile+".gz",'wb') as w:
        bgzip = subprocess.Popen(["bgzip","-c"], stdin=subprocess.PIPE, stdout=w)
        plHeaderFlag = 0
        line = "##"
        while line[0:2] == "##":
            line = f.readline()
            if line[0:16] == "##FORMAT=<ID=PL,":
                plHeaderFlag = 1
            if line[0:2] == "##":
                bgzip.stdin.write(line.encode('utf-8'))
            elif line[0:6] == "#CHROM":
                if plHeaderFlag == 0:
                    bgzip.stdin.write(b'##FORMAT=<ID=PL,Number=G,Type=Integer,Description="Phred-scale Genotype Likelihoods">\n')
                bgzip.stdin.write(line.encode('utf-8'))

        for line in f:

            if quiet == 0:
                ct += 1
                if ct % 100 == 0:
                    if ct > varCount:
                        varCount = int(ct*2)
                    secondTime = datetime.datetime.now()
                    timeToFinish = timediff(firstTime, secondTime, (varCount*1.0/ct - 1.0))
                    if timeToFinish == "0 second":
                        timeToFinish = "< 1 minute"
                    timeToFinish = "\nEstimated time remaining = " + timeToFinish + "          "
                sys.stdout.write("\033[F")
                sys.stdout.write("\033[F")
                sys.stdout.write("\033[F")
                print("Now processing variant " + str(ct) + "/" + str(varCount) + "           \n" + printProgressBar( min(ct*100.0/varCount,100) ) + timeToFinish + "             ")


            tempSplit = line.rstrip().split()
            #print(tempSplit)
            copyFields = tempSplit[0:8]  # directly copy to target file
            formatFields = tempSplit[8] # determine genotype format, and whether we need to update to add PL 
            genotypes = tempSplit[9:]    # genotypes, potentially need to be processed
            for field in copyFields: # First, copy over first 8 columns
                bgzip.stdin.write((field + "\t").encode('utf-8'))
            fmtSplit = formatFields.split(":")
            if "PL" in fmtSplit: # if PL is part of format field, copy everything over directly with no further processing
                bgzip.stdin.write(formatFields.encode('utf-8'))
                for geno in genotypes:
                    bgzip.stdin.write(("\t" + geno).encode('utf-8'))
                bgzip.stdin.write(b"\n")
            elif "GL" in fmtSplit: # assume it has GL
                glIdx   = fmtSplit.index("GL") # Find the index for GLs
                glArray = [[0,0,0]] * len(genotypes)
                for i in range(len(genotypes)):
                    if genotypes[i] != '.':
                        glArray[i] = [ float(y) for y in genotypes[i].split(":")[glIdx].split(",") ]
                        
                #print(genotypes)
                #glArray = [ [float(y[0]),float(y[1]),float(y[2])] for y in [x.split(":")[glIdx].split(",") for x in genotypes ] ]  # Convert GLs to floats
                glMax   = [ max(y) for y in glArray ] # Determine max GLs for each genotype
                
                pls     =[ [ int(min(round(-10*glArray[i][0]-glMax[i]),255)), int(min(round(-10*glArray[i][1]-glMax[i]),255)), int(min(round(-10*glArray[i][2]-glMax[i]),255)) ] for i in range(len(glMax)) ] # Generate PLs based on GLs
                # First, add "PL" to the formats field
                bgzip.stdin.write((formatFields+":PL").encode('utf-8'))
                # Write PLs as additional fields to genotypes
                for i in range(len(genotypes)):
                    bgzip.stdin.write(("\t" + genotypes[i] + ":" + str(pls[i][0]) + "," + str(pls[i][1]) + "," + str(pls[i][2])).encode('utf-8'))
                bgzip.stdin.write(b'\n')

    #print("\nFinished processing genotypes.\nCompressing " + outfile + " ...")
    #temp = subprocess.call(["bgzip","-f",outfile])
    (temp1,temp2) = bgzip.communicate()
    print("Indexing " + outfile + ".gz ...")
    temp = subprocess.call(["tabix","-f","-pvcf",outfile+'.gz'])
    print("Done!")
    #################
    #   End block   #
    #################
    
    #ct = ct + 1
    #sys.stdout.write("\033[F")
    #print("Processing #" + str(ct))
    
    # Put at the end of run
    endtime = datetime.datetime.now()
    timeTxt = timenow()
    print("\nFinished run at " + timeTxt)
    print("Total Runtime: " + timediff(starttime,endtime,1.0))
    
def usage():
    print('''gl2pl.py -- adds a PL field to VCF files that have GL fields
    
Usage:
python gl2pl.py -i [in.vcf.gz] -o [out.vcf] [-q] [-e {estimate}]

Optional parameter:
-q: Quiet mode: suppress remaining time estimate
-e [estimate]: Provide an estimate for the number of variants in the VCF file,
               which will allow the script to estimate the remaining runtime.

Note: script will bgzip and tabix the resulting vcf file automatically.
 You do not need to add the ".gz" to the end of the filename.
 This script should work with both Python 2.x and 3.x. 

In testing, this script runs faster with Python 2.7 vs. Python 3.6.

v0.4 - Merged the 2.x and 3.x versions
v0.3a - Added timediff functionality with Python 2.x
v0.3 - Created Python3 version
v0.2 - Now streams directly to a bgzipped file -- reduces I/O
v0.1 - Initial version

Written by Alan Kwong, amkwong@umich.edu
Last edited 2017-11-28
''')

if __name__ == "__main__":
    main()
