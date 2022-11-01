# Dependencies
# ============
# Non-standard
# ------------
# See https://flask.palletsprojects.com/en/2.0.x/
from flask import (
    Blueprint, Flask, abort, flash, redirect, render_template, request, url_for, current_app
)
app = Flask(__name__, instance_relative_config=True)
# See https://flask-wtf.readthedocs.io/
from flask_wtf import FlaskForm

from wtforms import validators, StringField

from werkzeug.utils import secure_filename

import random, json
import requests


bp = Blueprint('metastore', __name__)

app.config['ALLOWED_EXTENSIONS'] = ['XSD', 'JSON']

@bp.route('/metastore/<string(length=1):table><int:number>',
           methods=['GET', 'POST'])
def metaStore(table, number):

   #form to register schema
    form = metaStoreForm(request.form) 
    doc_id = number
    mimetype = None   
    #initialise form with default id
    if request.method == 'GET':
     form.schemeId.data = 'msc:m' + str(number)
     
    
    if request.method == 'POST' :
     #if schemeId is entered, save the id given as scheme ID, else save the default id
     if form.schemeId.data: 
        inputId = form.schemeId.data 
        #print(inputId)
     if request.files:
        #get uploaded scheme
       scheme_file = request.files['scheme_file']
       
      
      #if file has no filename
       if scheme_file.filename == "":
        flash('No file chosen') 
        return redirect(request.url)
       #check if extension is allowed 
       if allowed_extension(scheme_file.filename):
        filename = secure_filename(scheme_file.filename)      
        #scheme_file.save(os.path.join( app.config['FILE_UPLOADS'], filename))

     #depending on type given, set mimetype
     if request.form.get('type'):
      if request.form.get('type') == 'XML':
         mimetype = 'application/xml'
      else:
         mimetype = 'application/json'
    #in case of any error, stay on same page
    else:
     return render_template('metastore.html', doc_id=number, form=form) 
   
    #create record with mandatory fields only
    recordDict = {'schemaId' : inputId,'mimeType' : mimetype,'type' : request.form.get('type')} 
   
    #choose two random numbers 
    randomN1 = random.randint(1,1000)
    randomN2 = random.randint(1,1000)
   
    #create the filename using id of schema and two other random number, n is just a separator between the values
    validFilename = str(doc_id) + 'n' + str(randomN1) + str(randomN2)
    #print(validFilename)
    #add 'record' to make it clearer and add extension to filename
    recordName = validFilename + '-record.json'
    #convert dict containing mandatory fields to json
    with open(recordName, 'w') as rf:
     json.dump(recordDict, rf)

    #session = requests.Session()

    #read from the beginning of the uploaded file
    scheme_file.seek(0)
    #open the created file with in read-mode
    recordFile = open(recordName, "rb")
     #add schema uploaded and record created as a files attribute that will be used in the requests call
    f = {'schema':scheme_file.read(),'record': recordFile }

    #add schema uploaded and record created as a files attribute that will be used in the requests call
    #f = {'schema':scheme_file.read(),'record': (recordName, open(recordName, 'rb'), 'application/json')}
   
   
    url = 'http://localhost:8040/api/v1/schemas/'

    #get all stored schema ids in the metastore
    ids = getAllAvailableMetastoreIds()

    
    #the post request
    #r = requests.Request( 'POST', url, files = f)
    r = requests.post(url,  files = f)

    ##PRINT HTTP-CODE (for testing purposes)
    # prepped = session.prepare_request(r)
    # print("Sending request:")
    # print(format_prepped_request(prepped, 'utf8'))
    # print()
    # r = session.send(prepped, verify=False)

    #print(str(r.status_code))
    #print(str(r.text))
    
    #close file before deleting it
    recordFile.close()
    os.remove(recordName)
    # in case of success response code, check if the scheme Id was used before. If yes display error message, else
    # add schema to the metastore and display its id under identifiers
    if(str(r.status_code) == '201'): 

        if inputId in ids:
            flash("Schema Id already used before. Please choose another Id and try again.")
            return render_template('metastore.html', doc_id=number, form=form)
        else:    
            flash("Successfully added schema. You can find it by clicking on the 'Metastore ID' under 'Identifiers'")
            with transaction(tables['m']) as t:
                t.update({"metastoreId" : [{"id": str(inputId), "scheme": "Metastore"}]}, doc_ids = [number])
            return redirect(url_for('main.display', table = table, number = number))
        
    elif(str(r.status_code) == '403'):
        flash("Schema Id already used before. Please choose another Id and try again.")
        return render_template('metastore.html', doc_id=number, form=form)
    else:
        flash("Error occured. Please check your entries and try again")
        return render_template('metastore.html', doc_id=number, form=form) 
    #  return(str(r.text))

#This funtion validates a given metadata document against a saved scheme in the metastore
@bp.route('/<int:idNo>/validate', methods = ['GET', 'POST'])
def validateMetadataDocument(idNo):  

    form = validationForm(request.form)
    #print (idNo)
    #return json.dumps(tables['m'].all())

    #get all information about the selected standard using its id
    document = tables['m'].get(doc_id=int(idNo))
    #print(number)
    #print(json.dumps(document))
    #if document is None:
     #   return "True"
    session = requests.Session()
    #return json.dumps(document)

    #get the metastore Id (Scheme Id)   
    schemaId = document['metastoreId'][0]['id']
    
    #get uploaded metadata document 
    if request.method == 'POST' :
        if request.files:
         metadataDoc = request.files['metadata_document'] 

     #if file has no filename
        if metadataDoc.filename == "":
         flash('No file chosen') 
         return redirect(request.url)

        version = "1"


        if not allowed_extension(metadataDoc.filename): 
         return redirect(request.url)

    else:
        return render_template('validate-document.html', form = form, doc_id = idNo)
    metadataDoc.seek(0)
    data = {'version': version}
    f = {'document': metadataDoc.read()}

    url = "http://localhost:8040/api/v1/schemas/" + schemaId + "/validate?version=1"
    

    #send post-request by sending attached file and version number in the request
    r = requests.post(url,  files = f,  data = data)
    ##PRINT HTTP-CODE (for testing purposes)
    # prepped = session.prepare_request(r)
    # print("Sending request:")
    # print(format_prepped_request(prepped, 'utf8'))
    # print()
    # r = session.send(prepped, verify=False)


    if(str(r.status_code) == '204'): 
        flash("Scheme Validation successfull.")
        return render_template('validate-document.html', form = form, doc_id = idNo)
    if(str(r.status_code) == '422'): 
        flash(str(r.text))
        return render_template('validate-document.html', form = form, doc_id = idNo)
   # return render_template('validate-document.html', form = form)

 #This method retrieves all information related to the scheme from the metastore with the given schemaID   
@bp.route('/<number>/<schemaID>',
           methods=['GET', 'POST'])
def convertIdtoUrl(schemaID, number):
  schemaUrl = "http://localhost:8040/api/v1/schemas/" + schemaID 
  headers = {"Accept": "application/vnd.datamanager.schema-record+json"}
  r = requests.get(url = schemaUrl, headers = headers)
  response = r.text
  responseDict = json.loads(response)
  
  del responseDict['schemaDocumentUri']
  modifiedDict = responseDict
  #responseJson = json.dumps(modifiedDict) 
  return render_template('view-metastore-record.html', schema = modifiedDict, doc_id = number, schema_url = schemaUrl, sType = responseDict['type'])

#this function return alls schemes' ids in the metastore
def getAllAvailableMetastoreIds():
   schemaUrl = "http://localhost:8040/api/v1/schemas/" 
   r = requests.get(url = schemaUrl)
   response = json.loads(r.text) 
   ids = list(map(lambda r: r['schemaId'], response))
   return ids

#method for printing http code on console (for testing purposes)
def format_prepped_request(prepped, encoding=None):
    # prepped has .method, .path_url, .headers and .body attribute to view the request
    encoding = encoding or requests.utils.get_encoding_from_headers(prepped.headers)
    body = prepped.body.decode(encoding) if encoding else '<binary data>' 
    headers = '\n'.join(['{}: {}'.format(*hv) for hv in prepped.headers.items()])
    return f"""\
{prepped.method} {prepped.path_url} HTTP/1.1
{headers}

{body}""" 

@bp.route('/<schemaID>/')
def viewSchemaJSON(schemaID):
    schemaUrl = "http://localhost:8040/api/v1/schemas/" + schemaID
    r = requests.get(url = schemaUrl)
    response = r.text
    
    responseDict = json.loads(response)
    
    return render_template('view-metastore-schema-json.html', schema = responseDict, schema_id = schemaID)
#{{ url_for('viewSchema', schemaID = schema['schemaId'] , number = doc_id ) }}

#function responsible for viewing schemes of type xml
@bp.route('/<schemaID>/xml')
def viewSchemaXML(schemaID):
    schemaUrl = "http://localhost:8040/api/v1/schemas/" + schemaID
    r = requests.get(url = schemaUrl)
    response = r.text
    return render_template('view-metastore-schema-xml.html', schema = response, schema_id = schemaID)



#function to remove element from dict
def removekey(d, key):
    r = dict(d)
    del r[key]
    return r

#filter for formatting json in templates
@bp.app_template_filter('prettyjson') 
def to_pretty_json(value):
    return json.dumps(value,
                      indent=8, separators=(',', ': '))

        

#form for metastore
class metaStoreForm(FlaskForm): 
   schemeId = StringField('Schema Id') 
  # mimetype = StringField('Mime Type')
   #tp = StringField('Type')
   #sfile = StringField('Select File')
   tp = StringField('Type', validators=[validators.InputRequired(message ='Please choose a file type')])
   sfile = StringField('Select File', validators=[validators.InputRequired(message = 'Please upload a file')])

#form for metadata-document-validation   
class validationForm(FlaskForm):
    document = StringField('Select File')

def allowed_extension(filename):
    if not "." in filename:
        return False
    ext = getExtension(filename)
           
    
    if ext.upper() in app.config['ALLOWED_EXTENSIONS']:
        return True
    else:
        flash('Only xml or json files are allowed')
        return redirect(request.url)

def getExtension(filename):
    ext = filename.rsplit(".", 1)[1] 
    return ext

