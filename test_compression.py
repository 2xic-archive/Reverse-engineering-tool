import zlib  
import binascii


'''


	hopper uses 10 seconds (9739ms) to load the big binary I am working on loading
	FAST!

	this was intresting, a bit relevant as well
		-	https://speakerdeck.com/perone/pytorch-under-the-hood?slide=104

	need to make the software usable for bigger binaries as well.	
	json does generate a lot of (big)data.

	I kinda want to keep json mainly for readability reasons, makes reading 
	the code a lot easier. However the fact that it generated ~17MB of data is 
	way to much. Trafering that over the socket usally makes my session end,
	the times the session does not end it takes way to much time for the socket
	to recive the data. Not good. (this is when I run the backend not on localhost)

	Using zlib I got almost 5.5x smaller size. So that was great, a 3mb 
	data packet is better, but still very big. I can also split up parts of 
	the json. Currently I send the grapth data and section data in one
	packet. (mostly to keep the GUI synchronized). I can only split up so
	I send one and one section with data. However, the .text section is 
	still HUGE in a big binary so a smarter way have to be thougths off.



	Some analysis of the key functions of the GUI
		The gui get's less smooth when big binary gets loaded. I don't think that is because of the 
		underlaying functions.

		Small analysis:
			Currently the javascript function create_flat_view is O(nm) in theorhy, but it is a lot closer to
			O(n) in the practice, because most of the data is code, not section name.

			same is true for create_blocks, it's in theorhy O(nms), however s is just the section name and all of the
			actual bottleneck will be in the node and edge data, in other words O(nm) because section name is
			minimal. You need to know both edges and nodes to be able to create a block so hard to make this better.


			create_grapth is just O(nm). Because each section is spesfied before it get's drawn. N for node and m for 
			each edge.
			
		What I will do is create some good testcases for each of thesse functions. Generate X elements based on 
		test data. Then I will check if the bottleneck is because of the design of the functions or if it is
		because of the way the web standard is. I'm well aware that javascript has a bit of a mess underneath.
		This will help me debug if I should use better datastructure than relaying on document.get * . I kinda
		thought that javascript had gotten some good datastrctures over the years, but maybe not.

			-	after having written a small test on generating a lot of rows my first thougth was that my
			problems migth just be the memory footprint of the json data. 

	-	Another problem (because of the json) is the memory usage, I want to query the server for what
		is possible IF it does not make the user experience BAD.

			-	I should make the creation of new rows in a thread...


	I know the backend, especially the code responsible for the control grapth could need a optimization.
	However, generating a control grapth is not easy so I'm not sure how good of an alogritm you can get. 
	Need to do more research.


	why not just switch from web to qt? 
		I can write code in the web way faster than I can with QT. Also
		it will look nicer. There are some bottlenecks with writing code
		for the web that I just have to be cleaver about. However I'm sure QT can hold 
		way more objects in frame than a browser can, but program speed is not the reason
		why I choose to write the GUI in web. I want a seperate backend and frontend and having
		the web as a frontend makes the seperation easily. 

	I have also been thiking a bit about
		having features like if you are on a ctw team and multiple people are working on a binary
		you can have evrey team member working on a "fork" of the binary and then being able to push
		to a "master" fork, that then sends out a update to all the other forks. Then you can decide
		to merge that change if you want to. For instance, you find a key instruction that makes something
		bad/intresting happen. You give that instruction line a good name, push it to master and the other
		team members can decide to merge that comments.  



		
'''
import base64

data = "sega".encode() #open("big_binary.txt", "r").read().encode()

compress = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, +15)  
compressed_data = compress.compress(data)  
compressed_data += compress.flush()


print(list())

print(str(base64.b64encode(compressed_data)))


data2 = zlib.decompressobj()  
decompressed_data = data2.decompress(compressed_data)#[i:i+1024])
decompressed_data += data2.flush()

#print(decompressed_data)
#open("comressed", "w").write(str(base64.b64encode(decompressed_data)))


decompressed_data = str(decompressed_data)



#print('Decompressed data: ' + decompressed_data)


print('Original: %i' % len(data) )
print('Compressed data: %i' % len(str(binascii.hexlify(compressed_data))))
assert(str(decompressed_data) == str(data))