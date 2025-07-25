/** @odoo-module */

import { PortalHomeCounters } from '@portal/js/portal';

PortalHomeCounters.include({
    /**
     * @override
     */
    _getCountersAlwaysDisplayed() {
        return this._super(...arguments).concat(['payoff_count',"payslip_count","allocation_count"]);
    },
});
