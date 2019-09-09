var fs = require('fs');

var express = require('express');
const fetch = require("node-fetch");
var FormData = require('form-data');
var bodyParser = require('body-parser');
var multer = require('multer')
var upload = multer().single('file')


var app = express();
var router = express.Router();
var port = 4000;


app.use(express.json());
app.use('/', express.static(__dirname + '/static/build'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded());
// in latest body-parser use like below.
app.use(bodyParser.urlencoded({extended: true}));


var serverPath = "http://localhost:5555";

function ServerException(msg) {
    this.msg = msg;
    this.name = "ServerException";
}

var routes = {
    PING: "/ping",
    LOGIN: "/users/login",
    DATASETS: "/datasets",
    MODELS: "/models",
    MODEL: "/models/:id",
};

var httpMethods = {
    POST: "POST",
    GET: "GET"
};


var executeFetch = async (method, url, body, headers) => {
    let settings = {
        method: method,
        headers: headers,
        body: body
    };
    const response = await fetch(serverPath + url, settings);
    if (response.ok) {
        return await response.json()
    }
        throw new ServerException(response)

};


var executeFetchJson = async (method, url, body) => {
    let jsonHeaders = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    };
    return executeFetch(method, url, body, jsonHeaders)
};

app.get(routes.PING, async (req, res, next) => {
    console.log("ping")
    try {
        res.send("pong")
    } catch (e) {
        //this will eventually be handled by your error handling middleware
        next(e)
    }
});

app.post(routes.LOGIN, async (req, res) => {
    try {
        res.json(executeFetchJson(httpMethods.POST, routes.LOGIN, JSON.stringify(req.body)));
    } catch (e) {
        //this will eventually be handled by your error handling middleware
        console.log(e)
    }
});

app.post(routes.DATASETS, async (req, res) => {
    try {
        upload(req, res, function (err) {
            if (err instanceof multer.MulterError) {
                return res.status(500).json(err)
            } else if (err) {
                return res.status(500).json(err)
            }
            let formData = new FormData()
            formData.append(req.file["fieldname"], req.file["buffer"], {
                filename: req.file["originalname"],
                contentType: req.file["mimetype"]
            });
            return res.json(executeFetch(httpMethods.POST, routes.DATASETS, formData));
            ;

        })

    } catch (e) {
        //this will eventually be handled by your error handling middleware
        console.log(e)
    }
});


app.get(routes.DATASETS, async (req, res) => {
    try {
        res.json(await executeFetchJson(httpMethods.GET, routes.DATASETS));
    } catch (e) {
        //this will eventually be handled by your error handling middleware
        console.log(e)
    }
});


app.get(routes.MODELS, async (req, res) => {
    try {
        res.json(await executeFetchJson(httpMethods.GET, routes.MODELS));
    } catch (e) {
        //this will eventually be handled by your error handling middleware
        console.log(e)
    }
});


app.get(routes.MODEL, async (req, res) => {
    try {
        console.log(req.param("tagId"))
        res.json(await executeFetchJson(httpMethods.GET, routes.MODEL));
    } catch (e) {
        //this will eventually be handled by your error handling middleware
        console.log(e)
    }
});


app.listen(port, () => console.log(`Example app listening on port ${port}!`))