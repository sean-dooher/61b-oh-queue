export const UPDATE_TICKETS = 'UPDATE_TICKETS';

export function updateTickets(tickets) {
    return {
        type: UPDATE_TICKETS,
        tickets
    };
}

export function getTickets() {
    return dispatch => fetch("/api/tickets", window.getHeader)
	.then(r => r.json().then(tickets => {
		dispatch(updateTickets(tickets));
	}));   
}