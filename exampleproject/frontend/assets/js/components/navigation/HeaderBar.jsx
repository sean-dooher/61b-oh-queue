import React from "react";
import PropTypes from "prop-types";
import { Link } from 'react-router-dom'

export class HeaderBar extends React.Component {
    render() {
        return <header>
            <div className="navbar navbar-expand-md navbar-dark bg-dark">
                <a className="navbar-brand" href="/">React Project</a>
                <button className="navbar-toggler d-lg-none" type="button" data-toggle="collapse"
                        data-target="#main-nav" aria-controls="main-dev" aria-expanded="false"
                        aria-label="Toggle navigation">
                    <span className="navbar-toggler-icon"/>
                </button>
                <div className="collapse navbar-collapse" id="main-nav">
                    <ul className="navbar-nav mr-auto">
                        {
                            this.props.links.map((link, key) => (
                                    <li className={"nav-item" + (this.props.active === link.name ? " active" : "")} key={key}>
                                        <Link className="nav-link" to={link.href} onClick={() => this.props.changePage(link.name)}>{link.name}</Link>
                                    </li>))
                        }
                    </ul>
                </div>
            </div>
        </header>;
    }
}

HeaderBar.propTypes = {
    links: PropTypes.array,
    active: PropTypes.string,
    changePage: PropTypes.func
};
