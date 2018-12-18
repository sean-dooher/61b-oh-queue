import React from "react";
import NavLinkBar from "../../containers/navigation/NavLinkBar";
import PropTypes from "prop-types";

export class Navigation extends React.Component {
    constructor(props) {
        super(props);
    }
    render(){
        return (
            <div>
                <NavLinkBar changePage={this.props.changePage} />
                {this.props.children}
            </div>
        );
    }
}

Navigation.propTypes = {
    changePage: PropTypes.func
}

