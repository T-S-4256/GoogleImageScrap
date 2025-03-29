import requests
from bs4 import BeautifulSoup
import pymongo
from flask import Flask, render_template, request, jsonify
import os
import logging

app = Flask(__name__)


@app.route("/")
def HomePage():
    print("Home Page Fetched")
    return render_template("index.html")


@app.route("/review", methods=["POST", "GET"])
def ResultPage():
    if request.method == "POST":
        # TAKE INPUT FROM THE USER
        searchstring = request.form["searchValue"]

        # REPLACE SPACE WITH +
        searchstring = searchstring.replace(" ", "+")

        # CREATE AN URL
        searchUrl = f"https://www.google.com/search?sca_esv=8d80958cb2551b43&rlz=1C1JJTC_enIN1108IN1108&sxsrf=AHTn8zqh7xeOJyRSdErSf8HXeKANlqyGyw:1743225315089&q={searchstring}&udm=2&fbs=ABzOT_CkkUBxgBnVfpE7bSuDpclGRbjLQ45XVN0UfR5V5ce3jQM8PBCA8-CKa_Ojw56lXoDYpklyOFcFT1tyhvQlEcLnZ-54hGwEi5gcMTaQmqFU_WVkm_dh5_qk2Z27hJ5zDAkVvw6_yNKalu67rqHC2qmYeNCfdUXz516AnjOWEC9YRdO47sxdpauCT06aWPBZY3qLr9EtHlr6DLJv1zPFdUPtk6Inw-RkvW-zs5nC6VLh01D8M3BIPSa07LqHMYf5ofHtjvLfR5mc44M-CKQznDClHF1MnA&sa=X&sqi=2&ved=2ahUKEwj6ja2txK6MAxVuUGwGHTRKLW8QtKgLegQIFRAB&biw=1280&bih=598&dpr=1.5"

        # CREATE A FILE FOR SAVE THE LOGS
        my_dir = os.path.join(os.getcwd(), "LogData", "data.log")
        logging.basicConfig(filename=my_dir, level=logging.INFO)

        # DEFINE A HEADER FOR MIMIC THE REAL BROWSER REQUEST
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0 Safari/537.36"
        }

        # OPEN THE URL
        try:
            googleData = requests.get(searchUrl)
        except Exception as e:
            logging.info(e)

        # USED (.CONTENT) BECAUSE THE DATA IS IMAGE SO WE NEED BINARY FORMAT NOT IN TEXT
        # PARSE THE DATA IMTO HTML FORMAT
        try:
            google_HTML_data = BeautifulSoup(googleData.content, "html.parser")
        except Exception as e:
            logging.info(e)

        # FETCH ALL THE IMAGE TAGS
        ImagesLinkContainer = google_HTML_data.find_all("img")

        # DELETE THE WASTE DATA
        del ImagesLinkContainer[0]

        # CREATE A EMPTY LIST TO STORE ALL THE IMAGES DATA
        dataContainer = []

        # CREATE A PATH FOR STORING THE DATA
        my_path = os.path.join(os.getcwd(), "ImageData")

        # CONNECT WITH MONGO DB TO STORE THE DATA
        try:
            Client = pymongo.MongoClient(
                "mongodb+srv://Recursion:ReturnBaseValue@cluster0.i7kp3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
            )
            db = Client["GoogleImageScrap"]
            image_col = db["ImageData"]
        except Exception as e:
            logging.info(e)

        # FETCH EACH IMAGE
        for i in ImagesLinkContainer:
            # REQUEST THE IMAGE USING IMAGE LINK
            try:
                image_data = requests.get(i["src"])
            except Exception as e:
                logging.info(e)

            # GET THE BINARY FORMAT DATA OF THE  IMAGE DATA
            image_data = image_data.content

            # IMAGE STRORE FILE CREAING
            try:
                with open(
                    f"{my_path}\{searchstring.replace('+','')}_{ImagesLinkContainer.index(i)}.jpg",
                        "wb",
                ) as f:
                    f.write(image_data)
            except Exception as e:
                logging.info(e)

            # CRAETE A DICTIONARY OF EACH DATA
            my_dict = {"Url": i["src"], "Image": image_data}

            # STORE THE DICTIONARY INTO THE LIST
            dataContainer.append(my_dict)

            # STORE THE DATA INOT THE DATAABSE
            try:
                image_col.insert_many(dataContainer)
            except Exception as e:
                logging.info(e)
        # CLOSE THE LOG
        logging.shutdown()
        return render_template('result.html',container=dataContainer)
    else:
        logging.info("Not POST Method Fetched")
        return render_template("index.html")


if __name__ == "__main__":
    app.run(host='127.0.0.1')
