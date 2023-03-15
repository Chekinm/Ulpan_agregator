import asyncio
import json
import haversine as hs
from src.request import request  # import our request function.

class ulpan():
    """ for current stange we will hardcode ulpan information
    but in the future we can create admin interface to add ulpan
    class properties also can be extended if needed"""
    def __init__(self, name='ulpan', coord =(0,0), link='./index.html', link_to_photo='', web_link='www.gov.il', dist=0, user_coord =(0,0)):
        self.name = name
        self.coord = coord
        self.link = link
        self.link_to_photo = link_to_photo 
        self.web_link = web_link
        self.dist = 0
        self.user_coord = user_coord

    def measure_dist(self, user_coord):
        """for now we need only one method
           - to measure distanse to user adress
           in the future we can add some rating or request about 
           free places"""
        self.dist =  hs.haversine(self.coord, user_coord)

# list of our ulpans#

a = ulpan(name='Gordon', coord=(32.085863013828636, 34.77188926210782), link = '/index.html',
          link_to_photo='https://ulpangordon.co.il/wp-content/uploads/2023/01/47-1024x683.jpg', 
          web_link='https://ulpangordon.co.il/',
          dist=0,
          )
b = ulpan('b',(32.066797729488634, 34.77080540392143),'./index.html','https://ulpangordon.co.il/wp-content/uploads/2023/01/47-1024x683.jpg', web_link='https://ulpangordon.co.il/',dist = 0,user_coord=(0,0))
c = ulpan('c',(32.166797729488634, 35.77080540392143),'./index.html','https://ulpangordon.co.il/wp-content/uploads/2023/01/47-1024x683.jpg', web_link='https://ulpangordon.co.il/',dist = 0,user_coord=(0,0))
d = ulpan('d',(28,40),'./index.html','https://ulpangordon.co.il/wp-content/uploads/2023/01/47-1024x683.jpg', web_link='https://ulpangordon.co.il/',dist = 0,user_coord=(0,0))
e = ulpan('e',(90,0),'./index.html','https://ulpangordon.co.il/wp-content/uploads/2023/01/47-1024x683.jpg', web_link='https://ulpangordon.co.il/',dist = 0,user_coord=(0,0))
f = ulpan('f',(90,0),'./index.html','https://ulpangordon.co.il/wp-content/uploads/2023/01/47-1024x683.jpg', web_link='https://ulpangordon.co.il/',dist = 0,user_coord=(0,0))

ulpan_list = [a,b,c,d,e,f]

def set_google_map(user_coord, ulpan_coord):
    g_direction_url = "https://www.google.com/maps/embed/v1/directions"
    origin = "&origin=" + str(user_coord)
    destin = "&destination=" + str(ulpan_coord)
    g_api = "?key="+"AIzaSyAW_jEvBezwNuaFUUg3u_CFLsZqk8_UNJU"
    mode = "&mode=walking"
    g_src = g_direction_url + g_api + origin + destin + mode
    return g_src

def ulpan_1():
    g_src = set_google_map(ulpan_list[0].user_coord, ulpan_list[0].coord)
    js.document.getElementById("map2").src = g_src

def ulpan_2():
    g_src = set_google_map(ulpan_list[1].user_coord, ulpan_list[1].coord)
    js.document.getElementById("map2").src = g_src

def ulpan_3():
    g_src = set_google_map(ulpan_list[2].user_coord, ulpan_list[2].coord)
    js.document.getElementById("map2").src = g_src
    

async def get_coord(address):
    """function request geo info for address_string we got from user input
    we search using microsoft bing api
    then transcript response into json obj 
    if no adress found or bing not sure (confidence is not high) 
    return error, if confidence 'high' return geo coordinates"""

    
    search_api = "http://dev.virtualearth.net/REST/v1/"
    api_key = 'ArGH_I3FimB7iNG-97oiz_24UeOtXfgpt66X3gYHR8A64AXAoXmO5uaq2j9oroHB'       
    base_url = search_api + "Locations?q=" + address + '&key=' + api_key 
    headers = {"Content-type": "application/json"}

    # we use function from pyscript tutorial to perform http request
    # it use pyfetch inside
    try:

        response = await request(f"{base_url}", method="GET", headers=headers)

        resp_json = (await response.json())
        number_of_variant = resp_json['resourceSets'][0]['estimatedTotal']
        if number_of_variant == 0 or resp_json['resourceSets'][0]['resources'][0]['confidence'] != "High":
            # Bing cannot find adress or don't sure about it so we raise an adress error
            # wrong adress error box raise
            error_obj = js.document.getElementById("error_box")
            error_msg = js.document.getElementById("error_msg")
            error_action = js.document.getElementById("error_action")
            error_obj.classList.remove ('hidden')
            error_msg.innerText = "Sorry, we are not sure about your address! \n Check it and try again!"
            error_action.innerText = "Try again"

            error_obj.classList.remove ('hidden')  # make it visible       
        else:
            coord = tuple(resp_json['resourceSets'][0]['resources'][0]['point']['coordinates'])
    
    except:
        # some general problem occurs on the server side
        # can't do nothing until them fix it
        error_obj = js.document.getElementById("error_box")
        error_msg = js.document.getElementById("error_msg")
        error_action = js.document.getElementById("error_action")
        error_obj.classList.remove ('hidden')
        error_msg.innerText = "Looks that something goes wrong with remote servers or coonection has lost!"
        error_action.innerText = "Try again later!"
        
        coord = (32.08530045, 34.78180695) # set to default coordinates (Tel-Aviv center)
    
    return coord


async def find_ulpan(ulpan_list):
    """function which performs onlick on find button
    user enter his adress, we found it using get_coord function
    then we calcualte distanse from user to each ulpan in the list
    then sort it by distanse and present closest 3 on the page"""

    address = Element("user_address").value
    user_coord = await get_coord(address)

    for ulpan in ulpan_list:
        ulpan.measure_dist(user_coord)
        ulpan.user_coord = user_coord   # we will use it to change direction to ulpan on map 
                                    #maps on hover on ulapn name element 
    ulpan_list.sort(key=lambda x: x.dist)

    for i in  range(3):   # we add text to corresponding div and made it unhidden
                          # i can do it in different way, but think this wau is better
        elem_id = 'ulpan' + str(i + 1)
        ulpan_name_obj_id = 'ulpan' + str(i + 1)+'_name'
        ulpan_dist_obj_id = 'ulpan' + str(i + 1)+'_dist'
        js.document.getElementById(ulpan_name_obj_id).innerText = ulpan_list[i].name
        js.document.getElementById(ulpan_dist_obj_id).innerText = 'Just ' + str(round(ulpan_list[i].dist,2)) + ' km from you!'
        js.document.getElementById(elem_id).classList.remove ('hidden')


    g_src = set_google_map(user_coord, ulpan_list[0].coord)
    js.document.getElementById("map2").src = g_src
    



def ulpan_1():
    g_src = set_google_map(ulpan_list[0].user_coord, ulpan_list[0].coord)
    js.document.getElementById("map2").src = g_src

def ulpan_2():
    g_src = set_google_map(ulpan_list[1].user_coord, ulpan_list[1].coord)
    js.document.getElementById("map2").src = g_src

def ulpan_3():
    g_src = set_google_map(ulpan_list[2].user_coord, ulpan_list[2].coord)
    js.document.getElementById("map2").src = g_src

def close_error_msg():

    error_obj = js.document.getElementById("error_box")
    error_obj.classList.add ('hidden')


# async def main()
#     await print(get_distance())

# asyncio.run(main())
# #asyncio.ensure_future(main())
