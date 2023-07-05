# FIXMY PHONE
#### Video Demo:  <https://youtu.be/6NQwZOIfca8>
#### Description:
It is a program that helps the user to manage data such as clients or devices information, this application will permit to:
- register users 
- add or delete clients
- add or delete devices
- fix,receive paiement and return devices to the client
- history of user activities 
#### Centents:
there is 2 directory:
1. static has:
	- png files for set an icon of our website 
	- styles.css : set some css style
	- fontawesome : this is fontawesome library i set it locally in my website (this library content icons that i used in some pages )
2. templates:
	- layout.html:
		- is the main template and it has :
			1. head tag : 
				- link tag to set bootstrap and jquery 
				- link tag to set an icon 
				- title tag for tite site
				- link tag for fontawesome icons
			2. body tag : 
				- navbar for menu
				- repaire modal (contains form of inputs that i used on it some regular expression with css style)
				- add device modal (contains form of inputs that i used on it some regular expression with css style)
				- pick up modal
			3. script tag :
				- has some js to style the selected menu
			4. main block :
				- to permit flask inject the others template code in this block
			5. title block :
				- change title for every page (permit to flask inject the title of the template page code in this block)
	- register.html :
		- it is the extends of layout template and it has :
			1. title block :
				- content the title page
			2. main block :
				- registration form :
					- user information inputs 
					- submit button
	- login.html :
		- it is the extends of layout template and it has :
			1. title block :
				- content the title page
			2. main block :
				- login form :
					- user information inputs
					- submit button
	- settings.html :
		- it is the extends of layout template and it has :
			1. title block :
				- content the title page
			2. main block :
				- settings form :
					- user information inputs
					- submit button
	- index.html :
		- it is the extends of layout template and it has :
			1. title block :
				- content the title page
			2. main block :
				- search and filter section
				- table of data
	- add_client.html :
	this template is use as a clients api when i use ajax and it will give the user a dropbox of option and it will generate when the user add or delete a client
	- apology.html :
	this template generate if we want to inform the user with some information in case of error and it has :
		1. title block :
			- content the title page
		2. main block :
			- image whith the error code on it
	- del_device.html :
	this template generate when the user delete a device and it contents is a table of information about the exist devices in the database, if there is no device it will show a message that there is no devices to show
	- delete_client.html :
	this use just as route to skip the error message of flask and it has a function "delete()" in app.py
	- devices_list.html :
	this template will generate when the user select a client and it content a table of information about the client's devices 	
	- devices_table.html :
	this tamplete will generate when the user search or apply a filter on the devices in the home page 
	- drop_off.html :
	this template will generate when the user select drop off from the menu and it has :
		1. title block :
			- content the title page
		2. main block :
			- here we have two sections :
				- one for the selected client (we can add more client if you want)
				- and the other for the client's devices (we can add more devices if you want)
	- history.html :
	this template is used as a history log and it has:
		- 1. title block :
			- content the title page
		2. main block :
		table of infotmation about what happened and at what time
2. app.py:
   	- is the python application and it has libraries ,functions and routes :
   	  	- libraries like: cs50 ,Flask, flask_session ...
   	  	- functions like: registration ,login, logout ...
3. helpers.py:
   	- is a helper make us focus and reduce the code in our app.py code and it has:
   		- some useful functions:
   	   		- apology, login_required, clean_txt, is_number ....
4. fixphone.db: it is sqlite3 database of our application it has :
   	- tables: users, clients, devices, ....
	- indexes: 
5. requirements: contents cs50 Flask Flask-Session requests

