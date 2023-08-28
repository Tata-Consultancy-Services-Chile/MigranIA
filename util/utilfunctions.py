   
import os
import shutil


def extractzipfile(filename,outputFolder):
    if not os.path.exists(outputFolder):
        os.mkdir(outputFolder)

    if os.path.exists(filename):
        shutil.unpack_archive(filename, outputFolder) 
        msg= ("["+filename+"] archivo descomprimido exitosamente")
        print(msg)
    else:
        print("Archivo "+filename+" No encontrado.!",-3);
    return ""


def createhtml( request, response, languageorigen, languagedestino,  comentarios ):
    htmlTemplate = readfile(os.getcwd() + "/config/report.html")
    #copy file to output folder
    
    htmlstr=htmlTemplate.format(request=request,response=response,comentarios=comentarios,languageorigen=languageorigen,languagedestino=languagedestino)
    return htmlstr

def readfile(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            data = file.read()
        return data
    else:
        print("Archivo "+filename+" No encontrado.!");
    return ""