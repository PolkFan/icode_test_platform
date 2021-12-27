import csv

from conf.readconfig import *

def csvAverage(filename,dividenum:int):
    """
    :param filename: 文件名
    :param dividenum: 切分文件数
    """
    i = 1
    j = 0
    if filename is not None:
        with open(rootPath() + "/docs/import_files/" + filename, 'r') as f:
            header = f.readlines()[0]
        with open(rootPath() + "/docs/import_files/" + filename, 'r') as f:
            reader = csv.reader(f)
            next(reader)
            for textline in reader:
                filenames = filename[0:(len(filename) - 4)] + "_%d.csv" % (i % dividenum + 1)
                with open(rootPath() + "/docs/export_files/" + filenames, "a+") as word:
                    if j<dividenum:
                        word.write(header)
                        j=j+1
                    for text in textline:
                        word.write(text + ",")
                    word.write("\n")
                i = i + 1
        return True
    return False


if __name__=='__main__':
    csvAverage("test.csv",2)