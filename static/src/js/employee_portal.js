/** @odoo-module */
console.log("employee_portal.js loaded");
import { PortalHomeCounters } from '@portal/js/portal';

PortalHomeCounters.include({
    /**
     * @override
     */
    _getCountersAlwaysDisplayed() {
        return this._super(...arguments).concat(['payoff_count',"payslip_count","allocation_count","approval_count","attendance_count"]);
    },
});
