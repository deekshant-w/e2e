from django.shortcuts import render,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from json import loads,dumps
import requests
from .models import Message
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime
import base64

website = 'http://192.168.0.37:8000/'
fromToConversionTable = {'1':'a','2':'b'}

def landing(request):
	return HttpResponse("Hello World or something? I dont know.\nTry being a or b.", content_type="text/plain")

def test(request):
	data	= Message.objects.all()[10].msg
	nonce 	= data[:16]
	tag 	= data[16:32]
	msg		= data[32:]
	key 	= keyExchange('a').encode()
	key2	= keyExchange('b').encode()
	decrypt	= AES.new(key, AES.MODE_EAX, nonce=nonce)
	msg 	= decrypt.decrypt(msg)
	print(nonce,tag,msg,key,key2,sep='\n\n')
	return HttpResponse(msg)

def msgDecrypt(msg,key):
	msg = base64.b64decode(msg)
	nonce 	= msg[:16]
	tag 	= msg[16:32]
	msg		= msg[32:]
	decrypt	= AES.new(key, AES.MODE_EAX, nonce=nonce)
	msg 	= decrypt.decrypt(msg).decode()
	return msg

def stringToDate(s):
	return datetime.strptime(s,'%Y-%m-%d %H:%M:%S.%f%z')

def user(request,uid=None):
	if(uid is None):
		return HttpResponse("What were you expecting? Magic?", content_type="text/plain")
	if(uid!='a' and uid!='b'):
		return HttpResponse("We are not here yet!", content_type="text/plain")
	key = keyExchange(uid).encode()
	data = requests.get(url=website+'server/all/').json()['data']
	cleanData = []
	for x in range(len(data)):
		cleanData.append([
			msgDecrypt(data[x]["msg"],key),
			data[x]["sender"],
			stringToDate(data[x]['timeStamp'])
		])
	data = dumps(cleanData,default=str)
	print(cleanData[x][0])
	return render(
		request,
		'main/main.html',
		{
			'user':uid,
			'data':data,
			'website':website,
		}
	)

def stringToNumber(string):
	mapping = loads(open('mapping','r').read())
	number = ""
	for x in string:
		number += mapping[x]
	return int(number)

def numberToString(string,l):
	mapping = loads(open('mapping','r').read())
	result = ""
	for x in range(0,len(string),2):
		try:
			result += mapping[string[x:x+2]]
		except:
			result += str(int(string))
	return result[:l]

def combine1(user):
	privateKey 	= stringToNumber(open(f"./privateKeys/KeyFor{user.capitalize()}").read())
	publicKey	= stringToNumber(open(f"PublicKey").read())
	modulus		= stringToNumber(open(f"modulus").read())
	generatedKey= str(pow(publicKey,privateKey,modulus))
	return generatedKey

def combine2(user,base):
	privateKey 	= stringToNumber(open(f"./privateKeys/KeyFor{user.capitalize()}").read())
	base 		= int(base)
	modulus		= stringToNumber(open(f"modulus").read())
	generatedKey= pow(base,privateKey,modulus)
	return generatedKey

def exchange1(request,uid):
	return HttpResponse(combine1(uid))

def keyExchange(user):
	if(user=='a'):
		user='b'
	else:
		user='a'
	e1 = requests.get(website+"e1/"+user).text
	if(user=='a'):
		user='b'
	else:
		user='a'
	key = combine2(user,e1)
	result = numberToString(str(key),32)
	return result

def getHeader(data):
	newHeader = {}
	newHeader['X-Csrftoken'] = data['X-Csrftoken']
	newHeader['Cookie'] = data['Cookie']
	return newHeader

def ajax(request,uid):
	if(request.method == 'POST'):
		message = request.POST.get("msg").encode("utf8")
		key = keyExchange(uid).encode()
		cipher = AES.new(key, AES.MODE_EAX)
		ciphertext, tag = cipher.encrypt_and_digest(message)	#x 		#16
		nonce = cipher.nonce	#16
		ciphertext = nonce + tag + ciphertext	# 16 	#16 	#x
		newHeader = getHeader(request.headers)
		responce = requests.post(
			url = website+"server/save/",
			data = {
				'user' : uid
			},
			files = {
				'msg' : ciphertext
			},
			headers=newHeader
		)
		# d = AES.new(key, AES.MODE_EAX, nonce=nonce)
		# p = d.decrypt(ciphertext)
		return HttpResponse(responce.text)
	return HttpResponse("Error")

def newMsg(request,uid):
	if(request.method=='POST'):
		timeStamp = request.POST.get('lastStamp')
		newHeader = getHeader(request.headers)
		responce = requests.post(
			url = website + 'server/fromTS/',
			data = {
				'timeStamp':timeStamp,
				
			},
			headers=newHeader
		)
		

######################################################################
######## Server Code Below : Can be Seperated ########################
######################################################################
def serverSave(request):
	if(request.method=='POST'):
		user = request.POST.get('user').strip()
		msg = request.FILES['msg'].read()
		msg = str(base64.b64encode(msg))[2:-1]
		newMsg = Message(msg = msg, sender=user)
		newMsg.save()
		return HttpResponse(e)
	return HttpResponse("SERVER!")

def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()

def serverGetAll(request):
	if(request.method=='GET'):
		data = Message.objects.values('timeStamp','sender','msg')
		payload = dumps({'data':list(data)},default=str)	#,cls=DjangoJSONEncoder)
		print(payload)
		return HttpResponse(payload)
	# a = datetime.strptime(testing['data'][0]['timeStamp'],'%Y-%m-%dT%H:%M:%S.%fZ')
	return HttpResponse("Not that easy")

def serverFromTS(request):
	if(request.method=='POST'):
		timeStamp = stringToDate(request.GET.get('timeStamp'))
		data = Message.objects.filter(timeStamp__gt=timeStamp)
		result = {}
		print(data)
		if(len(data)):
			result['status'] = 1
			result['data'] = data
		else:
			result['status'] = 0
		payload = dumps(result,default=default)
		return HttpResponse(payload)
	return HttpResponse("Server From Index")
