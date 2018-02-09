![Versión Python](https://img.shields.io/badge/python-2.7-blue.svg)
![Licencia](https://img.shields.io/badge/License-Apache%202.0-blue.svg)

<p align="center"><img src="logo.png" /></p>

### Sistema de Extracción Automática y Visualización 3D de Moléculas en Textos Biomédicos
---
**II Hackathon de tecnologías del Lenguaje**

Sistema de **análisis de texto de documentos biomédicos**, que extrae referencias a medicamentos, moléculas, y otros compuestos químicos, mediante **técnicas de reconocimiento de entidades biomédicas nombradas**, y que permite visualizar en 3 dimensiones las estructuras moleculares detectadas, así como ver información semántica complementaria de ellas. 
La aplicación está pensada para ayudar a estudiantes de titulaciones de ciencias de la salud (Medicina, Farmacia, Biotecnología, etc.). Se utilizan técnicas de Procesamiento del Lenguaje Natural para extraer las entidades químicas nombradas y, mediante consultas a fuentes de Datos Enlazados Abiertos (Linked Open Data) se **recupera información semántica multilingüe** sobre dichas entidades, además de información de la fórmula y la estructura molecular del compuesto. Esa estructura se dibuja y **se muestra a los usuarios en un modelo 3D** que permite rotar y hacer zoom en las moléculas para poder estudiarlas mejor. Además, la librería que hemos desarrollado permite realizar búsquedas en sciELO de artículos científicos que hablen sobre las moléculas detectadas (también de forma multilingüe), visualizar los artículos, o cargarlos en la aplicación para buscar nuevas moléculas y compuestos.

## Instalación
El sistema necesita las siguientes librerías externas para funcionar: 

* Bottle - Python Web Framework: https://bottlepy.org
* ChemDataExtractor: http://chemdataextractor.org
* SPARQLWrapper - SPARQL Endpoint interface to Python: https://rdflib.github.io/sparqlwrapper/
* Requests: http://python-requests.org
* Untangle: http://untangle.readthedocs.io


### 1. Descargar el código 

```bash
$ git clone https://github.com/epuertas/ChemPLN.git
$ cd ChemPLN
```

### 2. Instalar las dependencias

```bash
$ mkvirtualenv ChemPLN
$ pip install -r requirements.txt
```
  
Si tienes instalado **Anaconda** también se puede utilizar esta herramienta para instalar las dependencias. Puedes consultar como hacerlo en la web de cada módulo.

### 3. Descarga de modelos de ChemDataExtractor

```bash
$ cde data download
```

## Ejecución y uso de la herramienta
Para utilizar la aplicación, lo primero que hay que hacer es lanzar el servicio de procesamiento de información: Abrimos un terminal en el directorio del proyecto y escribimos la siguiente línea:
```bash
python chemInfo3D.py
```

La interfaz del sistema es una aplicación web a la que podemos acceder abriendo en un navegador web la dirección **"localhost:8080"**. 
Lo primero que veremos es un editor de texto en el que podemos introducir el texto biomédico que queremos analizar. La interfaz carga por defecto un ejemplo con un texto de un fragmento de un caso clínico.

Una vez introducido el documento, pulsando en el botón **"Procesar Texto"**, se analiza, y cuando termina el análisis se nos muestra un panel con un listado de los compuestos químicos encontrados. Al pinchar en un compuesto, se muestra la siguiente información:

* Nombre del compuesto.
* Formulación químicas.
* Descripción del compuesto (multilingüe).
* Visualizazción 3D interactiva.
* Imagen en 2D.
* Listado de artículos disponibles en **SciELO** relacionados con el compuesto seleccionado (multilingüe).

En la parte superior del panel de información tenemos un selector de idioma que nos permite elegir, para aquellos elementos multilingües, en qué idioma queremos recuperar y ver la información. Aunque el prototipo sólo muestra opciones para inglés y español, el sistema tiene implementado soporte para todos los idiomas disponibles en ScieLO para los artículos (español, inglés, portugués, etc.), y todos los idiomas de la Wikipedia para la información general.




