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

import logging
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
        self.currentlypath=os.getcwd()
        filenamelog=self.creararchivolog()
        logging.basicConfig(filename=filenamelog, level=logging.DEBUG)
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

        try:
            self.response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=self.messages)

            if self.response == "" or len (self.response)== 0:
                ###logging.error("ChatGTP no ha retornado ninguna respuesta a su consulta, favor intente más tarde.")  
                return self.error("ChatGTP no ha retornado ninguna respuesta a su consulta, favor intente más tarde.", -1)
            return True
        except openai.error.APIError as e:
        #Handle API error here, e.g. retry or log
            ###logging.error(f"OpenAI API returned an API Error: {e}")
            return self.error(f"OpenAI API returned an API Error: {e}",-10)
        except openai.error.APIConnectionError as e:
        #Handle connection error here
            ###logging.error(f"Failed to connect to OpenAI API: {e}")
            return self.error(f"Failed to connect to OpenAI API: {e}",-10)
        except openai.error.RateLimitError as e:
        #Handle rate limit error (we recommend using exponential backoff)
            ###logging.error(f"OpenAI API request exceeded rate limit: {e}")
            return self.error(f"OpenAI API request exceeded rate limit: {e}",-10)


    def migrar(self, origin_path, origin_tech, destiny_tech):
        self.origin_path = origin_path
        self.origin_tech = origin_tech
        self.destiny_tech = destiny_tech
        if not os.path.exists(origin_path):
            return self.error("\n * El directorio '"+origin_path+"' especificado No existe", -1)            
        
        if not self.findFiles(origin_path, origin_tech):
            return False
        return True
        
    def findFiles(self, pathFiles, origin_tech):           
        #TODO : Tarea pendiente identificar la extencion de la tecnologia de origen
        if origin_tech.startswith("java") or len(origin_tech)>0:     
            ###logging.info(pathFiles)
            for root, dirs, files in os.walk(pathFiles, topdown=False):
                for name in files:
                    if name.endswith(".java"):
                        ###logging.info("name:"+name)
                        if not self.migraSource(root,name):
                            return False
            return True
        else:
            return self.error("\n * Lenguage de origen '" + origin_tech+ "' Aun no se encuentra implementado para traducir. \n Intente con Java !!! ", -2)


    def creararchivolog(self):
        
        logpath=self.currentlypath+"\\log"

        if not os.path.exists(logpath):
            try:
                subprocess.run(["mkdir", logpath], shell=True, check=True)                
            except subprocess.CalledProcessError as e:
                return self.error("No se pudo crear la carpeta log': {e}",-1)     

        temporarylog = datetime.now().strftime("%Y%m%d%H%M%S")
        filog=logpath+"\\log"+temporarylog+".txt"
        return filog   
    
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
        
        requestia = prompt
        
        # Contexto del asistente
        context = {"role": "assistant", "content": "Eres un developer senior."}
        messages = [context]
        
        messages.append({"role": "assistant", "content": requestia})

        try:
            ## haciendo la pregunta a CHATGPT
            responseia = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages)   

            if responseia == "" or len (responseia)== 0:
                ###logging.error("ChatGTP no ha retornado ninguna respuesta a su consulta, favor intente más tarde.")  
                return self.error("ChatGTP no ha retornado ninguna respuesta a su consulta, favor intente más tarde.", -1)

        except openai.error.APIError as e:
            #Handle API error here, e.g. retry or log
            ###logging.error(f"OpenAI API returned an API Error: {e}")
            return self.error(f"OpenAI API returned an API Error: {e}",-10)
        except openai.error.APIConnectionError as e:
            #Handle connection error here
            ###logging.error(f"Failed to connect to OpenAI API: {e}")
            return self.error(f"Failed to connect to OpenAI API: {e}",-10)
        except openai.error.RateLimitError as e:
             #Handle rate limit error (we recommend using exponential backoff)
            ###logging.error(f"OpenAI API request exceeded rate limit: {e}")
            return self.error(f"OpenAI API request exceeded rate limit: {e}",-10)

         ## Obteniendo la respuesta de CHATGPT
        response_content = responseia.choices[0].message.content        

        self.historiaIA(filename,prompt, response_content)
        messages.append({"role": "assistant", "content": response_content})

        if response_content == "" or len (response_content)== 0:
            ###logging.error("ChatGTP no ha retornado ninguna respuesta a su consulta, favor intente más tarde.")  
            return self.error("ChatGTP no ha retornado ninguna respuesta a su consulta, favor intente más tarde.", -1)

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
                    if self.createSource(temporarypath, nameFile, contentFile):
                        isNameFile=True
                        nameFile =""
                        contentFile =""
                    else:
                        return False
                    
        return True

    def historiaIA(self,filename,request, response):
        ###Crea un archivo en formato html 
        # que donde pueda almacenar en un textarea el request y en otro text area el response
        path = os.getcwd() +"\\"+ filename + ".html"
        file = open(path,"w")
        file.write("""
                   <html>
                    <body>
                        <textarea rows="45" cols="80">{request}</textarea>
                        <hr/>
                        <textarea rows="45" cols="80">{response}</textarea>
                    </body>
                   </html>
                   """.format(request=request,response=response))
        file.close()

    def createSource(self,temporarypath, filename,content):
        table = Table(filename)
        table.add_row(content)
        print(table)    

        ### temporarypath = datetime.now().strftime("%Y%m%d%H%M%S")
        relativepath= temporarypath.replace(self.origin_path, "")
        
        ###get current path
        currentpath = os.path.dirname(os.path.realpath(__file__))
##        print("currentpath1111:"+currentpath)
##        ###logging.info("os.getcwd():"+os.getcwd())
##        self.salir("saliendo!!!!!",-1)

        outputmainfolder = currentpath +"\\output" + relativepath 

        if not os.path.exists(outputmainfolder):
            try:
                subprocess.run(["mkdir", outputmainfolder], shell=True, check=True)                
            except subprocess.CalledProcessError as e:
                return self.error("No se pudo crear la carpeta '{outputmainfolder}': {e}",-1)     

        path = outputmainfolder +"\\"+ filename
        logging.info("creando  archivo  =>"+path)
        file = open(path,"w")
        file.write(content)
        file.close()   
        return True     


    def save_response_IA(self,response):
        return True

    def error(self, mensaje, codSalida):
        logging.error(mensaje)
        return False
