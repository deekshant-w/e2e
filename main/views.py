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
fromToConversionTable = {1:'a',2:'b'}

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
	nonce 	= msg[:16]
	tag 	= msg[16:32]
	msg		= msg[32:]
	decrypt	= AES.new(key, AES.MODE_EAX, nonce=nonce)
	msg 	= decrypt.decrypt(msg).decode()
	print(msg)
	return msg

def user(request,uid=None):
	if(uid is None):
		return HttpResponse("What were you expecting? Magic?", content_type="text/plain")
	if(uid!='a' and uid!='b'):
		return HttpResponse("We are not here yet!", content_type="text/plain")
	key = keyExchange(uid).encode()
	data = Message.objects.all()
	cleanData = {}
	for x in range(len(data)):
		cleanData[data[x].id] = [msgDecrypt(data[x].msg,key),fromToConversionTable[data[x].fromTo.to_integral()]]
	data = dumps(cleanData)
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


######################################################################
######## Server Code Below : Can be Seperated ########################
######################################################################
def serverSave(request):
	if(request.method=='POST'):
		user = request.POST.get('user')
		msg = request.FILES['msg'].read()
		temp = msg
		msg = str(base64.b64encode(msg))[2:-1]
		print(f'aadcs we fasef 123 {base64.b64decode(msg)==temp}')
		print(type(msg))
		try:
			newMsg = Message(msg = msg)
			if(user=='a'):
				newMsg.fromTo = 1
			else:
				newMsg.fromTo = 2
			newMsg.save()
			return HttpResponse("Success")
		except Exception as e:
			return HttpResponse(e)
	return HttpResponse("SERVER!")

def serverGetAll(request):
	allData = Message.objects.all()
	startCounter = 0
	payload = []
	msgChunk = b''
	for msgs in allData:
		slot = {}
		slot['timeStamp']	= msgs.timeStamp
		slot['fromTo'] 		= msgs.fromTo
		slot['start'] 		= startCounter
		slot['end'] 		= startCounter + len(msgs.msg)
		print(msgs.msg,len(msgs.msg),slot['start'] ,slot['end'] )
		startCounter 		= startCounter + len(msgs.msg)
		msgChunk			+= msgs.msg
		payload.append(slot)
	data = dumps({'data':payload},cls=DjangoJSONEncoder)
	testing = loads(data)
	print(dumps(testing,indent=2))
	a = datetime.strptime(testing['data'][0]['timeStamp'],'%Y-%m-%dT%H:%M:%S.%fZ')
	print(msgChunk)
	return HttpResponse(data)
