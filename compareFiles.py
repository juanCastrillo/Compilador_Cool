import re
def compareFiles(file1, file2):
    f1 = open(file1, 'r')
    f2 = open(file2, 'r')

    for l1, l2 in zip(f1, f2):
        if l1.strip() == '': continue
        l1.strip().split()
        l2.strip().split()
        if str(l1) != str(l2):
            print(l1)
            # print(l2)
            # print()
            break

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Pasar nombre del fichero .cool")
        exit(1)
    filename = sys.argv[1]
    fname1 = "01/grading/"+filename+".cool.nuestro"
    fname2 = "01/grading/"+filename+".cool.bien"
    compareFiles(fname1, fname2)