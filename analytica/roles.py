from rolepermissions.roles import AbstractUserRole

class Admin(AbstractUserRole):
    available_permissions = {

        'view_profile_analytic' : True,
        'view_profile_record': True,
        'view_profile_gis': True,

        'view_payment_analytic': True,
        'view_payment_record': True,
        'view_payment_gis': True,

        'view_performance_analytic': True,
        'view_performance_record': True,
        'view_performance_gis': True,
    }

class Contributor(AbstractUserRole):
    available_permissions = {
        'view_profile_analytic' : True,
        'view_profile_record': True,
        'view_profile_gis': True,

        'view_payment_analytic': True,
        'view_payment_record': True,
        'view_payment_gis': True,
        
        'view_performance_analytic': False,
        'view_performance_record': False,
        'view_performance_gis': False,
    }

class Member(AbstractUserRole):
    available_permissions = {

        'view_profile_analytic' : True,
        'view_profile_record': True,
        'view_profile_gis': True,

        'view_payment_analytic': False,
        'view_payment_record': False,
        'view_payment_gis': False,
        
        'view_performance_analytic': False,
        'view_performance_record': False,
        'view_performance_gis': False,
    }

class Guest(AbstractUserRole):
    available_permissions = {

        'view_profile_analytic' : False,
        'view_profile_record': False,
        'view_profile_gis': False,

        'view_payment_analytic': False,
        'view_payment_record': False,
        'view_payment_gis': False,
        
        'view_performance_analytic': False,
        'view_performance_record': False,
        'view_performance_gis': False,
    }

class NHPUser(AbstractUserRole):
    available_permissions = {

        'view_profile_analytic' : False,
        'view_profile_record': False,
        'view_profile_gis': False,

        'view_payment_analytic': False,
        'view_payment_record': False,
        'view_payment_gis': False,
        
        'view_performance_analytic': False,
        'view_performance_record': False,
        'view_performance_gis': False,

        'view_nhp_profile_analytic' : True,
        'view_nhp_profile_record' : True,
        'view_nhp_profile_gis' : True,


    }


