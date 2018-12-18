import React from "react";
import {connect} from 'react-redux'
import {Navigation} from "./components/navigation/Navigation";
import PropTypes from "prop-types";

export class AppBase extends React.Component {
    render() {
        return (
            <Navigation>
                
            </Navigation>);
    }
}

AppBase.propTypes = {
};

const mapStateToProps = (state) => {
    return {};
};


let App = connect(mapStateToProps, null)(AppBase);
export default App;