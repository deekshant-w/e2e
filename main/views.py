from django.shortcuts import render,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from json import loads,dumps
import requests
from .models import Message

website = 'http://127.0.0.1:8000/'

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

def msgDecrypt(msg,uid):
	nonce 	= msg[:16]
	tag 	= msg[16:32]
	msg		= msg[32:]
	key 	= keyExchange(uid).encode()
	decrypt	= AES.new(key, AES.MODE_EAX, nonce=nonce)
	msg 	= decrypt.decrypt(msg)
	print(nonce,tag,msg,key,key2,sep='\n\n')
	return HttpResponse(msg)

def user(request,uid=None):
	if(uid is None):
		return HttpResponse("What were you expecting? Magic?", content_type="text/plain")
	if(uid!='a' and uid!='b'):
		return HttpResponse("We are not here yet!", content_type="text/plain")
	key = keyExchange(uid)
	print(key)
	data = Message.objects.all()
	for x in range(len(data)):
		data[x].
	return render(
		request,
		'main/main.html',
		{
			'user':uid,
			'data':data,
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
def server(request):
	if(request.method=='POST'):
		user = request.POST.get('user')
		msg = request.FILES['msg'].read()
		print(user)
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