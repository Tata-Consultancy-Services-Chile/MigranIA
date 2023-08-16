import json
import os
import openai  # pip install openai
import typer  # pip install "typer[all]"
from rich import print  # pip install rich
from rich.table import Table
import sys
import shutil
from datetime import datetime

EOF = "#############################################"

PROMPT_MIGRACION = """
    Migra los siguientes codigos fuentes : \n{fuentes}\n los cuales estan en {tecnologia_original}, debes migrar esto a {tecnologia_destino},
    quiero que tu respuesta este en el siguiento formato
    
    @@@@NOMBRE ARCHIVO
    CONTENIDO CODIGO MIGRADO
    #############################################

    No agregue espacios en blanco despues de la ultima linea de codigo, ya que esto puede generar errores en la migracion
    No coloques comentarios en el codigo, ya que esto puede generar errores en la migracion
    No menciones sugerencias ni acciones dentro del codigo, si quieres realizarlo comentalo en formato de comentario
    . \n
"""

def main():
    # obtener la llave de openai desde el archivo .env
    openai.api_key = os.getenv("OPENAI_API_KEY")

    print("🤖 [bold green]Migracion asistida por ChatGPT[/bold green]")
    origin_path =  typer.prompt("\nIngrese ruta de fuentes a migrar :")
    origin_tech =  typer.prompt("\nIngrese tecnologia de Origen  :")
    destiny_tech = typer.prompt("\nIngrese tecnologia de Destino :")
    sources = readFilePathsFromPath(origin_path, origin_tech)
    
    prompt = PROMPT_MIGRACION.format(fuentes=sources, 
                                    tecnologia_original=origin_tech, 
                                    tecnologia_destino=destiny_tech)

    requestIA = prompt
    
    # Contexto del asistente
    context = {"role": "system", "content": "Eres un developer senior."}
    messages = [context]
    
    messages.append({"role": "user", "content": requestIA})
    responseIA = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages)
    
    #print(responseIA)
    
    response_content = responseIA.choices[0].message.content
    messages.append({"role": "assistant", "content": response_content})

    #itera la lectura del response_content linea a linea
    isNameFile = True
    nameFile =""
    contentFile =""
    temporarypath = datetime.now().strftime("%Y%m%d%H%M%S")

    for line in response_content.splitlines():
        if isNameFile:
            if line.startswith('@@@@'):
                nameFile=line.replace("@@@@", "")
                isNameFile=False
        else:
            if line != EOF:
                contentFile += line + "\n"
            else:
                createSource(temporarypath, nameFile, contentFile)
                isNameFile=True
                nameFile =""
                contentFile =""

def createSource(temporarypath, filename,content):
    table = Table(filename)
    table.add_row(content)
    print(table)    

    relativepath= "./output"
    ##temporaryPath = destiny_tech+"_"+ datetime.now().strftime("%Y%m%d%H%M%S")
    
    outputmainfolder =relativepath +"/"+ temporarypath;

    #verificar si carpeta existe, sino se crea una en la ruta especificada
    if not os.path.exists(relativepath):
        os.mkdir(relativepath)
        os.mkdir(outputmainfolder)
   
    if not os.path.exists(outputmainfolder):
        os.mkdir(outputmainfolder);

    print("Los fuentes se crearan en la carpeta '"+outputmainfolder+"'")
    path = outputmainfolder +"/"+ filename
    print("creando  archivo  =>"+path)
    file = open(path,"w")
    file.write(content)
    file.close()

#crear funcion para leer nombres de archivos de un directorio e iterar cada nombre de archivo
#verifica que la extension de archivos de origen sea .java
def readFilePathsFromPath(path, origin_tech):
    contentSourcesFile = ""

    ## ------------------  INICIO - DESCOMPRIMIENDO ARCHIVO.------------------
    filename ="";
    ##Buscar archivo primer archivo .zip dentro del path
    for root, dirs , files in os.walk (path ):
        for file in files:
            if file.endswith(".zip"):
                filename = path +"\\"+ file
                print("archivo zip encontrado =>"+filename)
                break

    if not os.path.exists(filename):
        salir("Abortando ejecucion, archivo .zip No Existe dentro del directorio", -4)

    extractZipFile(filename, path)
    ##------------------ TERMINO - DESCOMPRIMIENDO ARCHIVO.------------------

    if not os.path.exists(path):
        salir("\n * El directorio '"+path+"' especificado No existe", -1)
 
    if "java" in origin_tech:
        print("Trabajando en la traduccion.... Espere un momento por favor...")
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".java"):
                    contentSourcesFile += "\n" + file + readContentFromPath(path +"\\" +file) + "\n"        
        return contentSourcesFile
    else:
        salir("\n * Lenguage de origen '" + origin_tech+ "' Aun no se encuentra implementado para traducir.", -2)


def readContentFromPath(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return content

def extractZipFile(filename,outputFolder):
    if not os.path.exists(outputFolder):
        os.mkdir(outputFolder)

    if os.path.exists(filename):
        shutil.unpack_archive(filename, outputFolder) 
        msg= ("["+filename+"] archivo descomprimido exitosamente")
        print(msg)
    else:
        salir("Archivo "+filename+" No encontrado.!",-3);
    return ""


def salir(mensaje, codSalida):
    print(mensaje)
    sys.exit(codSalida);

if __name__ == "__main__":
    typer.run(main)
