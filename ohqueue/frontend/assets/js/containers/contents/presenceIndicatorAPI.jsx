import { connect } from 'react-redux'
import { PresenceIndicator } from '../../components/content/presenceIndicator';

const mapStateToProps = (state) => {
    return {presence: {students: 12, staff: 2}};
};

const mapDispatchToProps = (dispatch) => {
    return {};
};

let PresenceIndicatorApi = connect(mapStateToProps, mapDispatchToProps)(PresenceIndicator);
export default PresenceIndicatorApi;
