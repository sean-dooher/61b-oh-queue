import React from "react";
import {connect} from 'react-redux'
import {Navigation} from "./components/navigation/Navigation";
import {changePage} from "./actions/navActions";
import {Router, Route, Switch} from "react-router-dom";
import { createBrowserHistory } from 'history';
import MainViewApi from "./containers/contents/mainAPI";

let history = createBrowserHistory();

history.listen(
    location => {
       window.store.dispatch(changePage(location.pathname));
   }
)

export class AppBase extends React.Component {
    componentDidMount(){
      window.store.dispatch(changePage(history.location.pathname));
      window.react_history = history;
    }

    render() {
        return (
            <Router history={history}>
                <Navigation> 
                    <Route exact={true} path="/queue" component={MainViewApi}/>
                </Navigation>
            </Router>);
    }
}

AppBase.propTypes = {
};

const mapStateToProps = (state) => {
    return {};
};


let App = connect(mapStateToProps, null)(AppBase);
export default App;