import React from "react";
import {connect} from 'react-redux'
import {Navigation} from "./components/navigation/Navigation";
import {PageOne} from "./components/content/page1";
import {PageTwo} from "./components/content/page2";
import {changePage} from "./actions/navActions";
import {Router, Route, Switch} from "react-router-dom";
import { createBrowserHistory } from 'history';

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
                    <Route exact={true} path="/queue" component={PageOne}/>
                    <Route path="/queue/page2" component={PageTwo}/>
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