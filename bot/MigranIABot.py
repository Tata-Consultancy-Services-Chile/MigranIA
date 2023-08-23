### +============================================================================< Agosto 2023 >===+
###    _____   .__                                .___    _____                 ____    _______   
###   /     \  |__|  ____ _______ _____     ____  |   |  /  _  \       ___  __ /_   |   \   _  \  
###  /  \ /  \ |  | / ___\\_  __ \\__  \   /    \ |   | /  /_\  \      \  \/ /  |   |   /  /_\  \ 
### /    Y    \|  |/ /_/  >|  | \/ / __ \_|   |  \|   |/    |    \      \   /   |   |   \  \_/   \
### \____|__  /|__|\___  / |__|   (____  /|___|  /|___|\____|__  / /\    \_/ /\ |___| /\ \_____  /
###         \/    /_____/              \/      \/              \/  \/        \/       \/       \/ 
###
### +==============================================================================================+ 
### Created by:
###
### Fernando Mateluna                                                                                          
### Martín Vergara B.
### 

import os
import sys
import openai  # pip install openai
import typer  # pip install "typer[all]"
from rich import print  # pip install rich
from rich.table import Table
import subprocess
import shutil
from datetime import datetime

class MigranIABot:

    def __init__(self, api_key):
        self.api_key = api_key
        self.messages = []
        self.response = ""
        self.EOF = "#############################################"
        self.PROMPT_MIGRACION = """
        Migra el siguiente codigo fuentes : \n{fuentes}\n el cual esta desarrollado en {tecnologia_original}, debes migrar esto a {tecnologia_destino},
        quiero que tu respuesta este en el siguiento formato
        
        @@@@NOMBRE ARCHIVO
        CONTENIDO CODIGO MIGRADO
        #############################################
        considera que los fuentes no vienen en orden logico, pero debes confiar que los import y las piezas mencionadas existen
        No agregue espacios en blanco despues de la ultima linea de codigo, ya que esto puede generar errores en la migracion
        No coloques comentarios en el codigo, ya que esto puede generar errores en la migracion
        No menciones sugerencias ni acciones dentro del codigo, si quieres realizarlo comentalo en formato de comentario
        NO agregar ``` o carecteres relacionados a comentarios en ninguna linea del codigo
       
        . \n
        """
            
    def context(self, context):
        context = {"role": "system",
                "content": context}
        
        self.messages = [context]
        content = "Eres un developer senior."
        self.messages.append({"role": "user", "content": content})
        self.origin_path = ""
        self.origin_tech = ""
        self.destiny_tech = ""

        self.response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=self.messages)

    def migrar(self, origin_path, origin_tech, destiny_tech):
        self.origin_path = origin_path
        self.origin_tech = origin_tech
        self.destiny_tech = destiny_tech
        if not os.path.exists(origin_path):
            self.salir("\n * El directorio '"+origin_path+"' especificado No existe", -1)
            return False
        self.findFiles(origin_path, origin_tech)
        return True
        
    def findFiles(self, pathFiles, origin_tech):           
        if "java" in origin_tech:     
            print(pathFiles)
            for root, dirs, files in os.walk(pathFiles, topdown=False):
                for name in files:
                    if name.endswith(".java"):
                        print("name:"+name)
                        self.migraSource(root,name)
        else:
            self.salir("\n * Lenguage de origen '" + origin_tech+ "' Aun no se encuentra implementado para traducir. \n Intente con Java !!! ", -2)


    def readContentFromPath(self,path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return content

    def migraSource(self, path,filename):
        #print("Migra el archivo : " + name + " hacia " +   self.destiny_tech)
        fileNameAndPath = path + "\\" + filename
        sources = self.readContentFromPath(fileNameAndPath)
            
        temporarypath = path
        
        subPrompt = filename + "\n" +sources
        
        
        prompt = self.PROMPT_MIGRACION.format(fuentes=subPrompt,
                                        tecnologia_original=self.origin_tech, 
                                        tecnologia_destino=self.destiny_tech)

        requestIA = prompt
        
        # Contexto del asistente
        context = {"role": "assistant", "content": "Eres un developer senior."}
        messages = [context]
        
        messages.append({"role": "user", "content": requestIA})
        responseIA = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages)        
            
        response_content = responseIA.choices[0].message.content        
        messages.append({"role": "assistant", "content": response_content})

        isNameFile = True
        nameFile =""
        contentFile =""

        for line in response_content.splitlines():
            if isNameFile:
                if line.startswith('@@@@'):
                    nameFile=line.replace("@@@@", "")
                    isNameFile=False
            else:
                if line != self.EOF:
                    contentFile += line + "\n"
                else:
                    self.createSource(temporarypath, nameFile, contentFile)
                    isNameFile=True
                    nameFile =""
                    contentFile =""        

    def createSource(self,temporarypath, filename,content):
        table = Table(filename)
        table.add_row(content)
        print(table)    

        ### temporarypath = datetime.now().strftime("%Y%m%d%H%M%S")
        relativepath= temporarypath.replace(self.origin_path, "")
        
        ###get current path
        currentpath = os.path.dirname(os.path.realpath(__file__))
        print("currentpath:"+currentpath)


        outputmainfolder = currentpath +"..\\output" + relativepath 
        print("outputmainfolder:"+outputmainfolder)


        if not os.path.exists(outputmainfolder):
            try:
                subprocess.run(["mkdir", outputmainfolder], shell=True, check=True)                
            except subprocess.CalledProcessError as e:
                print("No se pudo crear la carpeta '{outputmainfolder}': {e}")     

        path = outputmainfolder +"\\"+ filename
        print("creando  archivo  =>"+path)
        file = open(path,"w")
        file.write(content)
        file.close()        


    def save_response_IA(self,response):
        return True

    def salir(self, mensaje, codSalida):
        print(mensaje)
        sys.exit(codSalida)
