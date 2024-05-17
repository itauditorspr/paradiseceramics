# -*- coding: utf-8 -*-

import operator
import logging
from odoo import api, fields, models, _
from zk import ZK, const
from odoo.exceptions import UserError
from odoo.addons.hr_attendance_punch.models.biometric_device import BiomtericDeviceInfo

_logger = logging.getLogger(__name__)

class UpaloadEmployee(models.TransientModel):
    _name = "upload.employee"
    _description = 'Upload Employee Wizard'

    employee_ids = fields.Many2many('hr.employee',string="Employees")

    def action_upload(self):
        active_id = self.env['biomteric.device.info'].browse(self.env.context.get('active_id'))
        for rec in self.employee_ids:
            if active_id.mapped('device_employee_ids').filtered(lambda r: r.employee_id.id == rec.id):
                pass
            else:
                _logger.info("Uploading employee: %s...." %(rec.name))

                # print('rec.first_name',rec.first_name)
                # print('rec.last_name',str(rec.last_name)[0])
                # print('rec.alias',rec.alias)
                #
                # if rec.category_code == 'LOCAL':
                #     employee_name = "%s %s" % (rec.first_name, str(rec.last_name)[0])
                # else:
                #     employee_name = "%s" % (rec.alias)

                sequence = int(self.env['ir.sequence'].next_by_code(active_id.sequence_id.code))
                try:
                    conn = active_id._connect_device()
                    conn.set_user(uid=int(sequence), name=rec.name, privilege=const.USER_DEFAULT, password='', user_id=str(sequence))
                    record_id = self.env['employee.attendance.devices'].sudo().create({
                        'device_id': active_id.id,
                        'name': rec.name,
                        'employee_id': rec.id,
                        'attendance_id': str(sequence)
                    })
                    if record_id:
                        _logger.info("Employee successfully uploaded....")
                except Exception as e:
                    _logger.info(Warning(e))
                conn.disconnect()

        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Employee uploaded!',
                'type': 'rainbow_man',
            }
        }
