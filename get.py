### Instala librerías.
import os
os.system('pip3 install wikipedia')
os.system('pip3 install google_images_download')
os.system('pip3 install face_recognition')

### Importa librerías.
import wikipedia
from google_images_download import google_images_download
import face_recognition
import json, datetime, shutil, cv2, csv, numpy as np

### Lista de nacionalidades no caucásicas.
geo = ['Algeria','Egypt','Libya','Morocco','South Sudan','Sudan','Tunisia',
'Western Sahara','Burundi','Comoros','Djibouti','Eritrea','Ethiopia',
'Kenya','Madagascar','Malawi','Mauritius','Mayotte','Mozambique','Reunion',
'Rwanda','Seychelles','Somalia','Tanzania','Uganda','Zambia','Zimbabwe',
'Benin','Burkina Faso','Cape Verde','Ivory Coast','Gambia','Ghana',
'Guinea','Guinea-Bissau','Liberia','Mali','Mauritania','Niger','Nigeria',
'Saint Helena','Senegal','Sierra Leone','Togo','Angola','Cameroon',
'Central African Republic','Chad','Congo','Democratic Republic of the Congo',
'Equatorial Guinea','Gabon','Sao Tome and Principe','Botswana','Lesotho',
'Namibia','South Africa','Swaziland','Bahrain','Kuwait','Oman,Qatar',
'Saudi Arabia','United Arab Emirates','Yemen','Iraq','Jordan','Palestine'
'Syria','Iran','Egypt','Afghanistan','Bangladesh','Bhutan','Brunei','Cambodia',
'China','India','Indonesia','Japan','Kazakhstan','Kyrgyzstan','Laos',
'Malaysia','Maldives','Mongolia','Myanmar','Nepal','North Korea','Pakistan',
'Philippines','Singapore','South Korea','Sri Lanka','Taiwan','Tajikistan',
'Thailand','Timor-Leste','Turkmenistan','Uzbekistan','Vietnam','Haiti',
'Jamaica','Trinidad and Tobago','Guyana','Suriname','Bahamas','Belize',
'Barbados','Grenada','Curaçao','Algerian','Angolan','Beninese','Motswana',
'Burkinabé','Burkinabe','Burundian','Cameroonian','Cape Verdean','Cabo Verdean',
'Central African','Chadian','Comorian','Congolese','Djiboutian','Egyptian',
'Equatoguinean','Equatorial Guinean','Eritrean','Ethiopian','Gabonese',
'Gabonaise','Gambian','Ghanaian','Guinean','Bissau-Guinean','Ivorian','Kenyan',
'Mosotho','Liberian','Libyan','Malagasy','Malawian','Malian','Mauritanian',
'Mauritian','Moroccan','Mozambican','Namibian','Nigerien','Nigerian',
'Rwandan','Santomean','São Toméan','Sao Tomean','Senegalese','Seychellois',
'Seychelloise','Sierra Leonean','Somali','South Sudanese','Sudanese',
'Swazi','Tanzanian','Togolese','Tunisian','Ugandan','Zambian','Zimbabwean',
'Sahrawi','Sahrawian','Western Saharan','Saudi Arabian','Saudi','Iraqi',
'Iranian','Yemeni','Yemenite','Syrian','Jordanian','Emirati','Omani',
'Kuwaiti','Qatari','Bahrani','Pakistani','Uzbek','Kazakhstani','Afghan',
'Tajikistani','Kyrgyzstani','Kyrgyz','Turkmen','Palestinian','Maldivian',
'Bruneian','Indian','Nepalese','Sri Lankan','Bhutanese','Bangladeshi',
'Indonesian','Filipino','Philippine','Burmese','Myanma','Singaporean',
'Mongolian','Mongol','Laotian','Cambodian','Khmer','Malaysian','Thai',
'Hong Kongese','Hongkonger','Chinese','Vietnamese','Taiwanese','Korean',
'North Korean','South Korean','Japanese','Haitian','Jamaican','Trinidadian',
'Barbadian','Guyanese','Surinamese','Grenadian','Belizean', 'Bahraini',
'Arab','Anishinaabe','Bengali','Kazakh','Curaçaoan','Persian']

### Prepara el script Google Images Download.
response = google_images_download.googleimagesdownload()

### Prepara el script OpenCV.
face_cascade = cv2.CascadeClassifier('./haarcascade_frontalface_alt.xml')

### Lista de nombres de Wikipedia.
f = open('dataset.txt', 'r')
n = [line.rstrip() for line in f.readlines()]
f.close()

### Divide lista en grupos.
names = [n[i:i+400] for i  in range(0, len(n), 400)]

### Carpeta del dataset.
dir1 = './dataset/'
if not os.path.exists(dir1):
    os.mkdir(dir1)

### Horario en que comienza el programa.
time1 = datetime.datetime.now()

### Toma un grupo de nombres.
for x in names[4]:

    ### Comprueba si el nombre es una página de Wikipedia y obtiene los primeros 180 caracteres.
    wiki = True
    try:
        w = wikipedia.page(x)
        text = w.content[:180]
    except:
        wiki = False

    ### Comprueba si una nacionalidad no caucásica aparece en la página.
    caucasian = True
    try:
        for i in geo:
            if i in text:
                caucasian = False
    except:
        pass
    if caucasian is True:

        ### Descarga 20 imágenes de Google relacionadas con el nombre.
        name = x.replace(',','.')
        try:
            arguments = {"keywords":name,"limit":20, "extract_metadata":True}
            response.download(arguments)
            with open('./logs/'+name+'.json') as f:
                data1 = json.load(f)
        except:
            pass

        ### Descarga 10 imágenes de Google relacionadas con el nombre y la palabra 'face'.
        name_face = name + ' face'
        try:
            arguments = {"keywords":name_face,"limit":10, "extract_metadata":True, "image_directory":name}
            response.download(arguments)
            with open('./logs/'+name_face+'.json') as f:
                data2 = json.load(f)
        except:
            pass

        ### Crea una lista con los datos y fusiona los archivos.
        files = []
        for dat in data1:
            if os.path.exists('./downloads/'+name+'/'+dat['image_filename']):
                files.append(dat)
        for dat in data2:
            if os.path.exists('./downloads/'+name+'/'+dat['image_filename']):
                files.append(dat)
        os.remove('./logs/'+name+'.json')
        os.remove('./logs/'+name_face+'.json')
        with open('./logs/'+name+'.json', 'w') as f:
            json.dump(files, f)

        ### Elimina imágenes duplicadas.
        links = []
        for i in range(len(files)):
            if files[i]['image_link'] in links:
                os.remove('./downloads/'+name+'/'+files[i]['image_filename'])
            if files[i]['image_link'] not in links:
                links.append(files[i]['image_link'])

        print('Calculando...')

        ### Checkea si la imagen tiene caras. Si no tiene, o tiene más de dos, guarda el path en la variable "not_found".
        not_found = []
        for img in range(len(files)):
            try:
                image = face_recognition.load_image_file('./downloads/'+name+'/'+files[img]['image_filename'])
                face_locations = face_recognition.face_locations(image)
                num_faces = len(face_locations)
                if num_faces == 0:
                    not_found.append('./downloads/'+name+'/'+files[img]['image_filename'])
                if num_faces > 1:
                    image = cv2.imread('./downloads/'+name+'/'+files[img]['image_filename'])
                    grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(grayImage)
                    n = faces.shape[0]
                    if n > 1:
                        not_found.append('./downloads/'+name+'/'+files[img]['image_filename'])
            except:
                pass
        
        ### Calcula distancia.
        d=[]
        for p1 in range(len(files)):
            for p2 in range(len(files)):
                path1 = './downloads/'+name+'/'+files[p1]['image_filename']
                path2 = './downloads/'+name+'/'+files[p2]['image_filename']
                if path1 not in d:
                    if path1 not in not_found:
                        if path2 not in not_found:
                            if path1 != path2:
                                try:
                                    image_1 = face_recognition.load_image_file(path1)
                                    image_2 = face_recognition.load_image_file(path2)
                                    img_1 = face_recognition.face_encodings(image_1)[0]
                                    img_2 = face_recognition.face_encodings(image_2)[0]
                                    result = face_recognition.face_distance([img_1], img_2)
                                    result = result[0]
                                    if result < 0.55 and result != 0.0:
                                        if path1 not in d:
                                            d.append(path1)
                                        if path2 not in d:
                                            d.append(path2)
                                except:
                                    pass

        ### Genera la categoría en el dataset si hay por lo menos 4 imágenes.
        if len(d) > 3:
            dir2 = './dataset/'+name+'/'
            if not os.path.exists(dir2):
                os.mkdir(dir2)
            for path in d:
                shutil.copy2(path, dir2)
            count = 0
            for filename in os.listdir(dir2):
                count = count + 1
                os.rename(dir2+filename, dir2+name.replace(" ","_")+"_"+str(count)+".jpg")

            ### Genera un archivo csv con información de las categorías (nombre, fecha de nacimiento, path).
            if wiki is True and '(' in text and ')' in text:
                date = (text.split('('))[1].split(')')[0]
                months = ['January','February','March','April','May','June',
                'July','August','September','October','November','December']
                count = 0
                year = 'None'
                for yy in range(1900,2018):
                    if str(yy) in date:
                        year = str(yy)
                        count = count + 1
                month = 'None'
                for mm in range(len(months)):
                    if months[mm] in date:
                        month = months[mm]
                day = 'None'
                for dd in range(1,32):
                    if ' '+str(dd)+' ' in date:
                        day = str(dd).replace(' ','')
                    if ' '+str(dd)+',' in date:
                        day = str(dd).replace(' ','').replace(',','')
                if count > 1:
                    day, month, year = 'None', 'None', 'None'
                with open('dataset.csv', 'a') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    spamwriter.writerow([x, day+'-'+month+'-'+year, day, month, year, dir2])
            else:
                with open('dataset.csv', 'a') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    spamwriter.writerow([x, 'None', 'None', 'None', 'None', dir2])

### Borra la carpeta de descarga.
os.system('rm -rf downloads')

### Tiempo que tardó en ejecutar.
time2 = datetime.datetime.now()
print(time1)
print(time2)
print(time2 - time1)


