# Routes

## POST/Register
To register, go to host/register and in the request body in JSON, put in "author" with an username and "passwd" with a password.
![register route](https://i.imgur.com/sGnfC0T.png)

## GET/Login
To login, go to host/login and in the request body, put your username (author) and your password (passwd) after creating an account. You should then receive an authorised message and a token. Put that token as a bearer for authorization to be able to access protected content.
![login route](https://i.imgur.com/NgZpKSP.png)
![token example for login route](https://i.imgur.com/COhRTLA.png)

## GET/entries
Here you're able to see all entries on the API.
![get route all examples](https://i.imgur.com/h6P69F0.png)

## GET/entries/\<id>
Here you're able to see a specific entry. This means that if you only want to see the 4th entry you would go to host/entries/4.
![specific get example](https://i.imgur.com/3qPW6Bd.png)

## POST/entries
Here you're able to add your own entries. Just add a "game" key and "review" key to your JSON object and send the request!
![post route](https://i.imgur.com/xo8mJ7O.png)
![post route worked](https://i.imgur.com/5jhmCXC.png)

## PUT/entries/\<id>
Here you're able to update your own entries (you aren't able to change other people's). Just go to whichever entry you want to change and put the in the new details.
![put route](https://i.imgur.com/Ku7KK55.png)
![put route no dupes](https://i.imgur.com/xiLL30N.png)
![put route worked](https://i.imgur.com/El2rzuf.png)

## DELETE/entries/\<id>
Here you're able to delete your own entries (but not other people's). Just go to whichever entry you wish to delete and send the request.
![delete route](https://i.imgur.com/rjM6KHh.png)
![delete route worked](https://i.imgur.com/RvT6joN.png)
