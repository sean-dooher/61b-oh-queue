import { connect } from 'react-redux'
import { HeaderBar } from '../../components/navigation/HeaderBar'
import { changePage } from '../../actions/navActions';

const mapStateToProps = (state) => {
    return {links: state.navbar.links, active: state.navbar.active};
};

const mapDispatchToProps = (dispatch) => {
    return {};
};

let NavLinkBar = connect(mapStateToProps, mapDispatchToProps)(HeaderBar);
export default NavLinkBar;
