import { connect } from 'react-redux'
import { getTickets } from '../../actions/ticketActions';
import { MainView } from '../../components/content/main';

const mapStateToProps = (state) => {
    return {tickets: state.api.tickets};
};

const mapDispatchToProps = (dispatch) => {
    return {
        refreshTickets: () => dispatch(getTickets())
    };
};

let MainViewApi = connect(mapStateToProps, mapDispatchToProps)(MainView);
export default MainViewApi;
