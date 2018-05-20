import getopt, sys, subprocess, gzip

def openFile(filename):
    if filename[-3:] == ".gz":
        f = gzip.open(filename)
    else:
        f = open(filename)
    return(f)

def main():
    try:
        opts,args = getopt.getopt(sys.argv[1:],"i:o:f:h",["in=","out=","fields=","help"])
    except getopt.GetoptError, err:
        print str(err)
        sys.exit(2)
    for o,a in opts:
        if o in ["-i","--in"]:
            infile = a
        elif o in ["-o","--out"]:
            if a[-3:] == ".gz":
                outfile = a[:-3]
            else:
                outfile = a
        elif o in ["-f","--fields"]:
            fields = a.split(":")
        elif o in ["-h","--help"]:
            usage()
            sys.exit()
        else:
            print("Ignoring unknown option: " + o + " " + a)

    inf = openFile(infile)

    # First, get the file's FORMAT
    temp = inf.readline()
    while temp[0] == "#":
        temp = inf.readline()
    formatOriginal = temp.split()[8].split(":")
    inf.close()

    # Get the indices of the target fields
    fieldsIdx = []
    for i in range(len(fields)):
        fieldsIdx.append(formatOriginal.index(fields[i]))

    ct = 0
    inf = openFile(infile)
    with open(outfile,"w") as out:
        for line in inf:
            if line[0] == "#":
                out.write(line)
            else:
                ct = ct + 1
                lineSplit = line.split()
                out.write(lineSplit[0] + "\t" + lineSplit[1] + "\t" + lineSplit[2] + "\t" + lineSplit[3] + "\t" + lineSplit[4] + "\t" + lineSplit[5] + "\t" + lineSplit[6] + "\t" + lineSplit[7] + "\t" + fields[0])
                for i in range(len(fields)-1):
                    out.write(":"+fields[i+1])
                for i in range(len(lineSplit[9:])):
                    out.write("\t")
                    indivSplit = lineSplit[9+i].split(":")
                    newFields = indivSplit[fieldsIdx[0]]
                    for j in range(len(fieldsIdx)-1):
                        newFields = newFields + ":" + indivSplit[fieldsIdx[j+1]]
                    out.write(newFields)
                if ct % 1000 == 0:
                    print(str(ct) + " variants processed...")
                out.write("\n")
    print("All variants processed. Total: " + str(ct))
    inf.close()

    print("bgzipping " + outfile + "...")
    temp = subprocess.call(["bgzip","-f",outfile],stderr=subprocess.STDOUT)
    print("tabixing " + outfile + ".gz ...")
    temp = subprocess.call(["tabix","-f",outfile+".gz"],stderr=subprocess.STDOUT)
    print("Conversion finished.\n")

def usage():
    print('''convertVCF.py -- reorder and remove fields in samples in a VCF file
Usage: python convertVCF.py -i <input VCF> -o <output VCF> -f <target fields>
       where <target fields> is a colon-delimited list of fields you wish to retain in the final vcf file. example: "-f GT:DP:GQ:PL"

Written by Alan Kwong, amkwong@umich.edu
Last edited 2014-12-02
''')

if __name__ == "__main__":
    main()

