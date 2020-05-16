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

website = 'http://127.0.0.1:8000/'
newMsgAva = {'a':0,'b':0}

def landing(request):
	return HttpResponse("Hello World or something? I dont know.\nTry being a or b.", content_type="text/plain")

def invertUser(u):
	if(u=='a'):
		return 'b'
	return 'a'

def test(request):
	data	= Message.objects.all()[10].msg
	nonce 	= data[:16]
	tag 	= data[16:32]
	msg		= data[32:]
	key 	= keyExchange('a').encode()
	key2	= keyExchange('b').encode()
	decrypt	= AES.new(key, AES.MODE_EAX, nonce=nonce)
	msg 	= decrypt.decrypt(msg)
	# rint(nonce,tag,msg,key,key2,sep='\n\n')
	return HttpResponse(msg)

def msgDecrypt(msg,key):
	msg = base64.b64decode(msg)
	nonce 	= msg[:16]
	tag 	= msg[16:32]
	msg		= msg[32:]
	decrypt	= AES.new(key, AES.MODE_EAX, nonce=nonce)
	msg 	= decrypt.decrypt(msg).decode()
	return msg

def user(request,uid=None):
	if(uid is None):
		return HttpResponse("What were you expecting? Magic?", content_type="text/plain")
	if(uid!='a' and uid!='b'):
		return HttpResponse("We are not here yet!", content_type="text/plain")
	key = keyExchange(uid).encode()
	data = requests.get(url=website+'server/all/').json()
	last = data['last']
	data = data['data']
	cleanData = []
	for x in range(len(data)):
		cleanData.append([
			msgDecrypt(data[x]["msg"],key),
			data[x]["sender"],
		])
	data = dumps(cleanData,default=str)
	return render(
		request,
		'main/main.html',
		{
			'user':uid,
			'data':data,
			'website':website,
			'last': last,
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
	user = invertUser(user)
	e1 = requests.get(website+"e1/"+user).text
	user = invertUser(user)
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
		return HttpResponse(responce.text)
	return HttpResponse("Error")

def newMsgs(request,uid):
	thisUser = uid
	uid = invertUser(uid)
	if(request.method=='POST'):
		timeStamp = request.POST.get('last')
		newHeader = getHeader(request.headers)
		while(not newMsgAva[invertUser(uid)]):
			pass
		responce = requests.post(
			url = website + 'server/fromTS/',
			data = {
				'timeStamp':timeStamp,
				'user':uid,				
			},
			headers=newHeader
		).json()
		msgs = []
		if(responce['status']):
			key = keyExchange(thisUser).encode()
			for m in responce['data']:
				msgs.append(msgDecrypt(m['msg'],key))
			responce['data'] = msgs
		newMsgAva[invertUser(uid)] = 0
		return HttpResponse(dumps(responce))
	return HttpResponse('Well?')
		
def newMessageAvaialable(request,uid):
	if(request.method=='GET'):
		newMsgAva[uid] = 1
	return HttpResponse('OK!!')


######################################################################
######## Server Code Below : Can be Seperated ########################
######################################################################
def stringToDate(s):
	return datetime.strptime(s,'%Y-%m-%d %H:%M:%S.%f%z')

def serverSave(request):
	if(request.method=='POST'):
		user = request.POST.get('user').strip()
		msg = request.FILES['msg'].read()
		msg = str(base64.b64encode(msg))[2:-1]
		newMsg = Message(msg = msg, sender=user)
		newMsg.save()
		requests.get(url= website+'newMessageAvaialable/'+invertUser(user))
		return HttpResponse(200)
	return HttpResponse("SERVER!")

def serverGetAll(request):
	if(request.method=='GET'):
		data = Message.objects.values('sender','msg')
		last = Message.objects.latest('timeStamp').timeStamp
		payload = dumps({'data':list(data),'last':last},default=str)	#,cls=DjangoJSONEncoder)
		return HttpResponse(payload)
	return HttpResponse("Not that easy")

def serverFromTS(request):
	if(request.method=='POST'):
		timeStamp = stringToDate(request.POST.get('timeStamp'))
		user = request.POST.get('user')
		data = Message.objects.filter(timeStamp__gt=timeStamp,sender=user)
		msgData = list(data.values('msg'))
		result = {}
		if(len(data)):
			result['status'] = 1
			result['data'] = msgData
			result['last'] = data[len(data)-1].timeStamp
		else:
			result['status'] = 0
		payload = dumps(result,default=str)
		return HttpResponse(payload)
	return HttpResponse("Server From Index")
