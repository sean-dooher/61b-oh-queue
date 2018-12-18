import React from "react";
import {render} from "react-dom";
import App from "./app";
import {mainApp} from "./reducers/reducers";
import {createStore, applyMiddleware} from 'redux';
import {Provider} from 'react-redux';
import ReduxThunk from 'redux-thunk';
import Cookies from "js-cookie";

window.getParams = {
    method: 'get',
    credentials: "same-origin",
    headers: {
        "X-CSRFToken": Cookies.get("csrftoken"),
        "Accept": "application/json",
        "Content-Type": "application/json"
    },
    cache: "reload",
};

window.postParams = {
    method: 'post',
    credentials: "same-origin",
    headers: {
        "X-CSRFToken": Cookies.get("csrftoken"),
        "Accept": "application/json",
        "Content-Type": "application/json"
    },
    cache: "reload",
};

window.putParams = {
    method: 'put',
    credentials: "same-origin",
    headers: {
        "X-CSRFToken": Cookies.get("csrftoken"),
        "Accept": "application/json",
        "Content-Type": "application/json"
    },
    cache: "reload"
};

window.deleteParams = {
    method: 'delete',
    credentials: "same-origin",
    headers: {
        "X-CSRFToken": Cookies.get("csrftoken"),
        "Accept": "application/json",
        "Content-Type": "application/json"
    },
    cache: "reload"
};

window.store = createStore(mainApp, applyMiddleware(ReduxThunk));

render(<Provider store={store}><App /></Provider>, document.getElementById('react-app'));
