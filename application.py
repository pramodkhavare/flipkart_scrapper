from flask import Flask,request,jsonify,render_template
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
logging.basicConfig(filename="scrapper.log",level=logging.INFO)
application=Flask(__name__) 
app=application
@app.route("/",methods=["GET"])
def home_page():
    return render_template("index.html")                                         

@app.route("/review",methods=["GET" , 'POST'])
def index():
    if request.method=="POST":
        try:
            searchstring=request.form["content"].replace(" ","")
            flipkart_url="https://www.flipkart.com/search?q="+searchstring
            uclient=uReq(flipkart_url)                 #uReq used to hit URL directly(without clicking in console)

            flipkart_page=(uclient.read())             #You will get soursecode in html format 
            flipkart_html=bs(flipkart_page,"html.parser")  #parse means divide (a sentence) into grammatical parts and identify the parts and their relations to each other
                                            #    The HTML parser is a structured markup processing tool. It defines a class called HTMLParser, ​which is used to parse HTML files. It comes in handy for web crawling​.
            bigboxes=flipkart_html.find_all("div",{"class":"_1AtVbE col-12-12"})
            # del bigboxes[0:3]
            # box = bigboxes[0]
            box=bigboxes[2]

            productlink="https://www.flipkart.com"+(box.div.div.div.a['href'])
            productreq=requests.get(productlink)  #The requests module allows you to send HTTP requests using Python. The HTTP request returns a Response Object with all the response data (content, encoding, status, etc).
            productreq.encoding='utf-8'
            prod_html=bs(productreq.text, "html.parser")
 
            # print(prod_html)
            comment_boxes=prod_html.find_all("div",{"class":"_16PBlm"})
            # comment_box=comment_boxes[0]
            # print((comment_boxes))
        
            # create File 
            headers= "Product, Customer Name, Rating, Heading, Comment \n"
            filename = searchstring+".csv"
            fw = (open(filename,"w"))
            fw.write(headers)
                    
            reviews = []
            for commentbox in comment_boxes:
                try:
                    comment = commentbox.div.div.find_all("div",{"class":""})[0].div.text
                except :
                    logging.info("comment Not available")  
                try:  
                    name = commentbox.div.div.find_all("p",{"class":"_2sc7ZR _2V5EHH"})[0].text
                except :
                    logging.info("Name NOt Available")
                try:    
                    rating = commentbox.div.div.div.find_all("div",{"class":"_3LWZlK _1BLPMq"})[0].text
                except:
                    logging.info('Rating Not Available')
                # Create dictionary and Add data
                mydict={"Product":searchstring  ,"Name":name,"Rating":rating,"Comment":comment}
                reviews.append(mydict)
            logging.info("log my final result {}".format(reviews))
            return render_template('result.html',reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            logging.info(e)
            return "somrthing went wrong"
    else:   
        logging.info("Not Available") 
if __name__ == '__main__':
    app.run(host="127.0.0.1",port="5000")
    