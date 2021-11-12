from dateutil.relativedelta import relativedelta

from odoo.tests.common import tagged

from .common import PayrollTransactionCase


@tagged('hr_contract', 'post_install', '-at_install')
class HRContract(PayrollTransactionCase):

    def test_001_gross_salary(self):
        """Ensure gross salary is correct"""
        contract = self.env.ref('hr_payroll.hr_contract_gilles_gravie')
        self.env['hr.contract.gross.salary'].with_context(active_ids=contract.ids).create(
            {'net_salary': 50000}).set_wage()
        self.assertEqual(contract.wage, 64599.22, 'Wage not assigned correctly.')

    def test_002_net_gross_salary(self):
        """Ensure that gross salary is calculated correctly"""
        contract = self.env.ref('hr_payroll.hr_contract_gilles_gravie')
        contract.company_id.sudo().l10n_mx_edi_minimum_wage = 102.68
        contract.company_id.sudo().l10n_mx_edi_uma = 84.49
        self.env['hr.contract.gross.salary'].with_context(active_ids=contract.ids).create({
            'net_salary': 50000,
        }).set_wage()
        self.assertEqual(contract.wage, 64599.22, 'Incorrect wage calculated')

    def test_003_net_gross_salary_imss(self):
        """Ensure that gross salary with IMSS is calculated correctly"""
        contract = self.env.ref('hr_payroll.hr_contract_gilles_gravie')
        contract.company_id.sudo().l10n_mx_edi_minimum_wage = 102.68
        contract.company_id.sudo().l10n_mx_edi_uma = 84.49
        self.env['hr.contract.gross.salary'].with_context(active_ids=contract.ids).create({
            'net_salary': 50000,
            'include_imss': True,
        }).set_wage()
        self.assertEqual(contract.wage, 67067.83, 'Incorrect wage calculated')

    def test_004_net_gross_salary_subsidy(self):
        """Ensure that gross salary with IMSS + subsidy is calculated correctly"""
        contract = self.env.ref('hr_payroll.hr_contract_gilles_gravie')
        contract.company_id.sudo().l10n_mx_edi_minimum_wage = 102.68
        contract.company_id.sudo().l10n_mx_edi_uma = 84.49
        self.env['hr.contract.gross.salary'].with_context(active_ids=contract.ids).create({
            'net_salary': 6000.00,
            'include_imss': True,
            'include_subsidy': True,
        }).set_wage()
        self.assertEqual(contract.wage, 6316.52, 'Incorrect wage calculated')

    def test_sdi_variable(self):
        """Ensure that SDI variable is correctly calculated."""
        payroll = self.create_payroll()
        payroll.date_from = payroll.date_from - relativedelta(months=2)
        payroll.date_to = payroll.date_to - relativedelta(months=2)
        payroll.input_line_ids[0].input_type_id = self.env.ref(
            'l10n_mx_edi_payslip.hr_payslip_input_type_perception_028_g')
        payroll.compute_sheet()
        payroll.action_payslip_done()
        payroll.contract_id.compute_integrated_salary_variable()
        self.assertTrue(payroll.contract_id.l10n_mx_edi_sdi_variable, 'SDI variable not assigned.')
