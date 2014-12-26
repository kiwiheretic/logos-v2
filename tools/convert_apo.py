# convert TRK apo books to cancelbot format
import os
import csv
import re
import pdb

def convert_file(filename_in, filename_out):
    print "Converting %s to %s" % (filename_in, filename_out)
    fin = open(filename_in,"r")
    fout = open(filename_out + ".txt","w")
    chapter = 1  # some files don't have chapter numbers
    for line in fin.readlines():
        mch1 = re.match("\d+\s\w+\s(\d+):\d+-\d+", line, re.I)
        
        # chapter regexes (Macabees)
        if mch1:
            print line
            chapter = int(mch1.group(1))
            continue
        
        # verse regexes
        mch1 = re.match("\[(\d+)\]\s+(.*)", line, re.I)
        mch2 = re.match("(\d+):(\d+)\s+(.*)", line, re.I)
        mch3 = re.match("\s(\d+)\.\s+(.*)", line, re.I)
        mch4 = re.match("(\d+)\s(\w.*)", line, re.I)
        notmch4 = re.match("(\d+)\s\w+\s\d+:\d+-\d+", line, re.I)
        mch5 = re.match("\((\d+)\)\s+(.*)", line, re.I)

        if mch1:
            verse = int(mch1.group(1))
            text = mch1.group(2)
            fout.write("%d:%d %s\n" % (chapter, verse, text))    
        elif mch3:
            verse = int(mch3.group(1))
            text = mch3.group(2)
            fout.write("%d:%d %s\n" % (chapter, verse, text))    
        elif mch4 and not notmch4:
            verse = int(mch4.group(1))
            text = mch4.group(2)
            fout.write("%d:%d %s\n" % (chapter, verse, text))    
        elif mch5:
            verse = int(mch5.group(1))
            text = mch5.group(2)
            fout.write("%d:%d %s\n" % (chapter, verse, text))    

        elif mch2:
            chapter = int(mch2.group(1))
            verse = int(mch2.group(2))
            text = mch2.group(3)
            fout.write("%d:%d %s\n" % (chapter, verse, text))    
            
    fout.close()
    fin.close()
        

if __name__ == "__main__":
    base = os.path.dirname(os.path.realpath(__file__))
    outdir = os.path.join(base, 'output')
    trans_file = os.path.join(base, 'trans_file.csv')
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    if not os.path.exists(trans_file):
        fh = open(trans_file, "w")
        for f in os.listdir(base):
            if os.path.isfile(os.path.join(base, f)):
                fh.write( "\"%s\", \"\"\n" % (f,))
        fh.close()
    else:

        with open(trans_file, 'rb') as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                fn_in = row[0]
                fn_out = row[1]
                convert_file(os.path.join(base,fn_in),
                             os.path.join(outdir,fn_out))
        