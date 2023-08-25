    
def extractzipfile(self, filename,outputFolder):
    if not os.path.exists(outputFolder):
        os.mkdir(outputFolder)

    if os.path.exists(filename):
        shutil.unpack_archive(filename, outputFolder) 
        msg= ("["+filename+"] archivo descomprimido exitosamente")
        print(msg)
    else:
        self.salir("Archivo "+filename+" No encontrado.!",-3);
    return ""


def createhtml(request, response, languageorigen, languagedestino,  comentarios ):

    htmlstr="""
                    <!DOCTYPE html>
                    <html lang="es">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Tabla de Contenido</title>
                        <link rel="stylesheet" href="./util/styles.css">
                    </head>
                    <body>
                       <!--
                        <div class="container">
                            <div class="column" id="seccion1">
                                <h2>{languageorigen}</h2>
                                <p>{comentarios}</p>
                            </div>
                            <div class="column" id="seccion4">
                                <h2>{languagedestino}</h2>
                                <p>{comentarios}</p>
                            </div>
                        </div>
                        -->
                        <div class="container">
                            <div class="column">
                                <h2>{languageorigen}</h2>
                                <ul>
                                    <li><textarea rows="45" cols="80">{request}</textarea></li>
                                </ul>
                            </div>
                            <div class="column">
                                <h2>{languagedestino}</h2>
                                <ul>
                                    <li><textarea rows="45" cols="80">{response}</textarea></li>
                                </ul>
                            </div>
                        </div>
                    </body>
                    </html>
            """.format(request=request,response=response,comentarios=comentarios,languageorigen=languageorigen,languagedestino=languagedestino)

   
    return htmlstr
