import gzip, re, sys, optparse
vcfPattern = re.compile("^(?P<chrom>.*?)\t(?P<pos>.*?)\t(?P<rsid>.*?)\t(?P<ref>.*?)\t(?P<alt>.*?)\t(?P<qual>.*?)\t(?P<filt>.*?)\t(?P<info>.*?)\t(?P<form>.*?)\t(?P<geno>.*)")

def main():
    usageText = "Usage: %prog [options] arg"

    parser = optparse.OptionParser(usage=usageText,version="%prog v0.1")
    parser.set_defaults(infile="")
    parser.set_defaults(outfile="")
    parser.set_defaults(notes=False)

    parser.add_option("-n","--notes",dest="notes", action="store_true")
    parser.add_option("-i","--in", dest="infile", action="store", type="string", help="input file", metavar="INFILE")
    parser.add_option("-o","--out",dest="outfile", action="store", type="string", help="output file", metavar="OUTFILE")

    (options, args) = parser.parse_args()

    if (options.notes==True):
        notes()
        sys.exit()

    if "" in [options.infile, options.outfile]:
        print("Missing required parameters, exiting script.\n")
        parser.print_help()
        sys.exit(2)

    infile = options.infile
    outfile = options.outfile
    if outfile[-3:] != ".gz":
        outfile += ".gz"

    def printOptions():
        print("")
        parser.print_version()
        print("\nOptions in use:")
        print(" Input file:   [ " + infile + " ]")
        print(" Output file:  [ " + outfile + " ]")

    printOptions()

    with gzip.open(infile) as f:
        line = "##"
        while line[0:2] == "##":
            line = f.readline()
        # Line now holds #CHROM POS etc
        header = vcfPattern.match(line.rstrip('\n'))
        sampleList = header.group('geno').split("\t")
        haploDict = dict()
        for sample in sampleList:
            haploDict[sample] = ["",""]
        varList = []
        varText = "##COLUMN=<SAMPLE='the sample ID from the source VCF file'>\n##COLUMN=<HAPLO='Haplotype strand, either 1 or 2, where 1 is the first phased allele and 2 is the second phased allele in each genotype'>\n"
        for line in f:
            varLine = vcfPattern.match(line.rstrip('\n'))
            gtIdx = varLine.group('form').split(":").index("GT")
            varText += ("##" + varLine.group('rsid') + "=<POS=" + varLine.group('chrom') + ":" + varLine.group('pos') + "_" + varLine.group('ref') + "/" + varLine.group('alt') + ">\n") # ",INFO=" + varLine.group('info') + ">\n")
            varList.append(varLine.group('rsid'))
            genos = varLine.group('geno').split()
            for i in range(len(sampleList)):
                (h1,h2) = haploDict[sampleList[i]]
                (t1,t2) = genos[i].split(":")[gtIdx].split("|")
                h1 += t1
                h2 += t2
                haploDict[sampleList[i]] = [h1,h2]
                
    with gzip.open(outfile,'w') as w:
        w.write(varText)
        w.write("#SAMPLE\tHAPLO")
        for var in varList:
            w.write('\t' + var)
        w.write('\n')
        for i in range(len(sampleList)):
            (h1,h2) = haploDict[sampleList[i]]
            w.write(sampleList[i] + "\t1")
            for allele in h1:
                w.write('\t' + allele)
            w.write('\n')
            w.write(sampleList[i] + "\t2")
            for allele in h2:
                w.write('\t' + allele)
            w.write('\n')



def notes():
    print('''vcf2haplo.py - Converts a phased VCF file to a haplotype file 

This script uses all variants in the input vcf file, and assumes all genotypes are phased.

Written by Alan Kwong, amkwong@umich.edu
Last edited 2018-03-26
''')

if __name__ == "__main__":
    main()
