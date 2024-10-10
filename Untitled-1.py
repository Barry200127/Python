print("hello,world!")
print("sd")

from  flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    print("hello,world!")

if __name__ == '__main__':
    app.run(debug=True)  
    print("Server is running...")   