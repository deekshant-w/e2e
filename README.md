# End to End Encryption

This is a python(django) implementation of End to End Encryption using **Diffie Hellman Key Exchange** method along with **RSA encryption**. Although in real aaplications the user and server side of of such a chating service are supposed to be seperate. But for demonstration purposes in this project the users and the chatting server are combined. Although they are together yet they have been created in such a way that views and models of the user and the server are completely interdependent and and can easily be split onto seperate devices with a change in base server url.

## Getting Started
##### Setting up environment-
    virtualenv env
    .\env\scripts\activate

##### Getting the requirements-
    cd e2e
    pip install -r requirements.txt 

##### Setting up server-
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver

###### Note-
Skip the migrations part if you are using the included database file. In case a new database is being created or you wish to clean the database : Add a starting message in the databse through admin.py (In the Message model - [a,1111]).

## Url Description
#### User
1.  user/uid - Chattoom for user
1.  ajax/slug - Messages sent from frontend are recieved here, encrypted, and sent to the server
1.  e1/uid - Diffie Hellman Key Exchange between users
1.  newMsgs/uid - New messages are recieved here using ajax
1. newMessageAvaialable/uid - When server recieves a new message then this url for the other user is pinged to inform the availability of new messages.

#### Server
1. server/save - New encrypted messages are recieved by the server here, to be stored in the database and the other user is informed about the availability of new messages.
1. server/all - The complete database, with all its messages messages from all users are output here.
1. server/fromTS - Users can demand messages from server by providing a date of start and a user id.

#### Test Url
- /test - is used for debugging across the server and user.

## Base Functions
#### baseFunctions.py
This file contains functions to create basic files for the project.
1. **generateKey(n,l=None)** - It is used to create privatekeys for the user, public key for common use and modulus key. I have used 128 charecter long private keys, 59 charecters long modulus key, and 64 charecters long public key.
1. **diffieHellmanMapping()** - This function is used to create string to numeric and numeric to string mapping. 

## Important Links
[https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange](https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange)
[https://simple.wikipedia.org/wiki/RSA_algorithm](https://simple.wikipedia.org/wiki/RSA_algorithm)



