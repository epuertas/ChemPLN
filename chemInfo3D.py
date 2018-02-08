#  -*- coding: utf-8 -*-
from bottle import route, run, template, request, response, get, post, static_file
from chemdataextractor import Document
from SPARQLWrapper import SPARQLWrapper, JSON
import requests
import json
import re
import untangle

# Endpoint DBPedia para consultas web semántica
sparql = SPARQLWrapper("http://dbpedia.org/sparql")

#
# Parser de texto que extrae las entidades químicas nombradas.
# Utiliza la libreria ChemDataExtractor.
# 	
@post('/documento')
def extraerChemContent():
    documento = request.forms.get("text")
    doc = Document(documento)
    response.content_type = 'application/json'
    return json.dumps(doc.records.serialize())

#
# Consulta a DBPedia mediante una sentencia SPARQL
# para recuperar la definicion del compuesto en el idioma
# indicado como parametro. El idioma se especifica mediante 
# su código ISO (en = inglés; es = español; pt = portugués, etc.)
#
@route('/abstract/<unTermino>/<language>')
def dbpediaAbstract(unTermino, language):
	
    sparql.setQuery("""
    PREFIX res: <http://dbpedia.org/resource/>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    SELECT DISTINCT ?abstract
    WHERE {
    res:"""+unTermino+""" dbo:abstract ?abstract .
    filter (lang(?abstract) = '"""+language+"""' ) .
    }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    if results["results"]["bindings"]: 
        txtAbstract = results["results"]["bindings"][0]["abstract"]["value"]
        htmlResult = txtAbstract
    #Si no existe descripcuion en DBPedia, devolvemos un texto indicandolo
    else:
        if language == 'es':					    
            htmlResult = "No hay descripci&oacute;n disponible para este compuesto."
        else:
            htmlResult = "No description available for this compound."
	
    return htmlResult
	
#
# Devuelve el identificador pubchem de un compuesto
#
@route('/pubchem/<unTermino>')
def pubchemID(unTermino):

    r = requests.get('https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/'+unTermino+'/json')	
    results = json.loads(r.text)    
    return str(results["PC_Compounds"][0]["id"]["id"]["cid"])
	
#
# Devuelve una imagen en formato png de un compuesto (obtenida de pubchem)
#	
@route('/pubchem/th/<unTermino>')
def pubchemTH(unTermino):

    r = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/'+unTermino+'/PNG'	
    return str(r)


#
# Consulta a DBPedia mediante una sentencia SPARQL
# para recuperar el identificador en drugbank del compuesto 
#	
@route('/dbpedia/drugbankID/<unTermino>')
def drugbankID(unTermino):
    
    sparql.setQuery("""
    PREFIX res: <http://dbpedia.org/resource/>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    SELECT DISTINCT ?drugbank
    WHERE {
    res:"""+unTermino+""" dbo:drugbank ?drugbank
    }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    return results["results"]["bindings"][0]["drugbank"]["value"]

#
# Realiza una búsqueda de información de un compuesto en DRUGBANK
# y devuelve su descripción en inglés.
# 
	
@route('/drugbank/<unTermino>')
def drugbankInfo(unTermino):

    r = requests.get('https://www.drugbank.ca/unearth/q?searcher=drugs&query='+unTermino)
    html = r.text
    # Buscamos el primer resultado de la busqueda
    if r.history:
         urlXML = r.url + ".xml"
	
    match = re.search(r'hit-link"><a href="(.*?)">', html, re.IGNORECASE|re.DOTALL|re.MULTILINE)
    if match:                      
        urlXML = "https://www.drugbank.ca"+match.group(1)+ ".xml"
		
    o = untangle.parse(urlXML)
    return str(o.drugbank.drug.description.cdata +". "+o.drugbank.drug.classification.description.cdata)

#
# Realiza una búsqueda de un compuesto en DRUGBANK y devuelve su identificador
# 	
@route('/drugbank/id/<unTermino>')
def drugbankInfo(unTermino):

    r = requests.get('https://www.drugbank.ca/unearth/q?searcher=drugs&query='+unTermino)
    html = r.text
    # Buscamos el primer resultado de la busqueda
    if r.history:
         urlXML = r.url + ".xml"
	
    match = re.search(r'hit-link"><a href="(.*?)"', html, re.IGNORECASE|re.DOTALL|re.MULTILINE)
    if match:                      
        urlXML = "https://www.drugbank.ca"+match.group(1)+ ".xml"
		
    drugbankID = re.search(r'.ca/drugs/(.*?)\.xml', urlXML, re.IGNORECASE|re.DOTALL)
    return drugbankID.group(1)

#
# Dado el identificador en DRUGBANK de un compuesto, devuelve su estructura molecular en formato PDB
# 
@route('/drugbank/pdb/<drugbankID>')
def drugbankpdb(drugbankID):

    r = requests.get('https://www.drugbank.ca/drugs/'+drugbankID+'.pdb')
    return r.text

#
# Permite recuperar información de un compuesto de Chemical Identifier Resolver
# https://cactus.nci.nih.gov/chemical/structure
# 
@route('/opsin/<termino>/<formato>')
def opsin(termino,formato):	
    response = ''
    r = requests.get('https://cactus.nci.nih.gov/chemical/structure/%s/%s' % (termino, formato))
    if r.ok:
        response = r.text
    return response
	
#
# Realiza una consulta en el repositorio de articulos cientificos SciELO y devuelve una lista de articulos
# con el título, autores, abstract y enlace a articulo completo
# La consulta recupera los articulos en el idioma especificado como parametro
#	
@route('/scielo/<unTermino>/<lng>')
def scieloInfo(unTermino, lng):
    urlXML = 'https://search.scielo.org/?lang=%s&output=xml&sort=RELEVANCE&filter[la][]=%s&q=%s' % (lng,lng,unTermino)

    o = untangle.parse(urlXML)
    resultados = o.response.result.doc
    response = ''
    listaAutores = ''
    abstract = ''
    enlaceFullPaper = ''
    if resultados:
        for i, r in enumerate (resultados):
            response += '<div class="row"><div class="col-sm-12">'
            for paper in [attr for attr in r.arr if attr['name']=="ti_%s" % lng] :
                titulo = '<h6 class="text-info">%s</h6>' % paper.str.cdata.encode("utf-8")
            for autores in [attr for attr in r.arr if attr['name']=="au"] :            
                if autores:
                    listaAutores = '<div class="small">'+','.join([autor.cdata for autor in autores.str])+'</div>'
                else:
                    listaAutores = ''
            for anAbstract in [attr for attr in r.arr if attr['name']=="ab_%s" % lng] :
                abstract = anAbstract.str.cdata.encode("utf-8")
            for aLink in [attr for attr in r.arr if attr['name']=="fulltext_html_%s" % lng]:
                enlaceFullPaper = aLink.str.cdata.encode("utf-8")
            response += '%s %s </div></div>' % (titulo, listaAutores.encode("utf-8"))
            response += '<div style="display:none;" id="art%d">%s</div>' % (i, abstract)
            response += """<br/><div><button class="btn btn-info" onClick="cargarArticulo('art%d');">Analizar Abstract</button>""" % i
            response += """<a class="btn btn-secondary" style="margin-left:10px;" target="_blank" href="%s">Ver</a><div><hr />""" % enlaceFullPaper
    else:
        response = 'No se encontraron art&iacute;culos disponibles para este t&eacute;rmino'
    return response

	
####### Rutas estaticas ###############
@route('/')
def serve_homepage():
    return static_file('index.html', root='static/')
	
@get("/static/css/<filepath:re:.*\.css>")
def css(filepath):
    return static_file(filepath, root="static/css")

@get("/static/font/<filepath:re:.*\.(eot|otf|svg|ttf|woff|woff2?)>")
def font(filepath):
    return static_file(filepath, root="static/font")

@get("/static/img/<filepath:re:.*\.(jpg|png|gif|ico)>")
def img(filepath):
    return static_file(filepath, root="static/img")

@get("/static/js/<filepath:re:.*\.js>")
def js(filepath):
    return static_file(filepath, root="static/js")

###### EJECUCIÓN DEL SERVIDOR #######
	
run(host='localhost', port=8080)
