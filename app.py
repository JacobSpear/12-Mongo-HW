from flask import Flask, render_template
from scrape_mars import scrape
import pymongo


app = Flask(__name__)

conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)
db = client.mars 
mars_info = db.mars_info

@app.route("/scrape")
def write_db():
    data = scrape()
    mars_info.update({},data,upsert=True)
    return redirect("/", code=302)

@app.route("/")
def home():
    data = mars_info.find()
    return render_template("index.html",data = data)








if __name__=="__main__":
    app.run(debug=True)